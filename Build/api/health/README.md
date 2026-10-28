# API health and dev dependency probes (S04f)

Run from repository root:

```powershell
python -m pip install -r Build/api/health/requirements-test.txt
python -m uvicorn Build.api.health.app:app --host 127.0.0.1 --port 8001
python -m unittest Build.api.health.test_health Build.api.health.test_dependencies -v
```

- /health/live: 200, no downstream I/O. /api/version: validated full Railway SHA
  or unknown. Neither claims job readiness.
- /health/ready: Postgres SELECT 1, Redis PING, S3 HeadBucket. 200 only if all
  succeed; otherwise503. States: ok, not-configured (required fields missing),
  unavailable (invalid config, disabled environment, failure, missing SDK, timeout).
- Only R2S_ENVIRONMENT=development and RAILWAY_ENVIRONMENT_NAME=dev enable I/O.
  Railway env may be unset for local dev. No .env loading. Restart after config
  changes. Known service fields are read at app creation, never returned/logged.
- Response wait budget3s; process-wide pool3; one outstanding check per dependency
  per app, reused for5s. SDK connect/read limits2s, SQL statement limit2s, no
  Redis/S3 automatic retries. OS DNS can outlast socket limits; stuck probes
  occupy bounded pool slots but never create duplicate work or block readiness
  responses indefinitely. Liveness remains async/independent.
- SDK clients close. Explicit bucket credentials prevent ambient AWS/profile/
  metadata discovery. HTTPS and virtual-hosted S3 addressing for the new bucket.
  No SQL writes, migrations, queue work, uploads, model inference or GPU calls.

Direct runtime dependencies pinned; transitive versions not locked. Synthetic
adapter/SDK mocks and actual local HTTP/failed connections are NOT live Railway
integration or event-gate evidence. S04g must prove live reference resolution and
successful operations. See infra/railway/dev/README.md.
