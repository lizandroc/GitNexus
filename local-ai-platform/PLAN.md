# Local AI Platform — Implementation Plan

**The outcome first:** this repository now contains a working MVP of a private, local-first AI platform (`local-ai-platform/`). It runs open-source LLMs on a Mac through Ollama or LM Studio, exposes chat / summarize / classify / extract / RAG / tools through a clean localhost API, ingests private documents into a local vector index, answers questions with citations, ships three business tools and a dashboard, and sends **nothing** off the machine by default. This document is the plan behind it and the roadmap to an enterprise product.

What this product honestly is: a **private local AI platform** built on open-source models, RAG, and tools — with optional adapter fine-tuning later. It is not, and should never be marketed as, a foundation model trained from scratch.

---

## 1. Product vision

**For you (now):** one local AI engine on your Mac that every tool and automation you build can call — email analysis, lead recovery, contract summaries, CRM notes, report generation — with total privacy and no per-token cost.

**For enterprise clients (later):** the same platform packaged as a deployable appliance. Each company runs its **own instance** on its own hardware (Mac Studio, on-prem server, or private cloud), loads its own documents, picks its own models, controls its own users and audit logs. The pitch: *"Your AI. Your data. Your building."* Data sovereignty is the product; open-source models are the commodity underneath.

The business is repeatability: one codebase, deployed per client, customized with their knowledge bases, tools, and branding.

## 2. MVP scope

**In (built):** local model management over Ollama + LM Studio (list, switch, speed-test); model-agnostic HTTP API (chat, summarize, classify, extract, RAG query, tools); private document upload → local chunking → local embeddings → local vector search with cited answers; three example tools; dashboard (models, documents, KBs, runs, latency, privacy mode); usage logging; optional API-key auth; offline mock provider for testing.

**Out (deliberately):** multi-user accounts and RBAC, streaming responses, OCR of scanned documents, fine-tuning, cloud providers, Docker packaging, email/CRM connectors. All are roadmap items (§13, §15) — building them before the local core is proven would be overbuilding.

## 3. System architecture

```
┌────────────────────────────── Your Mac ──────────────────────────────┐
│                                                                      │
│  Dashboard (browser)      Your apps / automations                    │
│        │                        │                                    │
│        └──────────┬─────────────┘  HTTP (localhost:8130)             │
│                   ▼                                                  │
│  ┌──────────── FastAPI backend (app/) ────────────┐                  │
│  │  routes/   chat · documents · tools · system   │                  │
│  │  tools/    doc_qa · email_analyzer · workflows │                  │
│  │  rag/      extract → chunk → embed → retrieve  │                  │
│  │  providers/  ← privacy gate (local-only)       │                  │
│  └───────┬───────────────┬────────────┬───────────┘                  │
│          ▼               ▼            ▼                              │
│   Ollama :11434   LM Studio :1234   SQLite (data/platform.db)        │
│   (Metal/MLX-accelerated GGUF models)  docs · chunks+vectors · runs  │
│                                     data/documents/ (raw files)      │
└──────────────────────────────────────────────────────────────────────┘
```

Key decisions:
- **Provider abstraction** (`providers/base.py`): every runtime implements `health / list_models / chat / embed`. Ollama, LM Studio, and a mock provider exist today; the LM Studio adapter is OpenAI-compatible, so llama.cpp server, MLX server, or vLLM work by changing one URL. A future cloud provider is one module + registry entry — and is refused by the privacy gate unless cloud mode is explicitly on.
- **One SQLite file** holds documents, chunks, embeddings (float32 blobs), runs, and settings. Brute-force cosine search is milliseconds at MVP scale (thousands of chunks) and requires zero services. The store interface is the seam for sqlite-vec/LanceDB/pgvector later.
- **Tools are a registry**: a `ToolSpec` + `run()`; prompt-only tools are ~10-line declarations. This is the extension point for every future business tool.

## 4. Recommended tech stack

