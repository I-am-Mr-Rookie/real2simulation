# S15av-orch214 REPORT: DONE

Lane CLAUDE, model anthropic/claude-opus-5-5 high (assigned). UTC start 2026-10-31T14:00:00Z, work stopped 2026-10-31T14:10:59+00:00.
Branch run/S15av-orch214, worktree .worktrees/S15av-orch214, base main d7ba6433. Coding quota: OpenCodex-managed; not polled.
Tokens/cost: unknown (not observable). No paid, GPU, Meta, Railway or deploy action.

## Root cause
Deployed DEV web runs NODE_ENV=production in node:22-bookworm-slim (no Python). /api/lab rejected production
(local_lab_disabled) and its bridge spawns python Build/lab/session-bridge.py, which itself spawns node simulate.mjs.
So python is NOT reliably present in the web container (verified from infra/railway/dev/web.Dockerfile, not guessed).

## Change (smallest complete)
- Build/lab/session-service.mjs: one new remoteBridge() + callBridge switch. In production the existing handleLab
  (sessions, Mystery-g private state, schema checks, 64-session/4-bridge caps, DTO checks) is unchanged; only the two
  fixed bridge actions go to WORKSPACE_API_URL + /internal/lab/bridge with x-workspace-token (30 s timeout, 1 MB response cap).
  Local dev/test keep the localhost Python bridge.
- Build/web/src/app/api/lab/route.js: production allowed with same-origin check (x-forwarded-host or host); dev/test keep
  localhost-only. Every error gets a friendly error.message ending in a retry hint (LabClient already shows message
  before code, so no client change). 1 MB body cap kept.
- Build/api/lab/__init__.py (new) + 1 registration line in Build/api/health/app.py: POST /internal/lab/bridge, token
  checked with hmac.compare_digest against WORKSPACE_INTERNAL_TOKEN (unset fails closed), 1 MB body cap, JSON parse
  guard, then the SAME session-bridge.handle (strict action/key/template schema, 2000-sample cap, 20 s simulator timeout).
  Mounted before the Redis-dependent routers so it works without Redis.
- infra/railway/dev/stage.py: api allowlist adds Build/lab bridge files, Build/templates/, Build/instruments/,
  export_validated_setup.py, room-v1 synthetic scene, 3 simulator .mjs files.

Reuse: existing handleLab, session-bridge.handle, WORKSPACE_API_URL/WORKSPACE_INTERNAL_TOKEN pattern from the workspace
BFF proxy, auth.TOKEN_ENV. No new dependency, no new Railway variable. Mystery-g / SIMULATED / what-if labels untouched.

## Owns exceptions (controller please accept or reject)
- infra/railway/dev/api.Dockerfile (+2 lines): COPY --from=node:22-bookworm-slim /usr/local/bin/node, and `node --version`
  in the build smoke. Required: the bridge spawns node; without it the API returns synthetic_simulator_failed.
- infra/railway/dev/test_stage.py (1 line): expected api manifest now includes Build/simulator/rk4.mjs (fixture file).

## Checks (fresh, this worktree)
- node --test tests/lab, workspace, shell-workspace, web-private, web-workspace-api, pwa: 341 tests, 340 pass, 1 fail =
  contact-integration (missing Build/simulator/node_modules in fresh worktree); after junctioning canonical node_modules it
  passes 2/2. Log: evidence/S15av/node-tests.txt.
- New tests/lab/remote-bridge.test.mjs (5): production Mystery-g start+fit via HTTP stub running the real bridge, no private
  fields before reveal, normal trial, missing config and wrong token give friendly retry messages, cross-origin/schema/
  oversize/bad JSON rejected without reaching the API.
- New tests/lab/test_api_lab_bridge.py (3) + tests.lab.test_session_bridge + infra.railway.dev.test_stage: 21 OK.
- Updated lab tests: old "production route remains disabled" replaced by production guard test; r14 HTTP parser tests
  now strip the added message before comparing envelopes.
- npm run build (Build/web): Compiled successfully; /api/lab dynamic. Log: evidence/S15av/web-build.txt.
- stage.py api from commit 007a0e7 into a temp dir, then app imported from that dir only: start free_fall(mystery)/
  projectile/ramp/pendulum ok (201/201/201/1001 samples), fit ok, no token 401. evidence/S15av/staged-api-probe.txt.

## Not verified / risks
- Docker image build not run (Docker daemon off): Node binary copy into python:3.12-slim assumes libstdc++6 (present via
  apt in Debian slim). Build smoke `node --version` fails the build if wrong.
- Live DEV not exercised (controller deploys). Assumes WORKSPACE_API_URL + WORKSPACE_INTERNAL_TOKEN already set on web and
  api (STATE.md says so) and that Railway forwards host/x-forwarded-host matching Origin.
- In-memory sessions per web replica (unchanged design); a multi-replica web would need sticky sessions.
- Skipped: per-IP rate limiting (existing 4-bridge cap + 64-session cap bound load), LabClient retry button (message says
  try again; Run button stays usable).

## Deploy steps (controller)
1. Fast-forward main to run/S15av-orch214 after review.
2. `python infra/railway/dev/stage.py api <new-dir>` then `railway up --detach` that dir to the DEV api service (as README).
3. `python infra/railway/dev/stage.py web <new-dir>` then `railway up --detach` to the DEV web service.
4. Railway variables (names only, both already recorded): web WORKSPACE_API_URL, WORKSPACE_INTERNAL_TOKEN; api
   WORKSPACE_INTERNAL_TOKEN. No new variable.
5. Smoke: open /lab, Run trial (normal) then Guess the Gravity, fit and reveal; POST /internal/lab/bridge on api without
   token must be 401.

Communication: silent; one completion line only.
