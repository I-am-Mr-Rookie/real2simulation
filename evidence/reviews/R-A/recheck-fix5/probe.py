"""Offline fix5 review. Writes only alongside this script; no product mutations."""
from __future__ import annotations

import ast
import copy
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
from unittest.mock import patch

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "evidence/S14")]
(OUT / "tmp").mkdir(exist_ok=True)
original_temp = tempfile.TemporaryDirectory
tempfile.TemporaryDirectory = lambda *a, **kw: original_temp(*a, **dict(kw, dir=OUT / "tmp"))
tempfile.tempdir = os.environ["TEMP"]


def denied(*_a, **_kw):
    raise AssertionError("offline review: network/live calls/new extraction forbidden")


def audit(event, args):
    if event == "open":
        path, mode, flags = args
        if isinstance(path, (str, bytes, os.PathLike)):
            target = Path(os.fsdecode(path)).resolve()
            writing = bool(mode and any(c in mode for c in "wax+")) or bool(
                flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
            if writing and not target.is_relative_to(OUT):
                raise AssertionError(f"write outside owned review output: {target}")


sys.addaudithook(audit)
socket.socket.connect = socket.create_connection = denied
import S14g_fix5_gate_a as gate  # noqa: E402
from Build.agent import trial  # noqa: E402
from Build.agent.tools import safe_reply  # noqa: E402
from contracts.agent.validate import AgentContractError, CITE, numeric_issue, validate_response  # noqa: E402
from contracts.experiment.validate_experiment import validate_setup  # noqa: E402

fix, f3 = gate.FIX, gate.F4.F3
fix.live_post = denied
f3.understand.frame_jpeg = lru_cache(maxsize=32)(f3.understand.frame_jpeg)


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def snapshot():
    paths = [p for directory in ("Build", "contracts", "tests", "evidence/S14")
             for p in (ROOT / directory).rglob("*")
             if p.is_file() and "__pycache__" not in p.parts and "node_modules" not in p.parts
             and ".next" not in p.parts]
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)}


before = snapshot()
live = read(ROOT / "evidence/S14/S14g-fix3-live.json")
tools, sid = live["turns"][0]["tool_outputs"], live["turns"][0]["scene_id"]
number = {"type": "number", "ref": {"tool_output_id": tools[1]["id"], "quantity": "gravity"}}


def response_for(text, surface="segments", ref=number):
    field = [{"type": "text", "text": text}, copy.deepcopy(ref)]
    response = {"schema_version": "agent-response/1.0.0", "scene_id": sid,
                "segments": field if surface == "segments" else [copy.deepcopy(ref)], "questions": []}
    if surface == "rationale":
        response["candidates"] = [{"id": "candidate", "template": "free_fall", "rationale": field}]
    elif surface in ("prompt", "chip"):
        question = {"id": "q", "kind": "chips_and_free_text",
                    "prompt": [{"type": "text", "text": "Choose."}],
                    "chips": [{"id": "yes", "label": [{"type": "text", "text": "Yes."}]}]}
        if surface == "prompt":
            question["prompt"] = field
        else:
            question["chips"][0]["label"] = field
        response["questions"] = [question]
    return response


def validate_error(response):
    try:
        validate_response(response, tools, sid)
    except AgentContractError as error:
        return str(error)
    return None


# Reuse the prior review's exact cases, not its now-obsolete expected-failure assertions.
tree = ast.parse((ROOT / "evidence/reviews/R-A/recheck-fix4/probe.py").read_text("utf-8"))
cases = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "cases" for t in node.targets))
results = []
for name, text, bad in cases:
    response = response_for(text)
    shown, blocked = safe_reply(response, tools, sid)
    accepted, rejected = trial.check_trial({"scene_id": sid, "tool_outputs": tools},
                                          lambda _r: fix.OLD.body(json.dumps(response)))
    trial_shown, trial_blocked = safe_reply(accepted, tools, sid)
    residual = fix.visible(trial_shown, [fix.quantity_text(q) for o in tools for q in o["quantities"].values()])
    result = {"case": name, "text": text, "expected_bad": bad, "runtime_error": validate_error(response),
              "numeric_issue": numeric_issue(text), "oracle_issue": fix.oracle(text), "display_blocked": bool(blocked),
              "trial_rejections": len(rejected), "fallback": accepted["segments"][0]["text"].startswith(
                  "The automatic trial check"), "trial_blocked": bool(trial_blocked),
              "untraced_text_displayed": text in trial_shown, "trial_shown": trial_shown,
              "fallback_residual_oracle": fix.oracle(residual)}
    assert bool(result["runtime_error"]) == bool(result["oracle_issue"]) == bad
    assert result["display_blocked"] == bad and result["fallback"] == bad
    assert len(rejected) == (4 if bad else 0) and not trial_blocked
    assert result["untraced_text_displayed"] != bad and not result["fallback_residual_oracle"]
    results.append(result)

