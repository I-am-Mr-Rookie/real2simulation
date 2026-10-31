"""Global GPU check + durable reserve, projecting existing ledgers without rewriting them."""
import copy
import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from Build.guardrails.accounting import headroom_usd, liability_usd, usd
from Build.guardrails.admission import ReconstructionPaused, _provider, _unique_fields, require_reconstruction
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


def _scene_costs(row, doc):
    cost = doc.get("cost", {})
    for section, field in (("upper_bound", "est_usd"), ("estimated", "est_usd"), ("billed", "billed_usd")):
        if isinstance(cost.get(section), dict) and cost[section].get("total_usd") is not None:
            _costs(row, {field: cost[section]["total_usd"]})


def validate_journal(journal):
    if (not isinstance(journal, dict) or set(journal) != {"schema", "requests", "ledgers"}
            or journal["schema"] != "gpu-reservations/1"
            or not isinstance(journal["requests"], list) or not isinstance(journal["ledgers"], list)):
        raise ValueError("Invalid reservation journal")
    seen = set()
    for row in journal["requests"]:
        key = row["request_id"]
        if (not isinstance(key, str) or not key.strip() or key in seen
                or row["provider"] not in ("Modal", "Meta Model API", "AWS")):
            raise ValueError("Invalid/duplicate global reservation")
        seen.add(key)
        liability_usd(row)
    if any(not isinstance(p, str) or not Path(p).is_absolute() for p in journal["ledgers"]):
        raise ValueError("Invalid inventory path")


