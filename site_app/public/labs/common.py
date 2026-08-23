"""Shared helpers for the course labs.

Imports from the OpenAI SDK are intentionally lazy so every offline mode works
without installing dependencies or configuring an API key.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


LABS_ROOT = Path(__file__).resolve().parent
DEFAULT_TEXT_MODEL = "gpt-5.6-luna"
DEFAULT_TRANSCRIBE_MODEL = "gpt-transcribe"


def text_model() -> str:
    return os.getenv("OPENAI_TEXT_MODEL", DEFAULT_TEXT_MODEL)


def transcribe_model() -> str:
    return os.getenv("OPENAI_TRANSCRIBE_MODEL", DEFAULT_TRANSCRIBE_MODEL)


def openai_client():
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY is not set. Run the offline mode or export the key "
            "in your terminal before using --api."
        )
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit(
            "The OpenAI SDK is not installed. From labs/, run: "
            "python -m pip install -r requirements.txt"
        ) from exc
    return OpenAI()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def normalized(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).casefold().split())

