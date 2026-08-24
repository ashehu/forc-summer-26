#!/usr/bin/env python3
"""Turn an interview recording or transcript into a verified research memo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

LAB_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB_DIR.parent))

from common import normalized, openai_client, text_model, transcribe_model, write_json  # noqa: E402


MOCK_TRANSCRIPT = LAB_DIR / "data" / "mock_interview.txt"
SAMPLE_MEMO = LAB_DIR / "data" / "sample_memo.json"
OUTPUT_DIR = LAB_DIR / "output"


def transcribe_audio(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"Audio file not found: {path}")
    client = openai_client()
    with path.open("rb") as audio:
        result = client.audio.transcriptions.create(
            model=transcribe_model(),
            file=audio,
            response_format="json",
            prompt="A graduate-program research interview about a peer-methods clinic.",
        )
    return result.text


def memo_model():
    try:
        from pydantic import BaseModel
    except ImportError as exc:
        raise SystemExit("Install requirements.txt before using --api.") from exc

    class ActionItem(BaseModel):
        owner: str
        task: str
        due_date: str

    class InterviewMemo(BaseModel):
        summary: str
        themes: list[str]
        decisions: list[str]
        action_items: list[ActionItem]
        tensions: list[str]
        evidence_quotes: list[str]

    return InterviewMemo


def analyze_with_api(transcript: str) -> dict[str, Any]:
    response = openai_client().responses.parse(
        model=text_model(),
        input=[
            {
                "role": "system",
                "content": (
                    "Create a concise research memo from the supplied transcript only. Separate participant "
                    "statements from your synthesis. Do not infer emotion or demographic traits. Use 'not stated' "
                    "for missing owners or dates. evidence_quotes must be short verbatim transcript excerpts."
                ),
            },
            {"role": "user", "content": transcript},
        ],
        text_format=memo_model(),
    )
    return response.output_parsed.model_dump()


def verify_quotes(memo: dict[str, Any], transcript: str) -> list[str]:
    return [quote for quote in memo["evidence_quotes"] if normalized(quote) not in normalized(transcript)]


def inject_offline_failure(memo: dict[str, Any], transcript: str, mode: str | None) -> tuple[dict[str, Any], str]:
    if mode == "memo":
        memo["decisions"].append("Make the clinic mandatory")
        memo["evidence_quotes"].append("I would make the clinic mandatory.")
    elif mode == "transcript":
        transcript = transcript.replace(
            "I would not make the clinic mandatory.",
            "I would make the clinic mandatory.",
        )
        memo["decisions"].append("Make the clinic mandatory")
        memo["evidence_quotes"].append("I would make the clinic mandatory.")
    return memo, transcript


def show_trace(memo: dict[str, Any], transcript: str, failed_quotes: list[str]) -> None:
    relevant_line = next((line for line in transcript.splitlines() if "mandatory" in line.casefold()), "not present")
    print("\nTRACE · CONSEQUENTIAL CLAIM")
    print("Transcript:", relevant_line)
    print("Decisions:", json.dumps(memo["decisions"], ensure_ascii=False))
    print("Evidence quotes:", json.dumps(memo["evidence_quotes"], ensure_ascii=False))
    print("Unmatched quotes:", json.dumps(failed_quotes, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", action="store_true", help="Use the API to analyze the transcript.")
    parser.add_argument("--audio", type=Path, help="Transcribe a consented recording before analysis; requires --api.")
    parser.add_argument("--transcript", type=Path, help="Use a different text transcript.")
    parser.add_argument("--show-trace", action="store_true", help="Print the transcript-to-decision evidence trace.")
    injection = parser.add_mutually_exclusive_group()
    injection.add_argument("--inject-memo-error", action="store_true", help="Add an unsupported memo claim; offline demo only.")
    injection.add_argument("--inject-transcript-error", action="store_true", help="Corrupt one transcript negation and propagate it; offline demo only.")
    args = parser.parse_args()

    if args.audio and not args.api:
        raise SystemExit("--audio requires --api because transcription is an API operation.")
    if args.audio and args.transcript:
        raise SystemExit("Choose either --audio or --transcript, not both.")
    if args.api and (args.inject_memo_error or args.inject_transcript_error):
        raise SystemExit("Failure injection uses the offline sample memo. Remove --api.")

    if args.audio:
        transcript = transcribe_audio(args.audio)
        source = f"transcribed from {args.audio} with {transcribe_model()}"
    else:
        transcript_path = args.transcript or MOCK_TRANSCRIPT
        if not transcript_path.exists():
            raise SystemExit(f"Transcript not found: {transcript_path}")
        transcript = transcript_path.read_text(encoding="utf-8")
        source = str(transcript_path)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "transcript.txt").write_text(transcript.rstrip() + "\n", encoding="utf-8")

    if args.api:
        memo = analyze_with_api(transcript)
        mode = f"API analysis · {text_model()}"
    else:
        memo = json.loads(SAMPLE_MEMO.read_text(encoding="utf-8"))
        mode = "offline instructor-authored sample memo"

    injection_mode = "memo" if args.inject_memo_error else "transcript" if args.inject_transcript_error else None
    memo, transcript = inject_offline_failure(memo, transcript, injection_mode)
    if injection_mode:
        mode += f" · injected {injection_mode} error"
        (OUTPUT_DIR / "transcript.txt").write_text(transcript.rstrip() + "\n", encoding="utf-8")

    failed_quotes = verify_quotes(memo, transcript)
    artifact = {
        "mode": mode,
        "transcript_source": source,
        "injected_error": injection_mode,
        "memo": memo,
        "quote_check_passed": not failed_quotes,
        "unmatched_quotes": failed_quotes,
    }
    write_json(OUTPUT_DIR / "memo.json", artifact)

    print(f"Mode: {mode}\nTranscript: {source}")
    print("\nSUMMARY\n" + memo["summary"])
    print("\nTHEMES")
    for theme in memo["themes"]:
        print("  •", theme)
    print("\nQUOTE CHECK:", "passed" if not failed_quotes else f"failed for {len(failed_quotes)} quote(s)")
    if args.show_trace:
        show_trace(memo, transcript, failed_quotes)
    print("Saved: 04_voice_copilot/output/transcript.txt and memo.json")
    if injection_mode == "transcript" and not failed_quotes:
        print("\nIMPORTANT: the quote check passed against a corrupted transcript. Only audio review can catch the upstream error.")
    print("\nHuman review still required: correct the transcript, interpretations, and any consequential next step.")


if __name__ == "__main__":
    main()
