"""Calculate manual worker deadlines and reject early incomplete report receipts."""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def timestamp(value):
    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("Timestamp must include timezone")
    return value.astimezone(timezone.utc)


WINDOWS = (30, 60)  # Koushik Nov 1: integration runs may get 60 minutes


def issue(run_id, now=None, minutes=30):
    if minutes not in WINDOWS:
        raise ValueError("Window must be 30 or 60 minutes")
    start = now or datetime.now(timezone.utc)
    if start.tzinfo is None:
        raise ValueError("Dispatch clock must include timezone")
    start = start.astimezone(timezone.utc).replace(microsecond=0)
    deadline = start + timedelta(minutes=minutes)
    return {"id": run_id, "issued_at": start.isoformat(),
            "deadline_at": deadline.isoformat(),
            "implementation_cutoff_at": (deadline - timedelta(minutes=5)).isoformat(),
            "deadline_dhaka": deadline.astimezone(timezone(timedelta(hours=6))).isoformat()}


def check(receipt, now=None):
    start, deadline, stopped, reported = (
        timestamp(receipt[key]) for key in
        ("issued_at", "deadline_at", "work_stopped_at", "reported_at"))
    if deadline - start not in tuple(timedelta(minutes=m) for m in WINDOWS):
        raise ValueError("Each new worker requires a full 30- or 60-minute dispatch window")
    if not start <= stopped <= deadline:
        raise ValueError("Work stop must be within the original dispatch window")
    if not stopped <= reported <= (now or datetime.now(timezone.utc)):
        raise ValueError("Invalid or future report timestamp")
    status = receipt["status"]
    if status not in ("DONE", "PARTIAL", "BLOCKED"):
        raise ValueError("Unknown terminal status")
    exception = receipt.get("controller_exception")
    if exception and (exception.get("reason") not in ("owner_stop", "safety", "resource_stop")
                      or not exception.get("approval_receipt")):
        raise ValueError("Early-stop exception needs a controller approval receipt")
    if status != "DONE" and stopped < deadline and not exception:
        raise ValueError("EARLY INCOMPLETE: return to same worker; do not accept")
    return "TIMING PASS; controller must separately verify evidence and any exception"


if __name__ == "__main__":
    try:
        action, value, *rest = sys.argv[1:]
        if action == "issue":
            print(json.dumps(issue(value, minutes=int(rest[0]) if rest else 30), indent=2))
        elif action == "check":
            print(check(json.loads(Path(value).read_text(encoding="utf-8-sig"))))
        else:
            raise ValueError("Use issue <ID> [30|60] or check <TIMEBOX.json>")
    except (ValueError, KeyError, TypeError) as exc:
        sys.exit(str(exc))
