"""N12 live check: one muse-image-1.0 report illustration through daily_cap (image bytes not committed)."""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dotenv import dotenv_values  # noqa: E402

from Build.agent.record_muse import ENV  # noqa: E402
from Build.reports.lab_report import IMAGE_USD, illustrate  # noqa: E402

env = dotenv_values(ENV)
for k in ("MODEL_API_KEY", "MODEL_API_BASE_URL"):
    if env.get(k):
        os.environ[k] = env[k]
at = datetime.now(timezone.utc).isoformat(timespec="seconds")
b64 = illustrate("Lab report: measure the gravitational acceleration g from a falling object")
out = {"utc": at, "model": "muse-image-1.0", "ok": bool(b64), "b64_chars": len(b64 or ""),
       "est_usd": IMAGE_USD if b64 else 0, "note": "image not committed (media binary)"}
(Path(__file__).resolve().parent / "illustration_check.json").write_text(json.dumps(out, indent=2), "utf-8")
print(out)
