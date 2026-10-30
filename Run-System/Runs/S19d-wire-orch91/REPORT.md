# S19d-wire-orch91 REPORT
Lane CLAUDE; anthropic/claude-sonnet-5-5/medium (OpenCodex-managed; not polled). Start 2026-10-30T06:24Z. Status: DONE (local scope). Branch run/S19d-wire-orch91.

## Changes
- Build/web/src/pwa/SwRegister.jsx (new): registers /pwa/sw.js, scope '/'.
- Build/web/src/app/layout.jsx: metadata.manifest + icons, mounts SwRegister. Kept UI-a fonts and themeColor #f3eee3.
- Build/web/next.config.js: headers() adds Service-Worker-Allowed: / and Cache-Control: no-cache on /pwa/sw.js. **Owns deviation**: file is outside the Owns list but scope '/' is impossible without it (README of S19b says so). Controller should accept or revert.
- evidence/S19/check-served.mjs, s19d-wire-served.json, s19d-wire-browser.json.
- Public assets already existed in Build/web/public/pwa; no change needed. Cache rules (S19b cache-policy) untouched.

## Fresh checks
- next build --webpack OK (junction node_modules, no installs). next start :3919.
- manifest 200 application/manifest+json; sw.js 200 with Service-Worker-Allowed "/"; icon-192/512/maskable/svg 200. HTML head has manifest link, theme-color, icons.
- In-app browser: SW activated at scope '/', cache r2s-static-v1; 375px: no horizontal scroll on /, /library, /lab.
- node --test tests/pwa/*.test.mjs: 52 pass. python -m unittest Build/web/src/shell/test_contract.py: 7 OK.

## Not done / risks
- InstallGuidance not mounted (ShellFrame outside Owns; separate row). Installability only by criteria observed (manifest+192/512 icons+SW+HTTPS on localhost); no real install prompt or device test. Dev (Railway) not redeployed or re-checked; manifest/theme_color (#155a92) differs from layout themeColor (#f3eee3), left as is. Layout is force-dynamic; sw never caches navigations. APK deferred.
- Communication: silent; one final line to controller.

