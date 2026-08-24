# Lab 03 · Agentic data analysis

## The problem

A fictional academic-support program has 48 student records. Each record includes a baseline score, follow-up score, starting track, whether the student chose to use an AI planning assistant, department, and attendance hours.

The program team asks:

> What can we responsibly say about AI-assistant use and score gain—and what can these data not tell us?

A useful analysis must describe the data and missingness, reproduce the user/non-user comparison, test whether group composition changes it, distinguish association from causation, and name the evidence needed next.

The dataset is observational: students were not randomly assigned to use the assistant. It can describe patterns among these students. It cannot identify what would have happened to the same students if their AI use had been different.

## Why use an agent?

The arithmetic is easy. The difficult part is choosing a responsible sequence of checks:

`question → choose an allowed tool → local code runs → inspect result → choose again or explain`

The model cannot execute arbitrary Python. It receives a small allowlist of named functions with fixed arguments. We evaluate the analytical trace before the final prose.

## Learning goals

By the end, you should be able to:

- separate descriptive and causal questions;
- recognize how group composition can reverse an aggregate comparison;
- audit tool choices and intermediate results;
- design a narrow tool allowlist and approval boundary; and
- state a conclusion at the level the evidence supports.

## Student investigation · do this before the reveal

Use [TRACE_TEMPLATE.md](TRACE_TEMPLATE.md). Do not run the full offline demo yet: it prints the reversal.

### 1 · Meet the rows and create the outcome

Open `data/program_outcomes.csv`. One row is one participant.

Create:

`gain = followup_score - baseline_score`

Then run:

```bash
python 03_data_agent/lab.py --stage describe
python 03_data_agent/lab.py --stage missing
```

Record the unit of observation, fields, group sizes, and missing values. Predict which variables could make AI users and non-users different before the assistant was used.

### 2 · Make the first comparison

```bash
python 03_data_agent/lab.py --stage aggregate
```

Write a one-sentence interpretation before doing anything else. Include both group sizes. Is this sentence descriptive or causal?

### 3 · Choose the next comparison

Before running another command, choose a variable that might change the interpretation and explain why. Then run:

```bash
python 03_data_agent/lab.py --stage stratified
```

Explain why the aggregate and within-track comparisons point in opposite directions. Name the role of starting track and group composition.

### 4 · Limit the claim

```bash
python 03_data_agent/lab.py --stage adjusted
```

The adjusted model estimates an association after controlling for listed variables. Write one sentence it supports, one causal sentence it does not support, and one stronger study design or evidence source you would seek next.

## No-code path

Open `data/program_outcomes.csv` in a spreadsheet:

1. create a `gain` column;
2. inspect missing values;
3. calculate mean gain and `n` by `used_ai`;
4. choose a plausible comparison variable;
5. build a second pivot using that variable; and
6. write one supported and one unsupported claim.

Do not look at the result slides until your second pivot is complete.

## Instructor debrief · reveal the reversal

Keep the aggregate result visible, then run:

```bash
python 03_data_agent/lab.py --stage stratified
```

Ask what changed: the students, the outcome, or the comparison? Adjustment diagnoses structure; it does not convert self-selection into random assignment.

## Full offline trace

After the investigation:

```bash
python 03_data_agent/lab.py
```

This runs the fixed sequence and writes `output/gain_by_track.svg`.

## Optional · let a model choose tools

```bash
python 03_data_agent/lab.py --api --question "What can we responsibly say about AI planning-assistant use and score gain?"
```

Annotate each call as necessary, unnecessary, or missing. Did the agent inspect missingness and group composition without being told to check for a misleading aggregate?

## Done when

Your pair has:

- a completed trace with the reason for every analysis step;
- the aggregate and within-track comparisons;
- an explanation of the reversal in plain language;
- one supported descriptive claim and one rejected causal claim; and
- one proposed next study or evidence source.

## Safety extension

Add a pretend `email_results` tool on paper. Decide whether it should be automatic, require preview and approval, or be prohibited. Permissions, logs, and reversibility matter whenever an agent's outputs can change the world.
