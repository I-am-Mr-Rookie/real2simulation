"""N12 live agent run: two demo prompts through Muse Spark + the N12 lab tools. Costs reserved/settled in daily_cap.

Run: uv run --no-project --with-requirements Build/api/health/requirements.txt --with python-dotenv python evidence/N12/live_run.py
Key by NAME only (MODEL_API_KEY, MODEL_API_BASE_URL from the canonical .env); never printed or stored.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from dotenv import dotenv_values  # noqa: E402

from Build.agent import core  # noqa: E402
from Build.agent.record_muse import ENV, IN_USD, OUT_USD  # noqa: E402  (N05 list-price x1.5 constants)
from Build.api.agent import lab_handlers as h  # noqa: E402
from Build.guardrails import daily_cap  # noqa: E402

PROMPTS = {"ball": "Drop a 5 cm ball from 1.2 m and measure g", "pendulum": "Pendulum, 0.8 m, find the period"}
CONTEXT = "In the virtual lab editor (SIMULATED): "  # same prefix as Build/web/src/lab-editor/AgentPanel.jsx CONTEXT
WORST_USD = 0.5  # 6 steps x (<=8k in + 1.2k out) tokens at the margin prices
OUT = Path(__file__).resolve().parent


def main() -> None:
    # Evidence-only: --max-output-tokens N overrides core's 1200 cap to test whether reasoning exhausts it (not product code).
    cap = int(sys.argv[sys.argv.index("--max-output-tokens") + 1]) if "--max-output-tokens" in sys.argv else None
    post = (lambda body: core.http_post({**body, "max_output_tokens": cap})) if cap else core.http_post
    worst = WORST_USD * (cap or 1200) / 1200
    env = dotenv_values(ENV)
    for k in ("MODEL_API_KEY", "MODEL_API_BASE_URL"):
        if env.get(k):
            os.environ[k] = env[k]
    ledger = daily_cap.default_path()  # pin the spend ledger before R2S_DATA_DIR moves to the throwaway lab dir
    os.environ["R2S_DATA_DIR"] = tempfile.mkdtemp(prefix="n12-live-")
    log = []
    for name, prompt in PROMPTS.items():
        owner, history = f"n12-live-{name}", []
        queue = [CONTEXT + prompt, CONTEXT + "Write the lab report."]  # second turn = the panel's Write report button
        while queue and len(history) < 8:
            text = queue.pop(0)
            rid = daily_cap.reserve("Meta Model API", worst, f"N12 live lab run {name}", path=ledger)
            at = datetime.now(timezone.utc).isoformat(timespec="seconds")
            try:
                res = core.run_turn(text, post, owner=owner, history=history, handlers=h.HANDLERS)
                u = res["usage"]
                cost = u["input_tokens"] * IN_USD + u["output_tokens"] * OUT_USD
            except Exception as exc:  # settle worst case: the call may have billed
                daily_cap.settle(rid, worst, path=ledger)
                log.append({"utc": at, "prompt": text, "error": type(exc).__name__, "est_usd": worst})
                break
            daily_cap.settle(rid, round(cost, 6), path=ledger)
            log.append({"utc": at, "prompt": text, "model": res["model"], "stopped": res["stopped"], "steps": res["steps"],
                        "reply": res["reply"], "usage": u, "est_usd": round(cost, 6),
                        "tool_calls": [{"name": c["name"], "args": c["args"], "output": c["output"]} for c in res["tool_calls"]]})
            if res["stopped"] != "ask_user":
                history += [{"role": "user", "content": text}, {"role": "assistant", "content": res["reply"]}]
                continue
            history += [{"role": "user", "content": text}, {"role": "assistant", "content": res["reply"]}]
            queue.insert(0, CONTEXT + next(o["label"] for o in res["question"]["options"] if o["recommended"]))
        report = h._dir(owner) / "report.md"
        if report.exists():
            (OUT / f"report-{name}.md").write_text(report.read_text("utf-8"), "utf-8")
    total = round(sum(x["est_usd"] for x in log), 6)
    (OUT / "live_run.json").write_text(json.dumps({"max_output_tokens": cap or core.MAX_OUTPUT_TOKENS, "turns": log, "total_est_usd": total,
                                                  "pricing": "N05 list price x1.5 margin, not billing"}, indent=2), "utf-8")
    for x in log:
        print(x["utc"], x.get("model"), x.get("stopped"), [c["name"] for c in x.get("tool_calls", [])], x.get("usage"), x["est_usd"])
    print("total_est_usd", total)


if __name__ == "__main__":
    main()
