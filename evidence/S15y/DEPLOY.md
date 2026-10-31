# S15y-orch177 DEV deploy (Railway dev only)
Source revision 6b9e16d9d7821327cd3822acade1f3c48bd7a5c4 (run/S15y-orch177, rebased on main e8d329fe).
- `python infra/railway/dev/stage.py api %TEMP%\s15y-api-orch177` -> 88 files; `stage.py web %TEMP%\s15y-web-orch177` -> 111 files; both source_revision 6b9e16d9.
- `railway up --detach --project b07b0d66-... --environment c5823a28-... --service <id>` from each staged dir.
- api 88eb14d1-5be4-4d6b-a439-800293c2b703 SUCCESS (85c23646 REMOVED); web 75dcb815-b7a1-44ab-80da-44733b3d048e SUCCESS (20e728a2 REMOVED) per `railway deployment list`.
- 2026-10-31T00:13:20+00:00: api /health/live, /health/ready (postgres/redis/bucket ok), /api/version -> 200 revision 6b9e16d9d7821327cd3822acade1f3c48bd7a5c4; /internal/workspace/jobs/<id> -> 401 without token; web / -> 200.

For controller (deployments.json / verify.py NOT edited):
- api {deploymentId 88eb14d1-5be4-4d6b-a439-800293c2b703, previousDeploymentId 85c23646-2e35-4c25-af0d-cbe38a52c524, sourceRevision 6b9e16d9d7821327cd3822acade1f3c48bd7a5c4} — update verify.py pin to 6b9e16d9d7821327cd3822acade1f3c48bd7a5c4.
- web {deploymentId 75dcb815-b7a1-44ab-80da-44733b3d048e, previousDeploymentId 20e728a2-e0f5-45f1-90b8-4734d2e00bfb, sourceRevision 6b9e16d9d7821327cd3822acade1f3c48bd7a5c4}.

Not verified here: the signed-in owner upload walk of OWN01/OWN02 on DEV (controller's job; no owner video uploaded by this worker).
