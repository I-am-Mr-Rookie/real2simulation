"""S14b Muse Wonder scene understanding: number-free scene context in, validated agent-response out.

The model sees only `tools.scene_context` (ids/labels/statuses, no numbers) and no tool outputs, so any
number segment it emits has nothing to reference and is rejected by `validate_response`.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from contracts.agent.validate import RESPONSE_VERSION, TEMPLATES, AgentContractError, validate_response

MODEL = "muse-wonder-1.0"
MAX_OUTPUT_TOKENS = 1500
MAX_RETRIES = 3  # S14d: re-asks after the first attempt; worst case 4 Muse calls per scene
FEEDBACK_ISSUES, FEEDBACK_CHARS = 8, 200  # bound what rejected-reply issues add to the retry prompt
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


def build_request(context: Mapping[str, Any], model: str = MODEL, feedback: Sequence[str] = ()) -> dict[str, Any]:
    """Responses-API body; structured output via the S14a schema. feedback = validator issues of the last reply."""
    instructions = INSTRUCTIONS
    if feedback:
        instructions += (" Your previous reply was rejected by the validator. Reply again and fix: "
                         + "; ".join(i[:FEEDBACK_CHARS] for i in feedback[:FEEDBACK_ISSUES]))
    # minimal reasoning: at default effort Wonder spent 1498/1500 tokens reasoning (fixture live-room-v1-a)
    return {"model": model, "instructions": instructions, "max_output_tokens": MAX_OUTPUT_TOKENS,
            "reasoning": {"effort": "minimal"},
            "input": json.dumps(context, ensure_ascii=False, sort_keys=True),
            "text": {"format": {"type": "json_schema", "name": "agent_response", "schema": SCHEMA, "strict": False}}}


def output_text(body: Mapping[str, Any]) -> str:
    """Concatenate output_text parts of a Responses-API body; reject incomplete replies (empty fails JSON parse)."""
    if body.get("status") not in (None, "completed"):
        raise AgentContractError([f"muse: response status {body.get('status')!r}"])
    return "".join(part.get("text", "") for item in body.get("output") or () if item.get("type") == "message"
                   for part in item.get("content") or () if part.get("type") == "output_text")


def understand(context: Mapping[str, Any], post: Callable[[dict[str, Any]], Mapping[str, Any]]) -> dict[str, Any]:
    """Call Muse (via `post`) and return a validated agent-response, or raise AgentContractError."""
    return validate_response(output_text(post(build_request(context))), (), context["scene_id"])


def ask_user(scene_id: str) -> dict[str, Any]:
    """Code-owned validated fallback: no candidates, one chip question whose chip ids are the S08 templates."""
    text = lambda s: [{"type": "text", "text": s}]
    return validate_response({
        "schema_version": RESPONSE_VERSION, "scene_id": scene_id,
        "segments": text("I could not understand this scene reliably, so I will not guess an experiment."),
        "questions": [{"id": "template", "kind": "chips", "prompt": text("Which experiment do you want to set up?"),
                       "chips": [{"id": t, "label": text(t.replace("_", " ").capitalize())} for t in sorted(TEMPLATES)]}],
        "candidates": [],
    }, (), scene_id)


def understand_with_retry(context: Mapping[str, Any], post: Callable[[dict[str, Any]], Mapping[str, Any]]
                          ) -> tuple[dict[str, Any], list[list[str]]]:
    """S14d: up to 1 + MAX_RETRIES validated attempts, each retry told the last reply's issues.

    Returns (response, issues of every rejected attempt). If no attempt validates, or the valid reply
    offers no candidate, the response is `ask_user` (the user picks; nothing is invented). Transport
    errors from `post` are not validator failures and propagate without retry.
    """
    rejected: list[list[str]] = []
    for _ in range(1 + MAX_RETRIES):
        body = post(build_request(context, feedback=rejected[-1] if rejected else ()))
        try:
            response = validate_response(output_text(body), (), context["scene_id"])
        except AgentContractError as error:
            rejected.append(list(error.issues))
            continue
        return (response if response.get("candidates") else ask_user(context["scene_id"])), rejected
    return ask_user(context["scene_id"]), rejected
