"""Offline S14a adapters between accepted contracts and the agent contract. No model calls."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

from contracts.agent.validate import (
    RESPONSE_VERSION, SCENE_CONTEXT_VERSION, TOOL_OUTPUT_VERSION, AgentContractError, numeric_issue,
    validate_response, validate_tool_output,
)
from contracts.scene.validate_scene import validate as validate_scene

BLOCKED = "A reply was blocked because it stated a value that no tool result backs. Tool results only:"


def scene_context(scene: Mapping[str, Any], root: Path) -> dict[str, Any]:
    """Validated scene bundle -> what the model sees: ids, labels and statuses, deliberately no numbers."""
    scene = validate_scene(scene, Path(root))
    return {
        "schema_version": SCENE_CONTEXT_VERSION,
        "scene_id": scene["id"],
        "label": scene["label"],
        "synthetic": scene["synthetic"],
        "scale_status": scene["scale"]["status"],
        "gravity_status": scene["gravity"]["status"],
        "surfaces": [surface["id"] for surface in scene["surfaces"]],
        "colliders": [{"id": c["id"], "shape": c["shape"]} for c in scene["colliders"]],
        "labels": [label["text"] for label in scene["labels"]],
    }


def fit_tool_output(output_id: str, fit_response: Mapping[str, Any]) -> dict[str, Any]:
    """Build.fitter.api.handle response -> validated tool output; labels come from the fitter."""
    if fit_response.get("status") != "ok" or not fit_response.get("gravity"):
        raise AgentContractError([f"fit_response: no usable gravity ({fit_response.get('status')!r})"])
    return validate_tool_output({"schema_version": TOOL_OUTPUT_VERSION, "id": output_id, "tool": "fitter",
                                 "status": "ok", "quantities": {"gravity": fit_response["gravity"]}})


def render(response: Any, tool_outputs: Iterable[Mapping[str, Any]], scene_id: str) -> str:
    """Validate, then render reply text; every number carries uncertainty, unit and label."""
    tool_outputs = [validate_tool_output(o) for o in tool_outputs]
    response = validate_response(response, tool_outputs, scene_id)
    index = {o["id"]: o["quantities"] for o in tool_outputs}
    parts = []
    for segment in response["segments"]:
        if segment["type"] == "text":
            parts.append(segment["text"])
        else:
            q = index[segment["ref"]["tool_output_id"]][segment["ref"]["quantity"]]
            parts.append(quantity_text(q))
    return "".join(parts)


def quantity_text(q: Mapping[str, Any]) -> str:
    """The only way a number reaches user text: value, uncertainty, unit and label from a tool output."""
    return f"{q['value']:.6g} ± {q['uncertainty']:.2g} {q['unit']} ({q['source']['label']})"


def tool_backed(scene_id: str, tool_outputs: Iterable[Mapping[str, Any]], lead: str = BLOCKED,
                tail: str = ".") -> dict[str, Any]:
    """Code-owned validated response: no model claim, every tool quantity as a traced number segment."""
    tool_outputs = list(tool_outputs)
    segments: list[dict[str, Any]] = [{"type": "text", "text": lead}]
    for output in tool_outputs:
        for name in output["quantities"]:
            words = name.replace("_", " ")
            words = words if numeric_issue(words) is None else "value"  # a name like "g2" must not put a digit in text
            segments += [{"type": "text", "text": f" {output['tool']} {words} "},
                         {"type": "number", "ref": {"tool_output_id": output["id"], "quantity": name}}]
    segments.append({"type": "text", "text": tail})
    return validate_response({"schema_version": RESPONSE_VERSION, "scene_id": scene_id, "segments": segments,
                              "questions": []}, tool_outputs, scene_id)


def safe_reply(response: Any, tool_outputs: Iterable[Mapping[str, Any]], scene_id: str) -> tuple[str, list[str]]:
    """S14f: the one path from a model reply to user text -> (text, blocked issues; [] if shown as-is).

    Any untraced number (or other contract issue) blocks the WHOLE reply - no partial redaction - and the
    user gets tool_backed text instead. Tool outputs are code-built: an invalid one raises, never masked.
    """
    tool_outputs = [validate_tool_output(o) for o in tool_outputs]
    try:
        return render(response, tool_outputs, scene_id), []
    except AgentContractError as error:
        return render(tool_backed(scene_id, tool_outputs), tool_outputs, scene_id), list(error.issues)
