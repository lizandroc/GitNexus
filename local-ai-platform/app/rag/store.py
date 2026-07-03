"""Local vector store on SQLite.

Embeddings live as float32 BLOBs in the `chunks` table and search is
brute-force cosine similarity in Python. That is deliberately simple: at
MVP scale (thousands of chunks) a full scan takes milliseconds, needs zero
extra services, and keeps every byte on local disk. The interface
(`add_embeddings` / `search`) is the seam where sqlite-vec, LanceDB, or
pgvector slot in later without touching callers.
"""
from __future__ import annotations

import array
import math
from dataclasses import dataclass

from ..db import get_conn


def _to_blob(vec: list[float]) -> bytes:
    return array.array("f", vec).tobytes()


def _from_blob(blob: bytes) -> list[float]:
    a = array.array("f")
    a.frombytes(blob)
    return a.tolist()


def _cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return -1.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return -1.0
    return dot / (na * nb)


@dataclass
class SearchHit:
    chunk_id: str
    document_id: str
    filename: str
    seq: int
    text: str
    score: float


def add_embeddings(chunk_ids: list[str], vectors: list[list[float]], model: str) -> None:
    conn = get_conn()
    conn.executemany(
        "UPDATE chunks SET embedding=?, embedding_model=? WHERE id=?",
        [(_to_blob(v), model, cid) for cid, v in zip(chunk_ids, vectors)],
    )
    conn.commit()


def search(query_vector: list[float], kb: str = "default", top_k: int = 5) -> list[SearchHit]:
    rows = get_conn().execute(
        "SELECT c.id, c.document_id, c.seq, c.text, c.embedding, d.filename "
        "FROM chunks c JOIN documents d ON d.id = c.document_id "
        "WHERE c.kb=? AND c.embedding IS NOT NULL",
        (kb,),
    ).fetchall()
    scored = []
    for r in rows:
        score = _cosine(query_vector, _from_blob(r["embedding"]))
        scored.append(SearchHit(
            chunk_id=r["id"], document_id=r["document_id"], filename=r["filename"],
            seq=r["seq"], text=r["text"], score=score,
        ))
    scored.sort(key=lambda h: h.score, reverse=True)
    return scored[:top_k]
