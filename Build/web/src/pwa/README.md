# PWA manifest and icons (S19a)

- `manifest.mjs` is the source of truth + `validateManifest`; `public/pwa/manifest.webmanifest` is generated.
- `icons.mjs` draws the icon (pendulum glyph) procedurally; `build-pwa-assets.mjs` writes the PNG/SVG files.
- **Provenance:** every icon is original, authored in this run from geometric primitives and the project colour #155a92. No third-party logo, font, stock image or Meta/NASA/Clerk artwork is used or embedded. The icon is a placeholder brand mark, not a legal trademark clearance.
- Manifest has no `orientation` member (no orientation lock claimed).
- **Not done here (outside Owns):** linking the manifest from `src/app/layout.jsx` (`...pwaMetadata`), service worker (S19b), install guidance (S19c), installability evidence (S19d). The manifest lives under `/pwa/` with `scope: "/"`; S19b must serve any service worker from a path allowed to control `/`.

## Service worker caching (S19b)

- `cache-policy.mjs` (pure, allowlist) + `sw-glue.js` -> `node Build/web/src/pwa/build-sw.mjs` -> generated `public/pwa/sw.js`. Test `tests/pwa/sw-cache.test.mjs` runs the generated file in a vm with fake caches and fails if it is stale.
- Only GET, same-origin, query-free `/pwa/*` icons/manifest and `/_next/static/*` are ever intercepted. Everything else (HTML/navigations, `/api/*`, `/workspace/*`, uploads, cross-origin, Authorization/Range requests) is left to the browser: never fetched, never stored by the worker.
- Even allowed URLs are stored only if the response is 200, basic, not redirected, and lacks `Cache-Control: no-store|private|no-cache`, `Vary: Cookie|Authorization|*`, `Set-Cookie`, `Content-Range`, `WWW-Authenticate`.
- Sign-out hook: `navigator.serviceWorker.controller?.postMessage({ type: 'CLEAR_CACHES' })`.
- **Not wired (outside Owns):** registration. A worker at `/pwa/sw.js` controls only `/pwa/` unless the server sends `Service-Worker-Allowed: /` (e.g. `headers()` in `next.config.js`) and the page calls `navigator.serviceWorker.register('/pwa/sw.js', { scope: '/' })`. Until then the worker is inert on app pages. Do that in S19c/S19d or an integration run.
- Limits: FIFO trim at 100 entries; no offline page (navigations are never cached); not run in a real browser yet (S19d).

