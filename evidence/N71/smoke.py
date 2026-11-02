"""One live Wonder picker-tier smoke turn, at most three calls and $0.50 reserved; no tools or GPU."""
import json
import os
from pathlib import Path

from dotenv import dotenv_values

from Build.agent import core
from Build.guardrails import daily_cap as dc

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT.parent.parent
OUT = Path(__file__).resolve().parent


def main():
    env = dotenv_values(CANONICAL / ".env")
    for name in ("MODEL_API_KEY", "MODEL_API_BASE_URL", "MODEL_PROXY_TOKEN"):
        if env.get(name):
            os.environ.setdefault(name, env[name])
    data = Path(os.environ.get("R2S_DATA_DIR", env.get("R2S_DATA_DIR") or "data"))
    ledger = (data if data.is_absolute() else CANONICAL / data) / "spend.sqlite3"
    dc.default_path = lambda: ledger
    original = core._reserve
    reservations, estimates = [], []

    def reserve(provider, estimate, label, own_cap=None):
        assert provider == "Meta Model API" and label == core.WONDER_MODEL
        assert len(reservations) < 3 and sum(estimates) + estimate <= 0.50
        rid = original(provider, estimate, "N71 smoke " + label, own_cap)
        reservations.append(rid)
        estimates.append(estimate)
        return rid

    def post(body):
        assert body["model"] == core.WONDER_MODEL  # never spend on a hidden fallback during this smoke
        return core.http_post(body)

    core._reserve = reserve
    result = None
    try:
        result = core.run_turn("I want to film a phone physics experiment. Ask me which experiment I want to film.",
                               post, tier="wonder", owner="n71-smoke", max_steps=1)
    finally:
        core._reserve = original
        with dc._connect(ledger) as con:
            rows = [con.execute("SELECT reserved_at,provider,label,reserved,actual FROM spend WHERE id=?",
                                (rid,)).fetchone() for rid in reservations]
        costs = [dict(zip(("utc", "provider", "label", "reserved_units", "actual_units"), row)) for row in rows]
        summary = {"calls": len(rows), "usd_per_unit": str(dc.UNIT), "ledger": costs,
                   "cost_usd": str(sum((r[4] if r[4] is not None else r[3]) for r in rows) * dc.UNIT),
                   "model": result.get("model") if result else None,
                   "stopped": result.get("stopped") if result else None,
                   "usage": result.get("usage") if result else None}
        (OUT / "live-smoke.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary))
    assert result["model"] == core.WONDER_MODEL and result["stopped"] in ("final", "ask_user", "refusal")
    assert not result.get("answered_by") and len(rows) <= 3


if __name__ == "__main__":
    main()
