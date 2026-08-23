# Lab 03 · A tool-using data analyst

## The task

The dataset describes a fictional academic-support program. A surface comparison suggests that students who used an AI planning assistant improved less. That conclusion changes when the data are separated by starting track.

The point is not to celebrate the model. It is to inspect an agent loop:

`question → model chooses a tool → local code runs → result returns to model → model explains`

The model cannot execute arbitrary Python. It receives a small allowlist of named functions with fixed arguments.

## 1. Run the analysis without an API

```bash
python 03_data_agent/lab.py
```

The offline demo runs the same tools in a fixed sequence. It also writes `output/gain_by_track.svg`.

Before reading the final comparison, predict:

1. the aggregate difference between AI users and non-users;
2. the difference within each starting track;
3. which comparison is relevant to a causal claim.

## 2. Let a model choose tools

```bash
python 03_data_agent/lab.py --api --question "Did use of the AI planning assistant improve student outcomes? Check for a misleading aggregate."
```

Watch the printed tool trace. A polished answer is not enough: did the model inspect missingness, stratify the comparison, and distinguish association from causation?

## No-code path

Upload `data/program_outcomes.csv` to a tool that can analyze spreadsheets. Ask it to show:

- row count and missingness;
- mean score gain by `used_ai`;
- mean score gain by `used_ai` within `track`;
- a chart;
- three reasons the result does not establish causality.

Require it to show the calculations, not only a narrative.

## Safety extension

Add a pretend `email_results` tool definition on paper. What approval should be required before it runs? Tool calling becomes “agentic” when outputs can change the world; permissions, previews, logs, and reversibility then matter as much as model quality.

