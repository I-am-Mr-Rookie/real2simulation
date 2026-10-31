# S15av-orch214 PLAN

Objective: public /lab (Run trial, fit, Mystery-g) works on deployed DEV (NODE_ENV=production) without raw error codes.

Approach (smallest safe): web container has no Python, so in production the web /api/lab route keeps sessions in Node
(handleLab unchanged) and sends only the fixed bridge actions to the API service at WORKSPACE_API_URL + /internal/lab/bridge
with WORKSPACE_INTERNAL_TOKEN. The API runs the same Build/lab/session-bridge.py. API image gets the Node binary
(COPY --from node:22-bookworm-slim) because the bridge spawns Build/lab/simulate.mjs. Friendly error.message on every error.

Owns: Build/web/src/app/api/lab/, Build/lab/session-service.mjs, Build/api/lab/ (+ app.py registration line),
infra/railway/dev/stage.py, tests/lab/, evidence/S15av/, Run-System/Runs/S15av-orch214/.
Owns exceptions needed (reported): infra/railway/dev/api.Dockerfile (2 lines), infra/railway/dev/test_stage.py (expected set).

Checks: new node + Python tests; node --test lab/workspace/shell-workspace/web-private/web-workspace-api/pwa; test_stage;
npm run build; stage.py api context runs the bridge end to end. No deploy.
