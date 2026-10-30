# S15o-orch161 — DEV walk (WALK.md)

Date: 2026-10-30 (UTC). Web https://web-dev-cd80.up.railway.app (deploy e6bf5fe2). API deploy a2777e67.
**Result: the signed-in walk could NOT be performed.** The ChatGPT in-app browser (iab) is unavailable in this worker chat
(`cua.createBrowserTab("iab", ...)` -> `Browser is not available: iab`; `cua.getState().browsers = []`; retried at 20:37Z, 20:43Z and later,
same error). Chrome / Playwright / any fresh browser were NOT used (owner: in-app browser only; a fresh browser is not the signed-in
profile and auth must not be changed). No screenshots exist; none were fabricated. Only logged-out HTTP checks were possible.

## Approved clip check (PASS)
RM04 = test-data/public/RM04.mp4 (25,336,829 bytes). sha256 8231fbca041d030f2fc39bd4281af6112e476bf811f548fc9019db53f7cb87ec equals the approved
value recorded in evidence/S07/S07b-errata/audit-orch58/README.md and tests/api-workspace/test_jobs.py (RM04_SHA). Clip was NOT uploaded.

## Stage table
| # | Stage | Result | Evidence / note |
|---|-------|--------|-----------------|
| 1 | Open own workspace (signed in) | NOT-RUN (iab unavailable) | logged-out /workspace -> 404 (by design, hides from anonymous) |
| 2 | LIVE notice (not fixture notice) | NOT-RUN | source text: LIVE_NOTICE in Build/web/src/shell/PrivateWorkspace.mjs:17. Not seen live. Logged-out bundle contains no workspace chunk (0 hits for LIVE notice) |
| 3 | Upload approved RM04 clip | NOT-RUN | sha256 verified only |
| 4 | RECORDED progress labels (S13h-orch46 / S14g-fix3) | NOT-RUN | |
| 5 | Job ready | NOT-RUN | |
| 6 | Interview questions -> answer | NOT-RUN | |
| 7 | Spec accepted, label 'scale unverified, not setup-validated' | NOT-RUN | string not present in logged-out pages/bundle (expected: it is a server-sent label from the S14j spec route) |
| 8 | Run (EXPECTED-BLOCKED by design: synthetic scenes only, Q20 pending) | NOT-RUN | exact error text NOT captured |
| 9 | Fit / HTML report | NOT-RUN | |
| 10 | 375px viewport, no horizontal scroll | NOT-RUN | needs a browser |
| 11 | No secret/token in UI or network panel | PARTIAL | logged-out only, see below; signed-in network panel not inspected |
| 12 | No paid call | PASS | no model/GPU/provider call made; only unauthenticated GETs and local hashing |

## Logged-out HTTP checks (what was actually verified)
| Request | Status | Notes |
|---|---|---|
| GET / | 200 text/html | |
| GET /library | 200 | |
| GET /lab | 200 | |
| GET /sign-in | 200 | |
| GET /workspace | 404 | owner-only route hidden when logged out |
| GET /api/library/manifest | 200 application/json | public library manifest |
| GET /api/workspace/jobs | 401 | body `{"status":"error","error":{"code":"UNAUTHORIZED","message":"Sign in required."}}` |
| GET /api/workspace/health | 401 | same body |
| GET /api/health | 404 | not a route |
| GET api-dev-6091.up.railway.app /health, /healthz, /jobs, /workspace/jobs | 404 | API root is internal; paths not probed further |

Secret scan of 5 logged-out HTML pages + 15 JS chunks (784,787 bytes): 0 hits for sk-/sk_live/Bearer/hf_/AKIA/ak-/postgres:///redis:///
WORKSPACE_INTERNAL_TOKEN. One Clerk **publishable** key (`pk_test_...`, public by design) appears in the page, plus SDK prefix-check strings
(`pk_live_`/`pk_test_` without key bodies). Note: the dev web uses a `pk_test_` Clerk key (expected for DEV). No value is recorded here.

## Defects / findings
None newly observed (nothing past the logged-out layer was exercised). Carry-over, not re-verified: S04o notes (run step, instruments, report shape) were
addressed in S15p; whether they work live is still UNVERIFIED.

## Blocker and next action
Need the in-app browser in a chat where `iab` exists (controller or owner session). Re-run S15o from stage 1; clip hash already verified
(sha256 above). No code change is implied by this run.

