"""Paragraph-aware chunking with overlap.

Splits on blank lines first (keeps semantic units together), packs
paragraphs into chunks up to `chunk_size` characters, and carries
`overlap` characters of trailing context into the next chunk so answers
that span a boundary still retrieve well. Oversized single paragraphs are
hard-split at sentence-ish boundaries.
"""
from __future__ import annotations

import re


def _split_long(paragraph: str, chunk_size: int) -> list[str]:
    parts, current = [], ""
    for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
        if current and len(current) + len(sentence) + 1 > chunk_size:
            parts.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
        # A single "sentence" longer than chunk_size gets hard-sliced.
        while len(current) > chunk_size:
            parts.append(current[:chunk_size])
            current = current[chunk_size:]
    if current:
        parts.append(current)
    return parts


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    paragraphs: list[str] = []
    for p in re.split(r"\n\s*\n", text):
        p = p.strip()
        if not p:
            continue
        if len(p) > chunk_size:
            paragraphs.extend(_split_long(p, chunk_size))
        else:
            paragraphs.append(p)

    chunks: list[str] = []
    current = ""
    for p in paragraphs:
        if current and len(current) + len(p) + 2 > chunk_size:
            chunks.append(current)
            tail = current[-overlap:] if overlap else ""
            current = f"{tail}\n{p}".strip() if tail else p
        else:
            current = f"{current}\n\n{p}".strip() if current else p
    if current:
        chunks.append(current)
    return chunks
