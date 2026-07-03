"""Ollama provider — the primary local runtime on Apple Silicon Macs.

Uses Ollama's native HTTP API (http://127.0.0.1:11434). Ollama runs models
via llama.cpp with Metal acceleration, so this is the fastest path on a Mac.
"""
from __future__ import annotations

import time
from typing import Optional

import httpx

from ..config import settings
from .base import ChatMessage, ChatResult, ModelInfo, Provider, ProviderError


class OllamaProvider(Provider):
    name = "ollama"
    is_local = True

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.ollama_url).rstrip("/")

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, timeout=settings.request_timeout)

    async def health(self) -> bool:
        try:
            async with self._client() as client:
                r = await client.get("/api/tags", timeout=3)
                return r.status_code == 200
        except httpx.HTTPError:
            return False

    async def list_models(self) -> list[ModelInfo]:
        try:
            async with self._client() as client:
                r = await client.get("/api/tags")
                r.raise_for_status()
        except httpx.HTTPError as e:
            raise ProviderError(f"Ollama unreachable at {self.base_url}: {e}") from e
        models = []
        for m in r.json().get("models", []):
            details = m.get("details", {})
            models.append(ModelInfo(
                name=m["name"],
                provider=self.name,
                size_bytes=m.get("size"),
                family=details.get("family"),
                details={
                    "parameter_size": details.get("parameter_size"),
                    "quantization": details.get("quantization_level"),
                },
            ))
        return models

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
            "stream": False,
            "options": {"temperature": temperature},
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        start = time.monotonic()
        try:
            async with self._client() as client:
                r = await client.post("/api/chat", json=payload)
                r.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ProviderError(f"Ollama chat failed ({e.response.status_code}): {e.response.text[:300]}") from e
        except httpx.HTTPError as e:
            raise ProviderError(f"Ollama unreachable at {self.base_url}: {e}") from e
        data = r.json()
        return ChatResult(
            text=data.get("message", {}).get("content", ""),
            model=model,
            provider=self.name,
            latency_ms=int((time.monotonic() - start) * 1000),
            prompt_tokens=data.get("prompt_eval_count"),
            completion_tokens=data.get("eval_count"),
        )

    async def embed(self, texts: list[str], model: str) -> list[list[float]]:
        try:
            async with self._client() as client:
                r = await client.post("/api/embed", json={"model": model, "input": texts})
                r.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ProviderError(f"Ollama embed failed ({e.response.status_code}): {e.response.text[:300]}") from e
        except httpx.HTTPError as e:
            raise ProviderError(f"Ollama unreachable at {self.base_url}: {e}") from e
        return r.json().get("embeddings", [])
