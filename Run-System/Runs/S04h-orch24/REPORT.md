# S04h-orch24 REPORT
Status: **PARTIAL** (build fix + deploy + guest/health E4 done; Google/OTP completion needs the owner). Lane/model: anthropic/claude-sonnet-5-5 high; coding quota: OpenCodex-managed; not polled. Tokens/cost: unobservable.
Window: issued 2026-10-29T15:03:04Z, deadline 15:33:04Z, work stopped 2026-10-29T15:15:10+00:00 (finished early because every remaining criterion needs owner login/consent, see owner-fallback; no safety exception claimed).
Branch/worktree: run/S04h-orch24 at .worktrees/S04h-orch24 (merged main 73303c1 first). Not merged into main; controller integrates.

## Defect fixed
Cause: web src imports `../../../simulator/*` (src/lab/browser-simulator.mjs) and `../../../../../lab/session-service.mjs` (src/app/api/lab/route.js); stage.py web allowlist and web.Dockerfile did not ship them (deploy 7e6e079d FAILED).
Fix (smallest): stage.py web prefixes += exact files Build/lab/session-service.mjs and Build/simulator/{trajectories,extended-templates,mystery-g,replay,rk4}.mjs (exact names, not the whole dir: keeps rapier/package.json/py out); web.Dockerfile `COPY Build/simulator /simulator` + `COPY Build/lab /lab` (the relative imports resolve to /simulator and /lab under WORKDIR /app). test_stage.py web fixture/expectations extended. Commit 45f4335.
Checks: `python -m unittest discover -s infra/railway/dev -p "test_*.py"` 14/14 OK. Docker daemon not running locally, so emulated the Dockerfile: staged context from committed 45f4335, laid out /app,/simulator,/lab, `npm install` + `npm run build` (next build --webpack, no next.config.js as in the image) -> compiled, routes incl. /api/lab and /lab. Negative control: same layout without /simulator and /lab fails with `Module not found: ../../../simulator/extended-templates.mjs` (reproduces the Railway failure). The real Railway build is the final proof (below).

## Deploy (dev only, owner-approved Oct27)
`railway up --detach` of the fresh staged context, existing web service 49f2938d..., dev env. Deployment **8a9bdc9f-afb7-40cc-b690-f0a17a6e030f** created 15:10:19Z, status SUCCESS. Prior ids: 8ab5d816 (SUCCESS, 790f976), 7e6e079d (FAILED). API d520a4f9 and worker 533e73fe untouched. No env/config/secret changes; no `railway link` (config untouched). deployments.json updated (web id/source revision/limits; key order/format rewritten by json dump).

## Verifier refresh
infra/railway/dev/verify.py had one stale expectation (/sign-in "Sign-in unavailable" fallback, gone since Clerk keys were set Oct29); changed to "Sign in to Real2Simulation" in verify.py and test_verify.py. 14/14 offline tests OK; live `verify.py` exit 0, 10/10 pass (evidence/S04/s04h/verify-live.json).

## E4 evidence (agent-observed, 2026-10-29)
- Health: evidence/S04/s04h/live-probe.json (15:11:37Z). API /health/live 200 ok, /health/ready 200 ok (postgres, redis, bucket ok), /api/version 200; worker /health/live 200, /health/ready 503 unavailable (redis/bucket ok, heartbeat unavailable = expected, no consumer), /api/version 200. Both report revision 300cd20 (unchanged API/worker builds).
- Guest route (in-app browser only, signed out): / , /library ("Guest browsing needs no account", no demos), /lab (new on this deploy; synthetic lab UI renders: evidence/S04/s04h/lab-guest.png, library-guest.png), /workspace/private-check -> "Page unavailable" (404, private boundary holds).
- Sign-in: /sign-in and /sign-up 200; Clerk widget renders (console: dev-keys warning only) with Continue with Google and email field. Clerk public environment (evidence/S04/s04h/clerk-public-environment.json): Google OAuth enabled, email first factor with email_code verification.
- Google: clicking Continue with Google reached Google's account chooser for the Clerk dev OAuth client (redirect clerk.shared.lcl.dev), i.e. hand-off works. I stopped there (see owner-fallback). Screenshots of the sign-in form/chooser were NOT saved: they show owner emails and browser-autofilled credentials.
- Clerk did not block anything; no log fallback needed.

## Owner-fallback (not done by agent)
1. Google: chooser lists 3 owner Google accounts; picking one and the Google consent for "Clerk" (email/profile) is a login + access grant. Not performed unattended. To finish: owner picks account at /sign-in, confirms the header shows the account menu.
2. Email OTP: needs the inbox code; not accessible. Owner S01b E2 receipt stands (evidence/owner/S01/S01B-RECEIPT.md); no new agent E4 for completed Google/OTP sign-in.

## Findings / limits
- /lab Run trial on Railway returns `local_lab_disabled` (no Python bridge/Build/lab files in the web image; by design local-only). Nav now shows "Local simulation lab" on dev; consider hiding or labelling it on Railway (outside Owns: Build/web/src is mine but unchanged here to keep scope).
- Docker not run locally (daemon off); emulated layout only. Transitive npm versions unpinned (existing limit).
- Temp build dir left at %TEMP%\s04h-run1 (outside repo, contains node_modules); no servers left running; IAB tab closed.
- Not merged/pushed; no production/judging deploy; no gate/real-scene/physical claim.

## Ponytail
Reused stage.py's own prefix mechanism and existing Dockerfile/test patterns: 2 added lines in stage.py, 2 COPY lines, test fixture entries; no new tool, no whole-dir staging, no Dockerfile restructure. Added only a ~30-line read-only probe (evidence/S04/s04h/probe.py) because verify.py is stale (hard-codes 300cd20 and "Sign-in unavailable" fallback). Skipped: rewriting verify.py, hiding the lab nav, a mobile-viewport check.
Communication: silent; one final line to controller as mandated.

