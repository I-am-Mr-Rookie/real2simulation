"""N04 global daily spend cap: SQLite ledger of every paid Meta Model API or Modal call.

reserve() before the call, settle() after with the actual cost. One BEGIN IMMEDIATE transaction per write, so
concurrent reservers serialize. Day = Dhaka calendar day at reservation time. Unsettled rows count at their
reservation; settled rows at their actual cost (a lower settle frees headroom, a higher one is still recorded).
"""
import os
import sqlite3
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from Build.guardrails.accounting import usd

DHAKA = timezone(timedelta(hours=6))
CAP_USD, JUDGING_CAP_USD = Decimal("10"), Decimal("20")
JUDGING = (date(2026, 11, 5), date(2026, 11, 8))  # inclusive, Dhaka dates
PROVIDERS = {"Meta Model API", "Modal"}
UNIT = Decimal("0.00000001")  # amounts stored as integer 1e-8 USD so SQL sums stay exact


class CapExceeded(RuntimeError):
    pass


def dhaka_day(now=None):
    return (now or datetime.now(timezone.utc)).astimezone(DHAKA).date()


def cap_for(day):
    return JUDGING_CAP_USD if JUDGING[0] <= day <= JUDGING[1] else CAP_USD


def default_path():
    return Path(os.environ.get("R2S_DATA_DIR", "data")) / "spend.sqlite3"


def _units(value):
    return int(usd(value) / UNIT)


def _connect(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=30, isolation_level=None)
    con.execute("CREATE TABLE IF NOT EXISTS spend (id TEXT PRIMARY KEY, day TEXT NOT NULL, provider TEXT NOT NULL,"
                " label TEXT NOT NULL, reserved INTEGER NOT NULL, actual INTEGER, reserved_at TEXT NOT NULL,"
                " settled_at TEXT)")
    return con


def _spent(con, day):
    return con.execute("SELECT COALESCE(SUM(COALESCE(actual, reserved)), 0) FROM spend WHERE day = ?",
                       (day.isoformat(),)).fetchone()[0]


def reserve(provider, est_usd, label="", path=None, now=None):
    """Return a reservation id, or raise CapExceeded if today's total + est_usd would exceed today's cap."""
    if provider not in PROVIDERS:
        raise ValueError("provider must be 'Meta Model API' or 'Modal'")
    amount = _units(est_usd)
    now = now or datetime.now(timezone.utc)
    day = dhaka_day(now)
    con = _connect(path or default_path())
    try:
        con.execute("BEGIN IMMEDIATE")
        total = _spent(con, day)
        if total + amount > int(cap_for(day) / UNIT):
            con.execute("ROLLBACK")
            raise CapExceeded(f"daily cap {cap_for(day)} USD for {day} (Dhaka): spent/reserved "
                              f"{Decimal(total) * UNIT}, request {Decimal(amount) * UNIT}")
        rid = uuid.uuid4().hex
        con.execute("INSERT INTO spend VALUES (?, ?, ?, ?, ?, NULL, ?, NULL)",
                    (rid, day.isoformat(), provider, str(label)[:200], amount, now.isoformat()))
        con.execute("COMMIT")
        return rid
    finally:
        con.close()


def settle(reservation_id, actual_usd, path=None, now=None):
    """Record the actual cost once (0 for a call that never ran). Raises on unknown or already settled ids."""
    amount = _units(actual_usd)
    con = _connect(path or default_path())
    try:
        con.execute("BEGIN IMMEDIATE")
        cur = con.execute("UPDATE spend SET actual = ?, settled_at = ? WHERE id = ? AND actual IS NULL",
                          (amount, (now or datetime.now(timezone.utc)).isoformat(), reservation_id))
        if cur.rowcount != 1:
            con.execute("ROLLBACK")
            raise ValueError("unknown or already settled reservation")
        con.execute("COMMIT")
    finally:
        con.close()


def today(path=None, now=None):
    """Read-only summary: {day, cap_usd, spent_usd, headroom_usd} (Decimal amounts)."""
    day = dhaka_day(now)
    con = _connect(path or default_path())
    try:
        spent = Decimal(_spent(con, day)) * UNIT
    finally:
        con.close()
    return {"day": day.isoformat(), "cap_usd": cap_for(day), "spent_usd": spent,
            "headroom_usd": max(Decimal(0), cap_for(day) - spent)}
