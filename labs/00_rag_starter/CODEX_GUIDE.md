# Build the first RAG proof of concept with Codex

Open the extracted starter-kit folder in Codex. Paste these prompts one at a time. Wait for the result and inspect it before using the next prompt.

## Prompt 1 — set up and run the preflight

> Treat the folder containing `README.md`, `chunk.py`, and `data/` as the project root, regardless of its folder name. Detect my operating system. Create a `.venv` virtual environment in the project root, install the exact packages in `requirements.txt`, and run `check_setup.py` with that environment's Python. Use the same virtual-environment Python for every later command, even if shell activation does not persist. Keep supplied source documents under `data/`, generated data under `output/`, and Python code in the project root. Do not move the source files, create a second project folder, or ask for an API key. Show the preflight results and stop.

## Prompt 2 — inspect the corpus

> Read `data/source_manifest.json`, `data/questions.json`, and all ten files in `data/source_txt/`. Explain how pages and metadata are represented. For the first three questions, predict which documents should contain the evidence. Do not write or change code yet. Show the predictions and stop.

## Prompt 3 — create and inspect chunks

> Review `chunk.py`, then run it with 120-word chunks and a 25-word overlap. Confirm that it writes `output/chunks.json` and produces exactly 34 chunks. Show three neighboring chunks, identify their repeated overlap, and confirm that every chunk retains its title, filename, page, document type, document ID, and chunk ID. If the count or metadata differs, diagnose it before continuing. Stop before embeddings.

## Prompt 4 — verify API access and create embeddings

> Using the project's virtual-environment Python, run `check_setup.py --require-key` without printing, requesting, or exposing the key. If the key is missing, open `API_KEY_SETUP.md`, create `.env` from `.env.example` with a blank value, and stop so I can add the key myself. After the preflight passes, review and run `build_index.py` with `text-embedding-3-small`. Confirm that `output/index.json` contains 34 vectors plus the source metadata and model name. Report the vector count and dimensions, then stop.

## Prompt 5 — test retrieval in the terminal

> Review the provided `retrieve.py`; do not create a different retrieval script. Run it for the first starter question with five results. Then run it for the Wednesday build-lab question with five results. For each result, show the score, title, filename, page, document type, and passage. Explain how the question embedding, cosine similarity, and top-k ranking produced the packet. Stop before launching the interface.

## Prompt 6 — launch the interface

> Review the existing `app.py`; preserve it and change only something required for it to run. Launch it with Streamlit and give me the local URL. Retrieve the first starter question with top-k set to five. Confirm that every result displays title, filename, page, document type, similarity score, and full passage. Keep the app retrieval-only: do not generate an answer or add a vector database.

## Prompt 7 — check the complete proof of concept

> Run `python retrieve.py --all --top-k 5`. Compare each packet with `data/evaluation_questions.json`. Produce a seven-row table with question ID, expected document, documents retrieved in the top five, and pass or investigate. For Q7, verify that the system retrieves the corpus-boundary passage and does not infer whether housing is provided. Confirm that every result traces back to a page. Finish with the exact commands needed to run the proof of concept again. Do not add answer generation.
