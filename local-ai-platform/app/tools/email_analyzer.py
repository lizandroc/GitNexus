"""Example tool 2: Email / Conversation Analyzer.

Paste an email thread or call transcript; get intent, sentiment, action
items, open questions, and a suggested reply — all processed locally.
"""
from __future__ import annotations

from .base import PromptTool, ToolSpec

SYSTEM = """You are a business communication analyst. You analyze emails, threads, and conversation transcripts for a busy executive. Be precise and practical. Output in this exact Markdown structure:

## Summary
(2-3 sentences)

## Sender intent
(one line)

## Sentiment
(positive / neutral / negative, with a short justification)

## Action items
(bullet list with owner if identifiable; write "None" if none)

## Open questions / risks
(bullet list; write "None" if none)

## Suggested reply
(a short, professional draft reply the user could send)

Base everything strictly on the provided text. Do not invent facts, names, or commitments."""

USER_TEMPLATE = """Analyze the following {kind}:

---
{content}
---
{goal_line}"""


class EmailAnalyzerTool(PromptTool):
    def __init__(self) -> None:
        super().__init__(
            spec=ToolSpec(
                name="email_analyzer",
                title="Email / Conversation Analyzer",
                description="Summarizes an email thread or conversation: intent, sentiment, action items, risks, and a suggested reply.",
                inputs={
                    "content": "The email thread or conversation text",
                    "kind": "What this is (email, thread, call transcript…) — default 'email thread'",
                    "goal_line": "Optional: what you want out of it (e.g. 'Goal: recover this lead')",
                },
                required=["content"],
            ),
            system_prompt=SYSTEM,
            user_template=USER_TEMPLATE,
        )

    async def run(self, inputs, model=None):
        inputs = dict(inputs)
        inputs.setdefault("kind", "email thread")
        inputs.setdefault("goal_line", "")
        if not inputs["kind"].strip():
            inputs["kind"] = "email thread"
        return await super().run(inputs, model)
