"""Local AI Platform — FastAPI entrypoint.

Run:  uvicorn app.main:app --host 127.0.0.1 --port 8130
Dashboard:  http://127.0.0.1:8130/        API docs:  /docs
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse

from .config import settings
from .db import get_conn
from .routes import chat, documents, system, tools

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("local-ai-platform")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings.ensure_dirs()
    get_conn()  # create schema eagerly
    log.info("Data dir: %s | default provider: %s | cloud allowed: %s",
             settings.data_dir, settings.default_provider, settings.allow_cloud)
    yield


app = FastAPI(
    title="Local AI Platform",
    description="Private, local-first LLM platform: chat, tasks, RAG, and tools over Ollama / LM Studio.",
    version="0.1.0",
    lifespan=lifespan,
)

STATIC_DIR = Path(__file__).parent / "static"


@app.middleware("http")
async def auth_and_log(request: Request, call_next):
    # Optional bearer auth: enabled the moment LAP_API_KEY is set.
    # The dashboard and docs stay open; every /v1 call requires the key.
    if settings.api_key and request.url.path.startswith("/v1"):
        auth = request.headers.get("authorization", "")
        if auth != f"Bearer {settings.api_key}":
            return JSONResponse({"detail": "Missing or invalid API key"}, status_code=401)
    response = await call_next(request)
    if request.url.path.startswith("/v1"):
        log.info("%s %s -> %s", request.method, request.url.path, response.status_code)
    return response


@app.get("/", include_in_schema=False)
def workspace() -> FileResponse:
    """End-user workspace: chat, document Q&A, and tools."""
    return FileResponse(STATIC_DIR / "workspace.html")


@app.get("/ops", include_in_schema=False)
def ops_dashboard() -> FileResponse:
    """Operations dashboard: models, documents, runs, privacy controls."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", include_in_schema=False)
def health() -> dict:
    return {"status": "ok"}


app.include_router(system.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(tools.router)
