# PWA manifest and icons (S19a)

- `manifest.mjs` is the source of truth + `validateManifest`; `public/pwa/manifest.webmanifest` is generated.
- Icons are the logo v2 files in public/brand (S15ap); build-pwa-assets.mjs writes only the manifest.
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


## Install guidance and orientation (S19c)

- `install-guidance.mjs` (pure): `getInstallGuidance` picks iOS / Android / desktop steps from the user agent; `orientationAdvice` only suggests landscape on narrow portrait screens. `install-client.mjs` captures `beforeinstallprompt` (preventDefault, single use), `appinstalled`, standalone state and resize/orientation changes. `InstallGuidance.jsx` is a small client component (renders nothing on the server or once installed). Tests: `tests/pwa/install-guidance.test.mjs`.
- **What the guidance says, and why it is true:**
  - Android (Chromium family): install via the browser menu; an in-page Install button appears only after the browser really fires `beforeinstallprompt` (Chromium-only, non-standard; not in Safari or Firefox). Install needs HTTPS (or localhost). Menu wording varies, so Firefox / unknown browsers get hedged text, no invented UI.
  - iOS / iPadOS: no install prompt exists, so the steps are manual: Share > Add to Home Screen (if missing: Edit Actions). Third-party iOS browsers can add to the Home Screen only on 16.4+. iPadOS with a desktop-class user agent is detected via `maxTouchPoints`.
  - Installing is optional and does **not** give offline simulations or video (the service worker caches only icons/manifest/static assets, see S19b).
- **Orientation: nothing is locked.** The manifest has no `orientation` member (validator and test enforce it). The code never calls `screen.orientation.lock()`: that API is unavailable on iOS Safari, needs fullscreen/installed context on Android, and always throws in desktop Chrome per MDN BCD; a lock is not needed for the lab. The UI only says rotation follows device settings and that landscape gives more room. A test greps `src/pwa` for a lock call.
- **Not done (outside Owns):** mounting `<InstallGuidance />` in a page/layout, service-worker registration + `Service-Worker-Allowed`, real-device checks (S19d). Guidance text is unit-tested against fake windows only; no real iOS or Android device or browser install was exercised.

### Sources (checked 2026-10-29)

- Install criteria (HTTPS, manifest, icons 192/512): https://web.dev/articles/install-criteria
- MDN, making PWAs installable (HTTPS/localhost; per-platform install): https://developer.mozilla.org/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable
- MDN, `BeforeInstallPromptEvent` (Chromium only, non-standard): https://developer.mozilla.org/docs/Web/API/BeforeInstallPromptEvent
- Apple, Add to Home Screen incl. Edit Actions: https://support.apple.com/guide/iphone/iph42ab2f3a7/ios
- WebKit, third-party browsers can Add to Home Screen from iOS/iPadOS 16.4: https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/
- MDN, `ScreenOrientation.lock()` (Safari iOS: no; desktop Chrome: always NotSupportedError; BCD 8.1.7): https://developer.mozilla.org/docs/Web/API/ScreenOrientation/lock
- MDN, manifest `orientation` (not supported on Safari iOS): https://developer.mozilla.org/docs/Web/Progressive_web_apps/Manifest/Reference/orientation
