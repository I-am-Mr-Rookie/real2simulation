# S19d-orch142 REPORT
Lane CLAUDE; anthropic/claude-sonnet-5-5/medium (OpenCodex-managed; not polled). Window 2026-10-30T11:36:38Z-12:06:38Z. Branch run/S19d-orch142.
**Status: DONE** (deploy, installability, library/viewer walkthrough pass on live dev; caveats below).

## Result
- Redeployed main 7dde2c9 to DEV web only: stage.py web (107 files incl. Build/web/library-snapshot/guest.json) + railway up -> deployment aa539357-ca0f-4ecb-a6f5-523979e37295 SUCCESS (prev da4b03e9). First live proof of S04k snapshot staging: build/deploy succeeded, no error, no edits to stage.py/Dockerfile.
- /library now populated from the snapshot: 3 playable/setup cards + 15 UNAVAILABLE with reasons; SIMULATED/UNAVAILABLE/SCALE_UNVERIFIED labels; Mystery-g card is setup-only, answer withheld, points to /lab.
- /api/library/manifest 200; 3 artifacts 200, Cache-Control public, max-age=31536000, immutable, sha256 matches manifest (255-416 ms).
- PWA: manifest at /pwa/manifest.webmanifest 200 (linked in HTML; standalone, 192/512/maskable icons 200), /pwa/sw.js 200 with Service-Worker-Allowed "/". (/manifest.webmanifest and /sw.js at root are 404 by design.)
- In-app browser (not Chrome): projectile and pendulum replay open with SVG, Play and time slider; projectile and pendulum scrub (mouse/keyboard) and play verified (play runs to end); 375px no horizontal scroll on /library incl. open replay (scrollWidth 360); desktop 1265<=1280. Viewport override reset.
- Tests: node --test tests/pwa 52/52 pass. verify.py 9/10 (stale text for /workspace/private-check, outside Owns).
Evidence: evidence/S19/s19d-orch142.json.

## Not met / risks
- Credits: manifest has source description only; cards do not render a credit/licence line (credit/license empty). Product gap, not in Owns.
- Replays are only 0.2-0.25 s long, so a paused state is not observable (play reaches the end faster than the tool round trip); no real install prompt/device; APK deferred. SW re-verified in the in-app browser via CDP: registration scope https://web-dev-cd80.up.railway.app/, state activated, script /pwa/sw.js, secure context.
- In-app browser CDP repeatedly timed out; timings include tool overhead.
- deployments.json updated (IDs/limit text only: web deploymentId aa539357, previous da4b03e9).

## Ponytail
Reused stage.py/railway up/verify.py, existing 52 tests, in-app browser; no code added. Skipped: fixing credit rendering, APK. Communication: silent.

