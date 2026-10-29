"""Offline S14a adapters between accepted contracts and the agent contract. No model calls."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

from contracts.agent.validate import (
    SCENE_CONTEXT_VERSION, TOOL_OUTPUT_VERSION, AgentContractError, validate_response, validate_tool_output,
)
from contracts.scene.validate_scene import validate as validate_scene


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
            parts.append(f"{q['value']:.6g} ± {q['uncertainty']:.2g} {q['unit']} ({q['source']['label']})")
    return "".join(parts)
