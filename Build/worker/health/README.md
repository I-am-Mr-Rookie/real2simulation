# Worker health (S04f probes; no job consumer)

Run from repository root; retain Build/api/health/dependencies.py in the image:

```powershell
python -m pip install -r Build/worker/health/requirements.txt
python -m uvicorn Build.worker.health.app:app --host 127.0.0.1 --port 8002
```

/health/live returns200 for this HTTP process only; /api/version is sanitized.
/health/ready uses real Redis/S3 probes but always returns503 while heartbeat is
unavailable: no job loop exists. Healthy dependencies never manufacture worker
readiness. Postgres is not required. See API README for dev guard, timeout/cache
policy and limitations. Standalone app:app launch from this directory is no longer
supported: shared module resolution requires repository root.

Install API test requirements, then run:
python -m unittest Build.api.health.test_health Build.api.health.test_dependencies -v
No credentials/user data/model calls in tests. No live worker/deployment proof.
