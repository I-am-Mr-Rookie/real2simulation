# S15p evidence — web DEV redeploy (2026-10-30 UTC)

- Source: run/S15p-orch160 commit bd3c05d42c8ae7bc622ae7a051fbd97dd711d6a9 (controller/navigation/PrivateWorkspace + tests).
- Path: `python infra/railway/dev/stage.py web <temp dir>` (111 files) -> `railway up --detach --project b07b0d66-2001-4ccc-915d-7d226744d189 --environment c5823a28-5118-49d8-b4d6-9851fa8ccc45 --service 49f2938d-1566-480d-94e3-c9f7fefe24c2` (web, dev).
- **Deployment e6bf5fe2-6013-42a6-9337-33888fcc9a1e SUCCESS** (created 20:30:14Z, updated 20:31:29Z; Railway MCP list_deployments). Previous 197153d3 now REMOVED.
- Controller line for infra/railway/dev/deployments.json: `services.web.deploymentId = "e6bf5fe2-6013-42a6-9337-33888fcc9a1e"`, previous `197153d3-5f88-4287-8e21-d7cf77cb4d27`, sourceRevision `bd3c05d42c8ae7bc622ae7a051fbd97dd711d6a9`, verifiedUtc 2026-10-30T20:32Z.
- No variables/config/link/credentials changed. API and worker untouched. No production/judging deploy, no GPU/Meta call.

## Logged-out HTTP checks, https://web-dev-cd80.up.railway.app (20:32Z, no redirects)
| Path | Status |
|---|---|
| /api/workspace/jobs/s04o-probe | 401 (BFF auth unchanged) |
| /workspace | 404 |
| /workspace/dev-fixture-0000 | 404 |
| / | 200 |

## Not verified
- Signed-in browser walk (S15o's job; not attempted here, no Chrome).
- Live run success: see REPORT "Structural gap" — API validated_setup is a bare spec, so the browser simulator fails closed on dev until the API returns the S10 validated artifact.
