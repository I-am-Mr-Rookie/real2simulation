"""S14b Muse Wonder scene understanding: number-free scene context in, validated agent-response out.

The model sees only `tools.scene_context` (ids/labels/statuses, no numbers) and no tool outputs, so any
number segment it emits has nothing to reference and is rejected by `validate_response`.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Mapping

from contracts.agent.validate import TEMPLATES, AgentContractError, validate_response

MODEL = "muse-wonder-1.0"
MAX_OUTPUT_TOKENS = 1500
SCHEMA = json.loads((Path(__file__).parents[2] / "contracts" / "agent" / "response.schema.json").read_text(encoding="utf-8"))
INSTRUCTIONS = (
    "You are the scene-understanding step of a physics lab. Input is a JSON scene context. "
    "Reply with ONE JSON object matching the given schema (schema_version agent-response/1.0.0, "
    "scene_id copied exactly). segments: a short description of the surfaces and objects you can use. "
    "candidates: up to three experiments; template must be one of: " + ", ".join(sorted(TEMPLATES)) + ". "
    "questions: at most one clarifying question for the user. HARD RULE: no numbers anywhere - no digits, "
    "no number words, no fractions, no units with values; you have no tool outputs, so never emit number segments. "
    "Say 'the table' not 'one table'. If the scene says synthetic or gravity unknown, say so plainly."
)


def build_request(context: Mapping[str, Any], model: str = MODEL) -> dict[str, Any]:
    """Responses-API body; structured output via the S14a schema."""
    # minimal reasoning: at default effort Wonder spent 1498/1500 tokens reasoning (fixture live-room-v1-a)
    return {"model": model, "instructions": INSTRUCTIONS, "max_output_tokens": MAX_OUTPUT_TOKENS,
            "reasoning": {"effort": "minimal"},
            "input": json.dumps(context, ensure_ascii=False, sort_keys=True),
            "text": {"format": {"type": "json_schema", "name": "agent_response", "schema": SCHEMA, "strict": False}}}


def output_text(body: Mapping[str, Any]) -> str:
    """Concatenate output_text parts of a Responses-API body; reject incomplete/empty replies."""
    if body.get("status") not in (None, "completed"):
        raise AgentContractError([f"muse: response status {body.get('status')!r}"])
    text = "".join(part.get("text", "") for item in body.get("output") or () if item.get("type") == "message"
                   for part in item.get("content") or () if part.get("type") == "output_text")
    if not text.strip():
        raise AgentContractError(["muse: no output_text"])
    return text


def understand(context: Mapping[str, Any], post: Callable[[dict[str, Any]], Mapping[str, Any]]) -> dict[str, Any]:
    """Call Muse (via `post`) and return a validated agent-response, or raise AgentContractError."""
    return validate_response(output_text(post(build_request(context))), (), context["scene_id"])
