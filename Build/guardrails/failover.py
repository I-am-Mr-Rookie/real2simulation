"""Default Modal preflight; AWS plans require a shared durable reservation. No launch."""
import json
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from Build.gpu import aws_adapter
from Build.guardrails.accounting import headroom_usd, liability_usd, usd
from Build.guardrails.durable import exclusive, read_json, write_json
from Build.guardrails.reservations import project, repository_root
from Build.guardrails.admission import (
    MAX_SNAPSHOT_AGE, ReconstructionPaused, _unique_fields, require_reconstruction,
)

MAX_SESSION_SECONDS = 3600
ROOT = Path(__file__).resolve().parents[2]


def _reserve_aws(state_path, bound, receipt, modal, meta, clock):
    root = repository_root(ROOT)
    runtime = root / "evidence/S20/runtime"
    with exclusive(runtime / "admission.lock"):
        journal = read_json(runtime / "reservations.json")
        state, paths = project(root, read_json(state_path), journal)
        write_json(runtime / "snapshot.json", state)
        admission = require_reconstruction(runtime / "snapshot.json", candidate_modal_usd=modal,
                                           candidate_meta_usd=meta, now=clock)
        if "AWS" not in state:
            raise ValueError("AWS liabilities bucket required before enablement")
        outstanding = sum((liability_usd(r) for r in journal["requests"]
                           if r["provider"] == "AWS"), Decimal(0))
        available = min(Decimal(50) - admission["aws_committed_usd"],
                        headroom_usd(state["AWS"]["credit_headroom_usd"]),
                        headroom_usd(receipt["remaining_gross_usd"]) - outstanding,
                        headroom_usd(receipt["credit_headroom_usd"]) - outstanding)
        if bound > available:
            raise ValueError("AWS outstanding liabilities exhaust headroom")
        request_id = "aws:" + uuid4().hex
        journal["requests"].append({"request_id": request_id, "provider": "AWS",
                                    "utc": clock.isoformat(), "reserved_usd": str(bound), "billed_usd": None})
        if usd(meta) > 0:
            journal["requests"].append({"request_id": request_id + ":meta", "provider": "Meta Model API",
                                        "reserved_usd": str(usd(meta)), "billed_usd": None})
        journal["ledgers"] = sorted(str(p) for p in paths)
        write_json(runtime / "reservations.json", journal)
        return admission, request_id


def _receipt(path, schema, clock):
    receipt = json.loads(Path(path).read_text(encoding="utf-8"),
                         object_pairs_hook=_unique_fields, parse_float=Decimal)
    as_of = datetime.fromisoformat(receipt["as_of"])
    if (receipt["schema"] != schema or receipt["owner_approved"] is not True
            or receipt["region"] != aws_adapter.REGION
            or clock.utcoffset() is None or as_of.utcoffset() is None
            or not timedelta(0) <= clock - as_of <= MAX_SNAPSHOT_AGE):
        raise ValueError("Unverified, wrong-region or stale AWS receipt")
    return receipt


def select_provider(state_path, *, candidate_modal_usd, candidate_meta_usd=0,
                    quota_receipt_path=None, budget_receipt_path=None,
                    candidate_aws_usd=None, max_session_seconds=None, env=None, now=None):
    """Return an admitted provider plan or raise nonretryable SPEND_PAUSED.

    Inputs/receipt paths must be server-owned, never upload/browser-controlled.
    shortcut: AWS reserves but does not launch; guaranteed-stop dispatch remains the caller's obligation.
    S20b remains mandatory even for AWS; no cap/floor failure grants failover.
    """
    clock = now if now is not None else datetime.now(timezone.utc)
    admission = require_reconstruction(state_path, candidate_modal_usd=candidate_modal_usd,
                                       candidate_meta_usd=candidate_meta_usd, now=clock)
    env = os.environ if env is None else env
    if env.get(aws_adapter.ENV_FLAG) != "1":
        return {"provider": "Modal", "admission": admission, "aws": None, "launched": False}
    try:
        quota = _receipt(quota_receipt_path, "aws-quota-receipt/1", clock)
        receipt = _receipt(budget_receipt_path, "aws-budget-receipt/1", clock)
        budget = receipt["budget"]
        if (quota["quota_code"] != aws_adapter.SPOT_QUOTA_CODE
                or type(quota["spot_quota_vcpu"]) is not int
                or budget["name"] != "Real2Sim EC2 50 USD"
                or usd(budget["amount_usd"]) != 50
                or Decimal(str(budget["amount_usd"])) != 50
                or budget["currency"] != "USD" or budget["period"] != "MONTHLY"
                or budget["gross"] is not True
                or not isinstance(budget["services"], list)
                or not isinstance(budget["alerts"], list)
                or receipt["coverage_verified"] is not True
                or receipt["credit_verified"] is not True):
            raise ValueError("Invalid quota or budget evidence")
        bound = usd(candidate_aws_usd)
        remaining, credit = (usd(receipt[key]) for key in
                             ("remaining_gross_usd", "credit_headroom_usd"))
        # Headroom must not be rounded up into permission to spend.
        if (remaining != Decimal(str(receipt["remaining_gross_usd"]))
                or credit != Decimal(str(receipt["credit_headroom_usd"]))
                or not 0 < bound <= min(remaining, credit) or remaining > 50
                or type(max_session_seconds) is not int
                or not 0 < max_session_seconds <= MAX_SESSION_SECONDS):
            raise ValueError("Unknown/insufficient headroom or unbounded AWS session")
        gates = {"region": quota["region"], "market": quota["market"],
                 "spot_quota_vcpu": quota["spot_quota_vcpu"],
                 "budget": {**budget, "amount_usd": 50}}
        result = aws_adapter.activate(gates, env=env)
        if not result["active"]:
            raise ValueError("AWS adapter refused activation")
        admission, request_id = _reserve_aws(state_path, bound, receipt, candidate_modal_usd,
                                              candidate_meta_usd, clock)
        return {"provider": "AWS", "admission": admission, "launched": False,
                "aws": {**result["plan"], "all_in_usd": bound,
                        "reservation_id": request_id,
                        "max_session_seconds": max_session_seconds, "stop_on_exit": True}}
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
        raise ReconstructionPaused("AWS failover evidence unavailable, invalid or insufficient") from None
