#!/usr/bin/env python3
"""Retrieve page-aware passages from the local embedding index."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

LAB_DIR = Path(__file__).resolve().parent
INDEX_PATH = LAB_DIR / "output" / "index.json"
QUESTIONS_PATH = LAB_DIR / "data" / "questions.json"
EVALUATION_PATH = LAB_DIR / "data" / "evaluation_questions.json"

load_dotenv(LAB_DIR / ".env")


class RetrievalError(RuntimeError):
    """A student-readable retrieval failure."""


def cosine(first: list[float], second: list[float]) -> float:
    dot = sum(a * b for a, b in zip(first, second))
    first_norm = math.sqrt(sum(value * value for value in first))
    second_norm = math.sqrt(sum(value * value for value in second))
    return dot / (first_norm * second_norm) if first_norm and second_norm else 0.0


def load_index() -> dict:
    if not INDEX_PATH.exists():
        raise RetrievalError("Missing output/index.json. Run chunk.py and build_index.py first.")
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def require_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY", "").strip():
        raise RetrievalError(
            "OPENAI_API_KEY is missing. Follow API_KEY_SETUP.md, then run "
            "python check_setup.py --require-key."
        )


def embed_queries(
    questions: list[str], model: str, client: Optional[OpenAI] = None
) -> list[list[float]]:
    require_api_key()
    try:
        response = (client or OpenAI()).embeddings.create(model=model, input=questions)
    except OpenAIError as error:
        raise RetrievalError(f"The embedding request failed: {error}") from error
    ordered = sorted(response.data, key=lambda item: item.index)
    if len(ordered) != len(questions):
        raise RetrievalError("The API returned a different number of vectors than questions.")
    return [item.embedding for item in ordered]


def rank_vector(query_vector: list[float], index: dict, top_k: int) -> list[dict]:
    return sorted(
        ({**item, "score": cosine(query_vector, item["embedding"])} for item in index["chunks"]),
        key=lambda item: item["score"],
        reverse=True,
    )[:top_k]


def rank_passages(question: str, index: dict, top_k: int = 5) -> list[dict]:
    vector = embed_queries([question], index["model"])[0]
    return rank_vector(vector, index, top_k)


def rank_many(questions: list[str], index: dict, top_k: int = 5) -> list[list[dict]]:
    vectors = embed_queries(questions, index["model"])
    return [rank_vector(vector, index, top_k) for vector in vectors]


def print_packet(question: str, results: list[dict], expected: list[str] | None = None) -> None:
    print(f"\nQUESTION\n{question}")
    if expected is not None:
        print("EXPECTED SOURCE(S)\n" + ", ".join(expected))
    print("TOP PASSAGES")
    for rank, item in enumerate(results, start=1):
        print(
            f"\n{rank}. {item['title']} · page {item['page']} · score {item['score']:.3f}\n"
            f"   {item['filename']} · {item['document_type']}\n"
            f"   {item['text']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", help="Question to retrieve evidence for")
    parser.add_argument("--top-k", type=int, default=5, help="Number of passages to return")
    parser.add_argument("--all", action="store_true", help="Run all seven evaluation questions")
    args = parser.parse_args()
    if not 1 <= args.top_k <= 10:
        raise SystemExit("Use --top-k between 1 and 10.")

    try:
        index = load_index()
        if args.all:
            evaluations = json.loads(EVALUATION_PATH.read_text(encoding="utf-8"))
            questions = [item["question"] for item in evaluations]
            packets = rank_many(questions, index, args.top_k)
            for item, packet in zip(evaluations, packets):
                print(f"\n{'=' * 72}\n{item['id']} · {item['evaluation_note']}")
                print_packet(item["question"], packet, item["expected_documents"])
        else:
            if args.question:
                question = args.question
            else:
                question = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))[0]
            print_packet(question, rank_passages(question, index, args.top_k))
    except RetrievalError as error:
        print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
