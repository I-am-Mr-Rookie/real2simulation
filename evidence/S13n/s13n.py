"""S13n operator steps (cwd = canonical checkout, PYTHONPATH = S13n worktree): read-only Modal reads,
RM04 app bind (bind.py pattern), orphan void and RM04 settlement via Build.guardrails only."""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from Build.guardrails.durable import exclusive, read_json
from Build.guardrails.reservations import project, repository_root
from Build.guardrails.settlement import settle_gpu

root = repository_root(Path(".").resolve())
rt, D = root / "evidence/S20/runtime", root / "evidence/S13n"
KEY = ":reconstruct:reconstruct:b3fe96a5bf8255d74ef35800d4142855bfa8da9af18d89bd98966131974613bb"
L1, L2 = "evidence/S13l/gpu-ledger.jsonl", "evidence/S13l/gpu-ledger-2.jsonl"
ORPHAN, RM04, APP = L1 + KEY, L2 + KEY, "ap-HyDn6NecaH49gRHPDZhiHh"
MODAL = ["uv", "run", "--no-project", "--python", "3.12", "--with", "modal==1.6.3", "--env-file", ".env", "modal"]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = lambda: datetime.now(timezone.utc).isoformat()


def view():
    journal = read_json(rt / "reservations.json")
    state, _ = project(root, read_json(rt / "receipt.json"), journal)
    return {"at": now(), "journal_unsettled_modal": [r["request_id"] for r in journal["requests"]
                                                     if r["provider"] == "Modal" and not r.get("settled")],
            "rows": [{k: r.get(k) for k in ("request_id", "reserved_usd", "app_id", "billed_usd", "settled")}
                     for r in state["Modal"]["requests"] if r["request_id"] in (ORPHAN, RM04)]}


def read(tag):
    """Read-only Modal CLI reads saved verbatim (UTF-8); read_at is taken after all three reads."""
    out = {}
    for name, args in (("app-list", ["app", "list", "--json"]), ("container-list", ["container", "list", "--json"]),
                       ("billing", ["billing", "report", "--start", "2026-10-31", "--end", "2026-11-01",
                                    "-r", "h", "--json", "--show-resources"])):
        proc = subprocess.run(MODAL + args, capture_output=True, text=True, encoding="utf-8", check=True)
        path = D / f"{name}-{tag}.json"
        json.loads(proc.stdout)  # must parse
        path.write_text(proc.stdout, encoding="utf-8")
        out[name] = path.relative_to(root).as_posix()
    out["read_at"] = now()
    (D / f"read-{tag}.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def bind():
    with exclusive(rt / "admission.lock"):
        lines = (root / L2).read_text(encoding="utf-8").splitlines()
        if not any(json.loads(line).get("app_id") == APP for line in lines if line.strip()):
            with (root / L2).open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"provider": "Modal", "request_id": RM04, "app_id": APP}) + "\n")
                stream.flush()
                os.fsync(stream.fileno())


def void(tag):
    r = read_json(D / f"read-{tag}.json")
    proof = {"schema": "modal-void/1", "request_id": ORPHAN,
             "reviewed_by": "S13n-orch222 worker (anthropic/claude-opus-5-5): attempt-A never dispatched "
                            "(no dispatch_operation, no app binding); every app/bill since its reservation is RM04's",
             "read_at": r["read_at"], "app_list": r["app-list"], "app_list_sha256": sha(root / r["app-list"]),
             "billing_report": r["billing"], "billing_report_sha256": sha(root / r["billing"])}
    path = D / "void-orphan.json"
    path.write_text(json.dumps(proof, indent=1), encoding="utf-8")
    return str(settle_gpu(root, ORPHAN, path))


def settle(tag):
    r = read_json(D / f"read-{tag}.json")
    rows = read_json(root / r["billing"])
    apps = {a["app_id"]: a for a in read_json(root / r["app-list"])}
    assert read_json(root / r["container-list"]) == [] and apps[APP]["state"] == "stopped"
    total = sum((Decimal(str(x["cost"])) for x in rows if x["object_id"] == APP), Decimal(0))
    log = D / "scene-log-RM04.json"
    log.write_text(json.dumps({"app_id": APP, "cost": {"billed": {"status": "billed", "total_usd": str(total)}},
                               "source": r["billing"]}, indent=1), encoding="utf-8")
    stopped = datetime.fromisoformat(apps[APP]["stopped_at"]).astimezone(timezone.utc).isoformat()
    proof = {"schema": "modal-settlement/1", "request_id": RM04, "status": "completed", "containers": [],
             "billing_final_verified": True, "app_id": APP,
             "reviewed_by": "S13n-orch222 worker (anthropic/claude-opus-5-5): app stopped, no containers, "
                            "billing read after 15:05Z so the 14:00Z hour is final",
             "completed_at": stopped, "completed_at_basis": "modal app list stopped_at",
             "billing_read_at": r["read_at"], "scene_log": log.relative_to(root).as_posix(), "scene_log_sha256": sha(log),
             "billing_report": r["billing"], "billing_report_sha256": sha(root / r["billing"])}
    path = D / "receipt-RM04.json"
    path.write_text(json.dumps(proof, indent=1), encoding="utf-8")
    return str(settle_gpu(root, RM04, path))


if __name__ == "__main__":
    step, *args = sys.argv[1:]
    result = {"view": view, "read": read, "bind": bind, "void": void, "settle": settle}[step](*args)
    print(json.dumps({"step": step, "result": result, "view": view()}, default=str))
