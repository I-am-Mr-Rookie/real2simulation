# S19d-orch69 REPORT
Lane CLAUDE, anthropic/claude-sonnet-5-5/medium (OpenCodex-managed; not polled). Start 2026-10-30T05:08:58Z (issue); end 2026-10-30T05:16:49.609Z. Verdict: **PARTIAL**.

## Results
- Unit: `node --test tests/pwa/*.test.mjs` -> 52 pass / 0 fail (manifest, SW cache policy, install guidance). Note: `node --test tests/pwa` (dir form) fails on this Node; use the glob.
- Deployed dev (web-dev-cd80.up.railway.app) is NOT installable: /pwa/manifest.webmanifest, sw.js and all 3 icons return 404; HTML has no `<link rel=manifest>`, no theme-color. The deploy predates S19c assets, and no source under Build/web/src outside pwa/ references the manifest or SW glue (app layout belongs to S04, outside my Owns).
- 375px walkthrough (in-app browser, 375x812) on /, /library, /lab: scrollWidth 360 <= 375 (no horizontal scroll); footer banner "Development build. Synthetic lab results are not calibrated measurements. No uploads are enabled." present on all three; library shows "Viewer not connected / not a reconstruction or simulation result". Viewport reset afterward.
- Install-prompt eligibility: not observable (no manifest/SW served; no local Next build: Build/web has no node_modules, installs forbidden).
- Evidence: evidence/S19/s19d-375-results.json.

## Needed to finish (not done)
1. Controller/S04 owner: wire `<link rel=manifest href=/pwa/manifest.webmanifest>`, theme-color and sw-glue registration into the app layout, build SW, redeploy dev (new deploy needs authorization/other run).
2. Re-run installability check after deploy (DevTools Application / install eligibility) + workspace walkthrough (S15k/S15l pending).
APK deferred.

## Ponytail
No code changed (no PWA defect fixable within Owns; the gap is layout wiring outside Owns). Reused existing tests and deployed site; no new tooling. Skipped: screenshots as files (REPL lacks fs), local build, service-worker scope runtime check. Risk: installability is unproven.
Communication: silent; one completion line only.
