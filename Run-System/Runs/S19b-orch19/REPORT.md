# S19b-orch19 REPORT — DONE
Lane/model: CLAUDE, anthropic/claude-sonnet-5-5 high. OpenCodex-managed; quota not polled. Tokens/cost: unobservable.
UTC start 2026-10-29T11:53:52Z; work stopped 2026-10-29T12:01:05+00:00 (verified fully DONE; early finish permitted).

## What changed
- `Build/web/src/pwa/cache-policy.mjs`: pure **allowlist** policy. Request side: GET, same-origin, no creds-in-URL, no Authorization/Range, not navigation, and path is exactly a precached `/pwa/*` file (no query) or under `/_next/static/`. Response side: 200, `type basic`, not redirected, no `Cache-Control no-store|private|no-cache`, no `Vary Cookie|Authorization|*`, no `Set-Cookie`/`Content-Range`/`WWW-Authenticate`.
- `sw-glue.js` (install precache, activate old-version cleanup, `CLEAR_CACHES` message for sign-out, cache-first fetch with FIFO trim at 100) and `build-sw.mjs` -> generated `Build/web/public/pwa/sw.js`.
- `tests/pwa/sw-cache.test.mjs` (39 tests): runs the *generated* sw.js in a node vm with fake caches/fetch.
- README section added with limits and the wiring note.

## Evidence (fresh)
- `node --test tests/pwa/manifest.test.mjs tests/pwa/sw-cache.test.mjs`: 44 pass, 0 fail (5 S19a + 39 new). Multi-file run is slow (~40 s, S19a icon render), single file ~2 s.
- Never intercepted (respondWith not called, no fetch, nothing stored): /api/lab GET+POST, dot-segment and %2e%2e traversal from /_next/static into /api, /workspace/*, navigations, /uploads/*, signed upload URL, upload-looking path under /pwa, Authorization header, Range, cross-origin, credentialed URL, query on pwa asset, unlisted /pwa/sw.js, PUT, navigation to allowed path.
- Allowed URL but unsafe response returned to page yet not stored: no-store, private, no-cache, Vary Cookie/Authorization/*, Set-Cookie, WWW-Authenticate, 206, redirected, opaque, 401/404/500.
- Mutation checks (temporary, restored): dropping `private` -> 1 fail; allowing `/api/` -> 3 fail; ignoring Set-Cookie -> 1 fail; removing navigate guard -> undetected, then added a test for it (redundant guard; allowlist already excludes navigations).
- Committed sw.js equals regenerated output (test).

## Ponytail choices
Reused S19a layout/node:test style; no dependency (no Workbox); allowlist instead of an ever-growing blocklist; one generated file so tests cover shipped code; skipped offline page, LRU, background sync, runtime caching of HTML/API/images/video; no registration helper (outside Owns).

## Limits / risks
- **Worker is inert in the app**: not registered, and /pwa/sw.js can only control /pwa/ unless the server sends `Service-Worker-Allowed: /` (next.config.js, outside Owns) plus a register call in layout. Needed by S19c/S19d or integration.
- Verified only against a fake Cache/fetch in vm; no real-browser run (S19d). Fake responses model headers; real browsers hide Set-Cookie from SW (guard is belt-and-braces). `_next/static` caching is cache-first on hashed URLs; if a deploy reuses URLs with different bytes, bump CACHE_VERSION.
- No gate/real-scene/physical evidence claimed. No deploys, installs, servers, or edits outside Owns.
- Communication compliance: silent; one completion message to controller only.
