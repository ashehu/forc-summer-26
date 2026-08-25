#!/usr/bin/env python3
"""A small, inspectable retrieval-augmented question-answering pipeline."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

LAB_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB_DIR.parent))

from common import normalized, openai_client, text_model, write_json  # noqa: E402


CORPUS_DIR = LAB_DIR / "data" / "corpus"
QUESTIONS_PATH = LAB_DIR / "data" / "questions.json"
OUTPUT_PATH = LAB_DIR / "output" / "answer.json"
TOP_K = 3
CHUNK_WORDS = 55
CHUNK_OVERLAP = 12
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
METADATA_FIELDS = {"DOCUMENT_ID", "TITLE", "GENRE", "DATE", "SOURCE_PAGE", "SOURCE_URL"}


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.casefold())


def tfidf_vectors(documents: dict[str, str], query: str) -> tuple[dict[str, dict[str, float]], dict[str, float]]:
    token_counts = {name: Counter(tokenize(text)) for name, text in documents.items()}
    document_frequency = Counter()
    for counts in token_counts.values():
        document_frequency.update(counts.keys())

    count = len(documents)
    idf = {term: math.log((1 + count) / (1 + frequency)) + 1 for term, frequency in document_frequency.items()}

    def vector(counts: Counter[str]) -> dict[str, float]:
        total = sum(counts.values()) or 1
        return {term: (frequency / total) * idf.get(term, 0.0) for term, frequency in counts.items()}

    return {name: vector(counts) for name, counts in token_counts.items()}, vector(Counter(tokenize(query)))


def cosine(first: dict[str, float], second: dict[str, float]) -> float:
    dot = sum(value * second.get(term, 0.0) for term, value in first.items())
    first_norm = math.sqrt(sum(value * value for value in first.values()))
    second_norm = math.sqrt(sum(value * value for value in second.values()))
    return dot / (first_norm * second_norm) if first_norm and second_norm else 0.0


def chunk_text(text: str, chunk_words: int = CHUNK_WORDS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    if chunk_words < 1:
        raise ValueError("chunk_words must be positive")
    if overlap < 0 or overlap >= chunk_words:
        raise ValueError("overlap must be at least 0 and smaller than chunk_words")
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_words, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - overlap
    return chunks


def parse_document(path: Path) -> tuple[dict[str, str], str]:
    metadata: dict[str, str] = {}
    body_lines: list[str] = []
    in_body = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() == "TEACHING EXCERPT":
            in_body = True
            continue
        if not in_body and ":" in line:
            key, value = line.split(":", 1)
            if key in METADATA_FIELDS:
                metadata[key.casefold()] = value.strip()
                continue
        if in_body:
            body_lines.append(line)
    body = "\n".join(body_lines).strip()
    if not body:
        raise ValueError(f"No TEACHING EXCERPT found in {path.name}")
    return metadata, body


def load_chunks(chunk_words: int = CHUNK_WORDS, overlap: int = CHUNK_OVERLAP) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    for path in sorted(CORPUS_DIR.glob("*.txt")):
        metadata, body = parse_document(path)
        for index, text in enumerate(chunk_text(body, chunk_words, overlap), start=1):
            chunks.append(
                {
                    "chunk_id": f"{path.name}#{index}",
                    "filename": path.name,
                    "chunk_index": index,
                    "text": text,
                    **metadata,
                }
            )
    return chunks


def retrieve(
    question: str,
    top_k: int = TOP_K,
    chunk_words: int = CHUNK_WORDS,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict[str, Any]]:
    chunks = load_chunks(chunk_words, overlap)
    text_by_id = {chunk["chunk_id"]: chunk["text"] for chunk in chunks}
    chunk_by_id = {chunk["chunk_id"]: chunk for chunk in chunks}
    document_vectors, query_vector = tfidf_vectors(text_by_id, question)
    ranked = sorted(
        ((chunk_id, cosine(vector, query_vector)) for chunk_id, vector in document_vectors.items()),
        key=lambda item: item[1],
        reverse=True,
    )[:top_k]
    return [{**chunk_by_id[chunk_id], "score": round(score, 3)} for chunk_id, score in ranked]


def grounded_answer_model():
    try:
        from pydantic import BaseModel
    except ImportError as exc:
        raise SystemExit("Install requirements.txt before using --api.") from exc

    class GroundedAnswer(BaseModel):
        answer: str
        citations: list[str]
        evidence_quotes: list[str]
        not_found: bool

    return GroundedAnswer


def answer_with_api(question: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
    context = "\n\n".join(
        f"SOURCE [{item['filename']}] CHUNK [{item['chunk_id']}]\n"
        f"GENRE [{item.get('genre', 'unknown')}] ORIGINAL [{item.get('source_url', 'not supplied')}]\n"
        f"{item['text']}"
        for item in evidence
    )
    response = openai_client().responses.parse(
        model=text_model(),
        input=[
            {
                "role": "system",
                "content": (
                    "Answer only from the supplied sources. Cite factual claims using exact filenames. "
                    "Return one or two short verbatim evidence quotes. If the sources do not answer "
                    "the question, set not_found true and say so plainly. Distinguish reported actions, "
                    "proposals, internal messaging, and independently evaluated outcomes. Do not fill gaps "
                    "with outside knowledge or provide medical advice."
                ),
            },
            {"role": "user", "content": f"QUESTION\n{question}\n\n{context}"},
        ],
        text_format=grounded_answer_model(),
    )
    return response.output_parsed.model_dump()


def validate(answer: dict[str, Any], evidence: list[dict[str, Any]]) -> list[str]:
    problems: list[str] = []
    citations = answer.get("citations", [])
    quotes = answer.get("evidence_quotes", [])
    if not normalized(answer.get("answer")):
        problems.append("Answer text is empty.")
    if not answer.get("not_found", False) and not citations:
        problems.append("A supported answer must include at least one citation.")
    if not answer.get("not_found", False) and not quotes:
        problems.append("A supported answer must include at least one evidence quote.")
    by_name: dict[str, list[str]] = {}
    for item in evidence:
        by_name.setdefault(item["filename"], []).append(item["text"])
    for citation in citations:
        if citation not in by_name:
            problems.append(f"Citation was not retrieved: {citation}")
    combined = "\n".join(item["text"] for item in evidence)
    for quote in quotes:
        if normalized(quote) not in normalized(combined):
            problems.append(f"Quote not found verbatim: {quote}")
    return problems


def show_evidence(question: str, evidence: list[dict[str, Any]]) -> None:
    print(f"\nQUESTION\n{question}\n\nRETRIEVED EVIDENCE")
    for item in evidence:
        preview = " ".join(item["text"].split())[:240]
        print(
            f"  [{item['chunk_id']}] score={item['score']:.3f}\n"
            f"    genre: {item.get('genre', 'unknown')}\n"
            f"    original: {item.get('source_url', 'not supplied')}\n"
            f"    {preview}…"
        )


def show_chunks(chunks: list[dict[str, Any]]) -> None:
    print("\nCHUNKS")
    for item in chunks:
        preview = " ".join(item["text"].split())[:150]
        print(
            f"  [{item['chunk_id']}] {len(item['text'].split())} words · "
            f"{item.get('genre', 'unknown')}\n    {preview}…"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", action="store_true", help="Generate a grounded answer with the OpenAI API.")
    parser.add_argument("--question", help="Ask one question instead of the three course questions.")
    parser.add_argument("-k", "--top-k", type=int, default=TOP_K, help="Number of chunks to retrieve.")
    parser.add_argument("--chunk-words", type=int, default=CHUNK_WORDS, help="Maximum words per chunk.")
    parser.add_argument("--overlap", type=int, default=CHUNK_OVERLAP, help="Words repeated across adjacent chunks.")
    parser.add_argument("-c", "--show-chunks", action="store_true", help="Print the chunks created before retrieval.")
    args = parser.parse_args()

    chunks = load_chunks(args.chunk_words, args.overlap)
    document_count = len({chunk["filename"] for chunk in chunks})
    print(
        f"PIPELINE\nDocuments: {document_count} · Chunks: {len(chunks)} · "
        f"Vectorizer: TF-IDF · Similarity: cosine · top_k: {args.top_k}"
    )
    if args.show_chunks:
        show_chunks(chunks)

    questions = [args.question] if args.question else json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    for question in questions:
        evidence = retrieve(question, args.top_k, args.chunk_words, args.overlap)
        show_evidence(question, evidence)
        if not args.api:
            print(
                "\nOFFLINE TASK\n"
                "  1. Decide whether this evidence packet answers the question.\n"
                "  2. Label each source as a report, proposal, internal message, or evaluation.\n"
                "  3. Write a short answer—or say 'not found.'\n"
                "  4. Cite the filename(s), then verify one quote against the original URL."
            )
            continue

        answer = answer_with_api(question, evidence)
        problems = validate(answer, evidence)
        artifact = {"question": question, "retrieved": evidence, "answer": answer, "validation_problems": problems}
        write_json(OUTPUT_PATH, artifact)
        print(f"\nANSWER\n{answer['answer']}")
        print("Citations:", ", ".join(answer["citations"]) or "none")
        print("Verification:", "passed" if not problems else "; ".join(problems))


if __name__ == "__main__":
    main()
