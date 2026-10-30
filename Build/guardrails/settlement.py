"""Reviewed final Modal billing releases slots, never history or monthly spend."""
import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from Build.guardrails.accounting import usd
from Build.guardrails.admission import ReconstructionPaused, _unique_fields
from Build.guardrails.durable import exclusive, read_json, write_json


def final_amount(root, row):
    """Recheck immutable evidence on every admission; a cost_log estimate is not final billing."""
    path = Path(row["settlement_receipt"])
    if not path.is_absolute() or not path.resolve().is_relative_to(root):
        raise ValueError("Settlement evidence must remain in this repository")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != row["settlement_sha256"]:
        raise ValueError("Settlement receipt changed")
    proof = json.loads(raw, object_pairs_hook=_unique_fields, parse_float=Decimal)
    if (proof["schema"] != "modal-settlement/1" or proof["request_id"] != row["request_id"]
            or proof["status"] != "completed" or proof["containers"] != []
            or proof["billing_final_verified"] is not True
            or not isinstance(proof["reviewed_by"], str) or not proof["reviewed_by"].strip()
            or not isinstance(proof["app_id"], str) or not proof["app_id"].startswith("ap-")):
        raise ValueError("Completed job and reviewed final billing required")
    completed, billed = (datetime.fromisoformat(proof[k]) for k in ("completed_at", "billing_read_at"))
    reserved = datetime.fromisoformat(row["utc"])
    if not reserved <= completed <= billed <= datetime.now(timezone.utc):
        raise ValueError("Invalid completion/billing chronology")
    docs = {}
    for name in ("scene_log", "billing_report"):
        source = (root / proof[name]).resolve()
        if not source.is_relative_to(root):
            raise ValueError("External settlement evidence")
        data = source.read_bytes()
        if hashlib.sha256(data).hexdigest() != proof[name + "_sha256"]:
            raise ValueError("Settlement source changed")
        docs[name] = json.loads(data, object_pairs_hook=_unique_fields, parse_float=Decimal)
    log, rows = docs["scene_log"], docs["billing_report"]
    if log["app_id"] != proof["app_id"] or not isinstance(rows, list):
        raise ValueError("Billing/app mismatch")
    mine = [r for r in rows if r["object_id"] == proof["app_id"]]
    if not mine or len({(r["environment"], r["interval_start"], r["resource"]) for r in mine}) != len(mine):
        raise ValueError("Missing or duplicated billing rows")
    # Sum exact provider values before the existing conservative eight-place USD rounding.
    for item in mine:
        usd(item["cost"])
        if any(not isinstance(item[k], str) or not item[k].strip()
               for k in ("resource", "environment", "interval_start")):
            raise ValueError("Missing billed resource/interval/environment")
    total = usd(sum((Decimal(str(r["cost"])) for r in mine), Decimal(0)))
    bill = log["cost"]["billed"]
    if bill["status"] != "billed" or usd(bill["total_usd"]) != total:
        raise ValueError("cost_log and billing report disagree")
    return total, proof["app_id"]


def settle_gpu(root, request_id, receipt_path):
    """Local operator action only; never auto-certify lagging billing or reset a journal."""
    from Build.guardrails.reservations import project, repository_root, validate_journal

    try:
        root = repository_root(root)
        runtime = root / "evidence/S20/runtime"
        path = Path(receipt_path).resolve()
        with exclusive(runtime / "admission.lock"):
            journal = read_json(runtime / "reservations.json")
            validate_journal(journal)
            matches = [r for r in journal["requests"] if r["request_id"] == request_id and r["provider"] == "Modal"]
            if len(matches) != 1 or matches[0].get("settled"):
                raise ValueError("One unsettled Modal reservation required")
            row = matches[0]
            candidate = {**row, "settlement_receipt": str(path),
                         "settlement_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            amount, app = final_amount(root, candidate)
            state, _ = project(root, read_json(runtime / "receipt.json"), journal)
            bound = [r for r in state["Modal"]["requests"]
                     if r.get("app_id") == app or app in r.get("app_ids", [])]
            if len(bound) != 1 or bound[0]["request_id"] != request_id or bound[0].get("app_ids"):
                raise ValueError("Billing needs one explicitly bound single-app reservation")
            if usd(bound[0].get("billed_usd") or 0) > amount:
                raise ValueError("Final bill contradicts a larger observed bill")
            row.update(candidate, billed_usd=str(amount), settled=True, app_id=app,
                       reconciliation_ref=str(path) + "#sha256=" + candidate["settlement_sha256"])
            # One atomic journal write: failure retains the full outstanding liability and slot.
            write_json(runtime / "reservations.json", journal)
            return amount
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
        raise ReconstructionPaused("Modal settlement evidence unavailable, ambiguous or invalid") from None


if __name__ == "__main__":
    import sys
    from Build.guardrails.reservations import repository_root
    if len(sys.argv) != 3:
        sys.exit("usage: python -m Build.guardrails.settlement REQUEST_ID REVIEWED_RECEIPT.json")
    print(settle_gpu(repository_root(Path(__file__).resolve().parents[2]), *sys.argv[1:]))
