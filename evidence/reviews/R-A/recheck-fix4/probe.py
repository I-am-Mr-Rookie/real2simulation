"""Offline read-only fix4 review; run with python -B from the worktree root.

Writes only beside this script. Saved response replay is not new model/physical evidence.
"""
from __future__ import annotations

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
original_temporary_directory = tempfile.TemporaryDirectory
tempfile.TemporaryDirectory = lambda *a, **kw: original_temporary_directory(*a, **dict(kw, dir=OUT / "tmp"))
tempfile.tempdir = os.environ["TEMP"]  # reuse the existing cache without tempfile's write-probe outside Owns


def denied(*_a, **_kw):
    raise AssertionError("offline review forbids network/live calls/new frame extraction")


def audit(event, args):
    if event == "open":
        path, mode, flags = args
        if isinstance(path, (str, bytes, os.PathLike)):
            target = Path(os.fsdecode(path)).resolve()
            if target.name == ".env":
                raise AssertionError("review never reads .env")
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
                isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
            if writing and not target.is_relative_to(OUT):
                raise AssertionError(f"write outside review Owns: {target}")


sys.addaudithook(audit)
socket.socket.connect = socket.create_connection = denied
import S14g_fix4_gate_a as gate  # noqa: E402
from Build.agent import trial  # noqa: E402
from Build.agent.tools import safe_reply  # noqa: E402
from contracts.agent.validate import AgentContractError, numeric_issue, validate_response  # noqa: E402
from contracts.experiment.validate_experiment import validate_setup  # noqa: E402

f3, fix = gate.F3, gate.FIX
fix.live_post = denied
f3.understand.frame_jpeg = lru_cache(maxsize=32)(f3.understand.frame_jpeg)


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def snapshot():
    paths = [p for directory in ("Build/agent", "contracts/agent", "tests/agent", "evidence/S14")
             for p in (ROOT / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)}


before = snapshot()
live = read(ROOT / "evidence/S14/S14g-fix3-live.json")
tools, sid = live["turns"][0]["tool_outputs"], live["turns"][0]["scene_id"]
number = {"type": "number", "ref": {"tool_output_id": tools[1]["id"], "quantity": "gravity"}}
cases = [
    ("original-second", "The elapsed time is a second.", True),
    ("original-minute", "The period is a minute.", True),
    ("original-radian", "The angle is a radian.", True),
    ("an-hour", "The period is an hour.", True),
    ("single-second", "The delay is a single second.", True),
    ("one-rad", "The angle is one rad.", True),
    ("a-millisecond", "The delay is a millisecond.", True),
    ("a-degree", "The angle is a degree.", True),
    ("pronoun-one", "This one fits the scene.", False),
    ("double-check", "Please double-check the fit.", False),
    ("unit-only", "Measure the angle in radians.", False),
    ("rate-unit-only", "The speed is expressed in metres per second.", False),
    ("a-full-second", "The elapsed time is a full second.", True),
    ("one-whole-minute", "The period is one whole minute.", True),
    ("one-full-radian", "The angle is one full radian.", True),
    ("one-full-metre", "The distance is one full metre.", True),
    ("one-hyphen-second", "This is a one-second delay.", True),
    ("single-hyphen-second", "The delay is a single-second interval.", True),
    ("one-short-g", "The mass is one g.", True),
    ("one-short-n", "The force is one N.", True),
]
results = []
for name, text, expected_numeric in cases:
    response = {"schema_version": "agent-response/1.0.0", "scene_id": sid,
                "segments": [{"type": "text", "text": text}, copy.deepcopy(number)], "questions": []}
    shown, blocked = safe_reply(response, tools, sid)
    accepted, rejected = trial.check_trial({"scene_id": sid, "tool_outputs": tools},
                                         lambda _r: fix.OLD.body(json.dumps(response)))
    trial_shown, trial_blocked = safe_reply(accepted, tools, sid)
    residual = fix.visible(trial_shown, [fix.quantity_text(q) for o in tools for q in o["quantities"].values()])
    results.append({"case": name, "text": text, "expected_numeric": expected_numeric,
                    "numeric_issue": numeric_issue(text), "display_blocked": bool(blocked),
                    "oracle_issue": fix.oracle(text), "trial_rejections": len(rejected),
                    "trial_fallback": accepted["segments"][0]["text"].startswith("The automatic trial check"),
                    "trial_blocked": bool(trial_blocked), "trial_shown": trial_shown,
                    "untraced_text_displayed": text in trial_shown, "trial_residual_oracle": fix.oracle(residual)})
assert all(r["display_blocked"] and r["oracle_issue"] and r["trial_fallback"]
           and r["trial_rejections"] == 4 and not r["untraced_text_displayed"] for r in results[:8])
assert all(not r["display_blocked"] and not r["oracle_issue"] and not r["trial_fallback"]
           and r["untraced_text_displayed"] for r in results[8:12])
assert all(not r["display_blocked"] and not r["oracle_issue"] and not r["trial_fallback"]
           and r["untraced_text_displayed"] and not r["trial_residual_oracle"] for r in results[12:16])

# Exercise the evidence runner itself as well as its trial/display components.
gate_turns = []
for case_index in (0, 1, 2, 12, 13, 14, 15):
    name, text, _bad = cases[case_index]
    response = {"schema_version": "agent-response/1.0.0", "scene_id": fix.OLD.SCENE_ID,
                "segments": [{"type": "text", "text": text},
                             {"type": "number", "ref": {"tool_output_id": "gate-a-t00-fit", "quantity": "gravity"}}],
                "questions": []}
    row = fix.turn(0, lambda _r: fix.OLD.body(json.dumps(response)), fix.OLD.SCENE_ID)
    if case_index < 3:
        assert not row["model_reply_shown"] and row["attempts"] == 4 and row["invented"] is None
    else:
        assert row["model_reply_shown"] and row["attempts"] == 1 and row["invented"] is None and text in row["shown"]
    gate_turns.append(dict(case=name, **row))