| Layer | MVP choice | Why / upgrade path |
|---|---|---|
| Model runtime | **Ollama** (primary), LM Studio (alt) | Metal-accelerated on Apple Silicon, one-line model pulls; LM Studio for GUI model shopping |
| Backend | **FastAPI + Python 3.11** | Async, auto OpenAPI docs, the RAG/ML ecosystem lives in Python |
| Vector store | **SQLite (embedded)** | Zero-ops; swap to sqlite-vec → LanceDB → pgvector as scale demands |
| Storage | File system + SQLite | → PostgreSQL in enterprise phase |
| Frontend | **Static HTML/JS dashboard served by the backend** | Zero build step for MVP; → Next.js + React + Tailwind in Phase 4 when multi-user UX arrives (the API is already the contract, so the frontend swap is clean) |
| Auth | Optional bearer key (`LAP_API_KEY`) | → per-user keys, then OIDC/SSO for enterprise |
| Packaging | venv + shell script | → Docker Compose for Linux/on-prem deploys (Ollama containers on Mac lose Metal, so on Mac stay native) |

## 5. File structure

```
local-ai-platform/
├── README.md               # quickstart + API reference
├── PLAN.md                 # this plan
├── requirements.txt
├── scripts/setup_mac.sh    # Ollama install + model pulls + venv
├── app/
│   ├── main.py             # FastAPI app, auth middleware, dashboard mount
│   ├── config.py           # env-driven settings, local-first defaults
│   ├── db.py               # SQLite schema: documents/chunks/runs/settings
│   ├── providers/          # base.py · ollama.py · lmstudio.py · mock.py · registry+privacy gate
│   ├── rag/                # extract.py · chunker.py · store.py · pipeline.py
│   ├── tools/              # base.py · doc_qa.py · email_analyzer.py · workflow_runner.py
│   ├── routes/             # chat.py · documents.py · tools.py · system.py
│   └── static/index.html   # dashboard
├── tests/test_api.py       # offline end-to-end suite (mock provider)
└── data/                   # created at runtime, gitignored: platform.db + documents/
```

## 6. Local Mac setup instructions

1. `cd local-ai-platform && ./scripts/setup_mac.sh` — installs Ollama (via Homebrew or prompts for the .dmg), starts it, pulls `llama3.2:3b`, `qwen2.5:7b`, `nomic-embed-text`, creates `.venv`, installs deps.
2. `./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8130`
3. Open `http://127.0.0.1:8130` (dashboard) and `/docs` (API explorer).
4. Upload a few documents, click a model's **Speed** button, ask a question in the RAG panel.

LM Studio (optional): install from lmstudio.ai, download a model in its UI, enable the local server (port 1234) — the platform detects it automatically.

## 7. Local LLM installation approach

Ollama is the management layer: `ollama pull <model>` downloads quantized GGUF weights; the platform's `/v1/models` endpoint lists whatever is installed, and the dashboard switches the active model with one click (persisted in settings, effective immediately — no restart). Model files live in `~/.ollama/models`. The dashboard's benchmark button gives latency + tokens/sec per model so you can compare on your own hardware. LM Studio models appear alongside Ollama's; the active provider+model pair is a single global setting every endpoint honors (overridable per request).

## 8. API design

Base URL `http://127.0.0.1:8130`, JSON in/out, optional `Authorization: Bearer <LAP_API_KEY>`. Errors are `{"detail": "..."}` with correct status codes (400 input, 401 auth, 404 unknown, 413 too large, 422 unprocessable, 502 provider down).

