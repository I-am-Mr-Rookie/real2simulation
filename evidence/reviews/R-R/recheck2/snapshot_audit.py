"""CPU-only, assert-based snapshot/threshold and synthetic control audit."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "Build/reconstruction/spike"))
import gate_r as gate
from test_gate_r import clip


def main():
    rel = "Build/reconstruction/spike/gate_r.py"
    source = (ROOT / rel).read_text(encoding="utf-8")
    before = subprocess.check_output(["git", "show", f"5660461^:{rel}"], cwd=ROOT, text=True)
    names = {"SCALE_TOL", "ANGLE_TOL_DEG", "GPU_MIN_PER_SCENE", "MIN_SCALE_PASSES", "GPU_S", "EPS", "COHORT"}

    def constants(text):
        return {ast.dump(node.targets[0]): ast.dump(node.value) for node in ast.parse(text).body
                if isinstance(node, ast.Assign) and names.intersection(
                    n.id for n in ast.walk(node.targets[0]) if isinstance(n, ast.Name))}

    assert constants(source) == constants(before)
    assert (gate.SCALE_TOL, gate.ANGLE_TOL_DEG, gate.GPU_S, gate.MIN_SCALE_PASSES, gate.EPS, gate.COHORT) == (
        0.1, 5.0, 240.0, 2, 1e-12, ("RM02", "RM04", "RM05"))
    saved_path = ROOT / "evidence/S05/S05f/GATE_R.json"
    rerun_path = OUT / "GATE_R-rerun.json"
    saved, rerun = (json.loads(p.read_text()) for p in (saved_path, rerun_path))
    assert saved == rerun and saved_path.read_bytes() == rerun_path.read_bytes()
    assert rerun["verdict"] == "FAIL" and rerun["summary"] == {
        "scale_passes": 0, "orientation_passes": 0, "qualifying_clips": 0, "gpu_passes": 3, "clips": 3}

    # Prove the review's exact malicious inputs distinguished the pre-fix evaluator.
    old = {"__name__": "pre_fix_review_control"}
    exec(compile(before, "pre-fix-gate_r.py", "exec"), old)
    frames = {cid: clip(1.0, 1.0) for cid in gate.COHORT}
    jobs = [{"app_id": cid, "scenes": [cid], "function_s": 160.0,
             "lifetime_s": 600.0 if cid == "RM02" else 190.0, "cost_usd": 0.06} for cid in gate.COHORT]
    assert old["evaluate"](frames, jobs)["verdict"] == "FAIL"
    old_controls = []
    for scenes in (["RM02"] * 3, ["RM02", "unknown1", "unknown2"]):
        malicious = copy.deepcopy(jobs)
        malicious[0]["scenes"] = scenes
        old_verdict = old["evaluate"](frames, malicious)["verdict"]
        assert old_verdict == "PASS"
        try:
            gate.evaluate(frames, malicious)
        except ValueError:
            old_controls.append({"scenes": scenes, "before": old_verdict, "after": "REJECTED"})
        else:
            raise AssertionError("D2 guard does not reject its historical control")

    # Changed membership checks may throw TypeError on non-hashable elements, but must not return PASS.
    type_checks = []
    for scenes in ([["RM02"]], [{"scene": "RM02"}]):
        malformed = copy.deepcopy(jobs)
        malformed[0]["scenes"] = scenes
        try:
            gate.evaluate(frames, malformed)
        except (TypeError, ValueError) as exc:
            type_checks.append({"scenes": scenes, "rejected_as": type(exc).__name__})
        else:
            raise AssertionError("non-scalar scene IDs accepted")

    paths = [rel, "Build/reconstruction/spike/test_gate_r.py", "evidence/S05/S05f/RESULT.json",
             "evidence/S05/S05c/RESULT.json", "evidence/S05/S05b/orch14/job-ledger.json",
             "evidence/S05/S05f/GATE_R.json"]
    data = {"snapshot": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "repair_commit": "56604618585aa0bce91e37c146cf5542c3c9bf38", "synthetic_controls_only": True,
            "threshold_assignments_unchanged": True, "threshold_ast": constants(source),
            "real_gate_parsed_equal": saved == rerun, "real_gate_bytes_equal": True,
            "real_gate_summary": rerun["summary"], "real_gate_verdict": rerun["verdict"],
            "old_vs_new_d2": old_controls, "non_scalar_scene_ids": type_checks,
            "sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
            "source_repair_diff": subprocess.check_output(
                ["git", "diff", "5660461^", "5660461", "--", rel], cwd=ROOT, text=True)}
    (OUT / "snapshot-audit.json").write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("Snapshot audit PASS: thresholds/EPS/cohort unchanged; real FAIL byte-identical; "
          "historical D2 false-PASS controls now rejected; non-scalar IDs fail closed")


if __name__ == "__main__":
    main()
