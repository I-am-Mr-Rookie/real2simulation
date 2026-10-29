"""Synthetic-only residual-defect reproductions, NOT acceptance tests. No GPU/API.

All output stays beside this file. Uses the real CLI and existing receipts.
"""
import copy
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
    real = json.loads((ROOT / "evidence/S05/S05f/RESULT.json").read_text())
    frames = {cid: {**clip(1, 1), "npz_sha256": real[cid]["npz_sha256"]} for cid in gate.COHORT}
    frames["RM05"] = {**clip(), "npz_sha256": real["RM05"]["npz_sha256"]}
    bad = copy.deepcopy(frames["RM02"])
    bad["metric_scale"]["metres_per_model_unit"] = 2.0
    bad["a4_plane_normal"]["angle_to_gravity_deg"] = 9.0
    real_jobs = gate.gpu_jobs(json.loads((ROOT / "evidence/S05/S05c/RESULT.json").read_text()),
                              json.loads((ROOT / "evidence/S05/S05b/orch14/job-ledger.json").read_text()))
    unique_control = gate.evaluate({**frames, "RM02": bad}, real_jobs)
    assert unique_control["verdict"] == "FAIL"
    # Conflicting duplicate RM02 is silently replaced by the final JSON member.
    text = '{"RM02":' + json.dumps(bad) + ',' + json.dumps(frames)[1:]
    path = OUT / "duplicate-frames.json"
    path.write_text(text + "\n", encoding="utf-8")
    target = OUT / "duplicate-cli-result.json"
    command = [sys.executable, "-B", str(ROOT / "Build/reconstruction/spike/gate_r.py"),
               "--frames", str(path), str(target)]
    proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    result = json.loads(target.read_text()) if target.exists() else None
    assert proc.returncode == 0 and result["verdict"] == "PASS", (proc.returncode, proc.stderr, result)
    jobs = [{"app_id": "synthetic", "scenes": [cid], "function_s": 160.0,
             "lifetime_s": 600.0 if cid == "RM02" else 190.0, "cost_usd": 0.0} for cid in gate.COHORT]
    control = gate.evaluate(frames, jobs)
    assert control["verdict"] == "FAIL" and not control["clips"]["RM02"]["gpu_pass"]
    jobs[0]["scenes"] *= 3
    duplicate_job = gate.evaluate(frames, jobs)
    assert duplicate_job["verdict"] == "PASS" and duplicate_job["clips"]["RM02"]["gpu_pass"]
    jobs[0]["scenes"] = ["RM02", "not-a-cohort-scene-1", "not-a-cohort-scene-2"]
    extra_job = gate.evaluate(frames, jobs)
    assert extra_job["verdict"] == "PASS" and extra_job["clips"]["RM02"]["gpu_pass"]
    evidence = {"synthetic_only": True,
                "duplicate_frame_keys": {"cli_exit": proc.returncode, "stdout": proc.stdout.strip(),
                                         "unique_bad_first_control": unique_control["verdict"],
                                         "observed": result["verdict"], "required": "reject duplicate scene IDs"},
                "duplicate_job_scene_ids": {"control": control, "observed": duplicate_job,
                                             "extra_unknown_ids_observed": extra_job,
                                             "required": "reject duplicate/unknown job scene IDs before amortization"}}
    (OUT / "remaining-defects.json").write_text(json.dumps(evidence, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("Residual defects reproduced: duplicate JSON scene key accepted; repeated job IDs turn 600s into 200s")


if __name__ == "__main__":
    main()
