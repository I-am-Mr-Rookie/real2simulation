# S04n evidence — web BFF proxy
Route: Build/web/src/app/api/workspace/[...path]/route.js (GET/POST/PUT, force-dynamic).
- Auth: same Clerk call as Build/web/src/auth/server-access.js readIdentity (`getClerkConfiguration().available` + `auth({acceptsToken:'session_token'})`); no userId -> 401 UNAUTHORIZED before any fetch.
- Config: WORKSPACE_API_URL / WORKSPACE_INTERNAL_TOKEN (names only) missing -> 503 DEPENDENCY_UNAVAILABLE; fetch error -> 502 DEPENDENCY_UNAVAILABLE.
- Body cap: lab-route readCapped pattern, bytes, 8388608 (policy chunk_bytes) for PUT uploads/*, 1000000 otherwise -> 413 INVALID_INPUT.
- Forward: `${WORKSPACE_API_URL}/internal/workspace/<encoded segments>?<query>`; headers only x-workspace-owner (Clerk userId), x-workspace-token, content-type, x-chunk-sha256. Client cookie/authorization/spoofed owner dropped. Response: upstream status/body/content-type + cache-control no-store; set-cookie dropped. '.', '..', empty or slash segments -> 404 before fetch. redirect: manual.
- Error body shape `{status:'error', error:{code,message}}` with workflow.mjs ERROR_CODES.

Checks (fresh, worktree): `node --test tests/web-workspace-api/*.test.mjs` 5/5 pass; `npm run build --prefix Build/web` exit 0, route listed `ƒ /api/workspace/[...path]` (temporary junction to canonical node_modules, removed after).

Integration gap (outside Owns): Build/web/src/proxy.js matcher is ['/workspace/:path*'], so clerkMiddleware does not run on /api/workspace/*; Clerk auth() throws there and this route fails closed (401) for everyone until the matcher adds '/api/workspace/:path*'. Unit tests mock auth(), so they do not prove deployed sign-in.

