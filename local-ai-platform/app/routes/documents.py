"""Document & knowledge-base endpoints: upload, list, delete, and RAG query.

Files are written to data/documents/ on local disk, indexed into SQLite,
and never leave the machine.
"""
from __future__ import annotations

import re
import time
from typing import Any, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from ..config import settings
from ..db import get_conn, new_id, record_run
from ..providers import ProviderError
from ..rag import answer_question, ingest_document

router = APIRouter(prefix="/v1", tags=["documents"])

MAX_UPLOAD_BYTES = 50 * 1024 * 1024


def _safe_name(filename: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]", "_", filename or "upload.txt")
    return name[-120:]


@router.post("/documents")
async def upload_document(file: UploadFile = File(...), kb: str = Form("default")) -> dict[str, Any]:
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"File exceeds {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit")
    if not data:
        raise HTTPException(400, "Empty file")

    doc_id = new_id()
    settings.ensure_dirs()
    path = settings.docs_dir / f"{doc_id}_{_safe_name(file.filename)}"
    path.write_bytes(data)

    conn = get_conn()
    conn.execute(
        "INSERT INTO documents(id,filename,kb,path,size_bytes,status,created_at) "
        "VALUES(?,?,?,?,?,'pending',?)",
        (doc_id, file.filename, kb, str(path), len(data), time.time()),
    )
    conn.commit()

    try:
        await ingest_document(doc_id)
    except ProviderError as e:
        raise HTTPException(502, f"Stored but not indexed — embedding provider error: {e}")
    except ValueError as e:
        raise HTTPException(422, f"Stored but not indexed: {e}")

    row = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    return _doc_dict(row)


@router.get("/documents")
def list_documents(kb: Optional[str] = None) -> dict[str, Any]:
    conn = get_conn()
    if kb:
        rows = conn.execute("SELECT * FROM documents WHERE kb=? ORDER BY created_at DESC", (kb,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
    return {"documents": [_doc_dict(r) for r in rows]}


@router.get("/knowledge-bases")
def list_knowledge_bases() -> dict[str, Any]:
    rows = get_conn().execute(
        "SELECT kb, COUNT(*) docs, SUM(num_chunks) chunks, SUM(size_bytes) bytes "
        "FROM documents GROUP BY kb ORDER BY kb"
    ).fetchall()
    return {"knowledge_bases": [
        {"name": r["kb"], "documents": r["docs"], "chunks": r["chunks"] or 0, "size_bytes": r["bytes"] or 0}
        for r in rows
    ]}


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str) -> dict[str, Any]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Document not found")
    conn.execute("DELETE FROM documents WHERE id=?", (doc_id,))  # chunks cascade
    conn.commit()
    try:
        from pathlib import Path
        Path(row["path"]).unlink(missing_ok=True)
    except OSError:
        pass  # DB row is gone; a stray file is harmless and local
    return {"deleted": doc_id}


class RagQueryIn(BaseModel):
    question: str
    kb: str = "default"
    top_k: Optional[int] = None
    model: Optional[str] = None


@router.post("/rag/query")
async def rag_query(body: RagQueryIn) -> dict[str, Any]:
    if not body.question.strip():
        raise HTTPException(400, "question must not be empty")
    try:
        return await answer_question(body.question, kb=body.kb, top_k=body.top_k, model=body.model)
    except ProviderError as e:
        record_run("rag_query", status="error", error=str(e)[:500])
        raise HTTPException(502, str(e))


def _doc_dict(row) -> dict[str, Any]:
    return {
        "id": row["id"], "filename": row["filename"], "kb": row["kb"],
        "size_bytes": row["size_bytes"], "num_chunks": row["num_chunks"],
        "status": row["status"], "error": row["error"], "created_at": row["created_at"],
    }
