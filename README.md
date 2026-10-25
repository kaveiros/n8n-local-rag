# n8n Local RAG (Ollama + PGVector)

A fully local Retrieval-Augmented Generation workflow for [n8n](https://n8n.io). It ingests PDF and text files from a folder into PostgreSQL/pgvector, then answers questions in a chat UI using only the retrieved content.

No cloud APIs: chat and embeddings both run on [Ollama](https://ollama.com).

**[Live preview of the workflow](https://kaveiros.github.io/n8n-local-rag/)** (interactive canvas, GitHub Pages)

## Architecture

```
INGESTION (manual trigger)
Execute workflow → Read Files from Disk → Switch (by file type)
   ├─ pdf  → Extract from File (PDF)   → Edit Fields      ┐
   └─ text → Extract from text file    → Edit Text fields ┴→ insertTo Documents (PGVector)
                                                              ├─ Embeddings Ollama (bge-m3)
                                                              └─ Default Data Loader + Recursive Character Text Splitter (800/100)

CHAT
Chat trigger → AI Agent ── Ollama Chat Model
                       ├── Simple Memory
                       └── Postgres PGVector Store (retrieve-as-tool, topK 5) + Embeddings Ollama (bge-m3)
```

## Requirements

- n8n (self-hosted; the workflow reads files from the server's disk)
- PostgreSQL 15+ with the [`pgvector`](https://github.com/pgvector/pgvector) extension
- Ollama with these models:
  - Embeddings: `bge-m3`
  - Chat: `krikri-4k` (a Llama 3-based Greek model), which works with the agent's tool calling. Any tool-capable Ollama model also works.

```bash
ollama pull bge-m3
# Chat model: krikri-4k (custom model) - or e.g. llama3.1 / qwen2.5
```

## Setup

### 1. Create the table

```bash
psql -U <user> -d <database> -f sql/init.sql
```

The schema uses `vector(1024)` to match `bge-m3`. If you change the embedding model, change the dimension and re-ingest.

### 2. Import the workflow

In n8n: **Workflows → Import from file →** `workflows/rag.json`.

### 3. Configure credentials

The export contains no secrets. After importing, open these nodes and select or create credentials:

| Node | Credential |
|------|------------|
| Ollama Chat Model, Embeddings Ollama | Ollama (base URL, e.g. `http://localhost:11434`) |
| Postgres PGVector Store, insertTo Documents | Postgres |

If n8n runs in Docker, `localhost` points at the container. Use `http://host.docker.internal:11434` for Ollama.

### 4. Set the documents folder

Open **Read Files from Disk** and set the path (default `/home/nikos/data/*`). The folder must be readable by the n8n process. In Docker, mount it as a volume.

### 5. Ingest

Click **Execute workflow** (manual trigger). Then check the table:

```sql
SELECT count(*), metadata->>'source' FROM documents GROUP BY 2;
```

### 6. Chat

Open the **When chat message received** node and use the chat panel, or activate the workflow and use the public chat URL.

## How it works

- **Chunking:** the Default Data Loader embeds only the `content` field, split by a Recursive Character Text Splitter (chunk 800, overlap 100).
- **Metadata:** each chunk stores `source` (the file name) for citation.
- **Retrieval:** the agent's system prompt forces a vector-store lookup for every question and tells it to answer only from the results.
- **Embeddings:** the same model (`bge-m3`) is used for insertion and retrieval. Never mix models in one table.

## Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| Agent answers without searching | Check the system prompt is set on the AI Agent node. If it still skips the tool, try a tool-capable model such as `llama3.1` or `qwen2.5`. |
| Tool is called but returns nothing | Table empty, or embeddings were created with a different model. `TRUNCATE documents;` and re-ingest. |
| Answers truncated or ignore context | Context window too small. Lower `topK` and raise `num_ctx` in the Ollama Chat Model options. |
| Duplicate chunks | Ingestion ran more than once. Truncate and re-run (or add dedupe by `metadata->>'source'`). |
| Scanned PDFs yield no text | They have no text layer. They need an OCR step first. |

## Roadmap

- [ ] DOCX support (Docling / Tika / mammoth)
- [ ] Image extraction and description with a vision model
- [ ] Dedupe on re-ingestion
- [ ] Docker Compose stack (n8n + Postgres/pgvector + Ollama)

## Project layout

```
.
├── README.md
├── workflows/rag.json   # n8n workflow (no credentials)
├── sql/init.sql         # documents table + indexes
├── docs/index.html      # GitHub Pages preview (generated)
├── scripts/build_pages.py  # regenerates docs/index.html from the workflow
├── data/                # local files to ingest (git-ignored)
└── .gitignore
```

## Security notes

- Never commit n8n credentials or `.env` files. The workflow here is exported without credential IDs.
- The chat trigger is set to **public**. Put n8n behind authentication or a reverse proxy before exposing it.
