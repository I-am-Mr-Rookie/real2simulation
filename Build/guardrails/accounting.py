"""Offline S20a accounting reference over existing ledger fields; no I/O or live admission lock."""
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR

META_ALLOCATION_USD = Decimal("150")
META_ROUTINE_STOP_USD = Decimal("120")
META_DEMO_RESERVE_USD = Decimal("30")


def usd(value):
    """Nonnegative known USD, rounded UP to the existing GPU receipts' eight decimal places."""
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
        raise ValueError("USD must be known, numeric and nonnegative")
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount < 0:
            raise ValueError("USD must be finite and nonnegative")
        return amount.quantize(Decimal("0.00000001"), rounding=ROUND_CEILING)
    except InvalidOperation as exc:
        raise ValueError("Invalid USD amount") from exc


def liability_usd(row):
    """Retain the worst known liability until explicit final billing reconciliation."""
    if not isinstance(row, dict):
        raise ValueError("Cost row must be an object")
    settled = row.get("settled", False)
    if not isinstance(settled, bool):
        raise ValueError("settled must be boolean")
    amounts = {key: usd(row[key]) for key in ("reserved_usd", "est_usd", "billed_usd")
               if row.get(key) is not None}
    if settled:
        if "billed_usd" not in amounts:
            raise ValueError("Settled request requires final billed USD")
        return amounts["billed_usd"]
    if "reserved_usd" not in amounts:
        raise ValueError("Unsettled request requires a conservative reservation")
    return max(amounts.values())


def headroom_usd(value):
    """Validate like a liability, but never round available credit up."""
    usd(value)
    return Decimal(str(value)).quantize(Decimal("0.00000001"), rounding=ROUND_FLOOR)


def meta_snapshot(historical_usd, requests, candidate_usd=0):
    """Count disjoint history + one current row/request + candidate; NOT dispatch authorization.

    Caller projects existing ledgers to request_id/provider plus their cost fields.
    Source coverage, balance freshness and atomic persistence remain integration obligations.
    """
    history, candidate = usd(historical_usd), usd(candidate_usd)
    if not isinstance(requests, (list, tuple)):
        raise ValueError("Requests must be a complete list of projected rows")
    seen, total = set(), Decimal(0)
    for row in requests:
        if not isinstance(row, dict):
            raise ValueError("Request row must be an object")
        key = row.get("request_id")
        if not isinstance(key, str) or not key.strip() or key in seen:
            raise ValueError("Each request needs a unique nonempty request_id")
        if row.get("provider") != "Meta Model API":
            raise ValueError("Only Meta Model API belongs in the Meta envelope")
        seen.add(key)
        total += liability_usd(row)
    committed = history + total
    projected = committed + candidate
    return {"historical_usd": history, "requests_usd": total, "committed_usd": committed,
            "candidate_usd": candidate, "projected_usd": projected,
            "routine_headroom_usd": max(Decimal(0), META_ROUTINE_STOP_USD - committed),
            "demo_reserve_usd": META_DEMO_RESERVE_USD,
            "routine_cap_allows": projected < META_ROUTINE_STOP_USD}
