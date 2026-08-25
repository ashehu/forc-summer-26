# API key setup for the RAG starter

The embedding and retrieval steps call the OpenAI Embeddings API. You need an API key with access to an OpenAI API project. The key is a secret: do not paste it into Codex, a shared chat, source code, screenshots, or a repository.

## 1 — create or obtain a key

Use the OpenAI API dashboard: https://platform.openai.com/api-keys

Confirm that the API project is able to make requests. If the course provides a managed API route, follow the instructor's directions instead of creating a personal key.

## 2 — create a local `.env` file

macOS or Linux:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Open `.env` yourself and place the key after the equals sign:

```text
OPENAI_API_KEY=your-key-goes-here
```

Save the file and close it. The supplied `.gitignore` excludes `.env` from Git. The file remains local and unencrypted, so protect the computer account and delete the file when it is no longer needed.

## 3 — verify without printing the key

```bash
python check_setup.py --require-key
```

The expected line is:

```text
[PASS] API key: available (value hidden)
```

## Troubleshooting

- `API key: missing`: confirm that the file is named exactly `.env` and the line begins with `OPENAI_API_KEY=`.
- `Missing credentials`: rerun the preflight from the folder containing `check_setup.py`.
- Authentication or project-access error: create a new project key or ask the instructor which API project to use.
- Rate-limit or quota error: wait briefly, confirm project access, or use the instructor's backup plan.

Official references:

- OpenAI API quickstart: https://developers.openai.com/api/docs/quickstart
- Embeddings model: https://developers.openai.com/api/docs/models/text-embedding-3-small
