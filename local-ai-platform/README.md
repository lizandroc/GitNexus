# Local AI Platform

A private, local-first AI platform for macOS (Apple Silicon optimized). Run open-source LLMs on your own Mac through Ollama or LM Studio, expose them to your apps through a clean HTTP API, ask questions of your private documents with a local RAG pipeline, and power business tools — with **zero data leaving your machine by default**.

See **[PLAN.md](PLAN.md)** for the full implementation plan, architecture, model strategy, and enterprise roadmap.

## Quickstart (Mac)

```bash
cd local-ai-platform
./scripts/setup_mac.sh          # installs Ollama, pulls starter models, creates venv
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8130
```

Open the dashboard at **http://127.0.0.1:8130** and the interactive API docs at **http://127.0.0.1:8130/docs**.

No Ollama yet? Try everything with the offline mock provider:

```bash
LAP_PROVIDER=mock LAP_MODEL=mock-small ./.venv/bin/uvicorn app.main:app --port 8130
```

## What you get

| Capability | Endpoint |
|---|---|
| Chat with the active local model | `POST /v1/chat` |
| Summarize / classify / extract | `POST /v1/summarize` · `/v1/classify` · `/v1/extract` |
| Upload private documents (.txt .md .pdf .csv .eml …) | `POST /v1/documents` |
| Ask your documents (RAG with citations) | `POST /v1/rag/query` |
| Run business tools | `GET /v1/tools` · `POST /v1/tools/{name}/run` |
| Models: list, switch, speed-test | `GET /v1/models` · `POST /v1/models/select` · `/v1/models/benchmark` |
| Status, privacy mode, usage | `GET /v1/status` · `POST /v1/privacy` · `GET /v1/runs` |

Built-in tools: **Private Document Q&A** (RAG-backed), **Email/Conversation Analyzer**, **Business Workflow Prompt Runner** (presets: `contract_summary`, `crm_note`, `report_draft`, or custom steps).

## Calling it from your own apps

```bash
curl -X POST http://127.0.0.1:8130/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Draft a follow-up email to a cold lead"}]}'
```

Set `LAP_API_KEY=<secret>` when starting the server to require `Authorization: Bearer <secret>` on all `/v1` calls.

## Privacy model

- **Local-only by default.** Only localhost providers (Ollama, LM Studio) are reachable. Documents, embeddings, and logs live in `./data/` on your disk.
- Cloud mode requires **two** explicit opt-ins: start the server with `LAP_ALLOW_CLOUD=true` *and* flip the toggle. Neither exists out of the box — there is no cloud provider wired in yet.
- The dashboard always shows the current privacy mode.

## Configuration

All via environment variables: `LAP_PORT` (8130), `LAP_DATA_DIR` (./data), `LAP_PROVIDER` (ollama), `LAP_MODEL` (llama3.2:3b), `LAP_EMBEDDING_MODEL` (nomic-embed-text), `LAP_OLLAMA_URL`, `LAP_LMSTUDIO_URL`, `LAP_API_KEY`, `LAP_ALLOW_CLOUD`, `LAP_CHUNK_SIZE`, `LAP_CHUNK_OVERLAP`, `LAP_TOP_K`.

## Tests

```bash
python3 -m pytest tests/ -q     # runs fully offline against the mock provider
```
