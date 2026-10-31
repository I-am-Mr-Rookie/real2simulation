# S13m-orch221 PLAN — Show RM04 geometry on DEV (CLAUDE lane, anthropic/claude-opus-5-5/high)

Issued 2026-10-31T14:43:42Z; deadline 15:13:42Z (Dhaka 21:13:42); minute-25 cutoff 15:08:42Z.
Objective: S13j Plan 2 wiring per controller storage decision (no volume/bucket/Git bytes).
Owns: Build/api/workspace/jobs.py; Build/web/src/shell/PrivateWorkspace.mjs; infra/railway/dev/stage.py;
infra/railway/dev/test_stage.py; tests/api-workspace/; tests/web-private/; evidence/S13m/; this run dir.
Checks: unittest test_jobs + test_stage; node --test workspace/web-private/web-workspace-api; npm run build; staged-API probe.
No deploy (controller deploys api+web and checks the viewer).