surfaces = []
for name, text, bad in cases:
    for surface in ("segments", "prompt", "chip", "rationale"):
        response = response_for(text, surface)
        issue = validate_error(response)
        oracle_issue = next(filter(None, map(fix.oracle, fix.visible_strings(response))), None)
        assert bool(issue) == bool(oracle_issue) == bad, (name, surface, issue, oracle_issue)
        surfaces.append({"case": name, "surface": surface, "blocked": bool(issue), "oracle_issue": oracle_issue})

forgeries = []
for marker in (CITE, "\uf8ff", "\U000f0000"):
    for surface in ("segments", "prompt", "chip", "rationale"):
        text = marker + " metres per second"
        issue = validate_error(response_for(text, surface))
        assert issue and "private_use_character" in issue
        record = {"marker": f"U+{ord(marker):04X}", "surface": surface, "blocked": True}
        if surface == "segments":
            response = response_for(text)
            accepted, rejected = trial.check_trial({"scene_id": sid, "tool_outputs": tools},
                lambda _r: fix.OLD.body(json.dumps(response, ensure_ascii=True)))
            assert len(rejected) == 4 and accepted["segments"][0]["text"].startswith("The automatic trial check")
            record["escaped_json_trial_rejections"] = len(rejected)
        forgeries.append(record)

# Bounded ordinary-language probes, including the exact worker-disclosed residual.
gaps = [
    ("disclosed-gravity-label", "The period is one whole minute: ", "gravity", True),
    ("full-second-label", "The elapsed time is a full second: ", "gravity", True),
    ("full-radian-label", "The angle is one full radian = ", "gravity", True),
    ("full-metre-label", "The distance is one full metre: ", "gravity", True),
    ("same-dimension-amount", "The elapsed time is a full second: ", "duration", True),
    ("full-second-comma", "The elapsed time is a full second, ", "gravity", False),
    ("full-second-period", "The elapsed time is a full second. ", "gravity", False),
    ("one-more-minute", "The period is one more minute. ", "gravity", False),
]
gap_results = []
gap_surfaces = []
for name, text, quantity, accepted_expected in gaps:
    ref = copy.deepcopy(number)
    if quantity == "duration":
        ref["ref"] = {"tool_output_id": tools[0]["id"], "quantity": quantity}
    response = response_for(text, ref=ref)
    accepted, rejected = trial.check_trial({"scene_id": sid, "tool_outputs": tools},
                                          lambda _r: fix.OLD.body(json.dumps(response)))
    shown, blocked = safe_reply(accepted, tools, sid)
    issue = validate_error(response)
    oracle_issue = next(filter(None, map(fix.oracle, fix.visible_strings(response))), None)
    actual_accept = issue is None
    assert actual_accept == accepted_expected, (name, issue)
    assert bool(oracle_issue) != accepted_expected
    assert len(rejected) == (0 if accepted_expected else 4) and not blocked
    assert (text in shown) == accepted_expected
    for surface in ("segments", "prompt", "chip", "rationale"):
        surface_response = response_for(text, surface, ref)
        surface_issue = validate_error(surface_response)
        surface_oracle = next(filter(None, map(fix.oracle, fix.visible_strings(surface_response))), None)
        assert bool(surface_issue) == bool(surface_oracle) == (not accepted_expected)
        gap_surfaces.append({"case": name, "surface": surface, "accepted": surface_issue is None,
                             "oracle_issue": surface_oracle})
    gap_results.append({"case": name, "text": text, "accepted": actual_accept,
                        "runtime_error": issue, "oracle_issue": oracle_issue,
                        "trial_rejections": len(rejected), "shown": shown,
                        "cited_quantity": next(o["quantities"][quantity] for o in tools
                                               if o["id"] == ref["ref"]["tool_output_id"])})

# Actual evidence runner: all six old misses now fall back; disclosed label miss is still shown.
gate_turns = []
for text in [row[1] for row in cases[12:18]] + [gaps[0][1]]:
    def post(_request, text=text):
        return fix.OLD.body(json.dumps({"schema_version": "agent-response/1.0.0", "scene_id": fix.OLD.SCENE_ID,
            "segments": [{"type": "text", "text": text}, {"type": "number", "ref": {
                "tool_output_id": "gate-a-t00-fit", "quantity": "gravity"}}], "questions": []}))
    row = fix.turn(0, post, fix.OLD.SCENE_ID)
    gate_turns.append({"text": text, **{k: row[k] for k in
        ("attempts", "model_reply_shown", "invented", "shown", "blocked")}})
