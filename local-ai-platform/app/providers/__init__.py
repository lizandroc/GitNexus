"""Provider registry + privacy gate.

`get_provider()` is the single place the rest of the app obtains a model
runtime. It enforces the privacy rule: providers marked `is_local=False`
are refused while cloud mode is off. Adding a future provider (e.g. a
cloud fallback for non-sensitive tasks) means one new module + one
registry entry — nothing else changes.
"""
from __future__ import annotations

from ..config import settings
from ..db import get_setting
from .base import ChatMessage, ChatResult, ModelInfo, Provider, ProviderError
from .lmstudio import LMStudioProvider
from .mock import MockProvider
from .ollama import OllamaProvider

_REGISTRY: dict[str, Provider] = {}


def _registry() -> dict[str, Provider]:
    if not _REGISTRY:
        _REGISTRY.update({
            "ollama": OllamaProvider(),
            "lmstudio": LMStudioProvider(),
            "mock": MockProvider(),
        })
    return _REGISTRY


def all_providers() -> dict[str, Provider]:
    return dict(_registry())


def cloud_enabled() -> bool:
    # Env var is the master switch; the dashboard toggle is stored in the DB
    # but can never turn cloud on if the env var forbids it.
    return settings.allow_cloud and get_setting("cloud_mode", "off") == "on"


def get_provider(name: str | None = None) -> Provider:
    name = name or get_setting("active_provider", settings.default_provider)
    provider = _registry().get(name)
    if provider is None:
        raise ProviderError(f"Unknown provider '{name}'. Available: {sorted(_registry())}")
    if not provider.is_local and not cloud_enabled():
        raise ProviderError(
            f"Provider '{name}' is not local and cloud mode is disabled. "
            "Privacy mode blocks all external calls by default."
        )
    return provider


def active_model() -> str:
    return get_setting("active_model", settings.default_model)


def auto_route_enabled() -> bool:
    return get_setting("auto_route", "on") == "on"


def resolve_model(kind: str, input_chars: int = 0, text: str = "",
                  explicit: str | None = None) -> tuple[str, str]:
    """Decide which model serves a request: an explicitly requested model
    always wins; otherwise auto-routing picks the cheapest fitting tier;
    with routing off, the user's active model is used."""
    if explicit:
        return explicit, "explicit model requested"
    if not auto_route_enabled():
        return active_model(), "active model (auto-routing off)"
    from ..routing import pick_model
    return pick_model(kind, input_chars=input_chars, text=text)


__all__ = [
    "ChatMessage", "ChatResult", "ModelInfo", "Provider", "ProviderError",
    "get_provider", "all_providers", "active_model", "cloud_enabled",
    "auto_route_enabled", "resolve_model",
]
