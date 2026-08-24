# Lab 01 · Structured extraction

## The task

Convert four short, differently written study records into one comparable schema:

`document_id · population · method · sample_size · main_finding · limitation · evidence_quote`

The records are fictional. A small gold set lets you score the result instead of judging it by feel.

## What you should learn

By the end, you should be able to:

- define a schema that represents both known and missing information;
- distinguish valid structure from correct content;
- compare a brittle rule with a semantically flexible model;
- verify that an evidence quote occurs in the original record.

Use the [extraction trace sheet](TRACE_TEMPLATE.md) to record the result of each test.

## Student lab · manual first

Before running a script or opening `data/gold.json`, choose A17 and complete all six fields yourself. Underline or copy the exact sentence supporting `main_finding`.

Then run the system and compare three things separately:

1. your manual row;
2. the system row; and
3. the gold row.

The objective is not to beat the model. It is to identify which disagreements come from the source, schema, extraction rule, evidence check, or interpretation.

## First watch one complete trace

Record D09 is useful because the prose explicitly says that the sample size was not reported. The correct structured value is `null`, not a plausible estimate.

```bash
python 01_structured_extraction/lab.py --record D09 --show-details
```

The regex baseline returns a perfectly shaped record but correctly extracts only one of five scored fields. Its `sample_size: null` happens to match the gold record, even though the rule did not understand the sentence. Shape, content, evidence, and meaning are different checks.

## 1. Run the brittle baseline

From the `labs/` folder:

```bash
python 01_structured_extraction/lab.py
```

The baseline uses regular expressions. It works when wording matches its rules and fails when format changes. The output reports three layers separately: schema shape, exact field matches, and whether the evidence quote occurs in the source. Inspect `01_structured_extraction/output/extractions.json` only after your manual A17 row is complete.

## 2. Diagnose before improving

With a partner, identify:

1. one field the rules extracted correctly;
2. one field they missed because the wording changed;
3. one field where a plausible answer would still be unsupported.

Then open `lab.py` and read `extract_with_rules()`.

Use `--record A17`, `--record B04`, `--record C22`, or `--record D09` to isolate one test. Add `--show-details` to print the source and every mismatch.

## 3. Try the API path

```bash
python 01_structured_extraction/lab.py --api
```

The API path uses Structured Outputs with a Pydantic schema. It still checks the returned evidence quote against the original record.

## No-code path · manual extraction

Choose one record at a time. Read it yourself or paste only that record into a model with this instruction:

> Extract one row per document with: document_id, population, method, sample_size, main_finding, limitation, and one exact evidence_quote. Use null for a sample size that is not stated. Do not infer facts. Return JSON only.

Paste the JSON into a spreadsheet and compare each field with `data/gold.json`. Then search the original record for `evidence_quote`. Do not award credit merely because the JSON parses.

## Three test conditions

- **Stable labels · A17:** Does the simple baseline succeed when the source uses its expected headings?
- **Changed wording · B04 or C22:** Can the extractor map prose and number words into the same schema?
- **Missing value · D09:** Does the extractor preserve `sample_size: null` without inventing a number?

## Done means more than “the JSON parsed”

Your pair should leave with:

- one completed row for each test condition;
- a separate shape, field, and quote result;
- one example of preserved missingness;
- one diagnosed failure: rule, schema, extraction, evidence, or meaning.

## Extension

Rewrite one record into a paragraph with no labels. Predict whether the regex baseline or the model will be more robust. Then test both. Robustness is not the same as truth: keep the evidence-quote check.

For a more consequential failure, imagine changing `sample_size` from `integer | null` to `integer`. The schema would no longer have a legal representation for “not reported.” A strict interface can create pressure to distort the source when the schema itself is wrong.
