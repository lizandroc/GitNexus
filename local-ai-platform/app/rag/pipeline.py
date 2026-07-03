"""RAG pipeline: ingest (extract → chunk → embed → store) and query
(embed question → retrieve → grounded prompt → answer with citations).

Only retrieved chunk text ever reaches the model — never whole documents —
and the model is instructed to answer strictly from that context and to
say so when the context doesn't contain the answer.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Optional

from ..config import settings
from ..db import get_conn, new_id, record_run
from ..providers import ChatMessage, active_model, get_provider
from . import store
from .chunker import chunk_text
from .extract import extract_text

GROUNDED_SYSTEM_PROMPT = """You are a private document assistant. Answer the user's question using ONLY the numbered context passages below. Rules:
- Base every claim on the passages; do not use outside knowledge.
- Cite passages inline like [1] or [2][3] after each claim they support.
- If the passages do not contain the answer, say plainly that the provided documents do not answer the question. Never guess.
- Be concise and factual."""


async def ingest_document(doc_id: str) -> None:
    """Process an already-registered document: extract, chunk, embed, store.

    Status transitions: pending → ready | error. Errors are recorded on the
    document row so the dashboard can surface them.
    """
    conn = get_conn()
    row = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    if row is None:
        raise ValueError(f"Unknown document {doc_id}")
    start = time.monotonic()
    try:
        text = extract_text(Path(row["path"]))
        chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
        if not chunks:
            raise ValueError("Document produced no text chunks.")
        chunk_ids = [new_id() for _ in chunks]
        conn.executemany(
            "INSERT INTO chunks(id,document_id,kb,seq,text) VALUES(?,?,?,?,?)",
            [(cid, doc_id, row["kb"], i, c) for i, (cid, c) in enumerate(zip(chunk_ids, chunks))],
        )
        conn.commit()

        provider = get_provider()
        embed_model = settings.embedding_model if provider.name != "mock" else "mock-embed"
        # Embed in small batches to keep memory and request sizes bounded.
        for i in range(0, len(chunks), 16):
            batch_ids = chunk_ids[i:i + 16]
            vectors = await provider.embed(chunks[i:i + 16], embed_model)
            store.add_embeddings(batch_ids, vectors, embed_model)

        conn.execute(
            "UPDATE documents SET status='ready', num_chunks=?, error=NULL WHERE id=?",
            (len(chunks), doc_id),
        )
        conn.commit()
        record_run("embed", provider=provider.name, model=embed_model,
                   latency_ms=int((time.monotonic() - start) * 1000),
                   input_chars=len(text))
    except Exception as e:
        conn.execute("UPDATE documents SET status='error', error=? WHERE id=?", (str(e)[:500], doc_id))
        conn.commit()
        record_run("embed", status="error", error=str(e)[:500])
        raise


async def answer_question(
    question: str,
    kb: str = "default",
    top_k: Optional[int] = None,
    model: Optional[str] = None,
) -> dict[str, Any]:
    """Retrieve relevant chunks and generate a grounded, cited answer."""
    provider = get_provider()
    model = model or active_model()
    embed_model = settings.embedding_model if provider.name != "mock" else "mock-embed"
    top_k = top_k or settings.top_k

    start = time.monotonic()
    query_vec = (await provider.embed([question], embed_model))[0]
    hits = store.search(query_vec, kb=kb, top_k=top_k)

    if not hits:
        return {
            "answer": "No indexed documents matched this question. Upload documents to this knowledge base first.",
            "sources": [],
            "model": model,
            "provider": provider.name,
        }

    context = "\n\n".join(
        f"[{i + 1}] (from \"{h.filename}\", section {h.seq + 1})\n{h.text}"
        for i, h in enumerate(hits)
    )
    messages = [
        ChatMessage("system", GROUNDED_SYSTEM_PROMPT),
        ChatMessage("user", f"Context passages:\n\n{context}\n\nQuestion: {question}"),
    ]
    result = await provider.chat(messages, model)
    latency_ms = int((time.monotonic() - start) * 1000)
    record_run("rag_query", provider=provider.name, model=model,
               latency_ms=latency_ms, input_chars=len(question),
               output_chars=len(result.text))
    return {
        "answer": result.text,
        "sources": [
            {
                "ref": i + 1,
                "document_id": h.document_id,
                "filename": h.filename,
                "chunk_seq": h.seq,
                "score": round(h.score, 4),
                "excerpt": h.text[:300],
            }
            for i, h in enumerate(hits)
        ],
        "model": model,
        "provider": provider.name,
        "latency_ms": latency_ms,
    }
