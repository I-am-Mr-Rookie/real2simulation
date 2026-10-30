"""S14g-fix5 Gate A OFFLINE re-run (R-A F1-R2 structural unit rule + owner Q16=A amendment).
Usage (repo root): python -B evidence/S14/S14g_fix5_gate_a.py

Reuses S14g_fix4_gate_a (network denied, saved fix3 Wonder responses, both spec paths). Changes only the live-turn
replay: a saved accepted reply that the fix5 validator now refuses is counted as a FALLBACK and replaced by the
code-owned tool-only reply (worst case offline: the live retries cannot be replayed), and every shown text is checked
by the independent oracle with cited quantities as CITE. No model call, $0.
gate_a: MET only via >= 9 setup-validator specs; MET_AMENDED_Q16 (owner Q16=A) when >= 9 numeric-contract specs and 0
invented shown numbers; else NOT_MET. Final Gate A clearance still needs the R-A recheck.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parents[1]), str(HERE)]
import S14g_fix4_gate_a as F4  # noqa: E402  (reuse: offline guards, specs(), production_setup, brief)
from S14g_fix_oracle import CITE  # noqa: E402
from Build.agent import trial  # noqa: E402
from contracts.agent.validate import AgentContractError, validate_response  # noqa: E402

FIX = F4.FIX
LABEL = "scale unverified, not setup-validated"  # owner Q16=A, verbatim


def rendered(q) -> str:
    return f"{q['value']:.6g} ± {q['uncertainty']:.2g} {q['unit']} ({q['source']['label']})"


def live_turns():
    live = json.loads((HERE / "S14g-fix3-live.json").read_text(encoding="utf-8"))
    out = []
    for row in live["turns"]:
        outputs, scene = row["tool_outputs"], row["scene_id"]
        assert FIX.sha(outputs) == row["tool_outputs_sha256"]
        rec = {"case_id": row["case_id"], "mystery": row.get("mystery")}
        try:
            response = validate_response(row["accepted_response"], outputs, scene)
            rec["fallback"] = None
        except AgentContractError as error:
            response = trial.tool_only(scene, outputs)
            rec["fallback"] = str(error)[:300]
        shown, blocked = FIX.safe_reply(response, outputs, scene)
        residual = shown
        for q in (q for o in outputs for q in o["quantities"].values()):
            residual = residual.replace(rendered(q), CITE)
        out.append(dict(rec, blocked=blocked, render_unchanged=rec["fallback"] is None and shown == row["shown"],
                        shown=shown, invented=FIX.oracle(residual) or next(
                            filter(None, map(FIX.oracle, FIX.visible_strings(response))), None)))
    return out


def run() -> dict:
    numeric, setup, turns = F4.specs(F4.NUMERIC_STAND_IN), F4.specs(F4.production_setup), live_turns()
    n_num = sum(bool(r.get("valid")) for r in numeric)
    n_set = sum(bool(r.get("valid")) for r in setup)
    invented = sum(bool(t["invented"]) for t in turns) + sum(bool(r.get("invented")) for r in numeric)
    fallbacks = sum(t["fallback"] is not None for t in turns)
    turns_ok = len(turns) == F4.TURNS and not any(t["blocked"] for t in turns) and not invented
    gate = ("MET" if n_set >= F4.SPEC_PASS and turns_ok else "MET_AMENDED_Q16" if n_num >= F4.SPEC_PASS and turns_ok
            else "NOT_MET")
    summary = {
        "gate_a": gate, "gate_a_label": LABEL if gate == "MET_AMENDED_Q16" else None,
        "amendment": "owner Q16=A (Oct30): numeric-contract validation on recorded scenes accepted, labelled verbatim; "
                     "not plain MET; final clearance needs the R-A recheck",
        "distinct_recorded_scenes": len({r["scene_id"] for r in numeric}),
        "numeric_contract_valid_specs": n_num, "setup_validator_valid_specs": n_set, "required_valid_specs": F4.SPEC_PASS,
        "numeric_contract_cases": F4.brief(numeric), "setup_validator_cases": F4.brief(setup),
        "live_turns_replayed": len(turns), "live_turns_shown_unchanged": sum(t["render_unchanged"] for t in turns),
        "live_turns_fallback_tool_only": fallbacks, "invented_shown_oracle": invented,
        "oracle_self_check": FIX.self_check(), "network_denied": True, "spend_usd": 0,
        "scope": "offline replay of saved fix3 responses under the fix5 structural unit rule; a refused saved reply is "
                 "shown as the code-owned tool-only fallback (live retries not replayable offline); synthetic interview "
                 "answers; turn tool outputs are synthetic-room-v1, not physical evidence"}
    return {"summary": summary, "numeric_contract_specs": numeric, "setup_validator_specs": setup, "live_turns": turns}


if __name__ == "__main__":
    result = run()
    (HERE / "S14g-fix5-offline.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=1, ensure_ascii=False))
