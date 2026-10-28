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


def issue(run_id, now=None):
    start = now or datetime.now(timezone.utc)
    if start.tzinfo is None:
        raise ValueError("Dispatch clock must include timezone")
    start = start.astimezone(timezone.utc).replace(microsecond=0)
    deadline = start + timedelta(minutes=30)
    return {"id": run_id, "issued_at": start.isoformat(),
            "deadline_at": deadline.isoformat(),
            "implementation_cutoff_at": (start + timedelta(minutes=25)).isoformat(),
            "deadline_dhaka": deadline.astimezone(timezone(timedelta(hours=6))).isoformat()}


def check(receipt, now=None):
    start, deadline, stopped, reported = (
        timestamp(receipt[key]) for key in
        ("issued_at", "deadline_at", "work_stopped_at", "reported_at"))
    if deadline - start != timedelta(minutes=30):
        raise ValueError("Each new worker requires a full 30-minute dispatch window")
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
        action, value = sys.argv[1:]
        if action == "issue":
            print(json.dumps(issue(value), indent=2))
        elif action == "check":
            print(check(json.loads(Path(value).read_text(encoding="utf-8-sig"))))
        else:
            raise ValueError("Use issue <ID> or check <TIMEBOX.json>")
    except (ValueError, KeyError, TypeError) as exc:
        sys.exit(str(exc))
