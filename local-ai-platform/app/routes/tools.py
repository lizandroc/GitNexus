"""Tool endpoints: discover tools and run them. Every run is logged to the
runs table so the dashboard can show tool usage."""
from __future__ import annotations

import time
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..db import record_run
from ..providers import ProviderError
from ..tools import all_tools, get_tool

router = APIRouter(prefix="/v1", tags=["tools"])


@router.get("/tools")
def list_tools() -> dict[str, Any]:
    return {"tools": [
        {"name": s.name, "title": s.title, "description": s.description,
         "inputs": s.inputs, "required": s.required}
        for s in all_tools()
    ]}


class ToolRunIn(BaseModel):
    inputs: dict[str, Any] = Field(default_factory=dict)
    model: Optional[str] = None


@router.post("/tools/{name}/run")
async def run_tool(name: str, body: ToolRunIn) -> dict[str, Any]:
    try:
        tool = get_tool(name)
    except KeyError as e:
        raise HTTPException(404, str(e))
    start = time.monotonic()
    try:
        result = await tool.run(body.inputs, model=body.model)
    except ValueError as e:
        record_run("tool", tool=name, status="error", error=str(e)[:500])
        raise HTTPException(400, str(e))
    except ProviderError as e:
        record_run("tool", tool=name, status="error", error=str(e)[:500])
        raise HTTPException(502, str(e))
    latency_ms = int((time.monotonic() - start) * 1000)
    record_run("tool", tool=name, provider=result.get("provider"), model=result.get("model"),
               latency_ms=latency_ms,
               input_chars=sum(len(str(v)) for v in body.inputs.values()),
               output_chars=len(str(result.get("output", ""))))
    result["tool"] = name
    return result
