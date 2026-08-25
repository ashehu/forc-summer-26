#!/usr/bin/env python3
"""Create page-aware overlapping chunks from the starter corpus."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
SOURCE_DIR = LAB_DIR / "data" / "source_txt"
OUTPUT_PATH = LAB_DIR / "output" / "chunks.json"
PAGE_MARKER = re.compile(r"^=== PAGE (\d+) ===$", re.MULTILINE)


def chunk_words(text: str, size: int, overlap: int) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - overlap
    return chunks


def parse_document(path: Path) -> tuple[dict[str, str], list[tuple[int, str]]]:
    raw = path.read_text(encoding="utf-8")
    first_marker = PAGE_MARKER.search(raw)
    if not first_marker:
        raise ValueError(f"No page markers found in {path.name}")
    header = raw[: first_marker.start()]
    metadata = {}
    for line in header.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip().lower()] = value.strip()
    matches = list(PAGE_MARKER.finditer(raw))
    pages = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        pages.append((int(match.group(1)), raw[match.end() : end].strip()))
    return metadata, pages


def build_chunks(size: int, overlap: int) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for path in sorted(SOURCE_DIR.glob("*.txt")):
        metadata, pages = parse_document(path)
        for page_number, page_text in pages:
            for chunk_number, text in enumerate(chunk_words(page_text, size, overlap), start=1):
                records.append(
                    {
                        "chunk_id": f"{path.stem}-p{page_number}-c{chunk_number}",
                        "filename": path.name,
                        "page": page_number,
                        "title": metadata.get("title", path.stem),
                        "document_id": metadata.get("document_id", path.stem),
                        "document_type": metadata.get("document_type", "unknown"),
                        "text": text,
                    }
                )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=120, help="Words per chunk")
    parser.add_argument("--overlap", type=int, default=25, help="Repeated words")
    args = parser.parse_args()
    if args.size < 20 or args.overlap < 0 or args.overlap >= args.size:
        raise SystemExit("Use size >= 20 and 0 <= overlap < size")
    chunks = build_chunks(args.size, args.overlap)
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(chunks, indent=2), encoding="utf-8")
    print(f"Wrote {len(chunks)} chunks to {OUTPUT_PATH.relative_to(LAB_DIR)}")
    for item in chunks[:3]:
        print(f"  {item['chunk_id']} · {len(str(item['text']).split())} words · {item['title']}")


if __name__ == "__main__":
    main()
