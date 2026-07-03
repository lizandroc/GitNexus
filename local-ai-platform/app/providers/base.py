"""Provider abstraction: every model runtime (Ollama, LM Studio, future
cloud providers) implements this same small interface, so the rest of the
platform is model-agnostic.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChatMessage:
    role: str  # system | user | assistant
    content: str


@dataclass
class ChatResult:
    text: str
    model: str
    provider: str
    latency_ms: int = 0
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None


@dataclass
class ModelInfo:
    name: str
    provider: str
    size_bytes: Optional[int] = None
    family: Optional[str] = None
    details: dict = field(default_factory=dict)


class ProviderError(RuntimeError):
    """Raised when a provider is unreachable or returns an error."""


class Provider(ABC):
    """A model runtime. `is_local` gates the privacy check: non-local
    providers are refused unless the user explicitly enables cloud mode."""

    name: str = "base"
    is_local: bool = True

    @abstractmethod
    async def health(self) -> bool:
        """True if the runtime is reachable."""

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        ...

    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> ChatResult:
        ...

    @abstractmethod
    async def embed(self, texts: list[str], model: str) -> list[list[float]]:
        ...