def project_ledger(path, source):
    """Fold reserve/result/billing events; retain envelopes, never add their child bills twice."""
    path = Path(path)
    if path.suffix == ".json":
        doc = read_json(path)
        names = ("new_all_in_reservation_usd", "new_reservation_usd", "reserve_usd")
        reserves = [usd(doc[k]) for k in names if doc.get(k) is not None]
        if not reserves:
            raise ValueError("Unknown job ledger reservation layout")
        row = {"request_id": source, "provider": "Modal", "source": source,
               "reserved_usd": str(max(reserves)), "app_ids": []}
        for field in ("app_id", "cpu_app_id"):
            if doc.get(field):
                row["app_ids"].append(doc[field])
        bills = [usd(doc[k]) for k in ("actual_usd", "actual_cost_usd", "exact_charge_usd",
                 "measured_total_usd", "measured_total_gpu_usd") if doc.get(k) is not None]
        children = doc.get("jobs", doc.get("gpu_attempts", []))
        if not isinstance(children, list):
            raise ValueError("Invalid child job inventory")
        child_total = Decimal(0)
        for job in children:
            if job.get("app_id"):
                row["app_ids"].append(job["app_id"])
            amounts = [usd(job[k]) for k in ("reserved_usd", "est_usd", "billed_usd",
                       "measured_cost_usd", "estimated_cost_usd", "upper_bound_cost_usd")
                       if job.get(k) is not None]
            if job.get("scene_log"):
                if Path(source).is_absolute():
                    raise ValueError("Job envelope needs a repository-relative inventory identity")
                root = path.parents[len(Path(source).parts) - 1]
                log = read_json(root / job["scene_log"])
                if log.get("app_id") != job.get("app_id"):
                    raise ValueError("Scene log/child app identity mismatch")
                costs = {}
                _scene_costs(costs, log)
                amounts.extend(usd(v) for v in costs.values())
            child_total += max(amounts, default=Decimal(0))
        # Parent envelope and children describe the SAME spend, not additive budgets.
        row["est_usd"] = str(child_total)
        row["billed_usd"] = str(max(bills, default=Decimal(0)))
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
            key = source + ":" + event.get("stage", "understand" if provider == "Meta Model API" else "") + ":" + event["idempotency_key"]
        row = next((r for r in rows if key and r["request_id"] == key), None)
        if row is None and app in apps:
            row = apps[app]
        if row is None and app:
            candidates = [r for r in rows if r.get("run") == event.get("run") and not r.get("app_id")]
            if len(candidates) > 1:
                raise ValueError("Ambiguous reservation/app association")
            row = candidates[0] if candidates else None
        if row is None and event.get("reserved_usd") is not None:
            row = {"request_id": key or f"{source}#L{line}", "provider": provider,
                   "source": source, "run": event.get("run"),
                   "stage": event.get("stage"), "idempotency_key": event.get("idempotency_key")}
            rows.append(row)
        if row is None:
            raise ValueError("Result/billing event has no matching reservation")
        if row["provider"] != provider:
            raise ValueError("Conflicting provider identity")
        if app:
            if row.get("app_id") and row["app_id"] != app:
                raise ValueError("Conflicting app identity")
            row["app_id"] = app
            apps[app] = row
        _costs(row, event)
        _scene_costs(row, event)
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
    validate_journal(journal)
    for name in ("Modal", "Meta Model API", "AWS"):
        if name in receipt:
            _provider(receipt, name)  # Reject duplicate receipt IDs before merging overlapping event views.
    state = copy.deepcopy(receipt)
    paths = inventory(root) | {Path(p) for p in journal["ledgers"]}
    projected = copy.deepcopy(journal["requests"])
    sources = set()
    for path in sorted(paths):
        source = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
        data = path.read_bytes()  # A previously inventoried missing ledger must pause.
        sources.add(source + "#sha256=" + hashlib.sha256(data).hexdigest())
        if not (path.name.endswith("scene-log.json") or path.name == "reconstruction.json"):
            projected.extend(project_ledger(path, source))
        if path.read_bytes() != data:
            raise ValueError("Ledger changed during projection")
    # Scene receipts can exceed a reservation; bind them by app, or the adjacent pipeline artifact.
    logs = set()
    for area in ("S05", "S06", "S07", "S12", "S13"):
        logs.update((root / "evidence" / area).rglob("*scene-log.json"))
    logs.update((root / "Run-System/Runs").rglob("*scene-log.json"))
    logs.update(p for p in paths if p.name.endswith("scene-log.json"))
    for path in sorted(logs):
        log = read_json(path)
        app = log["app_id"]
        matches = [r for r in projected if app and
                   (r.get("app_id") == app or app in r.get("app_ids", []))]
        if not matches:
            artifact = path.parent.parent / "reconstruction.json"
            doc = read_json(artifact)
            if doc["app_id"] != app:
                raise ValueError("Scene log/artifact app identity mismatch")
            matches = [r for r in projected if r.get("stage") == "reconstruct"
                       and r.get("idempotency_key") == doc["idempotency_key"]
                       and r.get("source")  # journal copies carry no source; their ledger projection does
                       and path.is_relative_to((root / r["source"]).parent)]
            sources.add(artifact.relative_to(root).as_posix() + "#sha256=" + hashlib.sha256(artifact.read_bytes()).hexdigest())
            paths.add(artifact)
        if len({r["request_id"] for r in matches}) != 1:
            raise ValueError("Scene log needs exactly one originating reservation")
        row = matches[0]
        if "app_ids" not in row:  # JSON envelopes already folded their child scene logs above.
            _scene_costs(row, log)
        sources.add(path.relative_to(root).as_posix() + "#sha256=" + hashlib.sha256(path.read_bytes()).hexdigest())
        paths.add(path)
    for provider in ("Modal", "Meta Model API", "AWS"):
        if provider not in state:
            if any(r["provider"] == provider for r in projected):
                raise ValueError("Missing provider liabilities bucket")
            continue
        merged = {}
        for row in [*state[provider]["requests"], *(r for r in projected if r["provider"] == provider)]:
            key = row["request_id"]
            if key not in merged:
                merged[key] = dict(row)
            else:
                _costs(merged[key], row)
                if row.get("app_id"):
                    if merged[key].get("app_id") not in (None, row["app_id"]):
                        raise ValueError("Conflicting projected app identity")
                    merged[key]["app_id"] = row["app_id"]
                merged[key].pop("settled", None)  # Projection cannot certify final reconciliation.
        for row in journal["requests"]:
            if row["provider"] == provider and row.get("settled"):
                from Build.guardrails.settlement import final_amount
                amount, app = final_amount(root, row)
                target = merged[row["request_id"]]
                if usd(target.get("billed_usd") or 0) > amount or usd(row["billed_usd"]) != amount:
                    raise ValueError("Settled bill conflicts with observed billing")
                target.update(settled=True, billed_usd=str(amount), app_id=app,
                              reconciliation_ref=row["reconciliation_ref"])
        state[provider]["requests"] = list(merged.values())
        reflected = {r["request_id"] for r in receipt[provider]["requests"]}
        outstanding = sum((liability_usd(r) for r in journal["requests"]
                           if r["provider"] == provider and r["request_id"] not in reflected), Decimal(0))
        state[provider]["credit_headroom_usd"] = str(max(Decimal(0),
            headroom_usd(state[provider]["credit_headroom_usd"]) - outstanding))
    state["sources"] = [*sorted(sources), "evidence/S20/runtime/receipt.json", "evidence/S20/runtime/reservations.json"]
    return state, paths


