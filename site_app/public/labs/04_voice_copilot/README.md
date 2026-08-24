# Lab 04 · A voice research copilot

## The problem

A researcher has a short, fictional interview about a graduate-support clinic:

> Turn the interview into a useful research memo without changing what the participant meant—and preserve enough evidence to audit every important claim.

A successful memo keeps three kinds of statement distinct:

1. **Participant evidence** — what the person actually said;
2. **Researcher synthesis** — a theme or interpretation supported by the record; and
3. **Program action** — a recommendation requiring judgment and authorization.

The supplied recording, transcript, and voices are synthetic course materials. They contain no real participant data. With real interviews, purpose, consent, minimum necessary data, access, storage, and retention belong inside the system design.

## Why this is difficult

`authorization → audio → transcript → memo → quote check → audio review → approved use`

Each arrow can change meaning. Transcript search can detect when a memo invents words absent from the transcript. It cannot detect an upstream transcription error when both transcript and memo contain the same wrong word. Audio remains the source for checking the transcript.

## Learning goals

By the end, you should be able to:

- correct a transcript against its audio source;
- separate quotation, synthesis, and action;
- identify authorization and data-minimization decisions before processing;
- preserve a trace from a memo claim to transcript and audio evidence;
- explain what transcript search can and cannot verify; and
- place human review before a consequential decision.

## Student lab · 18 minutes

Use [TRACE_TEMPLATE.md](TRACE_TEMPLATE.md). Do not open `data/mock_interview.txt`, the clean transcript, until your source audit is complete.

### 1 · Source audit · 5 minutes

Play:

`data/mock_interview.m4a`

Open:

`data/mock_interview_auto_transcript.txt`

The rough transcript contains three planted errors:

- one terminology error;
- one number error; and
- one missing negation.

Listen twice, correct the transcript, and record the exact audio evidence for each change.

### 2 · Build a small memo · 7 minutes

From your corrected transcript, produce:

- a two-sentence summary;
- one exact participant quote;
- one researcher synthesis;
- one proposed program action; and
- one unresolved limitation or tension.

Label every statement as **quote**, **synthesis**, or **action**. A recommendation must not be written as if the participant directly authorized it.

If your API key is ready, you may compare your memo with:

```bash
python 04_voice_copilot/lab.py --api --transcript 04_voice_copilot/data/mock_interview.txt
```

### 3 · Verify and break one boundary · 6 minutes

Run the clean offline trace:

```bash
python 04_voice_copilot/lab.py --show-trace
```

Then choose one failure:

```bash
python 04_voice_copilot/lab.py --inject-memo-error --show-trace
```

or:

```bash
python 04_voice_copilot/lab.py --inject-transcript-error --show-trace
```

For the memo error, explain why the quote check fails. For the transcript error, explain why text-to-text verification passes and why the audio must be revisited.

## Instructor demo · one clean trace and two failures

```bash
python 04_voice_copilot/lab.py --show-trace
python 04_voice_copilot/lab.py --inject-memo-error --show-trace
python 04_voice_copilot/lab.py --inject-transcript-error --show-trace
```

Ask what each check compares and which source of truth is unavailable to the quote checker.

## No-code path

Use the same audio and rough transcript. Correct the three errors, draft the memo manually or with a model, label the claim types, and use find/search to verify exact quotations. Finally compare one important claim directly with the audio.

## Optional · transcribe an authorized recording

```bash
python 04_voice_copilot/lab.py --api --audio /absolute/path/to/interview.m4a
```

Recorded files use a transcription model and then a text model creates the memo. Live streaming voice is an extension, not hidden inside this lab.

## Done when

Your pair has:

- three audio-grounded transcript corrections;
- a student-authored memo containing a quote, synthesis, action, and limitation;
- one verified exact quotation;
- an explanation of one injected failure; and
- one authorization decision and one human approval gate.

## Before using real interviews

- Obtain meaningful consent for recording and automated processing.
- Explain where audio and transcripts will go and who can access them.
- Remove identifiers that are not needed for the research purpose.
- Check institutional rules, current service controls, and participant promises.
- Treat transcripts, speaker labels, inferred emotion, and summaries as fallible.
- Keep the recording and transcript available for correction before analysis or action.
