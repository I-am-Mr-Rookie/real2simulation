"""Fail-closed reconstruction preflight; caller must serialize check + durable reserve.

Only new paid work calls this guard. Public library reads never call it.
No ledger discovery, reservation writes, provider switching or cloud calls occur here.
"""
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from Build.guardrails.accounting import headroom_usd, liability_usd, meta_snapshot, usd

MODAL_CAP_USD = Decimal("30")
MODAL_FLOOR_USD = Decimal("5")
MAX_SNAPSHOT_AGE = timedelta(minutes=5)


class ReconstructionPaused(Exception):
    code = "SPEND_PAUSED"
    retryable = False


def _unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate snapshot field")
        result[key] = value
    return result


def _provider(state, name):
    provider = state[name]
    if not isinstance(provider, dict) or not isinstance(provider["requests"], list):
        raise ValueError("Invalid provider snapshot")
    seen = set()
    for row in provider["requests"]:
        key = row["request_id"]
        if (not isinstance(key, str) or not key.strip() or key in seen
                or row["provider"] != name):
            raise ValueError("Invalid or duplicate request identity")
        seen.add(key)
        if row.get("settled") is True and not (
                isinstance(row.get("reconciliation_ref"), str) and row["reconciliation_ref"].strip()):
            raise ValueError("Final billing requires reconciliation evidence")
    return provider


def require_reconstruction(state_path, *, candidate_modal_usd, candidate_meta_usd=0, now=None):
    """Return accounting or raise nonretryable SPEND_PAUSED; never default unknown to zero.

    Snapshot is server-owned, complete, disjoint and freshly reconciled (see ADMISSION.md).
    credit_headroom_usd is verified credit NET of outstanding liabilities, not an allocation.
    shortcut: preflight only, wire inside the caller's global check/reserve transaction before live use.
    """
    try:
        state = json.loads(Path(state_path).read_text(encoding="utf-8"),
                           object_pairs_hook=_unique_fields, parse_float=Decimal)
        allowed = {"schema", "as_of", "paused", "coverage_verified", "credit_verified",
                   "sources", "Meta Model API", "Modal", "AWS"}
        if not isinstance(state, dict) or set(state) - allowed:
            raise ValueError("Unknown snapshot fields")
        clock = now if now is not None else datetime.now(timezone.utc)
        as_of = datetime.fromisoformat(state["as_of"])
        if (state["schema"] != "reconstruction-admission/1" or state["paused"] is not False
                or state["coverage_verified"] is not True or state["credit_verified"] is not True
                or clock.utcoffset() is None or as_of.utcoffset() is None
                or not timedelta(0) <= clock - as_of <= MAX_SNAPSHOT_AGE):
            raise ValueError("Unverified, paused or stale snapshot")
        sources = state["sources"]
        if (not isinstance(sources, list) or not sources
                or any(not isinstance(s, str) or not s.strip() for s in sources)
                or len(sources) != len(set(sources))):
            raise ValueError("Complete source inventory required")
        meta = _provider(state, "Meta Model API")
        modal = _provider(state, "Modal")
        meta_candidate, modal_candidate = usd(candidate_meta_usd), usd(candidate_modal_usd)
        if modal_candidate <= 0:
            raise ValueError("New reconstruction requires a positive all-in bound")
        accounting = meta_snapshot(meta["historical_usd"], meta["requests"], meta_candidate)
        committed = usd(modal["historical_usd"]) + sum(
            (liability_usd(row) for row in modal["requests"]), Decimal(0))
        projected = committed + modal_candidate
        meta_credit, modal_credit = headroom_usd(meta["credit_headroom_usd"]), headroom_usd(modal["credit_headroom_usd"])
        aws_committed = None
        if "AWS" in state:
            aws = _provider(state, "AWS")
            aws_committed = usd(aws["historical_usd"]) + sum(
                (liability_usd(row) for row in aws["requests"]), Decimal(0))
            if aws_committed > 50:
                raise ValueError("AWS liabilities exceed gross cap")
            headroom_usd(aws["credit_headroom_usd"])
        if (not accounting["routine_cap_allows"] or meta_credit < meta_candidate
                or projected > MODAL_CAP_USD or modal_credit < modal_candidate
                or min(MODAL_CAP_USD - projected, modal_credit - modal_candidate) < MODAL_FLOOR_USD):
            raise ReconstructionPaused("Reconstruction budget cap or credit floor reached")
        return {"meta": accounting, "modal_committed_usd": committed,
                "modal_projected_usd": projected, "aws_committed_usd": aws_committed}
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
        raise ReconstructionPaused("Reconstruction accounting state unavailable or invalid") from None
