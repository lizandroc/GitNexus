"""LM Studio provider — speaks the OpenAI-compatible API that LM Studio's
local server exposes (default http://127.0.0.1:1234/v1).

Because this class only needs a base URL, it doubles as the adapter for any
other OpenAI-compatible runtime (llama.cpp server, vLLM, MLX server) —
point LAP_LMSTUDIO_URL at it and everything works.
"""
from __future__ import annotations

import time
from typing import Optional

import httpx

from ..config import settings
from .base import ChatMessage, ChatResult, ModelInfo, Provider, ProviderError


class LMStudioProvider(Provider):
    name = "lmstudio"
    is_local = True

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.lmstudio_url).rstrip("/")

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, timeout=settings.request_timeout)

    async def health(self) -> bool:
        try:
            async with self._client() as client:
                r = await client.get("/v1/models", timeout=3)
                return r.status_code == 200
        except httpx.HTTPError:
            return False

    async def list_models(self) -> list[ModelInfo]:
        try:
            async with self._client() as client:
                r = await client.get("/v1/models")
                r.raise_for_status()
        except httpx.HTTPError as e:
            raise ProviderError(f"LM Studio unreachable at {self.base_url}: {e}") from e
        return [
            ModelInfo(name=m["id"], provider=self.name)
            for m in r.json().get("data", [])
        ]

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> ChatResult:
        payload: dict = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "stream": False,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        start = time.monotonic()
        try:
            async with self._client() as client:
                r = await client.post("/v1/chat/completions", json=payload)
                r.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ProviderError(f"LM Studio chat failed ({e.response.status_code}): {e.response.text[:300]}") from e
        except httpx.HTTPError as e:
            raise ProviderError(f"LM Studio unreachable at {self.base_url}: {e}") from e
        data = r.json()
        usage = data.get("usage", {})
        return ChatResult(
            text=data["choices"][0]["message"]["content"],
            model=model,
            provider=self.name,
            latency_ms=int((time.monotonic() - start) * 1000),
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
        )

    async def embed(self, texts: list[str], model: str) -> list[list[float]]:
        try:
            async with self._client() as client:
                r = await client.post("/v1/embeddings", json={"model": model, "input": texts})
                r.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ProviderError(f"LM Studio embed failed ({e.response.status_code}): {e.response.text[:300]}") from e
        except httpx.HTTPError as e:
            raise ProviderError(f"LM Studio unreachable at {self.base_url}: {e}") from e
        data = sorted(r.json().get("data", []), key=lambda d: d.get("index", 0))
        return [d["embedding"] for d in data]
