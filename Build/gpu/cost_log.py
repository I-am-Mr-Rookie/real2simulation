"""S06e scene-job receipt: cold start, GPU seconds, estimated vs billed cost (billed only from Modal's own report).

Reconcile after a job (billing is hourly and lags; read-only CLI, existing auth):
    modal billing report --for today -r h --json --show-resources > billing.json
    python Build/gpu/cost_log.py <scene-log.json> <billing.json>
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Modal list rates (modal.com/pricing, read 2026-10-28 in evidence/S06/pre-reset/READINESS.md). Back-solving the
# S06d billed rows (A10G $0.00794449, CPU $0.00068323 @2 cores, Memory $0.00092445 @16 GiB) gives ~26 s each: consistent.
# L4: https://modal.com/pricing (verified 2026-10-30), USD 0.000222 per GPU-second.
RATES = {"A10G": 0.000306, "L4": 0.000222, "CPU": 0.0000131, "Memory": 0.00000222}  # USD per GPU-s / core-s / GiB-s


def cost(seconds, gpu, cpu, mem_gib):
    by = {gpu: seconds * RATES[gpu], "CPU": seconds * cpu * RATES["CPU"], "Memory": seconds * mem_gib * RATES["Memory"]}
    return {"total_usd": round(sum(by.values()), 8), "by_resource_usd": {k: round(v, 8) for k, v in by.items()}}


def scene_log(app_id, call_epoch, return_epoch, remote, gpu, cpu, mem_gib, scaledown_s):
    """Client clock (call/return) vs container clock (remote epochs): separate NTP-synced hosts, small skew possible."""
    for k in ("container_start_epoch", "function_start_epoch", "function_end_epoch", "model_load_s", "inference_s"):
        if not isinstance(remote.get(k), (int, float)):
            raise ValueError(f"remote timing {k!r} missing")
    alive = remote["function_end_epoch"] - remote["container_start_epoch"]
    t = {
        "client_round_trip_s": return_epoch - call_epoch,
        "container_boot_s": remote["container_start_epoch"] - call_epoch,  # call -> our module imported in container
        "cold_start_s": remote["function_start_epoch"] - call_epoch,  # call -> function body runs (platform cold start)
        "model_load_s": remote["model_load_s"],
        "cold_start_to_model_ready_s": remote["function_start_epoch"] - call_epoch + remote["model_load_s"],
        "inference_s": remote["inference_s"],
        "function_s": remote["function_end_epoch"] - remote["function_start_epoch"],
        "container_python_alive_s": alive,
    }
    est_s = alive + scaledown_s  # misses pre-import boot: billed seconds may be a few s higher
    upper_s = t["client_round_trip_s"] + scaledown_s  # includes scheduling/transfer: over-estimate
    return {
        "schema": "s06e-scene-log/1", "app_id": app_id, "gpu": gpu, "cpu_cores": cpu, "memory_gib": mem_gib,
        "timing_s": {k: round(v, 3) for k, v in t.items()},
        "gpu_seconds": {"estimated": round(est_s, 3), "upper_bound": round(upper_s, 3), "billed": None},
        "cost": {"rates_usd_per_s": RATES, "estimated": cost(est_s, gpu, cpu, mem_gib),
                 "upper_bound": cost(upper_s, gpu, cpu, mem_gib),
                 "billed": {"status": "unavailable", "reason": "not yet reconciled (Modal hourly report lags)"}},
    }


def reconcile(log, rows, read_utc):
    """Fill billed cost from Modal's billing rows for this app only; never invent: absent rows stay unavailable."""
    mine = [r for r in rows if r.get("object_id") == log["app_id"]]
    if not mine:
        log["cost"]["billed"] = {"status": "unavailable", "read_utc": read_utc,
                                 "reason": f"no billing rows for {log['app_id']} yet (hourly report lags)"}
        return log
    by = {}
    for r in mine:
        by[r["resource"]] = round(by.get(r["resource"], 0.0) + float(r["cost"]), 8)
    total = round(sum(by.values()), 8)
    log["cost"]["billed"] = {"status": "billed", "read_utc": read_utc,
                             "source": "modal billing report --json --show-resources (read-only)",
                             "note": "report may still be accruing shortly after a job; re-run reconcile, latest read wins",
                             "total_usd": total, "by_resource_usd": by,
                             "estimated_minus_billed_usd": round(log["cost"]["estimated"]["total_usd"] - total, 8)}
    if log["gpu"] in by:
        log["gpu_seconds"]["billed"] = round(by[log["gpu"]] / RATES[log["gpu"]], 3)  # back-solved at list rate
    return log


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: cost_log.py <scene-log.json> <billing.json>")
    p = Path(sys.argv[1])
    raw = Path(sys.argv[2]).read_text(encoding="utf-8-sig")
    rows = json.loads(raw[raw.index("["):])  # tolerate CLI notices before the JSON array
    log = reconcile(json.loads(p.read_text(encoding="utf-8")), rows,
                    datetime.now(timezone.utc).isoformat(timespec="seconds"))
    p.write_text(json.dumps(log, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"gpu_seconds": log["gpu_seconds"], "estimated_usd": log["cost"]["estimated"]["total_usd"],
                      "billed": log["cost"]["billed"]}))
