"""After stopping ONLY the old smoke client, ledger its bounded possible future work and record missing telemetry.

Does not cancel, stop, deploy, or invoke a Modal function. Controller owns watching the still-pending input.
"""
import json
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import modal
from Build.guardrails import daily_cap
from Build.reconstruction import live_room

OUT = Path(__file__).resolve().parent
DATA = OUT / "runtime"
status = json.loads((DATA / "status.json").read_text(encoding="utf-8"))
assert status["state"] == "reconstructing", "Do not close out a completed smoke"
with sqlite3.connect(DATA / "spend.sqlite3") as con:
    con.row_factory = sqlite3.Row
    rows = [dict(row) for row in con.execute("SELECT * FROM spend")]
assert len(rows) == 1 and rows[0]["actual"] is None
row = rows[0]
# The queued input can still run later: reserve its FULL configured 240s startup + 300s execution + 900s idle.
# Queue wait itself has no GPU container. Do not treat the missing result as proof of zero GPU cost.
bound = live_room.cost(240 + 300 + 900, "L4", 2, 16)["total_usd"]
assert bound <= 0.50
daily_cap.settle(row["id"], bound, path=DATA / "spend.sqlite3")
stats = modal.Function.from_name("r2s-ondemand", "reconstruct").get_current_stats()
result = {"run": "N30-orch275", "state": "PARTIAL", "completed_at": datetime.now(timezone.utc).isoformat(),
          "started_at": row["reserved_at"], "wall_s": round(time.time() - datetime.fromisoformat(row["reserved_at"]).timestamp(), 3),
          "source": {"clip": "RM02", "license": "Pexels", "url":
                     "https://www.pexels.com/video/tracking-shot-of-empty-classroom-6671552/"},
          "app": "r2s-ondemand", "requested_gpu": "L4", "gpu": None, "gpu_name": None,
          "peak_allocated_bytes": None, "gpu_wall_s": None, "estimated_usd": bound, "budget_usd": 0.50,
          "ledger": "evidence/N30/runtime/spend.sqlite3 via daily_cap (local; not committed)",
          "reservation_id": row["id"], "reserved_usd": row["reserved"] / 1e8,
          "ledger_settled_upper_bound_usd": bound,
          "ledger_today": {k: str(v) for k, v in daily_cap.today(path=DATA / "spend.sqlite3").items()},
          "modal_stats": {"backlog": stats.backlog, "runners": stats.num_total_runners,
                          "running_inputs": stats.num_running_inputs},
          "paid_test_jobs_submitted": 1, "observed_gpu_executions": None,
          "client_stopped_at_cutoff": True, "remote_cancelled": False,
          "capacity_evidence": "Modal system log: waiting to be scheduled on a GPU_L4 worker; acquiring more capacity",
          "labels": {"cost": "MODEL-ESTIMATED full timeout envelope, NOT billed",
                     "telemetry": "NOT MEASURED: no result returned", "scale": "scale unverified"},
          "limitations": ["Old smoke used blocking remote before start-budget fix; no second smoke submitted",
                          "FunctionCallList API returned UnimplementedError; exact remote call could not be cancelled",
                          "Controller must watch remaining Modal backlog; this input may execute later",
                          "Local cap ledger is not an aggregated provider billing total"]}
live_room.set_status(DATA, state="failed", code="CAPACITY_PENDING_AT_CUTOFF", estimated_usd=bound,
                     error="Local smoke client stopped; remote input may still execute. Controller is watching.")
(OUT / "run.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result), flush=True)
