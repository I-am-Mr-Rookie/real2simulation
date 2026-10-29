"""Synthetic-only D1/D2 repaired-behaviour regressions. No GPU/API.

Supersedes historical defect-expecting assertions and remaining-defects.json.
New output goes to recheck2; historical counterexample files stay untouched.
Uses the real CLI, existing receipt hashes and the owner's clip fixture.
"""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1] / "recheck2"
sys.path.insert(0, str(ROOT / "Build/reconstruction/spike"))
import gate_r as gate
from test_gate_r import clip


def main():
    OUT.mkdir(exist_ok=True)
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
    # This would PASS under last-wins decoding; unique bad control must FAIL.
    text = '{"RM02":' + json.dumps(bad) + ',' + json.dumps(frames)[1:]
    path = OUT / "duplicate-frames.json"
    path.write_text(text + "\n", encoding="utf-8")
    cli_checks = []
    with tempfile.TemporaryDirectory(dir=OUT) as tmp:
        target = Path(tmp) / "out.json"
        command = [sys.executable, "-B", str(ROOT / "Build/reconstruction/spike/gate_r.py")]
        control_path = Path(tmp) / "control.json"
        control_path.write_text(json.dumps({**frames, "RM02": bad}), encoding="utf-8")
        control_proc = subprocess.run(command + ["--frames", str(control_path), str(target)],
                                      cwd=ROOT, capture_output=True, text=True)
        assert control_proc.returncode == 0, control_proc.stderr
        assert json.loads(target.read_text())["verdict"] == "FAIL"
        target.unlink()  # never let old output masquerade as a new rejection result
        inputs = {"--frames": path,
                  "--s05c": ROOT / "evidence/S05/S05c/RESULT.json",
                  "--orch14": ROOT / "evidence/S05/S05b/orch14/job-ledger.json"}
        for flag, original in inputs.items():
            doc = original.read_text(encoding="utf-8")
            # Duplicate an existing key in each real CLI input, including escaped-key equality.
            first_key, first_value = next(iter(json.loads(doc).items()))
            duplicate = "{" + json.dumps(first_key) + ":" + json.dumps(first_value) + "," + doc.lstrip()[1:]
            variants = {"top_level": duplicate,
                        "nested": '{"outer":{"a":1,"\\u0061":2}}'}
            for label, payload in variants.items():
                malformed = Path(tmp) / "duplicate.json"
                malformed.write_text(payload, encoding="utf-8")
                proc = subprocess.run(command + ["--frames", str(control_path), flag, str(malformed), str(target)],
                                      cwd=ROOT, capture_output=True, text=True)
                assert proc.returncode != 0 and "duplicate JSON members" in proc.stderr, proc.stderr
                assert not target.exists(), "rejected CLI input must not write a successful artifact"
                cli_checks.append({"input": flag, "variant": label, "exit": proc.returncode,
                                   "error": proc.stderr.strip().splitlines()[-1], "output_created": False})
        # The original conflicting frame counterexample, not merely an equal duplicate.
        proc = subprocess.run(command + ["--frames", str(path), str(target)],
                              cwd=ROOT, capture_output=True, text=True)
        assert proc.returncode != 0 and "duplicate JSON members" in proc.stderr, proc.stderr
        assert not target.exists()
        cli_checks.append({"input": "--frames", "variant": "original_conflicting_RM02",
                           "exit": proc.returncode, "error": proc.stderr.strip().splitlines()[-1],
                           "output_created": False})
    jobs = [{"app_id": "synthetic", "scenes": [cid], "function_s": 160.0,
             "lifetime_s": 600.0 if cid == "RM02" else 190.0, "cost_usd": 0.0} for cid in gate.COHORT]
    control = gate.evaluate(frames, jobs)
    assert control["verdict"] == "FAIL" and not control["clips"]["RM02"]["gpu_pass"]
    rejected = []
    for scenes in (["RM02"] * 3, ["RM02", "unknown1", "unknown2"], [], "RM02", None,
                   [True], [2], ["rm02"], ["RM02 "]):
        malformed = copy.deepcopy(jobs)
        malformed[0]["scenes"] = scenes
        try:
            gate.evaluate(frames, malformed)
        except ValueError as exc:
            rejected.append({"scenes": scenes, "error": str(exc)})
        else:
            raise AssertionError(("malformed job accepted", scenes))
    for reverse in (False, True):
        malformed = copy.deepcopy(jobs)
        malformed[1]["scenes"].append("RM02")
        if reverse:
            malformed.reverse()
        try:
            gate.evaluate(frames, malformed)
        except ValueError as exc:
            assert "conflicting GPU coverage" in str(exc)
            rejected.append({"cross_job_overlap_reversed": reverse, "error": str(exc)})
        else:
            raise AssertionError("conflicting job coverage accepted")
    legit_jobs = [dict(jobs[0], lifetime_s=190.0, cost_usd=0.06),
                  dict(jobs[1], scenes=["RM04", "RM05"], function_s=178.0,
                       lifetime_s=262.0, cost_usd=0.06)]
    legit = gate.evaluate(frames, legit_jobs)
    assert legit["verdict"] == "PASS" and legit["summary"]["qualifying_clips"] == 2
    for cid in ("RM04", "RM05"):
        gpu = legit["clips"][cid]["gpu"]
        assert (gpu["job_scenes"], gpu["lifetime_s_amortized"], gpu["cost_usd_amortized"]) == (2, 131.0, 0.03)
        assert gpu["function_s"] == 178.0  # function wall time remains unamortized
    for field, limit in (("lifetime_s", 480.0), ("function_s", 240.0)):
        boundary = copy.deepcopy(legit_jobs)
        boundary[1][field] = limit
        assert gate.evaluate(frames, boundary)["verdict"] == "PASS"
        boundary[1][field] += 0.000001
        assert gate.evaluate(frames, boundary)["verdict"] == "FAIL"
    missing = gate.evaluate(frames, legit_jobs[:1])
    assert missing["verdict"] == "FAIL" and missing["summary"]["gpu_passes"] == 1
    evidence = {"synthetic_only": True,
                "duplicate_frame_keys": {"cli_checks": cli_checks,
                                         "unique_bad_first_control": unique_control["verdict"],
                                         "observed": "REJECTED", "required": "reject duplicate scene IDs"},
                "duplicate_job_scene_ids": {"control": control, "observed": "REJECTED",
                                             "rejections": rejected, "legitimate_two_scene": legit,
                                             "timing_boundaries": "inclusive 240 s; immediately over FAIL",
                                             "missing_coverage": missing["verdict"],
                                             "required": "reject duplicate/unknown job scene IDs before amortization"}}
    (OUT / "repaired-reproduction.json").write_text(json.dumps(evidence, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"D1/D2 repaired checks PASS: {len(cli_checks)} real CLI rejections, {len(rejected)} job rejections; "
          "failing controls, legitimate 2-scene amortization and timing boundaries preserved; synthetic only")


if __name__ == "__main__":
    main()
