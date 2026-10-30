# S04o evidence — web DEV deploy + checks (2026-10-30 UTC)

## Deployment (Railway DEV only)
- **Current: 197153d3-5f88-4287-8e21-d7cf77cb4d27 SUCCESS** (created 20:18:42Z, source a09fe75707461fb9b81803f88448db46a0b1aea5 = controller route fix); it replaced 3f707632 (now REMOVED). Logged-out re-check 20:20Z: BFF 401, /workspace 404, other scene 404, / 200.
- Controller line for infra/railway/dev/deployments.json: `services.web.deploymentId = "197153d3-5f88-4287-8e21-d7cf77cb4d27"`, previous `db4b96a6-bc73-4a27-81f9-4e4af8cc9798`, sourceRevision `a09fe75707461fb9b81803f88448db46a0b1aea5`, verifiedUtc 2026-10-30T20:20Z.

First deploy (superseded):
- Path: `python infra/railway/dev/stage.py web <fresh temp dir>` (111 files, source_revision cbce5c0159f6026eee39e9d3a304746ae36fc278) -> `railway up --detach --project b07b0d66-… --environment c5823a28-… (dev) --service 49f2938d-… (web)`.
- Deployment **3f707632-db12-43db-911b-bbe71a5cedb9** created 20:12:20Z, status **SUCCESS** (Railway MCP list_deployments); previous db4b96a6. Deploy log: "Ready in 191ms", Clerk dev telemetry notice only, no errors.
- No variables/config/link/credentials changed. API 8bf100cc and worker untouched. No production/judging deploy, no GPU/Meta call.

## Logged-out HTTP checks against https://web-dev-cd80.up.railway.app (20:15Z, Invoke-WebRequest, no redirects)
| Path | Status | Note |
|---|---|---|
| /api/workspace/jobs/s04o-probe | 401 | `{"error":{"code":"UNAUTHORIZED","message":"Sign in required."}}` — BFF auth unchanged |
| /workspace | 404 | logged-out 404 unchanged |
| /workspace/dev-fixture-0000 (not owner's scene) | 404 | other-scene 404 unchanged |
| / | 200 | public page up |

## NOT verified (blocker)
- ChatGPT in-app browser is not available in this worker chat: `cua.createBrowserTab("iab", …)` -> "Browser is not available: iab"; `cua.listBrowsers()` and `cua.getState().browsers` -> `[]` (after a REPL reset too). Chrome is forbidden by owner rule; no auth change attempted. So: no signed-in round trip, no screenshots, no 375px check.

## End-to-end defect found — FIXED in this run (controller-approved Owns extension, commit a09fe75)
S15n controller paths vs S13i API routes (Build/web/src/workspace/controller.mjs vs Build/api/workspace/jobs.py):
1. Chunk upload: controller `PUT uploads/{id}?offset=N`; API `PUT /uploads/{upload_id}/chunks/{offset}` -> upload will fail at first chunk (API 404/405 -> NOT_FOUND/INVALID_INPUT shown).
2. Job start: controller `POST jobs {upload_id}` after complete; API has no POST /jobs — `POST uploads/{id}/complete` already returns `{upload, job, provenance}` (RECORDED replay runs inline). Controller also reads `approved_clip` from the complete body (API returns `upload`/`provenance`).
3. Progress: controller `GET jobs/{id}/progress?after=`; API `GET /jobs/{job_id}?after=` (returns job_progress doc + provenance, kind/job_id match).
Fixed at root in controller.mjs: PUT uploads/{id}/chunks/{offset}; job taken from the complete response (provenance kept in snapshot; approvedClip shows the server-confirmed sha256 prefix); progress GET jobs/{id}?after=R, first read always runs so an already-ready RECORDED replay still shows its events. API not edited. Still unverified live (no signed-in browser): for S15o.

