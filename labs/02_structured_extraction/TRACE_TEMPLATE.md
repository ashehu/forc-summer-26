# Structured extraction trace

Names: ________________________________

Participation path: **code / no code**

Score each layer separately. Valid JSON is not evidence that the fields are correct.

## Manual A17 row · complete before opening gold.json

| population | method | sample_size | main_finding | limitation | exact evidence_quote |
|---|---|---:|---|---|---|
| | | | | | |

After running the system, mark each field: **manual = system**, **manual = gold**, or **system = gold**. Explain the most important disagreement below.

| Test | Record | Shape valid? | Correct fields | Missingness preserved? | Exact quote found? | Failure stage, if any |
| --- | --- | --- | --- | --- | --- | --- |
| Stable labels | A17 |  |  / 5 |  |  |  |
| Changed wording | B04 or C22 |  |  / 5 |  |  |  |
| Missing value | D09 |  |  / 5 |  |  |  |

## Inspect one failure

- **Source wording:** What did the record actually say?
- **Extracted value:** What did the system return?
- **Expected value:** What should the field contain?
- **Diagnosis:** Did the rule, schema, extraction, evidence check, or interpretation fail?
- **Next test:** What one change would test your diagnosis?

## Break the interface on purpose

Imagine that `sample_size` must be an integer and `null` is forbidden.

- What could the system return for D09?
- Which outputs would be structurally valid but epistemically wrong?
- How would you redesign the field so absence has an honest representation?
