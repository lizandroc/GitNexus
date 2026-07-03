"""SQLite persistence: documents, chunks (with embeddings), runs, settings.

A single local file (data/platform.db) holds everything. Embeddings are
stored as float32 BLOBs next to their chunk text — no external vector DB
needed at MVP scale. WAL mode keeps reads non-blocking while ingesting.
"""
from __future__ import annotations

import sqlite3
import threading
import time
import uuid
from typing import Any, Optional

from .config import settings

_local = threading.local()

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    kb TEXT NOT NULL DEFAULT 'default',
    path TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    num_chunks INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
    error TEXT,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    kb TEXT NOT NULL DEFAULT 'default',
    seq INTEGER NOT NULL,
    text TEXT NOT NULL,
    embedding BLOB,
    embedding_model TEXT
);
CREATE INDEX IF NOT EXISTS idx_chunks_kb ON chunks(kb);
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,            -- chat | summarize | classify | extract | rag_query | tool | embed
    tool TEXT,
    provider TEXT,
    model TEXT,
    status TEXT NOT NULL,          -- ok | error
    error TEXT,
    latency_ms INTEGER,
    input_chars INTEGER,
    output_chars INTEGER,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def get_conn() -> sqlite3.Connection:
    conn = getattr(_local, "conn", None)
    if conn is None:
        settings.ensure_dirs()
        conn = sqlite3.connect(settings.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.executescript(SCHEMA)
        _local.conn = conn
    return conn


def new_id() -> str:
    return uuid.uuid4().hex[:16]


# --- settings -----------------------------------------------------------

def get_setting(key: str, default: str = "") -> str:
    row = get_conn().execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    conn = get_conn()
    conn.execute(
        "INSERT INTO app_settings(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    conn.commit()


# --- runs (usage tracking) ----------------------------------------------

def record_run(
    kind: str,
    *,
    tool: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    status: str = "ok",
    error: Optional[str] = None,
    latency_ms: Optional[int] = None,
    input_chars: Optional[int] = None,
    output_chars: Optional[int] = None,
) -> str:
    run_id = new_id()
    conn = get_conn()
    conn.execute(
        "INSERT INTO runs(id,kind,tool,provider,model,status,error,latency_ms,"
        "input_chars,output_chars,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (run_id, kind, tool, provider, model, status, error, latency_ms,
         input_chars, output_chars, time.time()),
    )
    conn.commit()
    return run_id


def recent_runs(limit: int = 50) -> list[dict[str, Any]]:
    rows = get_conn().execute(
        "SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(r) for r in rows]


def usage_stats() -> dict[str, Any]:
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) c FROM runs").fetchone()["c"]
    errors = conn.execute("SELECT COUNT(*) c FROM runs WHERE status='error'").fetchone()["c"]
    avg = conn.execute(
        "SELECT AVG(latency_ms) a FROM runs WHERE status='ok' AND latency_ms IS NOT NULL"
    ).fetchone()["a"]
    by_kind = conn.execute(
        "SELECT kind, COUNT(*) c FROM runs GROUP BY kind ORDER BY c DESC"
    ).fetchall()
    by_tool = conn.execute(
        "SELECT tool, COUNT(*) c FROM runs WHERE tool IS NOT NULL GROUP BY tool ORDER BY c DESC"
    ).fetchall()
    return {
        "total_runs": total,
        "errors": errors,
        "avg_latency_ms": round(avg) if avg else None,
        "runs_by_kind": {r["kind"]: r["c"] for r in by_kind},
        "runs_by_tool": {r["tool"]: r["c"] for r in by_tool},
    }
