"""Example tool 1: Private Document Q&A — a thin tool wrapper over the
RAG pipeline so automations can hit it through the uniform tools API.
"""
from __future__ import annotations

from typing import Any, Optional

from ..config import settings
from ..rag import answer_question
from .base import Tool, ToolSpec


class DocQATool(Tool):
    spec = ToolSpec(
        name="doc_qa",
        title="Private Document Q&A",
        description="Answers questions from your private knowledge base with source citations. Nothing leaves your machine.",
        inputs={
            "question": "The question to answer from your documents",
            "kb": "Knowledge base name (default: 'default')",
        },
        required=["question"],
    )

    async def run(self, inputs: dict[str, Any], model: Optional[str] = None) -> dict[str, Any]:
        self.validate(inputs)
        result = await answer_question(
            question=str(inputs["question"]),
            kb=str(inputs.get("kb") or "default"),
            top_k=settings.top_k,
            model=model,
        )
        return {
            "output": result["answer"],
            "sources": result["sources"],
            "model": result["model"],
            "provider": result["provider"],
            "latency_ms": result.get("latency_ms"),
        }
