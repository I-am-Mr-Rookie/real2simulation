# S04m-orch156 REPORT — DONE

Lane CODEX-2 (Claude preferred); model anthropic/claude-opus-5-5/high. UTC 2026-10-30T19:50:30Z–20:04Z.
Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable). Railway dev only; no GPU/Meta/AWS, no new paid resources.
Branch run/S04m-orch156 from main dc0c40d4 (main has since moved to 05d558f5; not rebased/merged — controller integrates).

## Changes
- Build/api/health/app.py: mounts `jobs.create_router(store)` + `analysis.create_router(jobs.scene_resolver(store))` on ONE
  `jobs.default_store()` (REDIS_URL -> redis-py, unset -> MemoryStore). /health/* and /api/version unchanged. A malformed
  REDIS_URL now leaves workspace unmounted instead of crashing liveness (caught by existing test_health secret-canary test).
- requirements.txt: + numpy==2.2.6 (fitter), jsonschema==4.23.0 (same pin as contracts/*/requirements.txt). redis==8.1.0 already present.
- api.Dockerfile: `COPY . /app` (context = stage.py allowlist only) + build-time import smoke `RUN python -B -c "import Build.api.health.app"`.
- stage.py: api allowlist = transitive import closure (Build/api, agent, fitter, pipeline, real2sim, reports, contracts — traced with
  sys.modules + audit hook) + runtime data (clips.csv, owner S02 APPROVAL.md, S02c-acquisition registry, S13h live recording, S14g-fix3 spec). 86 files, ~0.97 MB.
- test_stage.py: api manifest expectation includes workspace + data, excludes unlisted evidence.
- verify.py/test_verify.py: stale S15k text fixed (`Private workspaces require sign-in`), stale /library text fixed (`Demo library`, S04k);
  per-service revision (api 54d1575, worker 300cd20); new check `/internal/workspace/jobs/job_0…0` must be 401 UNAUTHORIZED without token; new rejection test.
- deployments.json: api 8bf100cc (+ previous 3af47dc9, d520a4f9), web db4b96a6 redeploy, variable names/sources.
- evidence/S04m/: README (variable name/source table), build log, verify.json, variable-check.json (booleans only), test tails.

## Railway (dev)
- Vars set by name via `railway variable set --stdin` from an in-process generator (never echoed/logged/committed): api
  WORKSPACE_INTERNAL_TOKEN, WORKSPACE_UPLOAD_DIR=/tmp/r2s-uploads; web WORKSPACE_INTERNAL_TOKEN (same value; equality checked
  in-process -> true), WORKSPACE_API_URL=http://${{api.RAILWAY_PRIVATE_DOMAIN}}:8080. REDIS_URL already referenced existing dev Redis (unchanged).
- API deploy: stage.py api -> `railway up --detach` -> 8bf100cc SUCCESS (source 54d1575). Web: as-is `railway redeploy` -> db4b96a6 SUCCESS.

## Checks (fresh)
- In-image import smoke: Railway build step [6/6] passed (evidence/S04m/api-build-log.txt). Local Docker daemon not running.
- verify.py from public URLs: exit 0, 11/11 at 2026-10-30T20:02:25Z (api /health ok rev 54d1575, ready postgres/redis/bucket ok; internal route 401).
- tests: railway-dev 16 OK; tests/api-workspace 16 OK; tests/pipeline 53 OK; local app TestClient: token+owner -> 404 (mounted), none -> 401.
- Build/api/health: 15/16; 1 error = local psycopg missing, same on canonical main (pre-existing).

## Ponytail
Reused jobs.default_store/scene_resolver, existing stage.py allowlist + Dockerfile, existing verify loop; one build-time RUN line
as the image smoke instead of a new script; transitive closure traced, not guessed. Skipped: no new Redis/service, no
variable-references.json edit (not Owns), no IPv6 bind change, no web code change.

## Limits / risks
- Authenticated web BFF -> API call over Railway private network NOT verified (needs signed-in session); dev env created Oct 2026 should be dual-stack (uvicorn binds 0.0.0.0).
- Uploads on ephemeral /tmp (lost on redeploy); readiness does not probe the workspace store.
- Data/approval files are baked into the API image (private dev only); the recorded RM04 replay is not live inference.
- Communication: silent; one completion message to controller.
