"""S06h checkpoint: consolidate EXISTING S06/S05 ledgers, scene logs and a read-only Modal billing read into CHECKPOINT.json.
No GPU/Modal job. Run from worktree root: python evidence/S06/S06h/checkpoint.py"""
import json
from pathlib import Path

H = Path("evidence/S06/S06h")
load = lambda p: json.loads(Path(p).read_text(encoding="utf-8-sig"))
month = load(H / "billing-month.json")
billed_by_app = {}
for r in month:
    billed_by_app[r["object_id"]] = round(billed_by_app.get(r["object_id"], 0.0) + float(r["cost"]), 8)

jobs = []
for run in ("S06a", "S06b", "S06d", "S06e", "S06f"):
    led = load(f"evidence/S06/{run}/job-ledger.json")
    for j in led["jobs"]:
        gpu = j.get("gpu") or led.get("gpu_requested") or ("A10G" if "A10G" in j["kind"] else None)
        jobs.append({"task": run, "app_id": j["app_id"], "kind": j["kind"], "gpu": gpu, "rc": j["rc"],
                     "launch_utc": j["launch_utc"], "end_utc": j.get("end_utc") or j.get("app_stopped_utc"),
                     "reservation_usd": led.get("new_all_in_reservation_usd"),
                     "estimated_usd": j.get("estimated_cost_usd"),
                     "ledger_billed_usd": j["measured_cost_usd"],
                     "billed_usd_now": billed_by_app.get(j["app_id"], 0.0)})
        jobs[-1]["ledger_lag_usd"] = round(jobs[-1]["billed_usd_now"] - j["measured_cost_usd"], 8)

scenes = {}
for clip in ("RM02", "RM04"):
    s = load(H / f"{clip}-scene-log.reconciled.json")
    scenes[clip] = {"task": "S06e" if clip == "RM02" else "S06f", "app_id": s["app_id"], "gpu": s["gpu"],
                    "timing_s_measured": s["timing_s"], "gpu_seconds": s["gpu_seconds"],
                    "estimated_usd": s["cost"]["estimated"]["total_usd"],
                    "upper_bound_usd": s["cost"]["upper_bound"]["total_usd"],
                    "billed_usd": s["cost"]["billed"]["total_usd"], "billed_read_utc": s["cost"]["billed"]["read_utc"],
                    "peak_allocated_bytes": s["peak_allocated_bytes"]}

gate = load("evidence/S05/S05f/GATE_R.json")
sam = load("evidence/S06/S06c/gate-default.json")
s06 = round(sum(j["billed_usd_now"] for j in jobs), 8)
total = round(sum(billed_by_app.values()), 8)
out = {
    "schema": "s06h-checkpoint/1",
    "evidence_class": "measured Modal runs on approved licensed public clips + read-only billing; NOT gate/physical/calibrated evidence",
    "billing_read_utc": "2026-10-29T15:49:15Z",
    "billing_source": "modal billing report --for 'this month' --json --show-resources (read-only; hourly/lagging)",
    "modal_month_to_date_billed_usd": total,
    "modal_month_to_date_by_resource_usd": {k: round(sum(float(r["cost"]) for r in month if r["resource"] == k), 8)
                                            for k in sorted({r["resource"] for r in month})},
    "modal_monthly_budget_usd": 30,
    "s06_jobs_billed_usd": s06,
    "jobs": jobs,
    "scenes": scenes,
    "s06d_rm02_function_elapsed_s": load("evidence/S06/S06d/job-ledger.json")["jobs"][0]["function_elapsed_s"],
    "gate_r": {"verdict": gate["verdict"], "summary": gate["summary"],
               "fallback": "Fallback 2 (planes + boxes textured with frames; scale UNVERIFIED)",
               "source": "evidence/S05/S05f/GATE_R.json", "cross_vendor_recheck": "R-R recheck (orch28) PENDING; not CLEAR"},
    # S06c gate-default.json predates the owner access receipt; access reason superseded by evidence/owner/S06/SAM3D-ACCESS.md
    "sam3d": {"backend": sam["backend"], "default": "off", "access": "GRANTED (evidence/owner/S06/SAM3D-ACCESS.md + SAM3D-ACCESS-granted-20261029.png)",
              "reasons_off": ["needs >=32 GB GPU: A10G %d MiB < %d MiB" % (sam["vram_mib_checked"], sam["min_vram_mib"]),
                              "checkpoint bytes/config/revision pin and runtime/output unverified"],
              "s06c_gate_reasons_at_run": sam["reasons"], "min_vram_mib": sam["min_vram_mib"],
              "vram_mib_checked": sam["vram_mib_checked"]},
    "chosen_path": {"reconstruction": "MapAnything facebook/map-anything-apache (Apache-2.0) on Modal A10G, s06d-scene-job entry point",
                    "colliders": "primitive (planes + boxes); SAM 3D Objects off by default (>=32 GB GPU needed, runtime unverified; access granted)",
                    "renderer": "Fallback 2: frame-textured planes + boxes, scale labelled unverified",
                    "aws": "adapter present, refuses without owner gates; no AWS launch (S06g)"},
}
# self-check: billing only accrues (fresh read >= ledger read), scene target met, totals sane
for j in jobs:
    assert j["ledger_lag_usd"] > -1e-6, j["app_id"]
for c, s in scenes.items():
    assert s["timing_s_measured"]["client_round_trip_s"] <= 300, c  # QUEUE S06f target <= 5 min incl. cold start
assert 0 < s06 <= total <= 30
(H / "CHECKPOINT.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
print(json.dumps({"month_to_date": total, "s06_jobs": s06, "jobs": len(jobs)}))
