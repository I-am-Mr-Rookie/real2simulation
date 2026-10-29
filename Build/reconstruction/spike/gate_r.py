"""Gate R evaluator (plan S05): scale <=10% on >=2/3 clips, gravity vs A4 normal <=5 deg, GPU <=4 min/scene.

CPU only. Reads existing receipts; never supplies an object size. A criterion with no measurement is a
measured failure of kind "unmeasured" (input missing), never a pass.
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

SCALE_TOL, ANGLE_TOL_DEG, GPU_MIN_PER_SCENE, MIN_SCALE_PASSES = 0.10, 5.0, 4.0, 2


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


def evaluate(frames, jobs):
    clips, fails = {}, []
    per_scene = {}
    for j in jobs:
        n = len(j["scenes"])
        for s in j["scenes"]:
            per_scene[s] = {"app_id": j["app_id"], "job_scenes": n,
                            "function_min_unamortized": round(j["function_s"] / 60, 3),
                            "lifetime_min_amortized": round(j["lifetime_s"] / 60 / n, 3),
                            "lifetime_min_unamortized": round(j["lifetime_s"] / 60, 3),
                            "cost_usd_amortized": round(j["cost_usd"] / n, 5)}
    for cid, r in frames.items():
        ms, a4, fl = r["metric_scale"], r["a4_plane_normal"], r["floor"]
        mpu = ms.get("metres_per_model_unit")
        scale_err = None if ms["status"] != "FIT" or not mpu else abs(1 / mpu - 1)  # MapAnything output is metric
        angle = a4.get("angle_to_gravity_deg") if a4["status"] == "MEASURED" else None
        t = per_scene.get(cid)
        c = {"floor": fl["status"], "gravity": r["gravity"]["status"],
             "scale_rel_error": scale_err, "scale_pass": scale_err is not None and scale_err <= SCALE_TOL,
             "a4_angle_deg": angle, "orientation_pass": angle is not None and angle <= ANGLE_TOL_DEG
             and r["gravity"]["status"] == "estimated",
             "gpu": t, "gpu_pass": bool(t) and t["function_min_unamortized"] <= GPU_MIN_PER_SCENE
             and t["lifetime_min_amortized"] <= GPU_MIN_PER_SCENE}
        if scale_err is None:
            fails.append({"clip": cid, "criterion": "scale<=10%", "kind": "unmeasured",
                          "reason": ms.get("missing_reference") or ms.get("reason")})
        elif not c["scale_pass"]:
            fails.append({"clip": cid, "criterion": "scale<=10%", "kind": "measured_above_threshold",
                          "value": scale_err})
        if angle is None:
            fails.append({"clip": cid, "criterion": "gravity_vs_A4<=5deg", "kind": "unmeasured",
                          "reason": "; ".join(x for x in (a4.get("reason"), r["gravity"].get("reason"),
                                                          None if fl["status"] == "FIT" else "floor " + fl["status"]) if x)})
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
               "gpu_passes": sum(c["gpu_pass"] for c in clips.values()), "clips": n}
    ok = (summary["scale_passes"] >= MIN_SCALE_PASSES and summary["orientation_passes"] >= MIN_SCALE_PASSES
          and summary["gpu_passes"] == n)
    return {"gate": "R", "verdict": "PASS" if ok else "FAIL",
            "thresholds": {"scale_rel": SCALE_TOL, "min_scale_passes": MIN_SCALE_PASSES,
                           "angle_deg": ANGLE_TOL_DEG, "gpu_min_per_scene": GPU_MIN_PER_SCENE},
            "summary": summary, "clips": clips, "failures": fails}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default="evidence/S05/S05d/RESULT.json")
    ap.add_argument("--s05c", default="evidence/S05/S05c/RESULT.json")
    ap.add_argument("--orch14", default="evidence/S05/S05b/orch14/job-ledger.json")
    ap.add_argument("out")
    a = ap.parse_args()
    rd = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))
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
