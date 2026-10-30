# S04n-orch145 REPORT — DONE
Lane CODEX-2 (army: Claude); model anthropic/claude-opus-5-5/medium; coding quota OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable); paid calls 0; deploys 0.
UTC issued 2026-10-30T11:40:47Z; work stopped 2026-10-30T11:53:49Z. Base main 1235cca; branch run/S04n-orch145.

## Changed
- Build/web/src/app/api/workspace/[...path]/route.js (new): Clerk-authenticated BFF -> `${WORKSPACE_API_URL}/internal/workspace/<path>`; details evidence/S04n/README.md.
- tests/web-workspace-api/proxy.test.mjs (new): 5 tests, real route imported with mocked Clerk + mocked fetch.
- Build/web/src/proxy.js: matcher ['/workspace/:path*', '/api/workspace/:path*'] — **Owns extension approved by controller** (clerkMiddleware did not run on /api/workspace, so auth() would throw -> route 401 for all users).
- tests/web-private/repository.test.mjs: :73 regex updated to two-entry matcher; '/api/workspace/x' positive case in actual-Next-matcher test — **Owns extension approved by controller**, limited to those two lines.
- evidence/S04n/README.md, this run's PLAN/TIMEBOX/REPORT.

## Acceptance
1. Signed-out / Clerk unavailable -> 401 UNAUTHORIZED, zero upstream fetches — PASS (test 1).
2. Forwards only x-workspace-owner/x-workspace-token (+content-type, x-chunk-sha256 needed by chunk contract); cookie/authorization/spoofed owner dropped; set-cookie dropped; cache-control no-store; 8 MiB PUT uploads/* accepted, 8 MiB+1 and JSON >1 MB -> 413 — PASS (tests 2-3).
3. Missing WORKSPACE_API_URL or token -> 503 DEPENDENCY_UNAVAILABLE (502 on unreachable) — PASS (test 4); `npm run build --prefix Build/web` exit 0, `ƒ /api/workspace/[...path]` + Proxy listed (rerun after proxy.js edit).

## Fresh checks
- `node --test tests/web-private/*.test.mjs tests/web-workspace-api/*.test.mjs` -> 15/15 pass (before the test edit: 14/15, :73 literal pin).
- `npm run build --prefix Build/web` -> EXIT=0 (twice; temp junction to canonical Build/web/node_modules, removed via non-recursive Directory.Delete).

## Ponytail
Reuse: same Clerk call as server-access.js readIdentity (getClerkConfiguration + auth({acceptsToken:'session_token'})) — could not import it (not exported; file read-only); lab route readCapped pattern copied with cap param + byte return (lab route unowned, its 1 MB/text version cannot carry chunks). Error shape uses workflow.mjs ERROR_CODES. One route file, no helper module, no new dependency; native fetch/Response. Test reuses web-private registerHooks mocking pattern.
Skipped: streaming passthrough (buffered, per PLAN R5), DELETE/PATCH methods (no contract row), retries, upstream header passthrough beyond content-type.

## Risks / limits
- Deployed Clerk sign-in through this route not verified (auth mocked; no deploy this wave). Middleware now runs on /api/workspace; its catch returns 404 (not 401) if clerkMiddleware itself throws.
- Upstream API routes (S14i/S13i) not yet present; contract only. Token/URL are names only, values not read.
- Path segments are encodeURIComponent'd; '.', '..', empty, slash/backslash -> 404.

Communication: two controller-authorized nonterminal blocker messages (matcher, test pin); one final line.
Next: S04m sets WORKSPACE_API_URL/WORKSPACE_INTERNAL_TOKEN on web; S04o consumes /api/workspace.

