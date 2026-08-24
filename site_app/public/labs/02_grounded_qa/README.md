# Lab 02 · Grounded question answering

## The task

Answer questions about a fictional graduate-support pilot using only five local documents. The lab exposes the complete pipeline: load the files, split them into overlapping chunks, create TF-IDF vectors, rank chunks with cosine similarity, assemble an evidence packet, generate an answer, and verify its citations and quotes.

This is a transparent miniature of retrieval-augmented generation (RAG):

`documents → chunks → vectors → retrieve → context → answer → verify`

## What you should learn

By the end, you should be able to:

- explain what each stage contributes;
- inspect a retrieval trace before trusting an answer;
- distinguish a retrieval failure from a generation failure;
- verify a cited filename and an exact evidence quote.

Use the [RAG pipeline trace](TRACE_TEMPLATE.md) to record what happens at each boundary.

## Meet the corpus before running retrieval

Open the five files in `data/corpus/`. For the multi-source question below, choose at most three passages by hand and record their filenames before running the script:

> Which school had the lowest median attendance, and what specific scheduling barrier did its students report?

Your manual selection is the first evidence packet. The system output is a second packet to compare—not an answer key.

## First watch one complete trace

The instructor will use the multi-source question because it exposes an important failure: one passage contains the attendance result, while a different passage contains the scheduling barrier.

```bash
python 02_grounded_qa/lab.py --show-chunks --question "Which school had the lowest median attendance, and what scheduling barrier did its students report?"
```

Then reduce retrieval to one passage:

```bash
python 02_grounded_qa/lab.py --top-k 1 --question "Which school had the lowest median attendance, and what scheduling barrier did its students report?"
```

The first result is still similar to the question, but the evidence packet is no longer sufficient. `top_k` always returns the requested number of highest-ranked chunks; it does not decide that the corpus truly answers the question.

## 1. Inspect documents and chunks

```bash
python 02_grounded_qa/lab.py --show-chunks
```

The default chunk size is 55 words with 12 words of overlap. Every chunk keeps its source filename and chunk number.

## 2. Inspect retrieval without an API

```bash
python 02_grounded_qa/lab.py
```

The offline run vectorizes every chunk and each question with TF-IDF, ranks chunks by cosine similarity, and prints the top three evidence chunks. One answer is deliberately absent from the corpus. Look for:

- a question answered by one document;
- a question requiring two documents;
- a question the system should refuse to answer.

Try your own question:

```bash
python 02_grounded_qa/lab.py --question "Why did evening attendance fall?"
```

For every evidence packet, complete the four printed offline steps: decide whether the packet is sufficient, answer or say “not found,” cite the filenames, and verify one exact quote in the original file.

## 3. Generate a grounded answer

```bash
python 02_grounded_qa/lab.py --api --question "Which group attended least, and what barrier was reported?"
```

The model receives only the retrieved evidence packet. The script then checks whether cited filenames were actually retrieved and whether every evidence quote occurs in the retrieved chunks.

## 4. Test the complete system

Run all three questions. Record the evidence packet before reading or writing the answer, then classify any failure by stage:

- **chunking:** was the needed passage split or stripped of useful context?
- **vectorization/retrieval:** did the needed chunk rank highly enough?
- **generation:** did the model use the retrieved evidence correctly?
- **verification:** did the filenames and quotations resolve?

For an 18-minute class run, complete the single-source and multi-source questions first. Treat the absent-answer question as the challenge condition if time is short.

## No-code path · manual retrieval

Do not upload all five files and let the interface hide retrieval. Instead:

1. Read the question in `data/questions.json`.
2. Search or skim the five files in `data/corpus/`.
3. Select at most three relevant passages and label each one with its filename.
4. Treat those passages as the evidence packet. Either answer directly or paste only that packet into a model with this instruction:

> Answer only from the supplied passages. Cite each factual sentence with [filename]. Include one short evidence quote. If the passages do not answer the question, say “Not found in the supplied passages.” Do not use outside knowledge.

5. Open every cited file and verify that the quotation is exact and that the passage supports the claim.

This path uses a human as the retriever, but it teaches the same evidence boundary as the code path.

## Done means more than “I got an answer”

Your pair should leave with three completed trace rows:

- the retrieved or manually selected passages;
- an answer or explicit “not found”;
- the cited filenames and one verified quote;
- the stage responsible for any failure.

## What to change

- Run with `--top-k 1`. Which multi-document answer breaks?
- Run with `--chunk-words 25 --overlap 5`. Does a useful passage split badly?
- Ask a vague question. Does lexical retrieval select the evidence you expected?
- Add a misleading file with overlapping keywords. Retrieval quality and generation quality are separate problems.
