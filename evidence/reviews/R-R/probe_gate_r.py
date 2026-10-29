"""Repaired-behaviour regressions, synthetic only; never a real Gate R pass.

Supersedes the old defect-expecting probe. Historical counterexamples.json/.txt
remain unchanged. See recheck2/RECHECK2.md for the latest D1/D2 disposition.
Run from the repository root with python -B.
"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Build/reconstruction/spike"))
import gate_r as gate
from test_gate_r import GateR, JOBS, clip, ev, ok3


def main():
    # Reuse the owner's actual-producer integration and F1–F6 regressions.
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(GateR))
    if not result.wasSuccessful():
        raise SystemExit(1)
    for value in (-999.0, float("-inf"), float("inf"), float("nan"), 91.0, True):
        frames = ok3()
        frames["A"]["a4_plane_normal"]["angle_to_gravity_deg"] = value
        with unittest.TestCase().assertRaises(ValueError):
            ev(frames)
    for field in ("function_s", "lifetime_s"):
        for value in (-60.0, float("-inf"), float("inf"), float("nan"), True):
            jobs = copy.deepcopy(JOBS)
            jobs[0][field] = value
            with unittest.TestCase().assertRaises(ValueError):
                ev(ok3(), jobs)
        jobs = copy.deepcopy(JOBS)
        jobs[0][field] = 240.029
        assert not ev(ok3(), jobs)["clips"]["A"]["gpu_pass"]
    for model_length in (1.09, 0.91, 1.11, 0.89):
        frames = ok3()
        frames["A"] = clip(1.0 / model_length, 1.0)
        assert abs(ev(frames)["clips"]["A"]["scale_rel_error"] - abs(model_length - 1)) < 1e-12
    frames = {cid: clip(1.0, 1.0) for cid in gate.COHORT}
    jobs = [{"app_id": "synthetic", "scenes": list(gate.COHORT),
             "function_s": 240.0, "lifetime_s": 720.0, "cost_usd": 0.0}]
    assert gate.evaluate(frames, jobs)["verdict"] == "PASS"
    for ratio in (0.89999999, 1.10000001):
        assert ev({cid: clip(1 / ratio, 1) for cid in "ABC"})["verdict"] == "FAIL"
    with unittest.TestCase().assertRaises(ValueError):
        gate.evaluate(ok3(), JOBS, cohort=("A", "A", "B"))
    print(f"Repaired checks PASS: {result.testsRun} owner regressions + independent numeric/default-cohort assertions; synthetic only")


if __name__ == "__main__":
    main()
