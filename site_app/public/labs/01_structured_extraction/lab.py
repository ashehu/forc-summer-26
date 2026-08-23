#!/usr/bin/env python3
"""Compare a brittle extraction baseline with schema-constrained LLM output."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

LAB_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB_DIR.parent))

from common import normalized, openai_client, text_model, write_json  # noqa: E402


RECORDS_DIR = LAB_DIR / "data" / "records"
GOLD_PATH = LAB_DIR / "data" / "gold.json"
OUTPUT_PATH = LAB_DIR / "output" / "extractions.json"


def first_match(pattern: str, text: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip().rstrip(".") if match else "NOT EXTRACTED"


def extract_with_rules(path: Path) -> dict[str, Any]:
    """A deliberately brittle baseline that expects Record A's labels."""
    text = path.read_text(encoding="utf-8")
    sample = re.search(r"^n\s*=\s*(\d+)", text, flags=re.IGNORECASE | re.MULTILINE)
    document = re.search(r"\b([A-D]\d{2})\b", text)
    finding = first_match(r"^Finding:\s*(.+)$", text)
    return {
        "document_id": document.group(1) if document else path.stem,
        "population": first_match(r"^Population:\s*(.+)$", text),
        "method": first_match(r"^Design:\s*(.+)$", text),
        "sample_size": int(sample.group(1)) if sample else None,
        "main_finding": finding,
        "limitation": first_match(r"^Limitation:\s*(.+)$", text),
        "evidence_quote": finding if finding == "NOT EXTRACTED" else finding + ".",
    }


def extraction_model():
    try:
        from pydantic import BaseModel
    except ImportError as exc:
        raise SystemExit("Install requirements.txt before using --api.") from exc

    class StudyExtraction(BaseModel):
        document_id: str
        population: str
        method: str
        sample_size: int | None
        main_finding: str
        limitation: str
        evidence_quote: str

    return StudyExtraction


def extract_with_api(path: Path) -> dict[str, Any]:
    client = openai_client()
    schema = extraction_model()
    response = client.responses.parse(
        model=text_model(),
        input=[
            {
                "role": "system",
                "content": (
                    "Extract only explicitly stated study information. Preserve uncertainty. "
                    "Use null when sample size is not reported. evidence_quote must be one "
                    "verbatim sentence from the record that supports main_finding."
                ),
            },
            {"role": "user", "content": path.read_text(encoding="utf-8")},
        ],
        text_format=schema,
    )
    return response.output_parsed.model_dump()


def evaluate(outputs: list[dict[str, Any]], gold: list[dict[str, Any]]) -> None:
    gold_by_id = {row["document_id"]: row for row in gold}
    fields = ["population", "method", "sample_size", "main_finding", "limitation"]
    correct = 0
    total = 0
    quote_checks = 0

    print("\nFIELD-LEVEL CHECK")
    for output in outputs:
        expected = gold_by_id.get(output["document_id"])
        if not expected:
            print(f"  {output['document_id']}: no gold row")
            continue
        row_correct = sum(normalized(output[field]) == normalized(expected[field]) for field in fields)
        correct += row_correct
        total += len(fields)
        source_path = RECORDS_DIR / f"study_{output['document_id'][0].lower()}.txt"
        source = source_path.read_text(encoding="utf-8")
        quote_ok = normalized(output["evidence_quote"]) in normalized(source)
        quote_checks += int(quote_ok)
        print(f"  {output['document_id']}: {row_correct}/{len(fields)} fields · evidence quote {'✓' if quote_ok else '✗'}")

    print(f"\nExact field accuracy: {correct}/{total} ({correct / total:.0%})")
    print(f"Verbatim evidence quotes: {quote_checks}/{len(outputs)}")
    print(f"Saved: {OUTPUT_PATH.relative_to(LAB_DIR.parent)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", action="store_true", help="Use the OpenAI API instead of regex rules.")
    args = parser.parse_args()

    records = sorted(RECORDS_DIR.glob("*.txt"))
    extractor = extract_with_api if args.api else extract_with_rules
    mode = f"API · {text_model()}" if args.api else "offline regex baseline"
    print(f"Mode: {mode}\nRecords: {len(records)}")
    outputs = [extractor(path) for path in records]
    write_json(OUTPUT_PATH, outputs)
    gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    evaluate(outputs, gold)


if __name__ == "__main__":
    main()
