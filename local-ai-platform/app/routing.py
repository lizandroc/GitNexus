"""Auto model routing: pick the cheapest model that fits the task.

When auto-routing is on (the default), requests that don't name a model
explicitly are routed by cheap heuristics — task kind, input size, and
reasoning cues — to either the fast tier (small model, most requests) or
the quality tier (larger model, only when the task earns it). No LLM call
is spent on the routing decision itself.

Tiers are configured with LAP_MODEL_FAST / LAP_MODEL_QUALITY and every
response reports which model was chosen and why, so the choice is always
auditable.
"""
from __future__ import annotations

from .config import settings

# Cues that a request needs real reasoning or composition quality.
REASONING_HINTS = (
    "why", "explain", "analyze", "analyse", "compare", "evaluate", "strategy",
    "plan", "draft", "write", "compose", "review", "recommend", "trade-off",
    "tradeoff", "pros and cons", "step by step", "in depth", "detailed",
)

# Structured, low-creativity tasks a small model handles well at any size.
FAST_KINDS = {"classify", "extract"}
# Multi-step composition where quality compounds across steps.
QUALITY_KINDS = {"tool:workflow_runner"}

LONG_INPUT_CHARS = 4000
LONG_QUESTION_CHARS = 400


def pick_model(kind: str, input_chars: int = 0, text: str = "") -> tuple[str, str]:
    """Return (model, reason) for a request under auto-routing."""
    fast, quality = settings.fast_model, settings.quality_model

    if kind in FAST_KINDS:
        return fast, f"fast tier: '{kind}' is a structured task"
    if kind in QUALITY_KINDS:
        return quality, f"quality tier: '{kind}' is multi-step composition"

    lowered = text.lower()
    hint = next((h for h in REASONING_HINTS if h in lowered), None)

    if kind == "summarize":
        if input_chars > LONG_INPUT_CHARS:
            return quality, f"quality tier: long input ({input_chars} chars)"
        return fast, "fast tier: short summarization"

    if kind == "rag_query":
        if hint or input_chars > LONG_QUESTION_CHARS:
            return quality, f"quality tier: {'reasoning cue ' + repr(hint) if hint else 'long question'}"
        return fast, "fast tier: short factual lookup"

    # chat and prompt tools: size + reasoning cues decide.
    if input_chars > LONG_INPUT_CHARS:
        return quality, f"quality tier: long input ({input_chars} chars)"
    if hint:
        return quality, f"quality tier: reasoning cue {hint!r}"
    return fast, "fast tier: short, direct task"