# Same common-modifier miss at all visible entry points, not just numeric_issue.
surface_results = []
for where in ("segments", "prompt", "chip", "rationale"):
    text = cases[12][1]
    response = {"schema_version": "agent-response/1.0.0", "scene_id": sid,
                "segments": [{"type": "text", "text": "Check the fit."}, copy.deepcopy(number)], "questions": []}
    field = [{"type": "text", "text": text}]
    if where == "segments":
        response["segments"] = field + [copy.deepcopy(number)]
    elif where == "rationale":
        response["candidates"] = [{"id": "k", "template": "free_fall", "rationale": field}]
    else:
        q = {"id": "q", "kind": "chips_and_free_text", "prompt": [{"type": "text", "text": "Pick."}],
             "chips": [{"id": "c", "label": [{"type": "text", "text": "Ball"}]}]}
        if where == "prompt":
            q["prompt"] = field
        else:
            q["chips"][0]["label"] = field
        response["questions"] = [q]
    validate_response(response, tools, sid)
    surface_results.append({"surface": where, "accepted": True, "oracle_issue": fix.oracle(text)})

# Fresh saved-response replay through the actual setup validator; no evidence/S14 CLI write.
setup_calls = []
original_production = gate.production_setup


def observe_setup(spec, scene, root):
    setup_calls.append({"scene_id": spec["scene"]["scene_id"], "bundle_is_none": scene is None,
                        "real_binding": gate.validate_setup is validate_setup})
    return original_production(spec, scene, root)


with patch.object(gate, "production_setup", observe_setup):
    replay = gate.run()
assert len(setup_calls) == 10 and all(c["real_binding"] and c["bundle_is_none"] for c in setup_calls)
assert gate.F3.interview.validate_setup is validate_setup
assert replay["summary"] == read(ROOT / "evidence/S14/S14g-fix4-offline.json")["summary"]
assert replay["summary"]["gate_a"] == "PROVISIONAL"
assert replay["summary"]["numeric_contract_valid_specs"] == 10
assert replay["summary"]["setup_validator_valid_specs"] == 0
assert replay["summary"]["live_turns_valid_and_render_unchanged"] == 30

# Summary-logic tests only: fake pass counts do NOT attest a successful real setup.
thresholds = []
for nset, turns_count, invented, expected in (
    (0, 30, False, "PROVISIONAL"), (8, 30, False, "PROVISIONAL"),
    (9, 30, False, "MET"), (10, 30, False, "MET"),
    (9, 29, False, "NOT_MET"), (9, 30, True, "NOT_MET"),
):
    numeric = [{"case_id": str(i), "scene_id": str(i), "valid": True} for i in range(10)]
    setup = [{"case_id": str(i), "scene_id": str(i), "valid": i < nset} for i in range(10)]
    turns = [{"valid_under_fix4": True, "render_unchanged": True, "invented": "test" if invented and i == 0 else None}
             for i in range(turns_count)]
    with patch.object(gate, "specs", side_effect=[numeric, setup]), patch.object(gate, "live_turns", return_value=turns):
        summary = gate.run()["summary"]
    assert summary["gate_a"] == expected
    thresholds.append({"synthetic_logic_test_only": True, "setup_passes": nset, "turns": turns_count,
                       "invention": invented, "expected": expected, "actual": summary["gate_a"]})

# Check fix3 relabel on saved fixture rows without re-running random simulation.
saved_specs = {r["case_id"]: r for r in live["specs"]}
with patch.object(f3, "spec_case", side_effect=lambda clip, _post: copy.deepcopy(saved_specs[clip])), \
     patch.object(fix, "turn", side_effect=lambda i, _post, _sid: copy.deepcopy(live["turns"][i])):
    relabel = f3.run("offline")["summary"]
assert relabel["gate_a"] == "PROVISIONAL"

# The oracle remains implementation-independent, although coverage can share conceptual gaps.
import ast
oracle_tree = ast.parse((ROOT / "evidence/S14/S14g_fix_oracle.py").read_text("utf-8"))
imports = [n.module for n in ast.walk(oracle_tree) if isinstance(n, ast.ImportFrom)]
assert not any(name and name.startswith("contracts.agent") for name in imports)
assert fix.self_check() == {"corpus_cases": 40, "oracle_agrees": True}
after = snapshot()
assert before == after, "review modified protected inputs"
output = {"verdict": "CHANGES_REQUIRED", "original_examples_closed": True,
          "new_common_modifier_misses": [r["case"] for r in results[12:16]],
          "probes": results, "actual_gate_turns": gate_turns, "visible_surfaces": surface_results, "setup_calls": setup_calls,
          "fix4_summary": replay["summary"], "threshold_logic_only": thresholds,
          "fix3_saved_fixture_summary_relabel": relabel, "oracle_imports": imports,
          "oracle_corpus": fix.self_check(), "protected_input_sha256": before,
          "protected_inputs_unchanged": True, "network_denied": True, "spend_usd": 0}
(OUT / "results.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "fix4-replay.json").write_text(json.dumps(replay, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({k: output[k] for k in ("verdict", "original_examples_closed", "new_common_modifier_misses",
                                        "fix4_summary", "oracle_corpus", "protected_inputs_unchanged")}, indent=2))