assert all(r["attempts"] == 4 and not r["model_reply_shown"] and not r["invented"] for r in gate_turns[:6])
assert gate_turns[-1]["attempts"] == 1 and gate_turns[-1]["model_reply_shown"] and not gate_turns[-1]["invented"]

# Fresh saved-response replay through the real setup validator, never the S14-writing CLI.
setup_calls = []
original_setup = gate.F4.production_setup


def observe_setup(spec, scene, root):
    setup_calls.append({"scene_id": spec["scene"]["scene_id"], "bundle_is_none": scene is None,
                        "real_binding": gate.F4.validate_setup is validate_setup})
    return original_setup(spec, scene, root)


with patch.object(gate.F4, "production_setup", observe_setup):
    replay = gate.run()
assert len(setup_calls) == 10 and all(r["bundle_is_none"] and r["real_binding"] for r in setup_calls)
assert f3.interview.validate_setup is validate_setup
assert replay["summary"] == read(ROOT / "evidence/S14/S14g-fix5-offline.json")["summary"]
summary = replay["summary"]
assert summary["gate_a"] == "MET_AMENDED_Q16" and summary["gate_a_label"] == "scale unverified, not setup-validated"
assert summary["numeric_contract_valid_specs"] == summary["distinct_recorded_scenes"] == 10
assert summary["setup_validator_valid_specs"] == summary["invented_shown_oracle"] == 0
assert summary["live_turns_replayed"] == summary["live_turns_shown_unchanged"] == 30
assert summary["live_turns_fallback_tool_only"] == 0
assert len({r["case_id"] for r in replay["live_turns"]}) == 30

# Summary logic only: synthetic counts below are not real setup successes.
thresholds = []
for specs_count, turns_count, invention, expected in (
    (8, 30, False, "NOT_MET"), (9, 30, False, "MET_AMENDED_Q16"),
    (10, 29, False, "NOT_MET"), (10, 30, True, "NOT_MET"),
):
    numeric = [{"case_id": str(i), "scene_id": str(i), "valid": i < specs_count} for i in range(10)]
    setup = [{"case_id": str(i), "scene_id": str(i), "valid": False} for i in range(10)]
    turns = [{"fallback": None, "blocked": False, "render_unchanged": True,
              "invented": "test-only" if invention and i == 0 else None} for i in range(turns_count)]
    with patch.object(gate.F4, "specs", side_effect=[numeric, setup]), patch.object(gate, "live_turns", return_value=turns):
        result = gate.run()["summary"]
    assert result["gate_a"] == expected
    thresholds.append({"synthetic_logic_only": True, "numeric_passes": specs_count, "turns": turns_count,
                       "invention": invention, "actual": result["gate_a"]})

oracle_tree = ast.parse((ROOT / "evidence/S14/S14g_fix_oracle.py").read_text("utf-8"))
imports = [n.module for n in ast.walk(oracle_tree) if isinstance(n, ast.ImportFrom)]
assert not any(name and name.startswith("contracts.agent") for name in imports)
assert fix.self_check() == {"corpus_cases": 56, "oracle_agrees": True}
after = snapshot()
assert before == after, "protected inputs changed"
output = {"verdict": "CHANGES_REQUIRED", "exact_prior_cases": results, "visible_surfaces": surfaces,
          "cite_forgeries": forgeries, "bounded_gap_probes": gap_results, "bounded_gap_surfaces": gap_surfaces,
          "actual_gate_turns": gate_turns,
          "setup_calls": setup_calls, "fix5_summary": summary, "threshold_logic_only": thresholds,
          "oracle_imports": imports, "oracle_corpus": fix.self_check(), "protected_input_sha256": before,
          "protected_inputs_unchanged": True, "network_denied": True, "spend_usd": 0}
(OUT / "results.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "fix5-replay.json").write_text(json.dumps(replay, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"verdict": output["verdict"], "prior_cases": len(results), "surface_checks": len(surfaces),
                  "cite_forgery_checks": len(forgeries), "accepted_gap_probes": sum(r["accepted"] for r in gap_results),
                  "fix5_summary": summary, "oracle_corpus": output["oracle_corpus"],
                  "protected_files": len(before), "protected_inputs_unchanged": True}, indent=2))
