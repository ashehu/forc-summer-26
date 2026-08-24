# RAG pipeline trace

Names: ________________________________

Participation path: **code / no code**

Record the evidence packet before reading or writing the answer. A high similarity score does not prove that the packet is sufficient.

## Manual packet before retrieval

For the multi-source question, write the filenames and passages you select before running the script.

**Predicted files:** ________________________________________________

**Selected passages:**
____________________________________________________________________
____________________________________________________________________

**After retrieval: what did the system add, omit, or rank differently?**
____________________________________________________________________

| Test | Question | Retrieved or manually selected passages | Is the packet sufficient? | Answer or “not found” | Filenames cited | Exact quote verified? | Failure stage, if any |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Single source | Which outcome showed the largest observed difference? |  |  |  |  |  |  |
| Multiple sources | Who attended least—and what barrier did they report? |  |  |  |  |  |  |
| Absent answer | Did doctoral completion increase? |  |  |  |  |  |  |

## Break one stage on purpose

Change one retrieval setting or invent an adversarial fourth question.

- **Prediction:** What do you expect to fail, and why?
- **Observation:** What actually changed in the trace?
- **Diagnosis:** Was the failure in chunking, retrieval, generation, or verification?
- **Next test:** What one change would test your diagnosis?
