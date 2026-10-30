"""Offline sidebar wire contracts. Validation never dispatches a tool or rebuild."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Literal, TypedDict

from jsonschema import Draft202012Validator

from contracts.agent.validate import TEMPLATES, validate_tool_output
from contracts.experiment.validate_experiment import parse_json, validate

VERSION = "sidebar-tools/1.0.0"
TOOLS = ("spec.patch", "scene.rebuild", "library.search")
# Same wire values as scene provenance; do not create a second licence vocabulary.
LICENSES = tuple(json.loads((Path(__file__).resolve().parents[2] /
    "contracts/scene/scene.schema.json").read_text(encoding="utf-8"))["$defs"]["source"]
    ["properties"]["license"]["enum"])
PATCH_FIELDS = ("environment", "body", "placement", "parameters", "simulation")


class ToolCall(TypedDict):
    schema_version: Literal["sidebar-tools/1.0.0"]
    id: str
    scene_id: str
    tool: Literal["spec.patch", "scene.rebuild", "library.search"]
    arguments: PatchArguments | RebuildArguments | SearchArguments


class ToolResult(TypedDict):
    schema_version: Literal["sidebar-tools/1.0.0"]
    call_id: str
    scene_id: str
    tool: Literal["spec.patch", "scene.rebuild", "library.search"]
    status: Literal["ok", "error"]
    payload: dict[str, Any]
    tool_outputs: list[dict[str, Any]]


class PatchArguments(TypedDict):
    base_spec_sha256: str
    patch: dict[str, dict[str, Any]]


class RebuildArguments(TypedDict):
    spec_sha256: str
    spec: dict[str, Any]


class SearchArguments(TypedDict):
    query: str
    limit: int
    templates: list[str]
    licenses: list[str]


class SidebarContractError(ValueError):
    """Untrusted wire input failed validation; no execution is authorized."""


def _object(properties, required=None):
    return {"type": "object", "additionalProperties": False, "properties": properties,
            "required": list(properties) if required is None else required}


TEXT = {"type": "string", "minLength": 1, "maxLength": 2048, "pattern": r"\S"}
ID = {"type": "string", "pattern": r"^[a-z][a-z0-9_-]{0,63}$"}
SHA = {"type": "string", "pattern": "^[a-f0-9]{64}$"}
URL = {"type": "string", "maxLength": 2048, "pattern": r"^https://[^\s/]+(?:/[^\s]*)?$"}
PATH = {"type": "string", "maxLength": 512,
        "pattern": r"^(?!/)(?!.*(?:^|/)\.\.?(/|$))[a-zA-Z0-9_./-]+$"}
SEARCH = _object({
    "query": {**TEXT, "maxLength": 256},
    "limit": {"type": "integer", "minimum": 1, "maximum": 20},
    "templates": {"type": "array", "uniqueItems": True,
                  "items": {"enum": sorted(TEMPLATES)}},
    "licenses": {"type": "array", "uniqueItems": True, "items": {"enum": list(LICENSES)}},
})
CALL_SCHEMA = _object({"schema_version": {"const": VERSION}, "id": ID, "scene_id": ID,
                       "tool": {"enum": list(TOOLS)}, "arguments": {"type": "object"}})
ARGUMENT_SCHEMAS = {
    "spec.patch": _object({"base_spec_sha256": SHA,
        "patch": {**_object({key: {"type": "object"} for key in PATCH_FIELDS}, []),
                  "minProperties": 1}}),
    "scene.rebuild": _object({"spec_sha256": SHA, "spec": {"type": "object"}}),
    "library.search": SEARCH,
}
SOURCE = _object({"clip_id": ID, "source_url": URL,
                  "license": {"enum": list(LICENSES)}, "license_url": URL,
                  "attribution": TEXT, "approval_evidence": PATH})
PROVENANCE = _object({"run_id": TEXT, "evidence": PATH,
    "numeric_label": {"enum": ["measured", "simulated", "synthetic", "unknown"]}})
LIBRARY_ITEM = _object({
    "id": ID, "title": TEXT, "template": {"enum": sorted(TEMPLATES)},
    "synthetic": {"type": "boolean"}, "source": SOURCE,
    "artifact": _object({"path": PATH, "sha256": SHA}), "provenance": PROVENANCE,
})
PAYLOAD_SCHEMAS = {
    "spec.patch": _object({"spec": {"type": "object"}, "spec_sha256": SHA,
                            "rebuild_required": {"const": True}}),
    "scene.rebuild": _object({"job_id": ID, "spec_sha256": SHA,
                               "state": {"const": "queued"}}),
    "library.search": _object({"query": {**TEXT, "maxLength": 256},
        "items": {"type": "array", "maxItems": 20, "items": LIBRARY_ITEM}}),
}
ERROR_SCHEMA = _object({"code": {"enum": ["invalid_request", "stale_spec", "not_found",
    "not_ready", "budget_blocked", "internal_error"]},
    "issues": {"type": "array", "minItems": 1, "maxItems": 32, "items": TEXT}})
RESULT_SCHEMA = _object({"schema_version": {"const": VERSION}, "call_id": ID,
    "scene_id": ID, "tool": {"enum": list(TOOLS)}, "status": {"enum": ["ok", "error"]},
    "payload": {"type": "object"}, "tool_outputs": {"type": "array", "maxItems": 20}})


def _check(data, schema):
    # Reuse strict JSON checks for Python objects too (nonfinite numbers/duplicate keys on wire).
    try:
        parse_json(json.dumps(data, allow_nan=False))
        issues = sorted(f"{list(e.absolute_path)}: {e.message}"
                        for e in Draft202012Validator(schema).iter_errors(data))
    except (ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise SidebarContractError(str(exc)) from exc
    if issues:
        raise SidebarContractError("; ".join(issues))


def spec_sha256(spec: dict[str, Any]) -> str:
    """Digest of a numerically validated snapshot; not scene-fit or source authentication."""
    validate(spec)
    return hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def _candidate(call, base_spec):
    if base_spec is None:
        raise SidebarContractError("spec.patch requires the trusted current base_spec")
    if call["arguments"]["base_spec_sha256"] != spec_sha256(base_spec):
        raise SidebarContractError("stale base_spec_sha256")
    if call["scene_id"] != base_spec["scene"]["scene_id"]:
        raise SidebarContractError("scene_id does not match base spec")
    candidate = copy.deepcopy(base_spec)
    candidate.update(copy.deepcopy(call["arguments"]["patch"]))
    validate(candidate)
    return candidate


def validate_call(call: Any, *, base_spec=None) -> ToolCall:
    """Validate before dispatch; patch uses whole-section replacement, never deep merge."""
    _check(call, CALL_SCHEMA)
    _check(call["arguments"], ARGUMENT_SCHEMAS[call["tool"]])
    try:
        if call["tool"] == "spec.patch":
            _candidate(call, base_spec)
        elif call["tool"] == "scene.rebuild":
            spec = call["arguments"]["spec"]
            if spec_sha256(spec) != call["arguments"]["spec_sha256"]:
                raise SidebarContractError("spec_sha256 mismatch")
            if call["scene_id"] != spec["scene"]["scene_id"]:
                raise SidebarContractError("scene_id does not match rebuild spec")
    except ValueError as exc:
        raise SidebarContractError(str(exc)) from exc
    return copy.deepcopy(call)


def validate_result(result: Any, call: Any, *, base_spec=None) -> ToolResult:
    """Correlate a code-owned result with its validated call; no numbers invented here."""
    call = validate_call(call, base_spec=base_spec)
    _check(result, RESULT_SCHEMA)
    for field, key in (("call_id", "id"), ("scene_id", "scene_id"), ("tool", "tool")):
        if result[field] != call[key]:
            raise SidebarContractError(f"result {field} does not match call")
    payload = result["payload"]
    _check(payload, ERROR_SCHEMA if result["status"] == "error" else PAYLOAD_SCHEMAS[call["tool"]])
    if result["tool_outputs"] and (result["status"] == "error" or call["tool"] != "scene.rebuild"):
        raise SidebarContractError("only successful rebuild results may carry numeric tool outputs")
    seen = set()
    for output in result["tool_outputs"]:
        try:
            output = validate_tool_output(output)
        except ValueError as exc:
            raise SidebarContractError(str(exc)) from exc
        if output["id"] in seen:
            raise SidebarContractError("duplicate numeric tool output id")
        seen.add(output["id"])
    if result["status"] == "ok":
        if call["tool"] == "spec.patch":
            candidate = _candidate(call, base_spec)
            try:
                actual_digest = spec_sha256(payload["spec"])
            except ValueError as exc:
                raise SidebarContractError(str(exc)) from exc
            if (payload["spec"] != candidate or payload["spec_sha256"] != spec_sha256(candidate)
                    or payload["spec_sha256"] != actual_digest):
                raise SidebarContractError("patch result must match validated candidate and digest")
        elif call["tool"] == "scene.rebuild":
            if payload["spec_sha256"] != call["arguments"]["spec_sha256"]:
                raise SidebarContractError("rebuild result spec_sha256 mismatch")
        else:
            args, items = call["arguments"], payload["items"]
            if payload["query"] != args["query"] or len(items) > args["limit"]:
                raise SidebarContractError("search query/limit mismatch")
            if len({item["id"] for item in items}) != len(items):
                raise SidebarContractError("duplicate library item id")
            for item in items:
                if args["templates"] and item["template"] not in args["templates"]:
                    raise SidebarContractError("library template outside requested filters")
                if args["licenses"] and item["source"]["license"] not in args["licenses"]:
                    raise SidebarContractError("library license outside requested filters")
                if item["synthetic"] != (item["provenance"]["numeric_label"] == "synthetic"):
                    raise SidebarContractError("synthetic item/provenance mismatch")
    return copy.deepcopy(result)
