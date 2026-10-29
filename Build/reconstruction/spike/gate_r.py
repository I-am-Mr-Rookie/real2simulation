"""Gate R evaluator (plan S05): scale <=10% AND orientation on >=2/3 of the fixed 3-clip cohort, gravity vs A4 normal <=5 deg, GPU <=4 min/scene.

CPU only. Reads existing receipts; never supplies an object size. A criterion with no measurement is a
measured failure of kind "unmeasured" (input missing), never a pass.
"""
import argparse
import json
import math
from datetime import datetime
from pathlib import Path

SCALE_TOL, ANGLE_TOL_DEG, GPU_MIN_PER_SCENE, MIN_SCALE_PASSES = 0.10, 5.0, 4.0, 2
GPU_S = GPU_MIN_PER_SCENE * 60           # R-R F4: compare unrounded seconds
EPS = 1e-12                              # R-R F6: inclusive 10% boundary vs binary-float roundoff only
COHORT = ("RM02", "RM04", "RM05")        # frozen S05c/S05d scene roster; RM05 stays (gravity-ineligible ISS)


def _t(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def gpu_jobs(s05c, orch14_ledger):
    """Per successful GPU job: scenes, function seconds, container lifetime seconds (launch->stopped)."""
    ok = [a for a in orch14_ledger["gpu_attempts"] if a.get("client", "").startswith("OK")]
    jobs = [{"app_id": a["app_id"], "scenes": ["RM02"], "function_s": a["function_elapsed_s"],
             "lifetime_s": (_t(a["app_stopped_utc"]) - _t(a["launch_utc"])).total_seconds(),
             "cost_usd": a["measured_cost_usd"]} for a in ok]
    # client_end_utc bounds the app lifetime from above (Modal reported the app stopped earlier).
    jobs.append({"app_id": s05c["app_id"], "scenes": [k for k, v in s05c["scenes"].items() if "inference_s" in v],
                 "function_s": s05c["function_elapsed_s"],
                 "lifetime_s": (_t(s05c["client_end_utc"]) - _t(s05c["launch_utc"])).total_seconds(),
                 "cost_usd": s05c["measured_cost_usd"]})
    return jobs


def _num(x, what, lo=None, hi=None):
    """Fail closed on malformed producer input (R-R F3): finite numbers within physical bounds, else error."""
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) \
            or (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"invalid {what}: {x!r}")
    return float(x)


def _unique_pairs(pairs):
    """R-R recheck D1: plain json.loads keeps only the last duplicate member; reject before data is lost."""
    keys = [k for k, _ in pairs]
    dup = sorted({k for k in keys if keys.count(k) > 1})
    if dup:
        raise ValueError(f"duplicate JSON members: {dup}")
    return dict(pairs)


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)


