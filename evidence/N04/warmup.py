"""N04 one-off warm-up proof: red -> yellow -> green -> red on the deployed r2s-ondemand app.

uv run --no-project --python 3.12 --with modal==1.6.3 --with fastapi --env-file .env python evidence/N04/warmup.py
Reserves Modal spend in the daily cap ledger first, settles with an upper-bound estimate (spawn -> red seen).
Idle check: at most twice (scaledown 900 s after the call returns, then +60 s).
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "Build/gpu"))
import modal
from Build.api import gpu
from Build.guardrails import daily_cap
from cost_log import cost

OWNER, LOG = "n04-warmup", []


def observe(note):
    stats = gpu.modal_stats()
    s = gpu.status(OWNER, stats, DB)
    LOG.append({"utc": datetime.now(timezone.utc).isoformat(), "unix": time.time(), "note": note,
                "runners_backlog": stats, **s})
    print(json.dumps(LOG[-1]), flush=True)
    return s["state"]


DB = Path(sys.argv[1]) / "gpu_jobs.sqlite3"
SPEND = Path(sys.argv[1]) / "spend.sqlite3"
rid = daily_cap.reserve("Modal", "0.50", "N04 warm-up A10G reconstruct([]) <=~16 min", path=SPEND)
assert observe("before") == "red", "GPU not asleep before warm-up"
job = gpu.enqueue(OWNER, "reconstruct", DB)
t_spawn = time.time()
call = modal.Function.from_name(gpu.APP_NAME, "reconstruct").spawn([])
seen = set()
while "green" not in seen and time.time() - t_spawn < 300:
    seen.add(observe("starting"))
    time.sleep(1)
gpu.start(job, DB)
result = call.get(timeout=300)
t_ret = time.time()
gpu.finish(job, DB)
observe("returned (warm, idle)")
time.sleep(max(0, t_ret + 905 - time.time()))
state = observe("idle check 1 (905 s)")
if state != "red":
    time.sleep(60)
    state = observe("idle check 2 (965 s)")
t_end = LOG[-1]["unix"]
upper_s = t_end - t_spawn  # spawn -> red observed: over-estimates billed container seconds
est = cost(upper_s, "A10G", 2, 16)
daily_cap.settle(rid, est["total_usd"], path=SPEND)
out = {"label": "MEASURED (Modal stats + job table); cost MODEL-ESTIMATED upper bound, not billed",
       "result": result, "states_seen_in_order": list(dict.fromkeys(e["state"] for e in LOG)),
       "final_state": state, "gpu_seconds_upper": upper_s, "estimated_usd": est,
       "reserved_usd": "0.50", "ledger_today": {k: str(v) for k, v in daily_cap.today(path=SPEND).items()}, "log": LOG}
(ROOT / "evidence/N04/warmup.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
print("DONE", out["states_seen_in_order"], state, upper_s, est["total_usd"])
