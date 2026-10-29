"""Read-only live dev probe (no credentials): health endpoints + web guest/auth routes. Writes JSON to argv[1]."""
import json, re, sys
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.request import urlopen

HOSTS = {"api": "api-dev-6091", "worker": "worker-dev-984d", "web": "web-dev-cd80"}
PATHS = {"api": ("/health/live", "/health/ready", "/api/version"),
         "worker": ("/health/live", "/health/ready", "/api/version"),
         "web": ("/", "/library", "/sign-in", "/sign-up", "/lab", "/workspace/private-check")}
out = []
for svc, paths in PATHS.items():
    for p in paths:
        url = f"https://{HOSTS[svc]}.up.railway.app{p}"
        try:
            try: r = urlopen(url, timeout=25)
            except HTTPError as e: r = e
            body = r.read().decode("utf-8", "replace")
            rec = {"url": url, "status": r.status}
            if svc != "web":
                d = json.loads(body); rec["body"] = {k: d[k] for k in ("service", "status", "revision", "dependencies") if k in d}
            else:
                m = re.search(r"<title>(.*?)</title>", body)
                rec["title"] = m and m[1]
                rec["markers"] = sorted(k for k in ("clerk", "Sign-in unavailable", "Continue with Google", "guest") if k.lower() in body.lower())
        except Exception as e:
            rec = {"url": url, "error": type(e).__name__}
        out.append(rec)
res = {"observed_utc": datetime.now(timezone.utc).isoformat(), "checks": out}
open(sys.argv[1], "w").write(json.dumps(res, indent=2) + "\n"); print(json.dumps(res, indent=1))
