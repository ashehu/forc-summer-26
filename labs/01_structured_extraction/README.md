# Lab 01 · Structured extraction

## The task

Convert four short, differently written study records into one comparable schema:

`document_id · population · method · sample_size · main_finding · limitation · evidence_quote`

The records are fictional. A small gold set lets you score the result instead of judging it by feel.

## 1. Run the brittle baseline

From the `labs/` folder:

```bash
python 01_structured_extraction/lab.py
```

The baseline uses regular expressions. It works when wording matches its rules and fails when format changes. Inspect `01_structured_extraction/output/extractions.json`.

## 2. Diagnose before improving

With a partner, identify:

1. one field the rules extracted correctly;
2. one field they missed because the wording changed;
3. one field where a plausible answer would still be unsupported.

Then open `lab.py` and read `extract_with_rules()`.

## 3. Try the API path

```bash
python 01_structured_extraction/lab.py --api
```

The API path uses Structured Outputs with a Pydantic schema. It still checks the returned evidence quote against the original record.

## No-code path

Upload the four files in `data/records/` to an LLM and ask:

> Extract one row per document with: document_id, population, method, sample_size, main_finding, limitation, and one exact evidence_quote. Use null for a sample size that is not stated. Do not infer facts. Return JSON only.

Paste the JSON into a spreadsheet and compare it with `data/gold.json`.

## Extension

Rewrite one record into a paragraph with no labels. Predict whether the regex baseline or the model will be more robust. Then test both. Robustness is not the same as truth: keep the evidence-quote check.

