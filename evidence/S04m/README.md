# S04m evidence (Railway DEV only)

API deployment `8bf100cc-f7eb-41d1-ac2d-87d15763e6cd` (source `54d15757aabf90b3041537cef8e22d4d0f4532a1`, SUCCESS);
first attempt `3af47dc9-0158-4294-82ad-7b71c27420a8` (`8efe5be`, SUCCESS) superseded by the malformed-REDIS_URL guard.
Web `db4b96a6-bc73-4a27-81f9-4e4af8cc9798` = as-is redeploy of `aa539357` build so the new variables load.

- [api-build-log.txt](api-build-log.txt): Railway build log of 8bf100cc; step `[6/6] RUN python -B -c "import Build.api.health.app"`
  is the in-image import smoke (app.py imports and mounts jobs + analysis routers; build fails if any import fails). Docker is
  not running locally, so the built Railway image is the only image smoke.
- [verify.json](verify.json): `python -B infra/railway/dev/verify.py` exit 0, 11/11 (api health/ready/version at 54d1575,
  `/internal/workspace/jobs/job_0…0` -> 401 UNAUTHORIZED without token, worker baseline, web pages). An earlier run had one
  transient URLError on web /sign-in; the immediate rerun passed.
- [variable-check.json](variable-check.json): booleans only (token equal on api/web, length >= 40, WORKSPACE_API_URL resolves to
  a *.railway.internal:8080 URL, REDIS_URL present); the check script read values in-process and printed none.
- tests-*.txt: fresh tails. api-workspace 16 OK, pipeline 53 OK, railway-dev (test_stage + test_verify) 16 OK,
  Build/api/health 16 with 1 error = missing local `psycopg` (same error on canonical main 05d558f5; pre-existing).

## Variable names and sources (values never printed/logged/committed)

| Service | Name | Source |
|---|---|---|
| api | WORKSPACE_INTERNAL_TOKEN | `secrets.token_urlsafe(32)` generated in-process, piped via `railway variable set --stdin` |
| web | WORKSPACE_INTERNAL_TOKEN | same in-process value, same method |
| web | WORKSPACE_API_URL | `http://${{api.RAILWAY_PRIVATE_DOMAIN}}:8080` (Railway reference, private network) |
| api | REDIS_URL | unchanged pre-existing `${{Redis.REDIS_URL}}` (existing dev Redis; no new service) |
| api | WORKSPACE_UPLOAD_DIR | `/tmp/r2s-uploads` (ephemeral container disk; uploads lost on redeploy) |

infra/railway/dev/variable-references.json is not in S04m Owns, so these names are recorded here only.
