"""S14a agent contracts: agent text is number-free; every number is a tool-output reference.

Trust boundary: tool outputs are built by code from fitter/simulator results (never by
the model) and validated here; model output is validated against them before display.
"""
from __future__ import annotations

import copy
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator

from contracts.experiment.validate_experiment import parse_json
from contracts.fit.quantity import validate_quantity

RESPONSE_VERSION = "agent-response/1.0.0"
TOOL_OUTPUT_VERSION = "agent-tool-output/1.0.0"
SCENE_CONTEXT_VERSION = "agent-scene-context/1.0.0"
TOOLS = frozenset(("fitter", "simulator"))
LABELS = frozenset(("measured", "simulated"))
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
_VALIDATOR = Draft202012Validator(json.loads(
    Path(__file__).with_name("response.schema.json").read_text(encoding="utf-8")))
# Candidate templates are the S08 experiment templates; single source of truth, no copy.
TEMPLATES = frozenset(json.loads((Path(__file__).parents[1] / "experiment" / "experiment.schema.json")
                                 .read_text(encoding="utf-8"))["properties"]["template"]["enum"])
# shortcut: word list catches common spelled-out numbers only ("one" stays allowed as a pronoun unless
# next to "point"; Roman-numeral letters and "first"/"second" are not caught); extend from Gate A misses (S14g).
_NUMBER_WORDS = re.compile(
    r"\b(zero|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|"
    r"sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
    r"hundred|thousand|million|billion|dozen|half|quarter|percent|twice|thrice|triple|"
    r"third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|twelfth|tenths|hundredths|"
    r"one\s+point|point\s+one|single\s+digit|"
    # S14g-fix (R-A F1): multipliers and "one/a" + unit are implicit numbers ("double the value", "one metre",
    # "a couple of metres"); pronoun "one", "double-check" and unit names alone ("in metres") stay allowed.
    r"double(?!-)|doubled|couple|pair\s+of|times\s+(?:as|the|larger|smaller|greater|bigger|more|less)|"
    r"(?:one|an?)\s+(?:(?:centi|milli|kilo)?(?:metres?|meters?)|(?:kilo)?grams?|newtons?|joules?|watts?|"
    r"hertz|kg|cm|mm|km|m|s|g|n)|one\s+(?:seconds?|minutes?|hours?|degrees?|radians?))\b", re.I)
_INVISIBLE = dict.fromkeys(i for i in range(0x110000) if unicodedata.category(chr(i)) == "Cf")


class AgentContractError(ValueError):
    """Contract violation; `issues` lists readable path-prefixed reasons."""

    def __init__(self, issues: Iterable[str]):
        self.issues = tuple(issues)
        super().__init__("; ".join(self.issues))


def numeric_issue(text: str) -> str | None:
    """Return why free text carries an untraced number, or None."""
    for ch in text:
        if ch.isnumeric():  # ASCII/Unicode digits, fractions, numeral characters
            return f"untraced_numeric_character {ch!r}"
    text = unicodedata.normalize("NFKC", text)  # fullwidth letters
    # zero-width/soft-hyphen chars both split ("nine<ZWSP>point") and hide ("se<SHY>ven") words: check both
    match = _NUMBER_WORDS.search(text) or _NUMBER_WORDS.search(text.translate(_INVISIBLE))
    return f"untraced_number_word {match.group(0)!r}" if match else None


def validate_tool_output(data: Any) -> dict[str, Any]:
    """Validate a code-built fitter/simulator output; return a normalized copy."""
    if not isinstance(data, Mapping):
        raise AgentContractError(["tool_output: must be an object"])
    issues = []
    extra = set(data) - {"schema_version", "id", "tool", "status", "quantities"}
    if extra:
        issues.append(f"tool_output: unknown fields {sorted(extra)}")
    if data.get("schema_version") != TOOL_OUTPUT_VERSION:
        issues.append(f"tool_output.schema_version: must be {TOOL_OUTPUT_VERSION}")
    if not isinstance(data.get("id"), str) or not _ID.match(data["id"]):
        issues.append("tool_output.id: invalid id")
    if data.get("tool") not in TOOLS:
        issues.append(f"tool_output.tool: must be one of {sorted(TOOLS)}")
    if data.get("status") != "ok":
        issues.append('tool_output.status: only "ok" outputs may back numbers')
    quantities = data.get("quantities")
    normalized: dict[str, Any] = {}
    if not isinstance(quantities, Mapping) or not quantities:
        issues.append("tool_output.quantities: must be a non-empty object")
    else:
        for name, value in quantities.items():
            if not isinstance(name, str) or not _ID.match(name):
                issues.append(f"tool_output.quantities: invalid name {name!r}")
                continue
            source = value.get("source") if isinstance(value, Mapping) else None
            label = source.get("label") if isinstance(source, Mapping) else None
            if label not in LABELS:
                issues.append(f"tool_output.quantities.{name}.source.label: must be measured or simulated")
                continue
            try:  # reuse S11 checks; its label gate is simulated-only, so validate a relabelled copy
                item = validate_quantity({**value, "source": {**source, "label": "simulated"}})
            except ValueError as exc:
                issues.append(f"tool_output.quantities.{name}: {exc}")
                continue
            item["source"]["label"] = label
            normalized[name] = item
    if issues:
        raise AgentContractError(issues)
    return {**data, "quantities": normalized}


