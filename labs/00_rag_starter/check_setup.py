#!/usr/bin/env python3
"""Preflight checks for the RAG starter lab without exposing credentials."""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ENV_PATH = LAB_DIR / ".env"

REQUIRED_FILES = [
    "README.md",
    "API_KEY_SETUP.md",
    "chunk.py",
    "build_index.py",
    "retrieve.py",
    "app.py",
    "data/source_manifest.json",
    "data/questions.json",
    "data/evaluation_questions.json",
    "data/rag_starter_corpus.pdf",
]
REQUIRED_PACKAGES = ["openai", "dotenv", "streamlit"]


def load_key_from_dotenv() -> bool:
    """Check a simple local .env file without printing any value."""
    if os.getenv("OPENAI_API_KEY", "").strip():
        return True
    if not ENV_PATH.exists():
        return False
    for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "OPENAI_API_KEY" and value.strip().strip("'\""):
            return True
    return False


def report(label: str, ok: bool, detail: str) -> None:
    marker = "PASS" if ok else "FAIL"
    print(f"[{marker}] {label}: {detail}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-key",
        action="store_true",
        help="Treat a missing OPENAI_API_KEY as a failure.",
    )
    args = parser.parse_args()
    failures = 0

    python_ok = sys.version_info >= (3, 9)
    report("Python", python_ok, sys.version.split()[0] + " (3.9 or newer required)")
    failures += int(not python_ok)

    missing_files = [name for name in REQUIRED_FILES if not (LAB_DIR / name).exists()]
    files_ok = not missing_files
    report("Starter files", files_ok, "complete" if files_ok else ", ".join(missing_files))
    failures += int(not files_ok)

    source_count = len(list((LAB_DIR / "data" / "source_txt").glob("*.txt")))
    source_ok = source_count == 10
    report("Source documents", source_ok, f"{source_count} of 10 text files found")
    failures += int(not source_ok)

    missing_packages = [name for name in REQUIRED_PACKAGES if importlib.util.find_spec(name) is None]
    packages_ok = not missing_packages
    report(
        "Python packages",
        packages_ok,
        "installed" if packages_ok else "missing " + ", ".join(missing_packages),
    )
    failures += int(not packages_ok)

    key_ok = load_key_from_dotenv()
    if key_ok:
        print("[PASS] API key: available (value hidden)")
    elif args.require_key:
        print("[FAIL] API key: missing; follow API_KEY_SETUP.md")
        failures += 1
    else:
        print("[WARN] API key: not configured yet; needed before the embedding step")

    chunks_path = LAB_DIR / "output" / "chunks.json"
    index_path = LAB_DIR / "output" / "index.json"
    print(f"[INFO] Chunks: {'ready' if chunks_path.exists() else 'not built yet'}")
    print(f"[INFO] Embedding index: {'ready' if index_path.exists() else 'not built yet'}")

    if failures:
        print(f"\nPreflight found {failures} blocking problem(s). Fix them before continuing.")
        return 1
    print("\nPreflight passed. Continue to the next lab prompt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
