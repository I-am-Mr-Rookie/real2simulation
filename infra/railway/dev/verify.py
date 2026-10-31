"""Read-only dev HTTP acceptance; no credentials or model calls."""
import json
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.request import urlopen

revision = "300cd2096f9e32bcdf3433520b36b67f709df0d5"
# S04m/S14j redeployed only the API (deployments.json api.sourceRevision).
revisions = {"api": "d195f270e74af29f817835130d0eeac7946245f9", "worker": revision}
checks = []
for service, host, paths in (
    ("api", "api-dev-6091.up.railway.app", ("/health/live", "/health/ready", "/api/version", "/internal/workspace/jobs/job_" + "0" * 32)),
    ("worker", "worker-dev-984d.up.railway.app", ("/health/live", "/health/ready", "/api/version")),
    ("web", "web-dev-cd80.up.railway.app", ("/", "/library", "/sign-in", "/workspace/private-check")),
):
    for path in paths:
        url = f"https://{host}{path}"
        record = {"service": service, "url": url}
        try:
            try:
                response = urlopen(url, timeout=20)
            except HTTPError as error:
                response = error
            body = response.read().decode()
            record["status"] = response.status
            if path.startswith("/internal/"):
                # No token sent: the mounted workspace router must fail closed.
                record["pass"] = response.status == 401 and '"UNAUTHORIZED"' in body
            elif service != "web":
                data = json.loads(body)
                record["body"] = {k: data[k] for k in ("service", "status", "revision", "dependencies") if k in data}
                expected = 503 if service == "worker" and path == "/health/ready" else 200
                record["pass"] = (
                    response.status == expected
                    and data.get("revision") == revisions[service]
                    and data.get("service") == service
                )
                # Version has service/revision only; status belongs to health.
                if path != "/api/version":
                    expected_status = "unavailable" if expected == 503 else "ok"
                    record["pass"] &= data.get("status") == expected_status
                if path == "/health/ready":
                    dependencies = {"redis": "ok", "bucket": "ok"}
                    dependencies["postgres" if service == "api" else "heartbeat"] = "ok" if service == "api" else "unavailable"
                    record["pass"] &= data.get("dependencies") == dependencies
            else:
                record["product_title"] = "Real2Simulation" in body
                record["auth_fallback"] = "unavailable" in body.lower()
                expected_content = {
                    "/": "Real2Simulation",
                    "/library": "Demo library",  # S04k snapshot-served cards replaced the empty state
                    "/sign-in": "Sign in to Real2Simulation",  # Clerk configured Oct29; was the unavailable fallback
                    "/workspace/private-check": "Private workspaces require sign-in",  # not-found.jsx since S15k
                }[path]
                record["expected_content_present"] = expected_content in body
                record["pass"] = response.status == (404 if path.startswith("/workspace/") else 200) and record["product_title"] and record["expected_content_present"]
        except Exception as error:
            record["error_type"] = type(error).__name__
            record["pass"] = False
        checks.append(record)
result = {"observed_utc": datetime.now(timezone.utc).isoformat(), "checks": checks}
print(json.dumps(result, indent=2))
sys.exit(0 if all(c["pass"] for c in checks) else 1)