def _index(tool_outputs: Iterable[Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for raw in tool_outputs:
        output = validate_tool_output(raw)
        if output["id"] in index:
            raise AgentContractError([f"tool_outputs: duplicate id {output['id']}"])
        index[output["id"]] = output
    return index


def _segments(segments: list, path: str, index: Mapping[str, Any], issues: list[str]) -> None:
    visible, before = [], len(issues)
    for i, segment in enumerate(segments):
        where = f"{path}[{i}]"
        if segment["type"] == "text":
            visible.append(segment["text"])
            problem = numeric_issue(segment["text"])
            if problem:
                issues.append(f"{where}.text: {problem}")
        else:
            visible.append(" ")  # a cited quantity renders as its own traced number
            ref = segment["ref"]
            output = index.get(ref["tool_output_id"])
            if output is None:
                issues.append(f"{where}.ref: unknown tool_output_id {ref['tool_output_id']!r}")
            elif ref["quantity"] not in output["quantities"]:
                issues.append(f"{where}.ref: tool output has no quantity {ref['quantity']!r}")
    # S14g-fix (R-A F2): check the VISIBLE run, so "ni" + "ne point ei" + "ght" cannot assemble a number
    problem = numeric_issue("".join(visible)) if len(issues) == before else None
    if problem:
        issues.append(f"{path}: visible text {problem}")


def validate_response(response: Any, tool_outputs: Iterable[Any], scene_id: str) -> Any:
    """Return the response unchanged or raise AgentContractError listing every issue."""
    if isinstance(response, str):
        try:  # strict: duplicate keys / NaN / malformed JSON rejected
            response = parse_json(response)
        except ValueError as exc:
            raise AgentContractError([f"response: {exc}"]) from exc
    index = _index(tool_outputs)
    errors = sorted(_VALIDATOR.iter_errors(response), key=lambda e: list(map(str, e.path)))
    if errors:
        raise AgentContractError(f"response/{'/'.join(map(str, e.path))}: {e.message}" for e in errors)
    issues: list[str] = []
    if response["scene_id"] != scene_id:
        issues.append(f"response.scene_id: expected {scene_id!r}")
    _segments(response["segments"], "response.segments", index, issues)
    # S14g: live Muse mislabels question kinds (S13e video replies); normalise the kind to match the chips
    # actually sent - chip text is still number-checked below, nothing is dropped or relaxed.
    if any((q["kind"] == "free_text") == bool(q["chips"]) for q in response["questions"]):
        response = copy.deepcopy(response)
        for question in response["questions"]:
            if not question["chips"]:
                question["kind"] = "free_text"
            elif question["kind"] == "free_text":
                question["kind"] = "chips_and_free_text"
    for q, question in enumerate(response["questions"]):
        where = f"response.questions[{q}]"
        _segments(question["prompt"], f"{where}.prompt", index, issues)
        for c, chip in enumerate(question["chips"]):
            _segments(chip["label"], f"{where}.chips[{c}].label", index, issues)
    seen: set[str] = set()
    for c, candidate in enumerate(response.get("candidates", ())):
        if candidate["template"] not in TEMPLATES:
            issues.append(f"response.candidates[{c}].template: must be one of {sorted(TEMPLATES)}")
        if candidate["id"] in seen:
            issues.append(f"response.candidates[{c}].id: duplicate {candidate['id']!r}")
        seen.add(candidate["id"])
        _segments(candidate["rationale"], f"response.candidates[{c}].rationale", index, issues)
    if issues:
        raise AgentContractError(issues)
    return response
