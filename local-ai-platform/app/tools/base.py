"""Tool system: a tool is a named, typed unit of AI work that apps and
automations can invoke through POST /v1/tools/{name}/run.

Most business tools (contract summarizer, CRM note writer, sales scripter…)
are just a prompt template + input schema, so `PromptTool` makes new tools
a ~10-line declaration. Tools that need retrieval or custom logic subclass
`Tool` directly (see doc_qa.py).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from ..providers import ChatMessage, active_model, get_provider


@dataclass
class ToolSpec:
    name: str
    title: str
    description: str
    inputs: dict[str, str]  # field name -> human description
    required: list[str] = field(default_factory=list)


class Tool(ABC):
    spec: ToolSpec

    @abstractmethod
    async def run(self, inputs: dict[str, Any], model: Optional[str] = None) -> dict[str, Any]:
        ...

    def validate(self, inputs: dict[str, Any]) -> None:
        missing = [f for f in self.spec.required if not str(inputs.get(f, "")).strip()]
        if missing:
            raise ValueError(f"Missing required input(s): {', '.join(missing)}")


class PromptTool(Tool):
    """A tool defined by a system prompt and a user-prompt template.

    Template placeholders like {field} are filled from the request inputs.
    """

    def __init__(self, spec: ToolSpec, system_prompt: str, user_template: str,
                 temperature: float = 0.2):
        self.spec = spec
        self.system_prompt = system_prompt
        self.user_template = user_template
        self.temperature = temperature

    async def run(self, inputs: dict[str, Any], model: Optional[str] = None) -> dict[str, Any]:
        self.validate(inputs)
        safe = {k: str(inputs.get(k, "")) for k in self.spec.inputs}
        user_prompt = self.user_template.format(**safe)
        provider = get_provider()
        result = await provider.chat(
            [ChatMessage("system", self.system_prompt), ChatMessage("user", user_prompt)],
            model or active_model(),
            temperature=self.temperature,
        )
        return {
            "output": result.text,
            "model": result.model,
            "provider": result.provider,
            "latency_ms": result.latency_ms,
        }
