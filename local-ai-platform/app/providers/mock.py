"""Mock provider: deterministic, offline, dependency-free.

Used by the test suite and by `LAP_PROVIDER=mock` so the whole platform
(API, RAG, tools, dashboard) can be exercised without a model runtime.
Embeddings are hash-based so identical text always lands on the same
vector — which makes retrieval assertions in tests deterministic.
"""
from __future__ import annotations

import hashlib
import math
from typing import Optional

from .base import ChatMessage, ChatResult, ModelInfo, Provider

_DIM = 64


def _hash_embed(text: str) -> list[float]:
    # Bag-of-words hashing into a fixed-size vector, L2-normalized.
    vec = [0.0] * _DIM
    for token in text.lower().split():
        h = int(hashlib.md5(token.encode()).hexdigest(), 16)
        vec[h % _DIM] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


class MockProvider(Provider):
    name = "mock"
    is_local = True

    async def health(self) -> bool:
        return True

    async def list_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(name="mock-small", provider=self.name),
            ModelInfo(name="mock-embed", provider=self.name),
        ]

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> ChatResult:
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        return ChatResult(
            text=f"[mock:{model}] {last_user[:400]}",
            model=model,
            provider=self.name,
            latency_ms=1,
        )

    async def embed(self, texts: list[str], model: str) -> list[list[float]]:
        return [_hash_embed(t) for t in texts]
