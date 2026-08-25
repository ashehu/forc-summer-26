# Case 01 · Evidence discovery across opioid-industry records

## The research problem

The U.S. opioid crisis unfolded through successive waves involving prescription opioids, heroin, and synthetic opioids. Litigation brought by governments against companies across the opioid supply chain subsequently made large collections of corporate records public through discovery, judgments, and settlements. The UCSF-Johns Hopkins archive preserves these records for research and public understanding.

The resulting collection contains millions of heterogeneous records: emails, marketing plans, sales-training guides, policy papers, compliance documents, exhibits, and reports. Researchers need to locate relevant passages, identify recurring themes and shifts across documents, and follow promising connections without losing the document identity, page, genre, and original source that make interpretation possible.

This lab asks:

> How can an AI-assisted research workbench help researchers find evidence, surface patterns and trends, and trace every insight back to the original record?

The desired output is not a generic summary. It is a bounded evidence memo containing:

- the question being answered;
- the passages selected for review;
- the genre and provenance of every source;
- a short synthesis that distinguishes reports, proposals, internal messaging, and evaluated outcomes;
- exact citations and at least one verified quotation; and
- an explicit statement of what the evidence does not establish.

The system must not provide medical advice, infer intent, treat a corporate statement as an independently verified outcome, or use interview-derived data.

## The real project and the classroom replica

The original Research RAG Workbench processes a much larger local collection of OCR-derived public litigation documents. It supports BM25, embedding, and hybrid retrieval; grounded answers; document summaries; and a web interface. The full project also contains internal and interview-related material that is not part of this course.

This classroom replica contains five short text files:

1. an archive description;
2. a pharmacy's public-facing response statement;
3. a manufacturer's policy paper;
4. an internal sales-training guide; and
5. federal commission recommendations.

Each teaching excerpt links to its original public record in the UCSF-Johns Hopkins Opioid Industry Documents Archive. The excerpts are selected for learning and are not a representative sample of the archive. See `data/source_manifest.json`.

## Why this is difficult

### 1 · OCR changes the evidence surface

Scanned pages must become searchable text. OCR can damage names, numbers, headings, tables, negation, and page boundaries. A passage that was never transcribed correctly cannot be retrieved correctly.

### 2 · Similar words do not imply the same source role

A policy recommendation, a corporate response statement, an internal sales guide, and an evaluation may all contain the same terms. They support different kinds of claims. Retrieval must preserve genre and provenance, not only text.

### 3 · One question may require several documents

Top-ranked passages can be individually relevant yet collectively insufficient. A comparison question may require one passage from each source type.

### 4 · Reported activity is not demonstrated impact

A document can support the claim that an organization reported an action. It cannot, by itself, establish that the action occurred as described or caused an outcome.

### 5 · A fluent answer can hide the failed layer

The error may originate in OCR, chunking, retrieval, context assembly, generation, or verification. The final prose does not reveal which boundary failed.

## Implementation map

The production workbench and the classroom replica share the same logic:

`public PDF → OCR + provenance → chunks → index → retrieve → evidence packet → bounded answer → source audit`

The production system uses BM25, embeddings, or hybrid retrieval. The classroom script uses TF-IDF and cosine similarity so every calculation remains inspectable without an API key.

The classroom implementation:

- reads metadata and excerpt text separately;
- creates overlapping 55-word chunks;
- keeps document ID, genre, source page, and original URL attached to every chunk;
- ranks chunks for each question;
- prints the evidence packet before any answer is generated;
- optionally asks an LLM to answer only from that packet; and
- checks that cited filenames and quotations occur in the retrieved evidence.

## Learning goals

By the end, you should be able to:

- translate a broad research interest into an answerable retrieval question;
- explain how OCR, chunking, retrieval, and context assembly affect the evidence;
- distinguish source relevance from source role and credibility;
- diagnose whether a failure occurred before or after generation; and
- produce a claim that is calibrated to what the documents actually establish.

Use [TRACE_TEMPLATE.md](TRACE_TEMPLATE.md) throughout the lab.

## Student investigation · manual first

Open the five files in `data/corpus/`. Before running code, answer these questions:

1. What genre is each document?
2. Which document can support a claim about a reported action?
3. Which document exposes an internal product-message strategy?
4. Which document, if any, independently evaluates outcomes?

For the comparison question below, choose at most three passages manually:

> Compare prevention and oversight in the Walgreens response and Mallinckrodt policy paper with product messaging in the internal sales guide.

Record the filenames and source roles before seeing the system ranking.

## 1 · Inspect the complete corpus and chunk boundaries

From the `labs` directory:

```bash
python 01_opioid_evidence/lab.py --show-chunks
```

Ask whether each 55-word chunk still carries enough surrounding meaning. Then try:

```bash
python 01_opioid_evidence/lab.py --chunk-words 30 --overlap 5 --show-chunks
```

Which claims or qualifications become separated?

## 2 · Compare human and system retrieval

```bash
python 01_opioid_evidence/lab.py \
  --question "Compare prevention and oversight in the Walgreens response and Mallinckrodt policy paper with product messaging in the internal sales guide."
```

Compare the top-three packet with your manual packet. A useful packet should include all three required genres.

Now break the comparison:

```bash
python 01_opioid_evidence/lab.py \
  --top-k 1 \
  --question "Compare prevention and oversight in the Walgreens response and Mallinckrodt policy paper with product messaging in the internal sales guide."
```

The highest-ranked passage may be relevant, but one passage cannot support a three-document comparison.

## 3 · Test an answerable and an unanswerable question

Single-source question:

```bash
python 01_opioid_evidence/lab.py \
  --question "What concrete measures did Walgreens say it was taking to address opioid misuse and overdose?"
```

Absent-outcome question:

```bash
python 01_opioid_evidence/lab.py \
  --question "Did the reported measures reduce overdose deaths?"
```

The second packet contains statements about actions and proposals, plus explicit limitations. It contains no independent outcome evaluation. The responsible answer is “not found in this corpus.”

## 4 · Optional API path

After auditing retrieval manually:

```bash
python 01_opioid_evidence/lab.py \
  --api \
  --question "What concrete measures did Walgreens say it was taking to address opioid misuse and overdose?"
```

The model receives only the retrieved packet. The validator checks filenames and exact quotations. Those checks do not establish source credibility or research validity; a human still owns those judgments.

## No-code path

1. Search the five files manually.
2. Select no more than three passages.
3. Label each passage with filename, genre, and original URL.
4. Answer directly, or give only those passages to a model with this instruction:

> Answer only from the supplied passages. Distinguish reported actions, policy proposals, internal messaging, and evaluated outcomes. Cite every factual sentence with [filename]. Include one short exact quote. If the passages do not answer the question, say “Not found in the supplied passages.” Do not use outside knowledge or provide medical advice.

5. Open the original UCSF record and verify one quote visually.

## Done means an auditable evidence memo

Your final trace must include:

- the manual and system evidence packets;
- a source-role label for every passage;
- an answer or explicit refusal;
- one exact quote verified against the original record;
- the failed pipeline stage for the `top_k=1` test; and
- one sentence explaining what the selected records cannot establish.

## Data boundary

All course files in this lab are short teaching excerpts from public archive records or course-authored context. No interview transcripts, interview-derived evaluation cases, cached indexes, credentials, or internal client trackers are included.
