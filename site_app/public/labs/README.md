# Practical AI labs

Four small systems, four different lessons:

1. **Structured extraction** — manually structure one record, then compare rules or a model with a gold set.
2. **Grounded Q&A** — select evidence yourself, then compare it with retrieval and test an absent answer.
3. **An agentic data analyst** — inspect raw rows and choose among safe, visible analysis steps.
4. **A voice research copilot** — correct a rough transcript against audio, create a memo, and verify consequential claims.

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
| 01 · Structured extraction | 35 min | Can a model reliably fill a research schema? | Manual/system/gold comparison + exact quote |
| 02 · Grounded Q&A | 45–50 min | Can it answer only from a local evidence set? | Human/system packet comparison + source check |
| 03 · Agentic data analysis | 50 min | Can a model choose the right analysis tool? | Student-built trace + aggregate/stratified comparison |
| 04 · Voice copilot | 40 min | Can speech become an auditable research memo? | Audio correction + quote and approval checks |

Open `index.html` for the student-facing lab hub, or read the README inside each numbered folder.

## A shared evaluation rule

Do not ask only, “Does the answer sound good?” Check three layers:

- **Interface:** Is the output in the required shape?
- **Evidence:** Can every consequential claim be traced to an input, source, or tool result?
- **Decision:** Is the conclusion appropriately calibrated, and does a human still own it?
