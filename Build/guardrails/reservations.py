"""Global GPU check + durable reserve, projecting existing ledgers without rewriting them."""
import copy
import hashlib
import json
from decimal import Decimal
from pathlib import Path

from Build.guardrails.accounting import headroom_usd, liability_usd, usd
from Build.guardrails.admission import ReconstructionPaused, _unique_fields, require_reconstruction
from Build.guardrails.durable import exclusive, read_json, write_json


def repository_root(root):
    """All linked worktrees use the main checkout's server-owned state."""
    root = Path(root).resolve()
    git = root / ".git"
    if git.is_file():
        directory = Path(git.read_text(encoding="utf-8").strip().removeprefix("gitdir: "))
        directory = (root / directory).resolve()
        common = (directory / (directory / "commondir").read_text().strip()).resolve()
        return common.parent
    return root


def _costs(target, row):
    for field in ("reserved_usd", "est_usd", "billed_usd"):
        if row.get(field) is not None:
            target[field] = str(max(usd(target.get(field, 0)), usd(row[field])))


def project_ledger(path, source):
    """Fold reserve/result/billing events; retain envelopes, never add their child bills twice."""
    path = Path(path)
    if path.suffix == ".json":
        doc = read_json(path)
        names = ("new_all_in_reservation_usd", "new_reservation_usd", "reserve_usd")
        reserves = [usd(doc[k]) for k in names if doc.get(k) is not None]
        if not reserves:
            raise ValueError("Unknown job ledger reservation layout")
        row = {"request_id": source, "provider": "Modal", "reserved_usd": str(max(reserves))}
        bills = [usd(doc[k]) for k in ("actual_usd", "actual_cost_usd", "exact_charge_usd",
                 "measured_total_usd", "measured_total_gpu_usd") if doc.get(k) is not None]
        children = doc.get("jobs", doc.get("gpu_attempts", []))
        child_total = sum((usd(job["measured_cost_usd"]) for job in children
                           if job.get("measured_cost_usd") is not None), Decimal(0))
        row["billed_usd"] = str(max([child_total, *bills]))
        return [row]
    rows, apps = [], {}
    for line, text in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not text.strip():
            continue
        event = json.loads(text, object_pairs_hook=_unique_fields)
        if not isinstance(event, dict):
            raise ValueError("Invalid ledger row")
        provider = event.get("provider", "Modal")
        if provider not in ("Modal", "Meta Model API", "AWS"):
            raise ValueError("Unknown ledger provider")
        app = event.get("app_id")
        key = event.get("request_id")
        if not key and event.get("idempotency_key"):
            key = source + ":" + event["stage"] + ":" + event["idempotency_key"]
        row = next((r for r in rows if key and r["request_id"] == key), None)
        if row is None and app in apps:
            row = apps[app]
        if row is None and app and not event.get("stage"):
            row = next((r for r in rows if r.get("run") == event.get("run") and not r.get("app_id")), None)
        if row is None and event.get("reserved_usd") is not None:
            row = {"request_id": key or f"{source}#L{line}", "provider": provider,
                   "run": event.get("run")}
            rows.append(row)
        if row is None and app:
            row = next((r for r in rows if r.get("run") == event.get("run") and not r.get("app_id")), None)
        if row is None:
            raise ValueError("Result/billing event has no matching reservation")
        if row["provider"] != provider:
            raise ValueError("Conflicting provider identity")
        if app:
            row["app_id"] = app
            apps[app] = row
        _costs(row, event)
        cost = event.get("cost", {})
        for section, field in (("upper_bound", "est_usd"), ("estimated", "est_usd"), ("billed", "billed_usd")):
            if isinstance(cost.get(section), dict) and cost[section].get("total_usd") is not None:
                _costs(row, {field: cost[section]["total_usd"]})
    for row in rows:
        liability_usd(row)
    return rows