def evaluate(frames, jobs, cohort=COHORT):
    """Fixed cohort (R-R F2): every expected clip must be present exactly once, ABSTAIN entries included.

    Policy (conservative, recorded in GATE_R.md): a clip QUALIFIES only if it passes scale AND orientation
    (common cohort); PASS needs >=2/3 qualifying clips and GPU within budget for every clip."""
    if sorted(frames) != sorted(cohort) or len(set(cohort)) != len(cohort):
        raise ValueError(f"cohort mismatch: got {sorted(frames)}, expected {sorted(cohort)}")
    clips, fails = {}, []
    per_scene = {}
    for j in jobs:
        sc = j["scenes"]  # R-R recheck D2: validate membership before amortizing lifetime/cost
        if not isinstance(sc, list) or not sc or len(set(sc)) != len(sc) or not set(sc) <= set(cohort):
            raise ValueError(f"job {j.get('app_id')}: scenes must be nonempty, unique, in cohort; got {sc!r}")
        if set(sc) & set(per_scene):
            raise ValueError(f"job {j.get('app_id')}: conflicting GPU coverage for {sorted(set(sc) & set(per_scene))}")
        n = len(j["scenes"])
        fs, ls = _num(j["function_s"], "function_s", 0), _num(j["lifetime_s"], "lifetime_s", 0)
        for s in j["scenes"]:
            per_scene[s] = {"app_id": j["app_id"], "job_scenes": n, "function_s": fs, "lifetime_s_amortized": ls / n,
                            "function_min_unamortized": round(fs / 60, 3),
                            "lifetime_min_amortized": round(ls / 60 / n, 3),
                            "lifetime_min_unamortized": round(ls / 60, 3),
                            "cost_usd_amortized": round(j["cost_usd"] / n, 5)}
    for cid in cohort:
        r = frames[cid]
        ms, a4, fl, gv = r["metric_scale"], r["a4_plane_normal"], r["floor"], r["gravity"]
        if ms["status"] not in ("calibrated", "ABSTAIN") or a4["status"] not in ("MEASURED", "ABSTAIN") \
                or fl["status"] not in ("FIT", "ABSTAIN") or gv["status"] not in ("estimated", "ABSTAIN"):
            raise ValueError(f"{cid}: unknown status {ms['status']}/{a4['status']}/{fl['status']}/{gv['status']}")
        # R-R F1: producer contract is scene_frame's "calibrated"; raw MapAnything output is metric, so
        # abs(1/mpu-1) = |model_len-true|/true is the RAW model scale error (not held-out post-calibration accuracy).
        scale_err = None
        if ms["status"] == "calibrated":
            scale_err = abs(1 / _num(ms.get("metres_per_model_unit"), f"{cid} metres_per_model_unit", 1e-12) - 1)
        angle = _num(a4.get("angle_to_gravity_deg"), f"{cid} angle", 0, 90) if a4["status"] == "MEASURED" else None
        eligible = fl["status"] == "FIT" and gv["status"] == "estimated"   # R-R F3/F5: floor + gravity prerequisites
        t = per_scene.get(cid)
        c = {"floor": fl["status"], "gravity": gv["status"], "orientation_eligible": eligible,
             "scale_rel_error": scale_err, "scale_pass": scale_err is not None and scale_err <= SCALE_TOL + EPS,
             "a4_angle_deg": angle, "orientation_pass": eligible and angle is not None and angle <= ANGLE_TOL_DEG,
             "gpu": t, "gpu_pass": bool(t) and t["function_s"] <= GPU_S and t["lifetime_s_amortized"] <= GPU_S}
        c["qualifies"] = c["scale_pass"] and c["orientation_pass"]
        if scale_err is None:
            fails.append({"clip": cid, "criterion": "scale<=10%", "kind": "unmeasured",
                          "reason": ms.get("missing_reference") or ms.get("reason")})
        elif not c["scale_pass"]:
            fails.append({"clip": cid, "criterion": "scale<=10%", "kind": "measured_above_threshold",
                          "value": scale_err})
        why = "; ".join(x for x in (None if fl["status"] == "FIT" else "floor " + fl["status"],
                                     None if gv["status"] == "estimated" else "gravity " + gv["status"] + ": "
                                     + str(gv.get("reason")), a4.get("reason")) if x)
        if not eligible:
            fails.append({"clip": cid, "criterion": "gravity_vs_A4<=5deg", "kind": "ineligible", "reason": why,
                          "a4_angle_deg": angle})
        elif angle is None:
            fails.append({"clip": cid, "criterion": "gravity_vs_A4<=5deg", "kind": "unmeasured", "reason": why})
        elif not c["orientation_pass"]:
            fails.append({"clip": cid, "criterion": "gravity_vs_A4<=5deg", "kind": "measured_above_threshold",
                          "value": angle})
        if not c["gpu_pass"]:
            fails.append({"clip": cid, "criterion": "gpu<=4min", "kind": "unmeasured" if not t else
                          "measured_above_threshold", "value": t})
        clips[cid] = c
    n = len(clips)
    summary = {"scale_passes": sum(c["scale_pass"] for c in clips.values()),
               "orientation_passes": sum(c["orientation_pass"] for c in clips.values()),
               "qualifying_clips": sum(c["qualifies"] for c in clips.values()),
               "gpu_passes": sum(c["gpu_pass"] for c in clips.values()), "clips": n}
    ok = summary["qualifying_clips"] >= MIN_SCALE_PASSES and summary["gpu_passes"] == n
    return {"gate": "R", "verdict": "PASS" if ok else "FAIL",
            "thresholds": {"scale_rel": SCALE_TOL, "min_qualifying_clips": MIN_SCALE_PASSES, "cohort": list(cohort),
                           "angle_deg": ANGLE_TOL_DEG, "gpu_min_per_scene": GPU_MIN_PER_SCENE,
                           "policy": "common cohort: a clip counts only if scale AND orientation pass; "
                                     "floor FIT + gravity estimated required for orientation"},
            "summary": summary, "clips": clips, "failures": fails}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default="evidence/S05/S05d/RESULT.json")
    ap.add_argument("--s05c", default="evidence/S05/S05c/RESULT.json")
    ap.add_argument("--orch14", default="evidence/S05/S05b/orch14/job-ledger.json")
    ap.add_argument("out")
    a = ap.parse_args()
    rd = load_json
    frames, s05c = rd(a.frames), rd(a.s05c)
    for cid, r in frames.items():  # input integrity: S05d analysed exactly the S05c/S05b npz
        want = s05c["scenes"][cid]["npz_sha256"]
        assert r["npz_sha256"] == want, (cid, r["npz_sha256"], want)
    res = evaluate(frames, gpu_jobs(s05c, rd(a.orch14)))
    res["inputs"] = {"frames": a.frames, "s05c": a.s05c, "orch14": a.orch14, "npz_hashes_match": True}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    print(res["verdict"], json.dumps(res["summary"]))


if __name__ == "__main__":
    main()
