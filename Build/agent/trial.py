"""S14e Muse Spark trial check (offline adapter; no live calls while Meta billing is on hold).

After one S10 lab trial, Spark sees the trial's simulator and fitter tool outputs and writes a short check.
Every number in its reply must be a ref to THOSE outputs (ids carry the trial id), so a claim can only
quote what the simulator/fitter actually produced; untraced, foreign-trial or uncited replies are rejected.
"""
from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

from Build.agent.muse import MAX_RETRIES, build_request, output_text
from Build.agent.tools import fit_tool_output, tool_backed
from contracts.agent.validate import (
    TOOL_OUTPUT_VERSION, AgentContractError, validate_response, validate_tool_output,
)

MODEL = "muse-spark-1.3"  # owner-reported working id (API_BUDGET.md); live use unverified and on hold
TRIAL_CONTEXT_VERSION = "agent-trial-context/1.0.0"
SIM_UNCERTAINTY = 1e-6  # session-bridge INSTRUMENTS time/distance uncertainty; keep in step with it
INSTRUCTIONS = (
    "You check one virtual-lab trial. Input is a JSON trial context whose tool_outputs come from the "
    "simulator and the fitter. Reply with ONE JSON object matching the given schema (schema_version "
    "agent-response/1.0.0, scene_id copied exactly, questions empty, no candidates). segments: a short check "
    "of whether the fitted result is consistent with the simulated run, and its limitations. HARD RULE: never "
    "write a number in text - no digits, no number words. To cite a value use a number segment "
    '{"type": "number", "ref": {"tool_output_id": ..., "quantity": ...}} naming a tool output and quantity '
    "from the input; cite at least one. Say plainly that the trial is simulated, not physical evidence."
)


def trial_outputs(trial_id: str, start: Mapping[str, Any], fit: Mapping[str, Any]) -> list[dict[str, Any]]:
    """S10 session-bridge start + fit results -> validated [simulator, fitter] tool outputs for this trial."""
    observations = start.get("observations")
    if start.get("status") != "ok" or start.get("source") != "simulated" or not observations:
        raise AgentContractError([f"trial_start: no simulated observations ({start.get('status')!r})"])
    evidence = f"S10 synthetic lab simulator run ({start.get('template')})"
    quantity = lambda value, unit: {"value": value, "unit": unit, "uncertainty": SIM_UNCERTAINTY,
                                    "source": {"label": "simulated", "evidence": evidence}}
    last = observations[-1]
    simulator = validate_tool_output({
        "schema_version": TOOL_OUTPUT_VERSION, "id": f"{trial_id}-sim", "tool": "simulator", "status": "ok",
        "quantities": {"duration": quantity(last["time_s"], "s"), "drop": quantity(last["position_m"], "m")}})
    return [simulator, fit_tool_output(f"{trial_id}-fit", fit)]


def trial_context(scene_id: str, trial_id: str, start: Mapping[str, Any], outputs: Sequence[Mapping[str, Any]]
                  ) -> dict[str, Any]:
    """What Spark sees: ids, template, limitations and the validated tool outputs (values included)."""
    return {"schema_version": TRIAL_CONTEXT_VERSION, "scene_id": scene_id, "trial_id": trial_id,
            "template": start["template"], "limitations": list(start.get("limitations") or ()),
            "tool_outputs": list(outputs)}


def build_check_request(context: Mapping[str, Any], feedback: Sequence[str] = ()) -> dict[str, Any]:
    return build_request(context, MODEL, feedback, INSTRUCTIONS)


def validate_check(reply: Any, outputs: Sequence[Mapping[str, Any]], scene_id: str) -> dict[str, Any]:
    """S14a validation against this trial's outputs, plus: a trial claim must cite at least one of them."""
    response = validate_response(reply, outputs, scene_id)
    issues = []
    if response["questions"] or response.get("candidates"):
        issues.append("trial_check: questions and candidates must be empty")
    if not any(segment["type"] == "number" for segment in response["segments"]):
        issues.append("trial_check.segments: must cite at least one simulator/fitter quantity")
    if issues:
        raise AgentContractError(issues)
    return response


def tool_only(scene_id: str, outputs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Code-owned fallback: no model claim, just every tool quantity as a traced number segment."""
    return validate_check(tool_backed(scene_id, outputs, "The automatic trial check gave no valid reply; tool results only:",
                                      ". Simulated, not physical evidence."), outputs, scene_id)


def check_trial(context: Mapping[str, Any], post: Callable[[dict[str, Any]], Mapping[str, Any]]
                ) -> tuple[dict[str, Any], list[list[str]]]:
    """S14d-style loop: up to 1 + MAX_RETRIES Spark calls, each retry told the last issues; else tool_only.

    Transport errors from `post` propagate without retry. Worst case 4 Spark calls per trial.
    """
    outputs, scene_id = context["tool_outputs"], context["scene_id"]
    rejected: list[list[str]] = []
    for _ in range(1 + MAX_RETRIES):
        body = post(build_check_request(context, rejected[-1] if rejected else ()))
        try:
            return validate_check(output_text(body), outputs, scene_id), rejected
        except AgentContractError as error:
            rejected.append(list(error.issues))
    return tool_only(scene_id, outputs), rejected
