# S04m-orch156 PLAN

Issued 2026-10-30T19:49:58Z; deadline 20:19:58Z; cutoff 20:14:58Z. anthropic/claude-opus-5-5/high (CODEX-2 lane). OpenCodex-managed; not polled.

Objective: mount S13i/S13k/S14i workspace routers in the dev API, make every router import inside the built image,
set workspace variable NAMES on Railway dev (values never printed), deploy the API to dev, fix verify.py stale text,
verify /health OK and internal routes 401 without token from the public URL.

Owns: Build/api/health/app.py; Build/api/health/requirements.txt; infra/railway/dev/{api.Dockerfile,stage.py,test_stage.py,
verify.py,test_verify.py,deployments.json}; evidence/S04m/; Run-System/Runs/S04m-orch156/.

Checks: build-time import smoke in api.Dockerfile (Railway build log); verify.py exit 0 from public URLs;
test_stage/test_verify, tests/api-workspace (16), tests/pipeline (53) fresh.