def reserve_meta(root, ledger, stage, key, amount, *, max_calls, cap_usd):
    """Reserve Meta globally before POST, retaining liabilities even if transport crashes."""
    try:
        root = repository_root(root)
        runtime = root / "evidence/S20/runtime"
        ledger, amount = Path(ledger).resolve(), usd(amount)
        if amount <= 0 or stage not in ("understand", "record_muse") or not isinstance(key, str) or not key.strip():
            raise ValueError("Invalid Meta reservation")
        with exclusive(runtime / "admission.lock"):
            receipt = read_json(runtime / "receipt.json")
            journal = read_json(runtime / "reservations.json")
            validate_journal(journal)
            if ledger.exists():
                journal["ledgers"] = sorted(set(journal["ledgers"]) | {str(ledger)})
            state, paths = project(root, receipt, journal)
            source = ledger.relative_to(root).as_posix() if ledger.is_relative_to(root) else str(ledger)
            local = project_ledger(ledger, source) if ledger.exists() else []
            request_id = "meta:" + stage + ":" + key
            prior = [r for r in state["Meta Model API"]["requests"] if r.get("stage") == stage]
            if (any(r["request_id"] == request_id for r in state["Meta Model API"]["requests"])
                    or len(prior) >= max_calls or len(local) >= max_calls
                    or sum((liability_usd(r) for r in prior), Decimal(0)) + amount > usd(cap_usd)
                    or sum((liability_usd(r) for r in local), Decimal(0)) + amount > usd(cap_usd)):
                raise ReconstructionPaused("Meta call count or reservation cap reached")
            write_json(runtime / "snapshot.json", state)
            require_reconstruction(runtime / "snapshot.json", candidate_modal_usd=0, candidate_meta_usd=amount)
            row = {"request_id": request_id, "provider": "Meta Model API", "stage": stage,
                   "utc": datetime.now(timezone.utc).isoformat(), "idempotency_key": key,
                   "reserved_usd": str(amount), "billed_usd": None}
            journal["requests"].append(row)
            journal["ledgers"] = sorted(str(p) for p in paths | {ledger})
            write_json(runtime / "reservations.json", journal)
            ledger.parent.mkdir(parents=True, exist_ok=True)
            with ledger.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(row) + "\n")
                stream.flush()
                import os
                os.fsync(stream.fileno())
            return request_id
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
        raise ReconstructionPaused("Meta admission state unavailable or invalid") from None


def reserve_gpu(root, ledger, stage, key, amount, *, max_jobs, cap_usd):
    """One global transaction; persist first, dispatch only after both writes succeed."""
    try:
        root = repository_root(root)
        runtime = root / "evidence/S20/runtime"
        ledger = Path(ledger).resolve()
        amount = usd(amount)
        if amount <= 0 or not isinstance(key, str) or not key.strip() or stage not in ("segment", "reconstruct"):
            raise ValueError("Unbounded/invalid reservation")
        with exclusive(runtime / "admission.lock"):
            receipt = read_json(runtime / "receipt.json")
            journal = read_json(runtime / "reservations.json")
            validate_journal(journal)
            source = ledger.relative_to(root).as_posix() if ledger.is_relative_to(root) else str(ledger)
            request_id = source + ":" + stage + ":" + key
            state, paths = project(root, receipt, journal)
            local = project_ledger(ledger, source) if ledger.exists() else []
            ids = {r["request_id"] for r in journal["requests"] if r["provider"] == "Modal"}
            settled = {r["request_id"] for r in journal["requests"] if r["provider"] == "Modal" and r.get("settled")}
            prior = [r for r in state["Modal"]["requests"] if r["request_id"] in ids - settled]
            active_local = [r for r in local if r["request_id"] not in settled]
            if (request_id in ids or any(r["request_id"] == request_id for r in local)
                    or len(prior) >= max_jobs or len(active_local) >= max_jobs
                    or sum((liability_usd(r) for r in prior), Decimal(0)) + amount > usd(cap_usd)
                    or sum((liability_usd(r) for r in active_local), Decimal(0)) + amount > usd(cap_usd)):
                raise ReconstructionPaused("GPU job count or all-in reservation cap reached")
            write_json(runtime / "snapshot.json", state)
            require_reconstruction(runtime / "snapshot.json", candidate_modal_usd=amount)
            row = {"request_id": request_id, "provider": "Modal", "stage": stage,
                   "utc": datetime.now(timezone.utc).isoformat(),
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
            return request_id
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
        raise ReconstructionPaused("GPU admission state unavailable or invalid") from None


def claim_gpu(root, request_id, operation):
    """Consume one durable reservation once; a pipeline child must not reserve a second job."""
    try:
        root = repository_root(root)
        runtime = root / "evidence/S20/runtime"
        with exclusive(runtime / "admission.lock"):
            journal = read_json(runtime / "reservations.json")
            validate_journal(journal)
            matches = [r for r in journal["requests"] if r["request_id"] == request_id and r["provider"] == "Modal"]
            stage = "segment" if operation.startswith("modal-track:") else "reconstruct"
            if len(matches) != 1 or matches[0].get("settled") or matches[0].get("dispatch_operation"):
                raise ValueError("One unclaimed active reservation required")
            row = matches[0]
            if row["stage"] != stage:
                raise ValueError("Reservation stage does not match launch")
            state, _ = project(root, read_json(runtime / "receipt.json"), journal)
            current = next(r for r in state["Modal"]["requests"] if r["request_id"] == request_id)
            amount = liability_usd(current)
            state["Modal"]["requests"].remove(current)
            state["Modal"]["credit_headroom_usd"] = str(headroom_usd(state["Modal"]["credit_headroom_usd"]) + amount)
            write_json(runtime / "snapshot.json", state)
            require_reconstruction(runtime / "snapshot.json", candidate_modal_usd=amount)
            row["dispatch_operation"] = operation
            write_json(runtime / "reservations.json", journal)
            return request_id
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError, OverflowError, StopIteration):
        raise ReconstructionPaused("GPU dispatch reservation unavailable, reused or invalid") from None
