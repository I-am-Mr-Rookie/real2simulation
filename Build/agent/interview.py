"""S14c interview: up to three code-owned questions per template; chip and free-text answers become
sourced spec inputs, and the S08 setup validator decides. No model calls, no default physical numbers."""
from __future__ import annotations

import copy
import math
import re
from pathlib import Path
from typing import Any, Mapping

from contracts.agent.validate import RESPONSE_VERSION, AgentContractError, validate_response
from contracts.experiment.validate_experiment import validate_setup

REST = {"at-rest": ("Starts at rest", 0.0)}  # "at rest" is an exact zero, not a default guess
# template -> ((parameter, kind, prompt, contract unit, {chip id: (label, value)}), ...); prompts are number-free
QUESTIONS: dict[str, tuple[tuple[str, str, str, str, dict[str, tuple[str, float]]], ...]] = {
    "free_fall": (
        ("drop_height", "free_text", "How far does the ball fall before it lands, in metres?", "m", {}),
        ("initial_vertical_velocity", "chips_and_free_text",
         "Is it released from rest? Otherwise type its upward speed in metres per second.", "m/s", REST),
    ),
    "projectile": (
        ("launch_height", "free_text", "How high is the launch point above the landing point, in metres?", "m", {}),
        ("horizontal_speed", "free_text", "How fast does it leave horizontally, in metres per second?", "m/s", {}),
    ),
    "ramp": (
        ("incline_angle", "free_text", "How steep is the ramp? Type the angle in deg or rad.", "rad", {}),
        ("friction_coefficient", "chips_and_free_text",
         "Is the ramp frictionless? Otherwise type the friction coefficient.", "1", {"frictionless": ("Frictionless", 0.0)}),
        ("initial_speed", "chips_and_free_text",
         "Does the ball start at rest? Otherwise type its speed in metres per second.", "m/s", REST),
    ),
    "pendulum": (
        ("length", "free_text", "How long is the pendulum, in metres?", "m", {}),
        ("release_angle", "free_text", "How far is it pulled back? Type the angle in deg or rad.", "rad", {}),
        ("initial_angular_velocity", "chips_and_free_text",
         "Is it released from rest? Otherwise type its angular speed in radians per second.", "rad/s", REST),
    ),
}
# accepted typed unit -> factor to the contract unit; "" = contract unit implied (never for angles: deg/rad ambiguity)
UNITS = {"m": {"": 1.0, "m": 1.0}, "m/s": {"": 1.0, "m/s": 1.0}, "1": {"": 1.0},
         "rad": {"rad": 1.0, "deg": math.pi / 180, "°": math.pi / 180}, "rad/s": {"": 1.0, "rad/s": 1.0}}
_NUMBER = re.compile(r"\s*([+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]{1,3})?)\s*(\S*)\s*")  # ASCII digits only


def _questions(template: str):
    if template not in QUESTIONS:
        raise AgentContractError([f"interview: unknown template {template!r}"])
    return QUESTIONS[template]


def template_of(response: Mapping[str, Any], candidate_id: str) -> str:
    """Template of the candidate the user picked from a validated (S14b) response."""
    for candidate in response.get("candidates") or ():
        if candidate["id"] == candidate_id:
            _questions(candidate["template"])
            return candidate["template"]
    raise AgentContractError([f"interview: unknown candidate {candidate_id!r}"])


def questions(scene_id: str, template: str) -> dict[str, Any]:
    """Validated number-free agent-response carrying this template's one to three questions."""
    text = lambda s: [{"type": "text", "text": s}]
    return validate_response({
        "schema_version": RESPONSE_VERSION, "scene_id": scene_id,
        "segments": text(f"A few questions to set up the {template.replace('_', ' ')} experiment."),
        "questions": [{"id": p, "kind": kind, "prompt": text(prompt),
                       "chips": [{"id": c, "label": text(label)} for c, (label, _) in chips.items()]}
                      for p, kind, prompt, _, chips in _questions(template)],
    }, (), scene_id)


def _parse(text: Any, unit: str) -> float:
    match = _NUMBER.fullmatch(text) if isinstance(text, str) and len(text) <= 64 else None
    factor = UNITS[unit].get(match.group(2).lower()) if match else None
    if factor is None:
        raise ValueError(f"expected a number with unit one of {sorted(UNITS[unit])} ('' = {unit})")
    value = float(match.group(1)) * factor
    if not math.isfinite(value):
        raise ValueError("number is not finite")
    return value


def answers_to_spec(base_spec: Mapping[str, Any], scene: Mapping[str, Any], scene_root: Path,
                    answers: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """Map {question id: {"chip": id} | {"text": str}} onto a copy of base_spec, then S08c-validate it.

    Answered quantities are labelled assumed (user input, uncertainty unquantified); everything else
    keeps the base spec's own provenance. Raises AgentContractError listing every problem.
    """
    qs = _questions(base_spec.get("template"))
    spec, issues = copy.deepcopy(dict(base_spec)), []
    issues += [f"answers.{k}: not a question for {base_spec['template']}" for k in answers if k not in {q[0] for q in qs}]
    for param, kind, _, unit, chips in qs:
        answer = answers.get(param)
        try:
            if not isinstance(answer, Mapping) or len(answer) != 1 or not {"chip", "text"} & set(answer):
                raise ValueError('expected exactly one of {"chip": id} or {"text": str}')
            if "chip" in answer:
                if answer["chip"] not in chips:
                    raise ValueError(f"unknown chip {answer['chip']!r}")
                value, how = chips[answer["chip"]][1], f"chip:{answer['chip']}"
            else:
                value, how = _parse(answer["text"], unit), "free-text"
        except ValueError as error:
            issues.append(f"answers.{param}: {error}")
            continue
        spec["parameters"][param] = {"value": value, "unit": unit, "uncertainty": None,
                                     "source": {"label": "assumed", "evidence": f"user-input:{param}:{how}"}}
    if issues:
        raise AgentContractError(issues)
    try:
        return validate_setup(spec, scene, scene_root)
    except ValueError as error:
        raise AgentContractError(list(getattr(error, "issues", None) or [str(error)])) from error
