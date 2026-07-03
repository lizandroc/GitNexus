"""Tool registry. Register a Tool instance here and it is immediately
listed at GET /v1/tools and runnable at POST /v1/tools/{name}/run.
"""
from __future__ import annotations

from .base import Tool, ToolSpec
from .doc_qa import DocQATool
from .email_analyzer import EmailAnalyzerTool
from .workflow_runner import WorkflowRunnerTool

_TOOLS: dict[str, Tool] = {}


def _registry() -> dict[str, Tool]:
    if not _TOOLS:
        for tool in (DocQATool(), EmailAnalyzerTool(), WorkflowRunnerTool()):
            _TOOLS[tool.spec.name] = tool
    return _TOOLS


def all_tools() -> list[ToolSpec]:
    return [t.spec for t in _registry().values()]


def get_tool(name: str) -> Tool:
    tool = _registry().get(name)
    if tool is None:
        raise KeyError(f"Unknown tool '{name}'. Available: {sorted(_registry())}")
    return tool


__all__ = ["Tool", "ToolSpec", "all_tools", "get_tool"]
