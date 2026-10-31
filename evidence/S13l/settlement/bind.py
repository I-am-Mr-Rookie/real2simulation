"""S13l: append app-id binding events to the standalone ledgers the way reserve_gpu appends
(under admission.lock, json.dumps + newline, fsync). Run with cwd = canonical checkout, PYTHONPATH = it."""
import json
import os
import sys
from pathlib import Path

from Build.guardrails.durable import exclusive, read_json
from Build.guardrails.reservations import project, repository_root

root = repository_root(Path(".").resolve())
rt = root / "evidence/S20/runtime"
L1, L2 = "evidence/S20/runtime/standalone-gpu-ledger.jsonl", "evidence/S20/runtime/standalone-gpu-ledger-2.jsonl"
BIND = [
    (L1, L1 + ":segment:modal-track:OWN01:24e8a04900af4ad49611ad152039ba07", "ap-9SEBfxKkipzckSWGcQRGvt"),
    (L1, L1 + ":segment:modal-track:batch:OWN02,OWN03,OWN04,OWN05,OWN06,OWN07,OWN08,OWN09,OWN10,OWN11:"
     "004ccb39a68e4e86bcce42e10b61c5d2", "ap-7qnUtLNN8xQy534jpuXcQs"),
    (L2, L2 + ":segment:modal-track:batch:OWN07,OWN08,OWN09,OWN10,OWN11:5626a16bf9844ea58231a3b666e21d22",
     "ap-HTu3CU7IfNE1A9Q6T9EyvL"),
]


def view():
    journal = read_json(rt / "reservations.json")
    state, _ = project(root, read_json(rt / "receipt.json"), journal)
    ids = {rid for _, rid, _ in BIND}
    return {"journal_unsettled_modal": sum(1 for r in journal["requests"] if r["provider"] == "Modal" and not r.get("settled")),
            "rows": [{k: r.get(k) for k in ("request_id", "reserved_usd", "app_id", "app_ids", "billed_usd", "settled")}
                     for r in state["Modal"]["requests"] if r["request_id"] in ids]}


if __name__ == "__main__":
    print(json.dumps({"before": view()}))
    if sys.argv[1:] == ["apply"]:
        with exclusive(rt / "admission.lock"):
            for ledger, rid, app in BIND:
                lines = (root / ledger).read_text(encoding="utf-8").splitlines()
                if any(json.loads(line).get("app_id") == app for line in lines if line.strip()):
                    continue  # idempotent: already bound
                with (root / ledger).open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps({"provider": "Modal", "request_id": rid, "app_id": app}) + "\n")
                    stream.flush()
                    os.fsync(stream.fileno())
        print(json.dumps({"after": view()}))
