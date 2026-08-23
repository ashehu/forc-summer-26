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
TOP_K = 2
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


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


def retrieve(question: str, top_k: int = TOP_K) -> list[dict[str, Any]]:
    documents = {path.name: path.read_text(encoding="utf-8") for path in sorted(CORPUS_DIR.glob("*.txt"))}
    document_vectors, query_vector = tfidf_vectors(documents, question)
    ranked = sorted(
        ((name, cosine(vector, query_vector)) for name, vector in document_vectors.items()),
        key=lambda item: item[1],
        reverse=True,
    )[:top_k]
    return [{"filename": name, "score": round(score, 3), "text": documents[name]} for name, score in ranked]


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
    context = "\n\n".join(f"SOURCE [{item['filename']}]\n{item['text']}" for item in evidence)
    response = openai_client().responses.parse(
        model=text_model(),
        input=[
            {
                "role": "system",
                "content": (
                    "Answer only from the supplied sources. Cite factual claims using exact filenames. "
                    "Return one or two short verbatim evidence quotes. If the sources do not answer "
                    "the question, set not_found true and say so plainly. Do not fill gaps with outside knowledge."
                ),
            },
            {"role": "user", "content": f"QUESTION\n{question}\n\n{context}"},
        ],
        text_format=grounded_answer_model(),
    )
    return response.output_parsed.model_dump()


def validate(answer: dict[str, Any], evidence: list[dict[str, Any]]) -> list[str]:
    problems: list[str] = []
    by_name = {item["filename"]: item["text"] for item in evidence}
    for citation in answer["citations"]:
        if citation not in by_name:
            problems.append(f"Citation was not retrieved: {citation}")
    combined = "\n".join(by_name.values())
    for quote in answer["evidence_quotes"]:
        if normalized(quote) not in normalized(combined):
            problems.append(f"Quote not found verbatim: {quote}")
    return problems


def show_evidence(question: str, evidence: list[dict[str, Any]]) -> None:
    print(f"\nQUESTION\n{question}\n\nRETRIEVED EVIDENCE")
    for item in evidence:
        preview = " ".join(item["text"].split())[:240]
        print(f"  [{item['filename']}] score={item['score']:.3f}\n    {preview}…")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", action="store_true", help="Generate a grounded answer with the OpenAI API.")
    parser.add_argument("--question", help="Ask one question instead of the three course questions.")
    args = parser.parse_args()

    questions = [args.question] if args.question else json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    for question in questions:
        evidence = retrieve(question)
        show_evidence(question, evidence)
        if not args.api:
            print("\nOFFLINE TASK\nOpen the files above. Decide whether they answer the question before generating prose.")
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

