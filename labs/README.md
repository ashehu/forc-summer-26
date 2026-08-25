# Practical AI labs

A practical RAG starter followed by four applied systems:

0. **RAG starter** — take a fictional 20-page corpus through chunking, embeddings, retrieval, and a source-visible interface.
1. **Evidence discovery across opioid-industry records** — inspect source roles, build a packet, compare retrieval, and preserve an absent outcome.
2. **Structured extraction** — manually structure one record, then compare rules or a model with a gold set.
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

Labs 01–04 include offline paths. In Lab 00, source inspection and chunking work offline; embeddings, query vectors, and the final retrieval interface require API access.

For the RAG starter, follow `00_rag_starter/API_KEY_SETUP.md`. It stores the key in a local, Git-ignored `.env` file so separate commands and Streamlit can read the same setting.

Optional model settings:

```bash
export OPENAI_TEXT_MODEL="gpt-5.6-luna"
export OPENAI_TRANSCRIBE_MODEL="gpt-transcribe"
```

Never paste a real key into Codex, chat, source code, a notebook, or a screenshot. Never commit `.env`.

## Suggested sequence

| Lab | Time | Core question | Verification target |
|---|---:|---|---|
| 00 · RAG starter | 30 min | Can I trace pages through chunks, embeddings, and retrieval? | Visible source + page + score + passage |
| 01 · Opioid-industry evidence discovery | ≈60 min | What do public records support—and what do they not establish? | Source role + human/system packet + original-page check |
| 02 · Structured extraction | 35 min | Can a model reliably fill a research schema? | Manual/system/gold comparison + exact quote |
| 03 · Agentic data analysis | 50 min | Can a model choose the right analysis tool? | Student-built trace + aggregate/stratified comparison |
| 04 · Voice copilot | 40 min | Can speech become an auditable research memo? | Audio correction + quote and approval checks |

Open `index.html` for the student-facing lab hub, or read the README inside each numbered folder.

## A shared evaluation rule

Do not ask only, “Does the answer sound good?” Check three layers:

- **Interface:** Is the output in the required shape?
- **Evidence:** Can every consequential claim be traced to an input, source, or tool result?
- **Decision:** Is the conclusion appropriately calibrated, and does a human still own it?
