"""Core AI endpoints: chat plus the task endpoints (summarize, classify,
extract) that other apps call. All of them are thin shapes over the active
local provider, with usage logged per request.
"""
from __future__ import annotations

import json
import time
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..db import record_run
from ..providers import ChatMessage, ProviderError, get_provider, resolve_model

router = APIRouter(prefix="/v1", tags=["ai"])


class ChatIn(BaseModel):
    messages: list[dict[str, str]] = Field(..., description="[{role, content}] — roles: system|user|assistant")
    model: Optional[str] = None
    provider: Optional[str] = None
    temperature: float = 0.2
    max_tokens: Optional[int] = None


class TaskIn(BaseModel):
    text: str
    model: Optional[str] = None
    provider: Optional[str] = None
    # summarize
    style: Optional[str] = Field(None, description="e.g. 'bullet points', 'one paragraph'")
    # classify
    labels: Optional[list[str]] = None
    # extract
    fields: Optional[dict[str, str]] = Field(None, description="field name -> description of what to extract")


async def _run_chat(kind: str, messages: list[ChatMessage], body_model: Optional[str],
                    body_provider: Optional[str], temperature: float = 0.2,
                    max_tokens: Optional[int] = None) -> dict[str, Any]:
    start = time.monotonic()
    input_chars = sum(len(m.content) for m in messages)
    user_text = " ".join(m.content for m in messages if m.role == "user")
    model, routing = resolve_model(kind, input_chars=input_chars, text=user_text,
                                   explicit=body_model)
    try:
        provider = get_provider(body_provider)
        result = await provider.chat(messages, model, temperature=temperature, max_tokens=max_tokens)
    except ProviderError as e:
        record_run(kind, status="error", error=str(e)[:500])
        raise HTTPException(status_code=502, detail=str(e))
    latency_ms = int((time.monotonic() - start) * 1000)
    record_run(kind, provider=result.provider, model=result.model, latency_ms=latency_ms,
               input_chars=input_chars, output_chars=len(result.text))
    return {
        "output": result.text,
        "model": result.model,
        "provider": result.provider,
        "routing": routing,
        "latency_ms": latency_ms,
        "prompt_tokens": result.prompt_tokens,
        "completion_tokens": result.completion_tokens,
    }


@router.post("/chat")
async def chat(body: ChatIn) -> dict[str, Any]:
    if not body.messages:
        raise HTTPException(400, "messages must not be empty")
    messages = [ChatMessage(m.get("role", "user"), m.get("content", "")) for m in body.messages]
    return await _run_chat("chat", messages, body.model, body.provider,
                           body.temperature, body.max_tokens)


@router.post("/summarize")
async def summarize(body: TaskIn) -> dict[str, Any]:
    style = body.style or "a short paragraph followed by key bullet points"
    messages = [
        ChatMessage("system", "You summarize documents faithfully. Never add facts that are not in the text."),
        ChatMessage("user", f"Summarize the following text as {style}:\n\n---\n{body.text}\n---"),
    ]
    return await _run_chat("summarize", messages, body.model, body.provider)


@router.post("/classify")
async def classify(body: TaskIn) -> dict[str, Any]:
    if not body.labels:
        raise HTTPException(400, "classify requires 'labels': a list of candidate labels")
    labels = ", ".join(body.labels)
    messages = [
        ChatMessage("system",
                    'You are a strict classifier. Reply with JSON only: {"label": "<one of the allowed labels>", "confidence": <0..1>, "reason": "<one sentence>"}'),
        ChatMessage("user", f"Allowed labels: {labels}\n\nClassify this text:\n---\n{body.text}\n---"),
    ]
    result = await _run_chat("classify", messages, body.model, body.provider, temperature=0.0)
    result["parsed"] = _try_parse_json(result["output"])
    return result


@router.post("/extract")
async def extract(body: TaskIn) -> dict[str, Any]:
    if not body.fields:
        raise HTTPException(400, "extract requires 'fields': {field_name: description}")
    field_lines = "\n".join(f'- "{name}": {desc}' for name, desc in body.fields.items())
    messages = [
        ChatMessage("system",
                    "You extract structured data from text. Reply with a single JSON object containing exactly the requested fields. Use null for anything not present in the text — never invent values."),
        ChatMessage("user", f"Fields to extract:\n{field_lines}\n\nText:\n---\n{body.text}\n---"),
    ]
    result = await _run_chat("extract", messages, body.model, body.provider, temperature=0.0)
    result["parsed"] = _try_parse_json(result["output"])
    return result


def _try_parse_json(text: str) -> Optional[dict]:
    """Best-effort JSON parse: local models often wrap JSON in prose/fences."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None
