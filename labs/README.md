# Practical AI labs

Four small systems, four different lessons:

1. **Structured extraction** — turn messy text into a schema, then score it against a gold set.
2. **Grounded Q&A** — retrieve evidence before generating an answer, and test what happens when the answer is absent.
3. **A tool-using data analyst** — let a model choose among safe, inspectable analysis functions.
4. **A voice research copilot** — transcribe a recording, create a memo, and verify every quoted line.

All source material and data are fictional and course-authored. Nothing in these folders is a claim about a real person, institution, or study.

## Setup

Python 3.11 or later is recommended.

```bash
cd labs
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

Every lab has an offline path. Start there; it does not require an account or an API key.

For the API path, set your key in the terminal—not in a notebook, browser, or source file:

```bash
export OPENAI_API_KEY="your-key-here"
```

Optional model settings:

```bash
export OPENAI_TEXT_MODEL="gpt-5.6-luna"
export OPENAI_TRANSCRIBE_MODEL="gpt-transcribe"
```

Never commit a real key. The included `.env.example` contains names only.

## Suggested sequence

| Lab | Time | Core question | Verification target |
|---|---:|---|---|
| 01 · Structured extraction | 30 min | Can a model reliably fill a research schema? | Field accuracy + exact evidence quote |
| 02 · Grounded Q&A | 40 min | Can it answer only from a local evidence set? | Citation exists + quote appears in source |
| 03 · Data agent | 45 min | Can a model choose the right analysis tool? | Tool trace + aggregate/stratified comparison |
| 04 · Voice copilot | 35 min | Can speech become an auditable research memo? | Transcript review + quote verification |

Open `index.html` for the student-facing lab hub, or read the README inside each numbered folder.

## A shared evaluation rule

Do not ask only, “Does the answer sound good?” Check three layers:

- **Interface:** Is the output in the required shape?
- **Evidence:** Can every consequential claim be traced to an input, source, or tool result?
- **Decision:** Is the conclusion appropriately calibrated, and does a human still own it?

