# Lab 04 · A voice research copilot

## The task

Turn a short interview into an auditable memo:

`audio → transcript → structured memo → quote verification → human review`

The supplied transcript is fictional and contains no real personal data. The offline path uses it directly. The API path can analyze that transcript or transcribe a recording you have consent to use.

## 1. Run the offline pipeline

```bash
python 04_voice_copilot/lab.py
```

The script copies the supplied transcript into `output/`, creates a sample memo, and checks whether every evidence quote really occurs in the transcript.

## 2. Analyze the transcript with the API

```bash
python 04_voice_copilot/lab.py --api
```

## 3. Optional: transcribe a consented recording

```bash
python 04_voice_copilot/lab.py --api --audio /absolute/path/to/interview.m4a
```

Recorded files use the Transcriptions API, then the text model creates the memo. Live, streaming voice would use a Realtime transcription architecture; that is an extension, not hidden inside this lab.

## No-code path

Use `data/mock_interview.txt` as the transcript. Ask an LLM for:

- a two-sentence summary;
- three themes;
- decisions and action items;
- unresolved tensions;
- three short exact quotes.

Then use find/search in the transcript to verify every quote.

## Before using real interviews

- Obtain meaningful consent for recording and automated processing.
- Explain where audio and transcripts will go and who can access them.
- Remove identifiers that are not needed for the research purpose.
- Check your institution's rules, the chosen service's current retention controls, and any promises made to participants.
- Treat transcripts, speaker labels, inferred emotion, and summaries as fallible.
- Keep the recording and transcript available for human correction before analysis.

