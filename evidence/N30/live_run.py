"""ONE paid RM02 smoke via live_room.run_job; no paid retry under the USD 0.50 smoke limit.

uv run --python 3.12 --with modal==1.6.3 --with numpy==2.2.6 --with fastapi==0.124.4
  --with jsonschema==4.23.0 --with python-multipart==0.0.20 --env-file ../../.env python evidence/N30/live_run.py
Raw reconstruction and SQLite remain local in runtime/. run.json contains measured telemetry and estimated cost.
"""
import json
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Build.guardrails import daily_cap
from Build.reconstruction import live_room

OUT = Path(__file__).resolve().parent
DATA = OUT / "runtime"
VIDEO = ROOT.parents[1] / "test-data/public/RM02.mp4"
assert VIDEO.is_file(), "RM02 source missing"
assert live_room.GPU == "L4" and live_room.ESTIMATE_USD <= 0.50
assert not (OUT / "run.json").exists() and not (DATA / "spend.sqlite3").exists(), "Smoke already attempted"
DATA.mkdir(exist_ok=True)
started = datetime.now(timezone.utc).isoformat()
calls, failure = [], None


def one_paid_call(frames):
    global failure
    assert not calls, "At most one paid call"
    calls.append({"utc": datetime.now(timezone.utc).isoformat(), "frames": len(frames), "gpu": "L4"})
    try:
        return live_room.modal_reconstruct(frames)
    except Exception as error:
        failure = {"type": type(error).__name__, "message": str(error)[:300]}
        # shortcut: this smoke stops on failure, test the A10G retry offline to stay within USD 0.50.
        raise RuntimeError("N30 single-attempt smoke budget stop") from None


t0 = time.time()
live_room.run_job(DATA, VIDEO, 17.75, "n30-rm02", remote=one_paid_call,
                  gpu_db=DATA / "gpu_jobs.sqlite3", cap_db=DATA / "spend.sqlite3")
status = json.loads((DATA / "status.json").read_text(encoding="utf-8"))
with sqlite3.connect(DATA / "spend.sqlite3") as con:
    con.row_factory = sqlite3.Row
    rows = [dict(row) for row in con.execute("SELECT * FROM spend")]
for row in rows:
    row["reserved_usd"] = row.pop("reserved") / 1e8
    row["estimated_usd"] = row.pop("actual") / 1e8 if row["actual"] is not None else None
result = {"run": "N30-orch275", "state": status["state"], "started_at": started,
          "completed_at": datetime.now(timezone.utc).isoformat(), "wall_s": round(time.time() - t0, 3),
          "source": {"clip": "RM02", "license": "Pexels", "url":
                     "https://www.pexels.com/video/tracking-shot-of-empty-classroom-6671552/"},
          "app": "r2s-ondemand", "gpu": status.get("gpu"), "gpu_name": status.get("gpu_name"),
          "peak_allocated_bytes": status.get("peak_allocated_bytes"), "timing_s": status.get("timing_s"),
          "estimated_usd": status.get("estimated_usd"), "attempts": status.get("gpu_attempts"),
          "budget_usd": 0.50, "paid_calls": calls, "ledger_rows": rows,
          "ledger": "evidence/N30/runtime/spend.sqlite3 via Build/guardrails/daily_cap.py (local, not committed)",
          "daily_cap": {k: str(v) for k, v in daily_cap.today(path=DATA / "spend.sqlite3").items()},
          "failure": failure, "status_error": status.get("error"),
          "labels": {"telemetry": "MEASURED", "cost": "MODEL-ESTIMATED upper bound including 900 s idle, not billed",
                     "geometry": "MODEL-ESTIMATED", "scale": status.get("scale", "scale unverified")},
          "limitations": ["A10G retry tested offline only; paid smoke permits one invocation",
                          "Local daily_cap ledger, not a combined live-service/provider billing total",
                          "Cost is list-rate estimate; billing not reconciled; scale is unverified"]}
(OUT / "run.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result), flush=True)
assert status["state"] == "done", status.get("error")
assert result["gpu"] == "L4" and result["peak_allocated_bytes"] > 0
assert len(rows) == len(calls) == 1 and 0 < result["estimated_usd"] <= 0.50
