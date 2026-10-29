"""Synthetic review counterexamples, NOT scene measurements or a Gate R pass.

Assertions confirm the reviewed revision's defects are reproducible; they are
not acceptance tests for a corrected evaluator. Run with python -B.
"""
import copy
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Build/reconstruction/spike"))
import gate_r as gate
import scene_frame as sf
from test_gate_r import JOBS, clip
from test_scene_frame import synth_npz


def frames():
    return {cid: clip(1.0, 1.0) for cid in "ABC"}


def record(name, inputs, jobs, observed, required, detail):
    result = gate.evaluate(inputs, jobs)
    assert result["verdict"] == observed, (name, result)
    return {"case": name, "observed": result["verdict"], "required": required,
            "summary": result["summary"], "detail": detail, "result": result}


def main():
    cases = []
    cases.append(record("baseline_synthetic", frames(), JOBS, "PASS", "PASS",
                        "Control only: fixture declares FIT/MEASURED; no scene claim."))
    cases.append(record("all_abstain", {cid: clip() for cid in "ABC"}, JOBS,
                        "FAIL", "FAIL", "Existing fail-closed ABSTAIN behavior retained."))

    # Reuse the producer's own fixture and analyse(), not a hand-written status.
    with tempfile.TemporaryDirectory(dir=Path(__file__).parent / "tmp") as directory:
        path = Path(directory) / "synthetic.npz"
        synth_npz(path)
        img = sf.load_views(path)[0]["pts_img"]
        p0, p1 = (100, 100), (200, 300)
        ref = {"view": 0, "p0": p0, "p1": p1,
               "length_m": float(sf.np.linalg.norm(img[p0] - img[p1])),
               "length_sd_m": 0.001, "source": "synthetic review reference, not footage"}
        metric = sf.analyse(path, refs=[ref])["metric_scale"]
    assert metric["status"] == "calibrated"
    assert abs(metric["metres_per_model_unit"] - 1.0) < 1e-12
    f = frames()
    for value in f.values():
        value["metric_scale"] = copy.deepcopy(metric)
    cases.append(record("actual_producer_calibrated_status", f, JOBS, "FAIL", "PASS",
                        "Scale is exactly 1, but producer 'calibrated' is rejected as unmeasured; orientation remains synthetic."))

    f = frames()
    del f["C"]
    cases.append(record("missing_third_scene", f, JOBS, "PASS", "FAIL_OR_INVALID",
                        "Two entries suffice; no fixed three-scene cohort enforced."))
    f = frames()
    f["C"] = clip(2.0, 1.0)
    f["D"] = clip(2.0, 1.0)
    jobs = copy.deepcopy(JOBS) + [{"app_id": "d", "scenes": ["D"],
            "function_s": 160, "lifetime_s": 190, "cost_usd": 0.06}]
    cases.append(record("two_of_four_scale_passes", f, jobs, "PASS", "FAIL_OR_INVALID",
                        "Only 50% scale passes, but hardcoded >=2 accepts."))

    f = frames()
    f["A"] = clip(1.0, 9.0)
    f["C"] = clip(2.0, 1.0)
    cases.append(record("disjoint_criterion_passes", f, JOBS, "PASS", "POLICY_CLARIFICATION",
                        "2 scale and 2 orientation passes, but only B passes both; plan gives no orientation 2/3 waiver."))

    f = frames()
    for value in f.values():
        value["floor"] = {"status": "ABSTAIN"}
    cases.append(record("no_floor", f, JOBS, "PASS", "FAIL_OR_INVALID",
                        "Required floor plane is only echoed, never included in verdict."))
    f = frames()
    for value in f.values():
        value["a4_plane_normal"]["angle_to_gravity_deg"] = -999.0
    cases.append(record("negative_angle", f, JOBS, "PASS", "FAIL_OR_INVALID",
                        "An impossible negative angle satisfies angle<=5."))
    f = frames()
    for value in f.values():
        value["a4_plane_normal"]["angle_to_gravity_deg"] = float("-inf")
    cases.append(record("nonfinite_negative_angle", f, JOBS, "PASS", "FAIL_OR_INVALID",
                        "Nonfinite -Infinity also passes; evaluator has no finite check."))

    jobs = copy.deepcopy(JOBS)
    for job in jobs:
        job["function_s"] = job["lifetime_s"] = -60.0
    cases.append(record("negative_gpu_time", frames(), jobs, "PASS", "FAIL_OR_INVALID",
                        "Negative measured durations pass both GPU comparisons."))
    jobs = copy.deepcopy(JOBS)
    jobs[0]["function_s"] = jobs[0]["lifetime_s"] = 240.029
    cases.append(record("rounded_gpu_over_threshold", frames(), jobs, "PASS", "FAIL",
                        "240.029 seconds rounds to 4.000 minutes before threshold comparison."))

    # Boundary controls: the scale formula is dimensionally correct for raw
    # metric predictions, not for an already-rescaled held-out validation.
    for model_length, truth in ((1.09, 1.0), (0.91, 1.0), (1.11, 1.0), (0.89, 1.0)):
        mpu = truth / model_length
        observed_error = gate.evaluate({"A": clip(mpu, 1.0)}, JOBS)["clips"]["A"]["scale_rel_error"]
        assert abs(observed_error - abs(model_length - truth) / truth) < 1e-12

    for ratio in (0.9, 1.1):
        f = {cid: clip(1.0 / ratio, 1.0) for cid in "ABC"}
        cases.append(record(f"inclusive_scale_boundary_{ratio}", f, JOBS, "FAIL", "PASS",
                            "Exactly 10% raw scale error becomes 0.10000000000000009 in binary float."))
    for angle, expected in ((5.0, True), (5.00001, False)):
        assert gate.evaluate({"A": clip(1.0, angle)}, JOBS)["clips"]["A"]["orientation_pass"] == expected
    jobs = copy.deepcopy(JOBS)
    jobs[0]["function_s"] = jobs[0]["lifetime_s"] = 240.0
    assert gate.evaluate(frames(), jobs)["clips"]["A"]["gpu_pass"]

    # A measured angle plus ABSTAIN gravity is correctly rejected, but the
    # reason must not claim a measured threshold exceedance at one degree.
    f = frames()
    f["A"] = clip(1.0, 1.0, gravity="ABSTAIN")
    result = gate.evaluate(f, JOBS)
    failure = next(item for item in result["failures"] if item["clip"] == "A")
    assert failure["kind"] == "measured_above_threshold" and failure["value"] == 1.0
    cases.append({"case": "abstain_gravity_reason", "observed": failure,
                  "required": "ineligible/abstained gravity reason, not angle above threshold"})

    # JSON numbers cannot represent Infinity. Summaries remain strict JSON;
    # full invalid-input results are deliberately not serialized as evidence.
    for case in cases:
        case.pop("result", None)
    output = Path(__file__).with_name("counterexamples.json")
    output.write_text(json.dumps({"synthetic_only": True, "cases": cases}, indent=2,
                                allow_nan=False) + "\n", encoding="utf-8")
    print(f"Confirmed {len(cases)} review cases + scale-formula assertions; synthetic only")
    for case in cases:
        print(case["case"], "observed=", case["observed"], "required=", case["required"])


if __name__ == "__main__":
    main()
