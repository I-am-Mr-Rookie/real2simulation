"""S13l: write modal-settlement/1 receipts + scene logs for the 3 bound standalone reservations (cwd = canonical)."""
import hashlib
import json
from decimal import Decimal
from pathlib import Path

D = Path("evidence/S13l/settlement")
REPORT = D / "modal-billing-report-2026-10-30_31-fresh.json"  # read-only modal billing report, read 14:30:58Z
L1, L2 = "evidence/S20/runtime/standalone-gpu-ledger.jsonl", "evidence/S20/runtime/standalone-gpu-ledger-2.jsonl"
JOBS = {
    "OWN01": (L1 + ":segment:modal-track:OWN01:24e8a04900af4ad49611ad152039ba07", "ap-9SEBfxKkipzckSWGcQRGvt"),
    "batch1": (L1 + ":segment:modal-track:batch:OWN02,OWN03,OWN04,OWN05,OWN06,OWN07,OWN08,OWN09,OWN10,OWN11:"
               "004ccb39a68e4e86bcce42e10b61c5d2", "ap-7qnUtLNN8xQy534jpuXcQs"),
    "batch2": (L2 + ":segment:modal-track:batch:OWN07,OWN08,OWN09,OWN10,OWN11:5626a16bf9844ea58231a3b666e21d22",
               "ap-HTu3CU7IfNE1A9Q6T9EyvL"),
}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rows = json.loads(REPORT.read_text(encoding="utf-8"))
for name, (rid, app) in JOBS.items():
    total = sum((Decimal(str(r["cost"])) for r in rows if r["object_id"] == app), Decimal(0))
    log = D / f"scene-log-{name}.json"
    log.write_text(json.dumps({"app_id": app, "cost": {"billed": {"status": "billed", "total_usd": str(total)}},
                               "source": str(REPORT)}, indent=1), encoding="utf-8")
    receipt = {"schema": "modal-settlement/1", "request_id": rid, "status": "completed", "containers": [],
               "billing_final_verified": True, "app_id": app,
               "reviewed_by": "S13l-orch219 worker (anthropic/claude-opus-5-5): fresh per-app hourly rows equal S13j 14:06Z read",
               "completed_at": "2026-10-31T00:00:00+00:00",
               "completed_at_basis": "upper bound: every billed row for this app is in hourly interval 2026-10-30T23:00; "
                                     "evidence/S07/S07j RETRACK-RUN/ENVELOPE-2 record the jobs stopped; modal app list empty 14:32:02Z",
               "billing_read_at": "2026-10-31T14:30:58+00:00",
               "scene_log": log.as_posix(), "scene_log_sha256": sha(log),
               "billing_report": REPORT.as_posix(), "billing_report_sha256": sha(REPORT)}
    (D / f"receipt-{name}.json").write_text(json.dumps(receipt, indent=1), encoding="utf-8")
    print(name, app, total, (D / f"receipt-{name}.json").resolve())
