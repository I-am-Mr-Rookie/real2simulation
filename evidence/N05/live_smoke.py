"""N05 live smoke: 3 agent turns + 1 short transcription on the Meta Model API. Keys by name only.

Usage: python evidence/N05/live_smoke.py <wav> [--transcribe-only]   (appends to evidence/N05/live_smoke.json)
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import dotenv_values

sys.path.insert(0, str(Path(__file__).parents[2]))
from Build.agent import core  # noqa: E402

ENV = Path(r"C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.env")
env = dotenv_values(ENV)
os.environ["MODEL_API_KEY"], os.environ["MODEL_API_BASE_URL"] = env["MODEL_API_KEY"], env.get("MODEL_API_BASE_URL") or "https://api.meta.ai/v1"
OUT = Path(__file__).with_name("live_smoke.json")
rows = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
cases = [] if "--transcribe-only" in sys.argv else [
    ("normal", "I want to measure g with a ball I drop. What should I do first?", False),
    ("off_topic", "Write me a short poem about the stock market.", False),
    ("contributor", "What files have I uploaded?", True)]
for name, text, contributor in cases:
    t0 = time.time()
    try:
        out = core.run_turn(text, core.http_post, owner="n05_smoke", contributor=contributor)
        rows.append({"case": name, "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "model": out["model"],
                     "stopped": out["stopped"], "steps": out["steps"], "usage": out["usage"], "reply": out["reply"][:600],
                     "tools": [c["name"] for c in out["tool_calls"]], "seconds": round(time.time() - t0, 1)})
    except Exception as exc:  # record the failure class and HTTP status only
        rows.append({"case": name, "error": type(exc).__name__, "http": getattr(getattr(exc, "response", None), "status_code", None),
                     "body": (getattr(getattr(exc, "response", None), "text", "") or "")[:300]})
if len(sys.argv) > 1:
    try:
        out = core.transcribe(Path(sys.argv[1]).read_bytes(), core.http_post_file)
        rows.append({"case": "transcribe", "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), **out})
    except Exception as exc:
        rows.append({"case": "transcribe", "error": type(exc).__name__, "http": getattr(getattr(exc, "response", None), "status_code", None),
                     "body": (getattr(getattr(exc, "response", None), "text", "") or "")[:300]})
OUT.write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
print(json.dumps(rows[-1], indent=1))

