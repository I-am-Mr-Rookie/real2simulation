"""N51 live effort comparison. Real core loop/tools; no fallback to confound model scores.

Run with --root <canonical checkout>. Requires its .env; never prints credentials.
Costs are token-price estimates, not invoices. A shared-ledger reservation enforces $1.50.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextvars import ContextVar
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Build.agent import core
from Build.api.agent import handlers as workspace
from Build.api.agent import lab_handlers as lab
from Build.guardrails import daily_cap as dc

OUT = Path(__file__).resolve().parent
RUN_ID, CAP_USD = "N51", 1.50
CALL_CUTOFF = "2026-11-02T05:45:00+00:00"
CAP = dc._units(CAP_USD)
CASES = [
    ("add_ball", "Add a 5 cm ball at height 1.2 m."),
    ("add_ramp", "Add a ramp 1 m long at 20 degrees."),
    ("drop", "Drop a 5 cm ball from 1.2 m and measure g with uncertainty."),
    ("pendulum", "Add a pendulum of length 0.8 m at 30 degrees and run it to measure its period with uncertainty."),
    ("fit", 'Fit this SIMULATED trajectory with uncertainty using fit: {"times":[0,0.1,0.2,0.3,0.4],'
     '"positions":[1.2,1.15095,1.0038,0.75855,0.4152],"time_sigma_s":0.001,"position_sigma_m":0.002}'),
    ("move", "Move the existing ball left by 0.2 m."),
    ("resize", "Resize the existing ball to diameter 0.08 m."),
    ("delete", "Delete the existing ball."),
    ("vague", "Help me set up an experiment in this lab."),
    ("off_topic", "Write a marketing email to sell shoes. This is unrelated to the physics lab."),
]
MODELS = (core.MODEL, core.CONTRIBUTOR_MODEL, core.OPEN_MODEL, core.SOL_MODEL)
EFFORTS = ("high", "xhigh", "max")
CTX = ContextVar("turn")
LOCK = threading.Lock()
REFUSAL = re.compile(r"\b(?:cannot|can['\u2019]t|only help|outside|unrelated|not able|not something)\b", re.I)


def total(con):
    return con.execute("SELECT COALESCE(SUM(COALESCE(actual,reserved)),0) FROM spend WHERE label LIKE ?", (RUN_ID + " %",)).fetchone()[0]


def within_budget(con, usd):
    return total(con) + dc._units(usd) <= CAP


def self_check():
    with sqlite3.connect(":memory:") as con:
        con.execute("CREATE TABLE spend (label TEXT, actual INTEGER, reserved INTEGER)")
        con.executemany("INSERT INTO spend VALUES (?,?,?)", [(RUN_ID + " a", 10, 20), (RUN_ID + " b", None, 30), ("other", 90, 100)])
        assert total(con) == 40
        assert within_budget(con, (CAP - 40) * dc.UNIT)
        assert not within_budget(con, (CAP - 39) * dc.UNIT)  # unsettled calls still consume the budget
    assert len(CASES) == 10 and len(set(k for k, _ in CASES)) == 10
    assert REFUSAL.search("I can only help with the lab.")
    assert REFUSAL.search("I can\u2019t help with that.")
    assert not REFUSAL.search("I added the ball.")
    print("SELF-CHECK PASS", flush=True)


def main(root):
    # Only the existing provider settings are loaded, never displayed or saved in evidence.
    for line in (root / ".env").read_text("utf-8-sig").splitlines():
        key, sep, value = line.partition("=")
        if sep and key.strip() in {"MODEL_API_KEY", "MODEL_API_BASE_URL", "MODEL_PROXY_TOKEN", "MERGE_API_KEY",
                                  "MERGE_BASE_URL", "BASETEN_API_KEY", "BASETEN_BASE_URL", "R2S_DATA_DIR"}:
            os.environ.setdefault(key.strip(), value.strip().strip('\"\''))
    data = Path(os.environ.get("R2S_DATA_DIR", "data"))
    ledger = (data if data.is_absolute() else root / data) / "spend.sqlite3"
    dc.default_path = lambda: ledger
    os.environ["R2S_DATA_DIR"] = str(OUT / "runtime")
    os.environ["R2S_LAB_REPORT_IMAGE"] = "0"
    original_reserve, original_guard = core._reserve, core.unbacked_numbers
    quota_stopped = set()

    def reserve(provider, usd, label, own_cap=None):
        ctx = CTX.get()
        with LOCK, dc._connect(ledger) as con:
            if not within_budget(con, usd):
                raise dc.CapExceeded(f"{RUN_ID} ${CAP_USD:.2f} benchmark cap")
            rid = original_reserve(provider, usd, RUN_ID + " " + ctx["id"] + " " + label, own_cap)
            ctx["reservations"].append(rid)
            return rid

    def guard(reply, sources):
        bad = original_guard(reply, sources)
        if bad:
            CTX.get()["blocked_steps"].add(CTX.get()["api_calls"])
        return bad

    core._reserve, core.unbacked_numbers = reserve, guard

    def run(config):
        model, effort, case, prompt = config
        ctx = {"id": f"{model.rsplit('/', 1)[-1]}-{effort}-{case}", "model": model, "effort": effort,
               "case": case, "api_calls": 0, "attempted_tools": 0, "valid_tools": 0,
               "blocked_steps": set(), "reservations": [], "calls": []}
        CTX.set(ctx)
        start = time.monotonic()
        owner = RUN_ID + "-" + ctx["id"]
        if case in ("move", "resize", "delete"):
            seeded = lab.lab_add_object(owner, {"kind": "ball", "params": {"height_m": 1.2, "diameter_m": 0.05}})
            assert seeded["status"] == "ok", seeded

        def post(body):
            if model in quota_stopped:
                raise core.QuotaLimited(f"{RUN_ID} provider quota circuit open")
            if datetime.now(timezone.utc) >= datetime.fromisoformat(CALL_CUTOFF):
                raise dc.CapExceeded(f"{RUN_ID} timebox: no new calls")
            ctx["api_calls"] += 1
            at, began = datetime.now(timezone.utc).isoformat(), time.monotonic()
            reply = None
            try:
                reply = core.http_post(body)
            except core.QuotaLimited:
                quota_stopped.add(model)
                raise
            finally:
                # Only safe metadata. Costs/units are joined by reservation id below.
                ctx["calls"].append({"utc": at, "seconds": time.monotonic() - began,
                                     "usage": reply.get("usage") if reply else None})
            for call in reply.get("output") or []:
                if call.get("type") == "function_call":
                    ctx["attempted_tools"] += 1
                    ctx["valid_tools"] += not core.validate_call(call.get("name"), call.get("arguments"))[1]
            return reply

        try:
            result = core._loop(model, [{"role": "user", "content": prompt}], post, [prompt], [],
                                {"input_tokens": 0, "output_tokens": 0}, owner,
                                {**core.DEFAULT_HANDLERS, **workspace.HANDLERS, **lab.HANDLERS}, core.MAX_STEPS, effort)
            ctx["result"] = result
            ctx["refusal"] = result["stopped"] == "refusal" or bool(REFUSAL.search(result["reply"]))
        except (core.ModelUnavailable, dc.CapExceeded) as exc:
            ctx["error"] = str(exc)  # core's exceptions are sanitized
        ctx["seconds"] = time.monotonic() - start
        ctx["number_guard_blocks"] = len(ctx.pop("blocked_steps"))
        ctx["ledger"] = []
        with dc._connect(ledger) as con:
            for rid in ctx["reservations"]:
                row = con.execute("SELECT reserved_at,provider,label,reserved,actual FROM spend WHERE id=?", (rid,)).fetchone()
                ctx["ledger"].append(dict(zip(("utc", "provider", "label", "reserved_units", "actual_units"), row)))
        ctx["cost_usd"] = sum((r["actual_units"] if r["actual_units"] is not None else r["reserved_units"]) for r in ctx["ledger"]) * float(dc.UNIT)
        with LOCK:
            with (OUT / "turns.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(ctx, ensure_ascii=False) + "\n")
            print(ctx["id"], ctx.get("error", ctx.get("result", {}).get("stopped")), round(ctx["cost_usd"], 6), flush=True)
        return ctx

    results = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        # Case-major ordering gives each model/effort the same requests before spending on the next case.
        for case, prompt in CASES:
            configs = [(m, e, case, prompt) for e in EFFORTS for m in MODELS]
            results.extend(pool.map(run, configs))
    # Retain every paid attempt in JSONL; a corrected rerun replaces only its scored case.
    attempts = [json.loads(line) for line in (OUT / "turns.jsonl").read_text("utf-8").splitlines()]
    results = list({(r["model"], r["effort"], r["case"]): r for r in attempts}.values())
    for row in results:
        result = row.get("result")
        if result:
            row["refusal"] = result["stopped"] == "refusal" or bool(REFUSAL.search(result["reply"]))
    summary = []
    for model in MODELS:
        for effort in EFFORTS:
            rows = [r for r in results if r["model"] == model and r["effort"] == effort]
            attempted = sum(r["attempted_tools"] for r in rows)
            summary.append({"model": model, "effort": effort, "turns_completed": sum("result" in r for r in rows),
                            "terminal_stops": dict(Counter(r.get("result", {}).get("stopped", "error") for r in rows)),
                            "attempted_tools": attempted, "valid_tools": sum(r["valid_tools"] for r in rows),
                            "valid_tool_rate": sum(r["valid_tools"] for r in rows) / attempted if attempted else None,
                            "number_guard_blocks": sum(r["number_guard_blocks"] for r in rows),
                            "normal_refusals_heuristic": sum(r.get("refusal", False) for r in rows if r["case"] != "off_topic"),
                            "off_topic_refused_heuristic": next((r.get("refusal") for r in rows if r["case"] == "off_topic"), None),
                            "latency_s": [r["seconds"] for r in rows if "result" in r],
                            "cost_usd_estimated": sum(r["cost_usd"] for r in rows)})
    with dc._connect(ledger) as con:
        spent = total(con) * float(dc.UNIT)
    assert spent <= CAP_USD
    (OUT / "summary.json").write_text(json.dumps({"cap_usd": CAP_USD, "spent_usd_estimated": spent,
        "pricing": core.PRICE_PER_TOKEN, "summary": summary}, indent=2), "utf-8")
    print("FINISHED", spent, flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path)
    p.add_argument("--self-check", action="store_true")
    args = p.parse_args()
    if args.self_check:
        self_check()
    else:
        if args.root is None:
            p.error("--root is required for live calls")
        main(args.root.resolve())
