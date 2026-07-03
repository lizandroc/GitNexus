"""Example tool 3: Business Workflow Prompt Runner.

Runs a saved or ad-hoc multi-step prompt workflow against input data —
the generic building block behind report generation, contract summaries,
CRM notes, sales scripts, and data extraction. Steps run sequentially and
each step sees the previous step's output, so workflows can refine.
"""
from __future__ import annotations

import json
from typing import Any, Optional

from ..providers import ChatMessage, get_provider, resolve_model
from .base import Tool, ToolSpec

SYSTEM = """You are a reliable business operations assistant executing one step of a workflow. Follow the step instruction exactly. Work only from the provided input data and prior step output. Do not invent facts. Keep output clean and directly usable."""

# A couple of ready-made workflows so the tool is useful out of the box.
PRESETS: dict[str, list[str]] = {
    "contract_summary": [
        "Extract the parties, effective date, term, payment terms, termination clauses, and liability caps from the input. Output as a Markdown table of Field | Value | Source quote.",
        "Using the extracted table, write a plain-English one-page summary for a non-lawyer, flagging anything unusual or risky in a 'Watch out' section.",
    ],
    "crm_note": [
        "From the input conversation or meeting notes, extract: contact name(s), company, deal stage signals, objections raised, and commitments made by either side. Output as labeled bullet points.",
        "Write a concise CRM activity note (under 120 words) and a 'Next step' line based on the extraction.",
    ],
    "report_draft": [
        "Organize the input data into logical sections with headers. Keep all figures exactly as given.",
        "Write an executive summary (max 5 bullets) on top of the organized sections, then output the full report in Markdown.",
    ],
}


class WorkflowRunnerTool(Tool):
    spec = ToolSpec(
        name="workflow_runner",
        title="Business Workflow Prompt Runner",
        description=(
            "Runs a multi-step prompt workflow over your input data. Use a preset "
            f"({', '.join(PRESETS)}) or pass custom steps as a JSON array of instructions."
        ),
        inputs={
            "input_data": "The source material the workflow operates on",
            "preset": f"Optional preset workflow: one of {', '.join(PRESETS)}",
            "steps": "Optional custom steps as a JSON array of strings (overrides preset)",
        },
        required=["input_data"],
    )

    async def run(self, inputs: dict[str, Any], model: Optional[str] = None) -> dict[str, Any]:
        self.validate(inputs)
        steps = self._resolve_steps(inputs)
        provider = get_provider()
        model, routing = resolve_model("tool:workflow_runner",
                                       input_chars=len(str(inputs["input_data"])),
                                       explicit=model)

        previous_output = ""
        step_results: list[dict[str, Any]] = []
        total_latency = 0
        for i, instruction in enumerate(steps):
            user_prompt = (
                f"Workflow step {i + 1} of {len(steps)}.\n"
                f"Instruction: {instruction}\n\n"
                f"Input data:\n---\n{inputs['input_data']}\n---\n"
            )
            if previous_output:
                user_prompt += f"\nOutput of the previous step:\n---\n{previous_output}\n---\n"
            result = await provider.chat(
                [ChatMessage("system", SYSTEM), ChatMessage("user", user_prompt)], model
            )
            previous_output = result.text
            total_latency += result.latency_ms
            step_results.append({"step": i + 1, "instruction": instruction, "output": result.text})

        return {
            "output": previous_output,
            "steps": step_results,
            "model": model,
            "provider": provider.name,
            "routing": routing,
            "latency_ms": total_latency,
        }

    def _resolve_steps(self, inputs: dict[str, Any]) -> list[str]:
        raw_steps = inputs.get("steps")
        if raw_steps:
            if isinstance(raw_steps, str):
                try:
                    raw_steps = json.loads(raw_steps)
                except json.JSONDecodeError as e:
                    raise ValueError(f"'steps' must be a JSON array of strings: {e}") from e
            if not isinstance(raw_steps, list) or not all(isinstance(s, str) and s.strip() for s in raw_steps):
                raise ValueError("'steps' must be a non-empty JSON array of instruction strings")
            return raw_steps
        preset = str(inputs.get("preset") or "").strip()
        if preset:
            if preset not in PRESETS:
                raise ValueError(f"Unknown preset '{preset}'. Available: {', '.join(PRESETS)}")
            return PRESETS[preset]
        raise ValueError("Provide either 'preset' or 'steps'.")
