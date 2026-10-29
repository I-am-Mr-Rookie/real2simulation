"""Free GET /models probe: prints host + model ids only; never prints key values."""
import os
from pathlib import Path
from urllib.parse import urlparse

import httpx
from dotenv import dotenv_values

env = dotenv_values(Path(r"C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.env"))
for k in ("MODEL_API_KEY", "MODEL_API_BASE_URL", "MODEL_API_MODEL"):
    print(k, "present" if env.get(k) else "MISSING")
base = env["MODEL_API_BASE_URL"].rstrip("/")
print("host", urlparse(base).netloc, "path", urlparse(base).path, "model", env.get("MODEL_API_MODEL"))
r = httpx.get(base + "/models", headers={"Authorization": "Bearer " + env["MODEL_API_KEY"]}, timeout=30)
print("status", r.status_code)
try:
    print(sorted(m.get("id") for m in r.json().get("data", [])))
except Exception as exc:  # noqa: BLE001
    print("body-unparsed", type(exc).__name__, r.text[:200].replace(env["MODEL_API_KEY"], "<redacted>"))
