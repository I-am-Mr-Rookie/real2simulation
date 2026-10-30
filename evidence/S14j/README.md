# S14j evidence — Q16 'scale unverified, not setup-validated' spec path (Railway DEV only)

API deployment `a2777e67-be64-4455-9d71-c8c5803c40a0` (source `49754d0b7ed031fb5ea21f659423a13fcac7e510`, SUCCESS,
created 2026-10-30T20:27:24Z); supersedes `8bf100cc-f7eb-41d1-ac2d-87d15763e6cd` (now REMOVED). /api/version reports 49754d0.

- [api-workspace-unittest.txt](api-workspace-unittest.txt): 20 OK (incl. 4 new test_spec_q16 + updated test_jobs RM04 job path).
- [pipeline-unittest.txt](pipeline-unittest.txt): tests/pipeline 53 OK.
- [verify.json](verify.json): committed `infra/railway/dev/verify.py` exit 1 — ONLY the 3 api checks fail because verify.py pins
  api revision 54d1575 (S04m); bodies show status ok, revision 49754d0, postgres/redis/bucket ok. verify.py is not S14j-owned.
- [verify-expected-49754d0.json](verify-expected-49754d0.json): same verify.py executed in-memory with only the api revision
  literal replaced by 49754d0 (file unchanged): exit 0, 11/11.
- Not verified live: an authenticated POST /scenes/{RM04 job}/spec on DEV (needs the internal token; not read). Covered offline
  by tests through the real jobs.scene_resolver RM04 recorded job.

Controller lines (not owned here):
- deployments.json services.api: deploymentId `a2777e67-be64-4455-9d71-c8c5803c40a0`, previousDeploymentIds += `8bf100cc-f7eb-41d1-ac2d-87d15763e6cd`,
  sourceRevision `49754d0b7ed031fb5ea21f659423a13fcac7e510` (or the main merge SHA if redeployed), providerStatus SUCCESS, verifiedUtc 2026-10-30T20:29:33Z,
  redeployNote "S14j-orch159: stage.py api + railway up (Q16 scale-unverified spec path)".
- infra/railway/dev/verify.py line 10: api revision -> `49754d0b7ed031fb5ea21f659423a13fcac7e510`.
