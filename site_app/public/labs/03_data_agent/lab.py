#!/usr/bin/env python3
"""A bounded data-analysis agent with transparent, allowlisted tools."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

LAB_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB_DIR.parent))

from common import openai_client, text_model  # noqa: E402


DATA_PATH = LAB_DIR / "data" / "program_outcomes.csv"
PLOT_PATH = LAB_DIR / "output" / "gain_by_track.svg"


def load_rows() -> list[dict[str, Any]]:
    with DATA_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["used_ai"] = int(row["used_ai"])
        row["baseline_score"] = float(row["baseline_score"])
        row["followup_score"] = float(row["followup_score"])
        row["gain"] = row["followup_score"] - row["baseline_score"]
        row["attendance_hours"] = float(row["attendance_hours"]) if row["attendance_hours"] else None
    return rows


ROWS = load_rows()


def describe_dataset(_: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "rows": len(ROWS),
        "columns": list(ROWS[0].keys()),
        "track_counts": dict(Counter(row["track"] for row in ROWS)),
        "ai_use_counts": dict(Counter(str(row["used_ai"]) for row in ROWS)),
        "important_note": "This is observational, synthetic course data; use does not imply treatment assignment.",
    }


def inspect_missing_data(_: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        column: sum(row[column] in (None, "") for row in ROWS)
        for column in ROWS[0]
    }


def compare_outcomes(arguments: dict[str, Any]) -> dict[str, Any]:
    outcome = arguments.get("outcome", "gain")
    stratify_by = arguments.get("stratify_by", "none")
    if outcome not in {"gain", "followup_score"}:
        raise ValueError("outcome must be gain or followup_score")
    if stratify_by not in {"none", "track", "department"}:
        raise ValueError("stratify_by must be none, track, or department")

    grouped: dict[tuple[str, int], list[float]] = defaultdict(list)
    for row in ROWS:
        stratum = "all students" if stratify_by == "none" else str(row[stratify_by])
        grouped[(stratum, row["used_ai"])].append(float(row[outcome]))

    results = []
    for (stratum, used_ai), values in sorted(grouped.items()):
        results.append({
            "stratum": stratum,
            "used_ai": used_ai,
            "n": len(values),
            "mean": round(statistics.fmean(values), 2),
        })
    return {"outcome": outcome, "stratified_by": stratify_by, "groups": results}


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    """Gauss-Jordan elimination for the tiny teaching regression below."""
    augmented = [row[:] + [value] for row, value in zip(matrix, vector)]
    size = len(vector)
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        if abs(divisor) < 1e-10:
            raise ValueError("Regression design is singular")
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [current - factor * pivot_value for current, pivot_value in zip(augmented[row], augmented[column])]
    return [row[-1] for row in augmented]


def fit_adjusted_model(_: dict[str, Any] | None = None) -> dict[str, Any]:
    """OLS: gain ~ used_ai + foundation_track + baseline_score."""
    x = [[1.0, float(row["used_ai"]), float(row["track"] == "Foundation"), row["baseline_score"]] for row in ROWS]
    y = [row["gain"] for row in ROWS]
    width = len(x[0])
    xtx = [[sum(row[i] * row[j] for row in x) for j in range(width)] for i in range(width)]
    xty = [sum(row[i] * target for row, target in zip(x, y)) for i in range(width)]
    coefficients = solve_linear_system(xtx, xty)
    return {
        "formula": "gain ~ used_ai + foundation_track + baseline_score",
        "coefficients": dict(zip(["intercept", "used_ai", "foundation_track", "baseline_score"], [round(value, 3) for value in coefficients])),
        "interpretation_guardrail": "Adjustment can reveal structure, but this observational dataset still does not identify a causal effect.",
    }


def make_plot(_: dict[str, Any] | None = None) -> dict[str, Any]:
    comparison = compare_outcomes({"outcome": "gain", "stratify_by": "track"})["groups"]
    colors = {0: "#75c9bd", 1: "#ed6a46"}
    labels = {(item["stratum"], item["used_ai"]): item for item in comparison}
    bars = []
    x_positions = [120, 230, 420, 530]
    keys = [("Advanced", 0), ("Advanced", 1), ("Foundation", 0), ("Foundation", 1)]
    for x_position, key in zip(x_positions, keys):
        item = labels[key]
        height = item["mean"] * 18
        y_position = 330 - height
        bars.append(
            f'<rect x="{x_position}" y="{y_position:.1f}" width="78" height="{height:.1f}" rx="6" fill="{colors[item["used_ai"]]}"/>'
            f'<text x="{x_position + 39}" y="{y_position - 10:.1f}" text-anchor="middle" class="value">{item["mean"]:.1f}</text>'
            f'<text x="{x_position + 39}" y="356" text-anchor="middle" class="label">AI {"yes" if item["used_ai"] else "no"}</text>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="700" height="430" viewBox="0 0 700 430">
<style>text{{font-family:Arial,sans-serif;fill:#102a33}}.title{{font-size:22px;font-weight:700}}.label{{font-size:14px}}.value{{font-size:16px;font-weight:700}}.group{{font-size:17px;font-weight:700}}</style>
<rect width="700" height="430" fill="#f3eee3"/><text x="40" y="42" class="title">Mean score gain within starting track</text>
<line x1="70" y1="330" x2="630" y2="330" stroke="#102a33" stroke-width="2"/>
{''.join(bars)}
<text x="214" y="397" text-anchor="middle" class="group">Advanced</text><text x="514" y="397" text-anchor="middle" class="group">Foundation</text>
</svg>'''
    PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLOT_PATH.write_text(svg, encoding="utf-8")
    return {"plot": str(PLOT_PATH), "message": "Chart written as an inspectable SVG."}


TOOL_FUNCTIONS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "describe_dataset": describe_dataset,
    "inspect_missing_data": inspect_missing_data,
    "compare_outcomes": compare_outcomes,
    "fit_adjusted_model": fit_adjusted_model,
    "make_plot": make_plot,
}

STAGE_TASKS: dict[str, tuple[str, dict[str, Any]]] = {
    "describe": ("describe_dataset", {}),
    "missing": ("inspect_missing_data", {}),
    "aggregate": ("compare_outcomes", {"outcome": "gain", "stratify_by": "none"}),
    "stratified": ("compare_outcomes", {"outcome": "gain", "stratify_by": "track"}),
    "adjusted": ("fit_adjusted_model", {}),
    "plot": ("make_plot", {}),
}

NO_ARGS = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
TOOLS = [
    {"type": "function", "name": "describe_dataset", "description": "Inspect row count, columns, group sizes, and study-design warning.", "parameters": NO_ARGS, "strict": True},
    {"type": "function", "name": "inspect_missing_data", "description": "Count missing values in every column.", "parameters": NO_ARGS, "strict": True},
    {
        "type": "function",
        "name": "compare_outcomes",
        "description": "Compare mean outcomes for AI users and non-users, optionally within important groups.",
        "parameters": {
            "type": "object",
            "properties": {
                "outcome": {"type": "string", "enum": ["gain", "followup_score"]},
                "stratify_by": {"type": "string", "enum": ["none", "track", "department"]},
            },
            "required": ["outcome", "stratify_by"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {"type": "function", "name": "fit_adjusted_model", "description": "Fit a small predefined adjusted regression for score gain.", "parameters": NO_ARGS, "strict": True},
    {"type": "function", "name": "make_plot", "description": "Write an SVG chart of mean score gain by AI use within track.", "parameters": NO_ARGS, "strict": True},
]


INSTRUCTIONS = """You are a cautious data-analysis assistant. Use the supplied tools rather than guessing.
Inspect the dataset and missingness. Compare aggregate and stratified results before answering.
Explain any reversal plainly. This is observational synthetic course data: never claim that AI use caused an outcome.
Mention the tool evidence behind the conclusion and end with one sensible next study design."""


def run_agent(question: str) -> None:
    client = openai_client()
    response = client.responses.create(model=text_model(), instructions=INSTRUCTIONS, input=question, tools=TOOLS)

    for step in range(1, 7):
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            print("\nAGENT ANSWER\n" + response.output_text)
            return
        outputs = []
        for call in calls:
            if call.name not in TOOL_FUNCTIONS:
                raise RuntimeError(f"Model requested a tool outside the allowlist: {call.name}")
            arguments = json.loads(call.arguments or "{}")
            result = TOOL_FUNCTIONS[call.name](arguments)
            print(f"STEP {step} · {call.name}({json.dumps(arguments)})")
            print(json.dumps(result, indent=2))
            outputs.append({"type": "function_call_output", "call_id": call.call_id, "output": json.dumps(result)})
        response = client.responses.create(
            model=text_model(),
            instructions=INSTRUCTIONS,
            previous_response_id=response.id,
            input=outputs,
            tools=TOOLS,
        )
    raise RuntimeError("Agent exceeded the six-step course limit")


def run_offline_demo() -> None:
    tasks = [
        ("describe_dataset", {}),
        ("inspect_missing_data", {}),
        ("compare_outcomes", {"outcome": "gain", "stratify_by": "none"}),
        ("compare_outcomes", {"outcome": "gain", "stratify_by": "track"}),
        ("fit_adjusted_model", {}),
        ("make_plot", {}),
    ]
    print("OFFLINE TOOL TRACE")
    for name, arguments in tasks:
        print(f"\n{name}({json.dumps(arguments)})")
        print(json.dumps(TOOL_FUNCTIONS[name](arguments), indent=2))
    print("\nNOTICE THE REVERSAL")
    print("AI users improve less in the aggregate, yet more within each starting track. Group composition creates the misleading surface result.")


def run_stage(stage: str) -> None:
    tool_name, arguments = STAGE_TASKS[stage]
    print(f"STAGE · {stage}\n{tool_name}({json.dumps(arguments)})")
    print(json.dumps(TOOL_FUNCTIONS[tool_name](arguments), indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", action="store_true", help="Let a model choose among the allowlisted tools.")
    parser.add_argument("--stage", choices=sorted(STAGE_TASKS), help="Run one deterministic analysis stage.")
    parser.add_argument("--question", default="Did use of the AI planning assistant improve student outcomes? Check for a misleading aggregate.")
    args = parser.parse_args()
    if args.api and args.stage:
        parser.error("Choose --api or --stage, not both.")
    if args.stage:
        run_stage(args.stage)
    elif args.api:
        run_agent(args.question)
    else:
        run_offline_demo()


if __name__ == "__main__":
    main()
