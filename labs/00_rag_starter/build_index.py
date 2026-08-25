#!/usr/bin/env python3
"""Embed the starter chunks with the OpenAI Embeddings API."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

LAB_DIR = Path(__file__).resolve().parent
CHUNKS_PATH = LAB_DIR / "output" / "chunks.json"
INDEX_PATH = LAB_DIR / "output" / "index.json"

load_dotenv(LAB_DIR / ".env")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"))
    args = parser.parse_args()
    if not CHUNKS_PATH.exists():
        raise SystemExit("Missing output/chunks.json. Run python chunk.py first.")
    if not os.getenv("OPENAI_API_KEY", "").strip():
        raise SystemExit(
            "OPENAI_API_KEY is missing. Follow API_KEY_SETUP.md, then run "
            "python check_setup.py --require-key."
        )
    chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    texts = [item["text"] for item in chunks]
    try:
        response = OpenAI().embeddings.create(model=args.model, input=texts)
    except OpenAIError as error:
        raise SystemExit(f"The embedding request failed: {error}") from error
    embeddings = sorted(response.data, key=lambda item: item.index)
    if len(embeddings) != len(chunks):
        raise SystemExit("The API returned a different number of embeddings than chunks.")
    for item, embedding in zip(chunks, embeddings):
        item["embedding"] = embedding.embedding
    dimensions = len(embeddings[0].embedding) if embeddings else 0
    artifact = {
        "model": args.model,
        "chunk_count": len(chunks),
        "vector_dimensions": dimensions,
        "chunks": chunks,
    }
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(artifact), encoding="utf-8")
    print(f"Embedded {len(chunks)} chunks with {args.model}")
    print(f"Vector dimensions: {dimensions}")
    print(f"Wrote {INDEX_PATH.relative_to(LAB_DIR)}")


if __name__ == "__main__":
    main()