| Endpoint | Purpose |
|---|---|
| `POST /v1/chat` | `{messages:[{role,content}], model?, provider?, temperature?, max_tokens?}` → `{output, model, provider, latency_ms, prompt_tokens, completion_tokens}` |
| `POST /v1/summarize` | `{text, style?}` → `{output, ...}` |
| `POST /v1/classify` | `{text, labels:[...]}` → `{output, parsed:{label,confidence,reason}}` |
| `POST /v1/extract` | `{text, fields:{name:desc}}` → `{output, parsed:{...}}` |
| `POST /v1/documents` (multipart) | upload + index into a knowledge base |
| `GET/DELETE /v1/documents` | list / remove (index rows cascade) |
| `GET /v1/knowledge-bases` | KBs with doc/chunk/size counts |
| `POST /v1/rag/query` | `{question, kb?, top_k?}` → `{answer, sources:[{ref,filename,chunk_seq,score,excerpt}]}` |
| `GET /v1/tools` · `POST /v1/tools/{name}/run` | discover / run tools: `{inputs:{...}, model?}` |
| `GET /v1/models` · `POST /v1/models/select` · `POST /v1/models/benchmark` | model management |
| `GET /v1/status` · `POST /v1/privacy` · `GET /v1/runs` | health+privacy+usage |

Every call is logged to the `runs` table (kind, tool, provider, model, status, latency, sizes) — that is the usage-tracking backbone the dashboard reads.

## 9. Database and vector storage design

SQLite (`data/platform.db`, WAL mode, foreign keys on):

- **documents** — id, filename, kb, path, size, num_chunks, status (`pending|ready|error`), error, created_at
- **chunks** — id, document_id (FK, cascade delete), kb, seq, text, embedding BLOB (float32), embedding_model
- **runs** — id, kind, tool, provider, model, status, error, latency_ms, input/output chars, created_at
- **app_settings** — key/value (active provider/model, cloud toggle)

Vector search is exact cosine over the KB's chunks in Python. Scaling ladder: ~50k chunks → `sqlite-vec` extension (same file, ANN); heavier multi-user → LanceDB; enterprise/Postgres phase → pgvector. Only `rag/store.py` changes.

## 10. RAG pipeline design

**Ingest:** extract text (txt/md/csv/json/eml/html directly, PDF via pypdf) → paragraph-aware chunking (default 1200 chars, 200 overlap, sentence-splitting oversized paragraphs) → embed in batches of 16 via the local embedding model (`nomic-embed-text`) → store vectors beside text. Failures mark the document `error` with the reason visible in the dashboard.

