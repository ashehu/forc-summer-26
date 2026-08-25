# RAG Starter — build retrieval over a 20-page corpus

This lab uses the fictional **Riverton Graduate Research Studio**: 10 short documents totaling exactly 20 pages. The topic is intentionally familiar so the first build can focus on chunking, embeddings, retrieval, provenance, and interface design.

The corpus contains no real people, student records, interviews, or institutional policies.

## What you will build

`20-page corpus → page-aware chunks → embeddings → local JSON index → similarity search → evidence interface`

This first version does **not** generate answers. It displays an evidence packet so retrieval can be inspected before another model is added.

## What you need

- Codex with this extracted folder open and permission to run local commands
- Python 3.9 or newer; Python 3.10+ is recommended
- Internet access for package installation and the embedding request
- An OpenAI API key with access to an API project for the embedding and query steps
- A web browser for the Streamlit interface

## Files

- `data/rag_starter_corpus.pdf` — human-readable 20-page collection
- `data/source_txt/` — the same content as page-preserving text files
- `data/questions.json` — seven starter questions
- `data/evaluation_questions.json` — expected sources and the corpus-boundary test
- `data/source_manifest.json` — scope and redistribution information
- `check_setup.py` — deterministic preflight that never prints the API key
- `chunk.py` — page-aware overlapping chunker
- `build_index.py` — batched OpenAI embeddings and local JSON index
- `retrieve.py` — terminal retrieval and seven-question evaluation runner
- `app.py` — retrieval-first Streamlit interface
- `API_KEY_SETUP.md` — safe local API-key instructions
- `CODEX_GUIDE.md` — seven prompts to paste into Codex in order

## Fastest path: use Codex

Open this extracted folder in Codex, then follow `CODEX_GUIDE.md`. Paste one prompt at a time and inspect each result before continuing.

## Manual setup — macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python check_setup.py
```

## Manual setup — Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python check_setup.py
```

## Configure the API key

Follow `API_KEY_SETUP.md`. The completed `.env` file stays local and is ignored by Git. Never paste the key into Codex, a shared chat, source code, or a screenshot.

Then verify it without printing it:

```bash
python check_setup.py --require-key
```

## 1 — inspect the source before code

Open the PDF and the ten text files. For each starter question, predict which document should contain the evidence. Q7 is a corpus-boundary test: the collection explicitly says it does not describe housing support.

## 2 — chunk the collection

```bash
python chunk.py --size 120 --overlap 25
```

Expected result: exactly 34 chunks in `output/chunks.json`. Each chunk retains filename, title, page, document type, document ID, and chunk ID.

## 3 — embed the chunks

```bash
python build_index.py --model text-embedding-3-small
```

Expected result: `output/index.json` contains 34 vectors, the model name, vector dimensions, and all source metadata. For this small corpus, JSON makes the vectors and metadata inspectable; a vector database is unnecessary.

## 4 — test retrieval in the terminal

```bash
python retrieve.py --top-k 5
```

Run a different question:

```bash
python retrieve.py --question "Where is the Wednesday build lab, what time does it meet, and what should I bring?" --top-k 5
```

Run the seven-question check:

```bash
python retrieve.py --all --top-k 5
```

## 5 — launch the interface

```bash
streamlit run app.py
```

Ask a question, change top-k, and inspect the evidence packet. Every result shows source, page, document type, score, and passage text.

## Completion criteria

You can:

1. explain the collection;
2. show how pages become overlapping chunks;
3. identify the embedding model;
4. trace a question into a query vector and ranked passages;
5. compare retrieval against expected sources; and
6. recognize that similarity search always returns passages even when the corpus does not answer the question.

Answer generation and broader evaluation come later.

## Official OpenAI references

- API quickstart: https://developers.openai.com/api/docs/quickstart
- Embeddings API: https://developers.openai.com/api/reference/resources/embeddings/methods/create
- Model page: https://developers.openai.com/api/docs/models/text-embedding-3-small