def inventory(root):
    sources = set()
    for area in ("S05", "S06", "S07", "S12", "S13", "S14"):
        directory = root / "evidence" / area
        for pattern in ("job-ledger.json", "*ledger.jsonl"):
            sources.update(p.resolve() for p in directory.rglob(pattern) if p.is_file())
    sources.update(p.resolve() for p in (root / "Run-System" / "Runs").rglob("gpu-ledger.jsonl"))
    return sources


def project(root, receipt, journal):
    state = copy.deepcopy(receipt)
    paths = inventory(root) | {Path(p) for p in journal["ledgers"]}
    projected = list(journal["requests"])
    sources = []
    for path in sorted(paths):
        source = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
        data = path.read_bytes()  # A previously inventoried missing ledger must pause.
        sources.append(source + "#sha256=" + hashlib.sha256(data).hexdigest())
        projected.extend(project_ledger(path, source))
    for provider in ("Modal", "Meta Model API", "AWS"):
        if provider not in state:
            continue
        merged = {}
        for row in [*state[provider]["requests"], *(r for r in projected if r["provider"] == provider)]:
            key = row["request_id"]
            if key not in merged:
                merged[key] = dict(row)
            else:
                _costs(merged[key], row)
                merged[key].pop("settled", None)  # Projection cannot certify final reconciliation.
        state[provider]["requests"] = list(merged.values())
        outstanding = sum((liability_usd(r) for r in journal["requests"] if r["provider"] == provider), Decimal(0))
        state[provider]["credit_headroom_usd"] = str(max(Decimal(0),
            headroom_usd(state[provider]["credit_headroom_usd"]) - outstanding))
    state["sources"] = [*sources, "evidence/S20/runtime/receipt.json", "evidence/S20/runtime/reservations.json"]
    return state, paths


def reserve_gpu(root, ledger, stage, key, amount, *, max_jobs, cap_usd):
    """One global transaction; persist first, dispatch only after both writes succeed."""
    root = repository_root(root)
    runtime = root / "evidence/S20/runtime"
    ledger = Path(ledger).resolve()
    try:
        amount = usd(amount)
        if amount <= 0 or not isinstance(key, str) or not key.strip() or stage not in ("segment", "reconstruct"):
            raise ValueError("Unbounded/invalid reservation")
        with exclusive(runtime / "admission.lock"):
            receipt = read_json(runtime / "receipt.json")
            journal = read_json(runtime / "reservations.json")
            if (set(journal) != {"schema", "requests", "ledgers"}
                    or journal["schema"] != "gpu-reservations/1"
                    or not isinstance(journal["requests"], list) or not isinstance(journal["ledgers"], list)):
                raise ValueError("Invalid reservation journal")
            source = ledger.relative_to(root).as_posix() if ledger.is_relative_to(root) else str(ledger)
            request_id = source + ":" + stage + ":" + key
            state, paths = project(root, receipt, journal)
            local = project_ledger(ledger, source) if ledger.exists() else []
            prior = journal["requests"]
            if (any(r["request_id"] == request_id for r in [*prior, *local])
                    or len(prior) >= max_jobs or len(local) >= max_jobs
                    or sum((liability_usd(r) for r in prior), Decimal(0)) + amount > usd(cap_usd)
                    or sum((liability_usd(r) for r in local), Decimal(0)) + amount > usd(cap_usd)):
                raise ReconstructionPaused("GPU job count or all-in reservation cap reached")
            write_json(runtime / "snapshot.json", state)
            require_reconstruction(runtime / "snapshot.json", candidate_modal_usd=amount)
            row = {"request_id": request_id, "provider": "Modal", "stage": stage,
                   "idempotency_key": key, "reserved_usd": str(amount), "billed_usd": None}
            journal["requests"].append(row)
            journal["ledgers"] = sorted(str(p) for p in paths | {ledger})
            # A crash between writes retains the liability and blocks missing-ledger recovery.
            write_json(runtime / "reservations.json", journal)
            ledger.parent.mkdir(parents=True, exist_ok=True)
            with ledger.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(row) + "\n")
                stream.flush()
                import os
                os.fsync(stream.fileno())
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
        raise ReconstructionPaused("GPU admission state unavailable or invalid") from None
