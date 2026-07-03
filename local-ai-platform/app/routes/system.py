"""System endpoints: status, models, model selection, privacy mode,
runs history, and a simple model speed benchmark."""
from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..config import settings
from ..db import get_conn, get_setting, recent_runs, record_run, set_setting, usage_stats
from ..providers import (ChatMessage, ProviderError, active_model, all_providers,
                         auto_route_enabled, cloud_enabled, get_provider)

router = APIRouter(prefix="/v1", tags=["system"])


@router.get("/status")
async def status() -> dict[str, Any]:
    providers = {}
    for name, p in all_providers().items():
        providers[name] = {"healthy": await p.health(), "local": p.is_local}
    conn = get_conn()
    doc_count = conn.execute("SELECT COUNT(*) c FROM documents").fetchone()["c"]
    chunk_count = conn.execute("SELECT COUNT(*) c FROM chunks WHERE embedding IS NOT NULL").fetchone()["c"]
    return {
        "server": "ok",
        "providers": providers,
        "active_provider": get_setting("active_provider", settings.default_provider),
        "active_model": active_model(),
        "embedding_model": settings.embedding_model,
        "routing": {
            "auto": auto_route_enabled(),
            "fast_model": settings.fast_model,
            "quality_model": settings.quality_model,
        },
        "privacy": {
            "mode": "cloud-enabled" if cloud_enabled() else "local-only",
            "cloud_allowed_by_env": settings.allow_cloud,
        },
        "documents": doc_count,
        "indexed_chunks": chunk_count,
        "data_dir": str(settings.data_dir),
        "usage": usage_stats(),
    }


@router.get("/models")
async def models() -> dict[str, Any]:
    result: dict[str, Any] = {"active_provider": get_setting("active_provider", settings.default_provider),
                              "active_model": active_model(), "providers": {}}
    for name, p in all_providers().items():
        entry: dict[str, Any] = {"healthy": await p.health(), "models": []}
        if entry["healthy"]:
            try:
                entry["models"] = [
                    {"name": m.name, "size_bytes": m.size_bytes, "family": m.family, **m.details}
                    for m in await p.list_models()
                ]
            except ProviderError as e:
                entry["error"] = str(e)
        result["providers"][name] = entry
    return result


class SelectModelIn(BaseModel):
    provider: str
    model: str


@router.post("/models/select")
async def select_model(body: SelectModelIn) -> dict[str, Any]:
    try:
        get_provider(body.provider)  # validates existence + privacy gate
    except ProviderError as e:
        raise HTTPException(400, str(e))
    set_setting("active_provider", body.provider)
    set_setting("active_model", body.model)
    return {"active_provider": body.provider, "active_model": body.model}


class BenchmarkIn(BaseModel):
    provider: str | None = None
    model: str | None = None


@router.post("/models/benchmark")
async def benchmark(body: BenchmarkIn) -> dict[str, Any]:
    """One-shot speed probe: short fixed prompt, reports latency and tok/s."""
    try:
        provider = get_provider(body.provider)
        model = body.model or active_model()
        start = time.monotonic()
        result = await provider.chat(
            [ChatMessage("user", "Reply with a one-sentence description of what you are.")],
            model, temperature=0.0, max_tokens=60,
        )
    except ProviderError as e:
        raise HTTPException(502, str(e))
    latency_ms = int((time.monotonic() - start) * 1000)
    tokens_per_s = None
    if result.completion_tokens and latency_ms:
        tokens_per_s = round(result.completion_tokens / (latency_ms / 1000), 1)
    record_run("chat", provider=result.provider, model=model, latency_ms=latency_ms,
               output_chars=len(result.text))
    return {"provider": result.provider, "model": model, "latency_ms": latency_ms,
            "completion_tokens": result.completion_tokens, "tokens_per_second": tokens_per_s,
            "sample": result.text[:200]}


class RoutingIn(BaseModel):
    auto: bool


@router.post("/routing")
def set_routing(body: RoutingIn) -> dict[str, Any]:
    """Toggle auto model routing. On: each request gets the cheapest model
    that fits the task (saves tokens/compute). Off: every request uses the
    manually selected active model."""
    set_setting("auto_route", "on" if body.auto else "off")
    return {
        "auto": auto_route_enabled(),
        "fast_model": settings.fast_model,
        "quality_model": settings.quality_model,
    }


class PrivacyIn(BaseModel):
    cloud_mode: bool


@router.post("/privacy")
def set_privacy(body: PrivacyIn) -> dict[str, Any]:
    if body.cloud_mode and not settings.allow_cloud:
        raise HTTPException(
            403,
            "Cloud mode is disabled by server configuration. Start the server with "
            "LAP_ALLOW_CLOUD=true to make this toggle available.",
        )
    set_setting("cloud_mode", "on" if body.cloud_mode else "off")
    return {"privacy_mode": "cloud-enabled" if cloud_enabled() else "local-only"}


@router.get("/runs")
def runs(limit: int = 50) -> dict[str, Any]:
    return {"runs": recent_runs(min(limit, 200)), "stats": usage_stats()}
