"""S14g-fix4 Gate A OFFLINE re-run (R-A F3-R). Usage (repo root): python -B evidence/S14/S14g_fix4_gate_a.py

No network (sockets denied), no Meta calls, no spend, no new frame extraction. Replays the SAVED fix3 Wonder
responses (S14g-fix3-recorded.json) through the fix3 spec_case twice:
  A) numeric-contract scope: fix3's validate() stand-in (unchanged) -> provisional evidence only;
  B) REAL production path: interview.answers_to_spec -> contracts.experiment.validate_setup, with the scene bundles
     that actually exist for these clips (none: S05d abstained on scale) -> expected refusal.
and re-validates the 30 saved LIVE fix3 turns under the current (fix4) display boundary: exact render + oracle.
gate_a is MET only if >= 9 specs pass path B; a numeric-contract-only pass is PROVISIONAL, never MET.
"""
from __future__ import annotations

import json
import socket
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT), str(HERE)]


def denied(*_a, **_k):
    raise AssertionError("fix4 offline re-run forbids network and new frame extraction")


socket.socket.connect = denied
socket.create_connection = denied
import S14g_fix3_gate_a as F3  # noqa: E402  (reuse: recorded replay, spec_case, clip custody)
from Build.agent import interview  # noqa: E402
from contracts.agent.validate import validate_response  # noqa: E402
from contracts.experiment.validate_experiment import validate_setup  # noqa: E402

F3.keyframes.extract = F3.seek_frames = F3.keyframes._run = denied
FIX = F3.FIX
SPEC_PASS, TURNS = FIX.SPEC_PASS, FIX.TURNS
NUMERIC_STAND_IN = F3.spec_only  # fix3's validate()-only stand-in (scope A)


def production_setup(spec, scene, root):
    """The real validator, unmodified; a non-ValueError crash on the absent bundle is recorded, not hidden."""
    try:
        return validate_setup(spec, scene, root)
    except ValueError:
        raise
    except Exception as error:  # noqa: BLE001
        raise ValueError(f"validate_setup raised {type(error).__name__} with no bundle: {error}") from error


def specs(stand_in):
    F3.spec_only = stand_in  # fix3 spec_case installs F3.spec_only as interview.validate_setup for the call
    rows = [F3.spec_case(clip, F3.recorded_post(clip)[0]) for clip in F3.CLIPS]
    assert interview.validate_setup is validate_setup  # restored after each case
    return rows


def live_turns():
    live = json.loads((HERE / "S14g-fix3-live.json").read_text(encoding="utf-8"))
    out = []
    for row in live["turns"]:
        outputs = row["tool_outputs"]
        assert FIX.sha(outputs) == row["tool_outputs_sha256"]
        rec = {"case_id": row["case_id"], "mystery": row.get("mystery")}
        try:
            response = validate_response(row["accepted_response"], outputs, row["scene_id"])
        except ValueError as error:
            out.append(dict(rec, valid_under_fix4=False, why=str(error)[:300]))
            continue
        shown, blocked = FIX.safe_reply(response, outputs, row["scene_id"])
        residual = shown
        for q in (q for o in outputs for q in o["quantities"].values()):
            residual = residual.replace(f"{q['value']:.6g} ± {q['uncertainty']:.2g} {q['unit']} ({q['source']['label']})", " ")
        out.append(dict(rec, valid_under_fix4=True, render_unchanged=shown == row["shown"] and not blocked,
                        invented=FIX.oracle(residual) or next(filter(None, map(FIX.oracle, FIX.visible_strings(response))), None)))
    return out


def brief(rows):
    return {r["case_id"]: (True if r.get("valid") else (r.get("why") if isinstance(r.get("why"), str) else list(r.get("why") or [])[:2]))
            for r in rows}


def run() -> dict:
    numeric = specs(NUMERIC_STAND_IN)
    setup = specs(production_setup)
    turns = live_turns()
    n_num = sum(bool(r.get("valid")) for r in numeric)
    n_set = sum(bool(r.get("valid")) for r in setup)
    invented = sum(bool(t.get("invented")) for t in turns) + sum(bool(r.get("invented")) for r in numeric)
    turns_ok = len(turns) == TURNS and all(t.get("valid_under_fix4") and t.get("render_unchanged") for t in turns) and not invented
    gate = "MET" if n_set >= SPEC_PASS and turns_ok else ("PROVISIONAL" if n_num >= SPEC_PASS and turns_ok else "NOT_MET")
    summary = {
        "gate_a": gate,
        "why": None if gate == "MET" else (
            f"numeric-contract scope only: {n_num}/{len(numeric)} recorded specs pass contracts.experiment validate(); "
            f"real interview.validate_setup path passes {n_set}/{len(setup)} (no authoritative scene bundle with known "
            "scale exists for these clips). Gate A needs >= 9 on the normal setup path or an owner-approved amendment."),
        "distinct_recorded_scenes": len({r["scene_id"] for r in numeric}),
        "numeric_contract_valid_specs": n_num, "setup_validator_valid_specs": n_set, "required_valid_specs": SPEC_PASS,
        "numeric_contract_cases": brief(numeric), "setup_validator_cases": brief(setup),
        "live_turns_replayed": len(turns), "live_turns_valid_and_render_unchanged": sum(bool(t.get("valid_under_fix4") and t.get("render_unchanged")) for t in turns),
        "invented_shown_oracle": invented, "oracle_self_check": FIX.self_check(),
        "spec_sources": "recorded (S14g-fix3-recorded.json); no new model call", "network_denied": True, "spend_usd": 0,
        "scope": "offline replay of saved fix3 responses; synthetic interview answers (fixture, not user evidence); "
                 "turn tool outputs are synthetic-room-v1, not physical evidence"}
    return {"summary": summary, "numeric_contract_specs": numeric, "setup_validator_specs": setup, "live_turns": turns}


if __name__ == "__main__":
    result = run()
    (HERE / "S14g-fix4-offline.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=1, ensure_ascii=False))

