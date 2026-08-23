# Lab 02 · Grounded question answering

## The task

Answer questions about a fictional graduate-support pilot using only five local documents. The system first retrieves likely evidence, then—only in API mode—asks a model to answer from that evidence.

This is a transparent miniature of retrieval-augmented generation (RAG):

`question → search local files → select context → answer with citations → verify`

## 1. Inspect retrieval without an API

```bash
python 02_grounded_qa/lab.py
```

The offline run prints evidence packets for three questions. One answer is deliberately absent from the corpus. Look for:

- a question answered by one document;
- a question requiring two documents;
- a question the system should refuse to answer.

Try your own question:

```bash
python 02_grounded_qa/lab.py --question "Why did evening attendance fall?"
```

## 2. Generate a grounded answer

```bash
python 02_grounded_qa/lab.py --api --question "Which group attended least, and what barrier was reported?"
```

The script checks whether cited filenames were actually retrieved and whether every evidence quote occurs in one of those files.

## No-code path

Upload the five files in `data/corpus/` and use this instruction:

> Answer only from the uploaded documents. Cite each factual sentence with [filename]. Include one short evidence quote. If the documents do not answer the question, say “Not found in the provided documents.” Do not use outside knowledge.

Ask the three questions in `data/questions.json`. Open the cited file each time.

## What to change

- Set `TOP_K = 1`. Which multi-document answer breaks?
- Ask a vague question. Does lexical retrieval select the evidence you expected?
- Add a misleading file with overlapping keywords. Retrieval quality and generation quality are separate problems.

