"""S13l: controller-approved trusted-operator receipt.json refresh (only after explicit controller OK).
Keeps the old shape; Modal historical = fresh read-only Oct billing total; Meta unchanged. cwd = canonical."""
import json
import shutil
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from Build.guardrails.durable import exclusive, read_json, write_json

rt = Path("evidence/S20/runtime")
total = Decimal(sys.argv[1])  # fresh read-only modal billing report total for the Oct cycle
read_at = sys.argv[2]
with exclusive(rt / "admission.lock"):
    old = read_json(rt / "receipt.json")
    shutil.copyfile(rt / "receipt.json", "evidence/S13l/receipt-before.json")
    new = {**old, "as_of": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
           "sources": [f"Read-only CLI modal billing report --start 2026-10-01 --end 2026-11-01 -r d --json at {read_at}: "
                       f"Oct cycle total {total} (evidence/S13l/billing-oct-daily.json); modal app list empty; "
                       "Starter $30 monthly credit only (+$100 grant not counted); refresh approved by controller for S13l-orch219",
                       *old["sources"]],
           "Modal": {**old["Modal"], "historical_usd": str(total), "credit_headroom_usd": str(Decimal(30) - total)}}
    write_json(rt / "receipt.json", new)
print(json.dumps(new, indent=1))