**Query:** embed question → top-k cosine retrieval within the chosen KB → build a numbered-context prompt → local model answers under a grounding system prompt (answer **only** from passages, cite `[n]` inline, say plainly when the context doesn't contain the answer) → response carries structured `sources` (file, section, score, excerpt). Only retrieved chunks reach the model — never whole documents. An empty KB returns an honest "no documents matched" instead of a hallucination.

## 11. Dashboard feature list (all live)

Privacy badge (local-only vs cloud-enabled) · server + per-provider health · active provider/model · stat tiles (documents, indexed chunks, total runs, avg latency) · model list per provider with one-click **Use** and **Speed** (tok/s) buttons · document upload with KB assignment, status, delete · KB listing · RAG ask-your-documents panel with cited sources · three tool forms with output + latency · recent-runs table (kind, tool, model, status, latency) auto-refreshing.

## 12. Example tools (built)

1. **`doc_qa` — Private Document Q&A**: RAG over any KB, returns cited answers. The template for internal knowledge assistants.
2. **`email_analyzer` — Email/Conversation Analyzer**: paste a thread → summary, intent, sentiment, action items, risks, suggested reply. The template for lead recovery and comms triage.
3. **`workflow_runner` — Business Workflow Prompt Runner**: sequential multi-step prompt chains where each step sees the previous output. Presets: `contract_summary`, `crm_note`, `report_draft`; custom steps via JSON array. The template for report generation, extraction, and sales scripting.

New tools are a `ToolSpec` + prompt template (see `tools/base.py`) — most of the future catalog (CRM notes, sales scripts, data extraction) is configuration, not code.

## 13. Enterprise roadmap

| Stage | Additions |
|---|---|
| **E1 — Multi-user** | User accounts, per-user API keys, roles (admin/member/viewer), per-KB permissions; SQLite → PostgreSQL + pgvector; runs table becomes an append-only audit log with actor identity |
| **E2 — Deployable instance** | Docker Compose (API + Postgres + Ollama) for Linux servers/private cloud; native install for Mac hardware; instance config file (branding, model allowlist, retention policies); admin console (users, docs, models, logs, retention) |
| **E3 — Enterprise trust** | SSO (OIDC/SAML), encryption at rest (SQLCipher / FileVault+LUKS guidance), data-retention automation, exportable audit reports, white-label theming |
| **E4 — Customization** | Per-client tool packs, connectors (IMAP email, CRM, shared drives) running inside the instance, LoRA/adapter fine-tuning on client corpora (local training via MLX/axolotl), optional per-client evaluation harness |

Each client = one isolated instance of this codebase. No shared tenancy, no data pooling, no training on client data unless the client explicitly commissions it (E4).

## 14. Security and privacy plan

**Now:** binds to 127.0.0.1 only; provider registry hard-blocks non-local providers; cloud mode needs two explicit opt-ins (`LAP_ALLOW_CLOUD=true` env **and** dashboard toggle) and no cloud provider is even wired in; all data under `./data/` (gitignored); optional bearer-key auth; every AI call audit-logged; uploads size-capped and filename-sanitized; dashboard renders all model/tool output as text (XSS-escaped); no telemetry, no hidden calls — `grep httpx` shows exactly two localhost client classes.

**Enterprise phase:** per-user auth + RBAC (E1), encryption at rest (E3), TLS for LAN access, retention automation, immutable audit exports. Honest limits today: single shared API key, no per-user isolation, SQLite unencrypted at rest (rely on FileVault) — all called out so nobody mistakes the MVP for the enterprise build.

## 15. Step-by-step build phases

- **Phase 0–3 (done, this commit):** scaffold + config + DB; provider layer (Ollama/LM Studio/mock) with privacy gate; API endpoints; RAG pipeline; three tools; dashboard; offline test suite (8 tests passing).
- **Phase 4 — Daily-driver polish (1–2 wks):** streaming responses (SSE), background/async document ingestion with progress, folder-watch ingestion, richer benchmark page; swap dashboard to Next.js + Tailwind when UI complexity warrants it.
- **Phase 5 — Tool catalog (2–3 wks):** wire real workflows you use — IMAP inbox analyzer, lead-recovery pipeline, contract intake folder; tool definitions in config files so non-developers can add tools.
- **Phase 6 — Hardening (2 wks):** sqlite-vec for ANN search, retrieval eval set (golden Q&A pairs per KB), hybrid keyword+vector retrieval, per-key rate limits.
- **Phase 7 — E1/E2 enterprise base (4–6 wks):** Postgres + pgvector, users/roles, Docker Compose, admin console, first pilot client deployment.
- **Phase 8 — E3/E4 (ongoing):** SSO, encryption at rest, white-label, connectors, adapter fine-tuning.

## 16. Testing checklist

Automated (`python3 -m pytest tests/ -q`, offline, all passing): health/status; privacy mode reported and cloud toggle refused without env opt-in; model list/select; chat/summarize/classify/extract happy + error paths; upload → index → RAG query returns correct citations; empty-KB honesty; delete cascades; all three tools incl. validation errors; usage stats populate; API-key auth (401 without, 200 with, `/health` open).

Manual on the Mac: `setup_mac.sh` completes; dashboard shows Ollama healthy with pulled models; switching models takes effect on next call; Speed button reports tok/s; PDF upload indexes; RAG answer cites the right file; `curl` from a second terminal works with and without `LAP_API_KEY`; with Wi-Fi off, everything still works — the definitive privacy test.

**Self-verification against the brief:** runs local models on Mac ✔ (Ollama/LM Studio, Metal-accelerated) · other apps call it via API ✔ (§8) · private upload/index/search ✔ (§9–10) · RAG with citations works ✔ (tested) · dashboard shows models/docs/tools/privacy ✔ (§11) · evolves to enterprise ✔ (§13) · no foundation-model claims ✔ (positioning in §1) · not over-engineered ✔ (one process, one DB file, no queues/microservices/build steps).
