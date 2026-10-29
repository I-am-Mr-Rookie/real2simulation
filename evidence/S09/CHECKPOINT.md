# S09 checkpoint — 3D viewer evidence (S09a–S09j)

Consolidation of existing evidence plus one fresh S09j check (2026-10-29 UTC). Measured numbers only, each with its source.
Two evidence classes are kept separate; neither is Gate R, physics, calibrated-scale or production evidence.

## A. Synthetic fixture (authored S05a room-v1; no reconstruction, accuracy or performance claim)

Banner in UI: "SYNTHETIC fixture — authored geometry, not reconstruction, physics or Gate R evidence".
Runner: tests/viewer/browser-smoke.mjs (headless chrome-headless-shell, SwiftShader WebGL2) + node unit suites with fake DOM.

| Capability | Run | Result | Source |
|---|---|---|---|
| Adapter + synthetic scene contract | S09a | 11/11 unit; scene validator PASS synthetic=True | [S09a.md](S09a.md) |
| three.js points + orbit, leak-free unmount | S09b | smoke ok; after abort geometries 0, context lost | [S09b.md](S09b.md) |
| Validating loader (sha256, allowlist, size/point limits) + splat decode | S09c | 24/24 unit; 7 mutations each caught | [S09c.md](S09c.md) |
| Colliders, camera path, labels | S09d | alignmentIssues [], pointsOnFace [4,4] | [S09d.md](S09d.md) |
| DPR/detail budget | S09e | 375@3 → tier reduced, DPR 1.5, no AA; 800@1 → full, DPR 1 | [S09e.md](S09e.md) |
| Pause when idle/hidden/offscreen | S09f | idleFrames 0, framesWhileOffscreen 0, resume 1 frame | [S09f.md](S09f.md) |
| 375 px compact layout | S09g | scrollW 375 = viewport; buttons 44×44 inside viewport, hit true | [S09g.md](S09g.md) |

Fresh S09j re-run (this worktree, main be06dda): `node --test "tests/viewer/*.test.mjs"` → 46/46 pass, 0 skip (local media
present via temporary junction); `SMOKE_DEVICE=375x667@3 node tests/viewer/browser-smoke.mjs` → ok true, layoutOk true,
viewportW 375 / scrollW 375 / canvasCssW 359, buttons 44×44 (left 211..right 359); default 800 px → ok true, scrollW 800, mode full.

## B. Real reconstruction scenes RM02 / RM04 / RM05 (MapAnything nominal output, metric scale **UNVERIFIED**)

Banner in UI: "RECONSTRUCTION — metric scale UNVERIFIED (nominal model output, not calibrated); not physics or Gate R evidence".
Gate R FAIL → S05f **Fallback 2** (planes + boxes); these bundles are points only — no Fallback-2 surfaces/colliders exist in them,
none invented. RM05 is UNAPPROVED_CANDIDATE / SCENE_ONLY_UNTIL_SCALE_VERIFIED (NASA PD ISS interior, microgravity, display-only).
Bundles: 20000 points each, scale status `estimated`, rebuilt CPU-only by Build/gpu/scene_job.py; sha256/provenance in
[S09h-real-scenes.md](S09h-real-scenes.md).

Load (S09h): all three `loading,ready` in node (real-scenes.test.mjs) and in-app browser at 1280 px and 375 px; scrollWidth 375.

Performance (S09i, measured; HP 250 G7, i3-1005G1, Intel UHD via ANGLE D3D11, ChatGPT in-app browser, DPR 1; 6 s 360° orbit):

| Scene | View | fps mean | frame ms p50/p95/max | frames >33 ms | JS heap |
|---|---|---|---|---|---|
| RM02 | 1280 | 59.97 | 16.7 / 16.9 / 18.1 | 0 | 14.3 MB |
| RM04 | 1280 | 59.97 | 16.7 / 17.0 / 19.7 | 0 | 14.3 MB |
| RM05 | 1280 | 59.97 | 16.7 / 17.1 / 22.9 | 0 | 14.9 MB |
| RM02 | 375 | 56.32 | 17.8 / 18.2 / 19.5 | 0 | 15.0 MB |
| RM04 | 375 | 56.40 | 17.7 / 18.3 / 18.7 | 0 | 15.0 MB |
| RM05 | 375 | 56.31 | 17.7 / 18.4 / 22.2 | 0 | 15.0 MB |

Source: [S09i-perf.md](S09i-perf.md), raw [S09i-perf.json](S09i-perf.json). ≥30 fps acceptance met (min 56.3 fps).

Fresh S09j visual check (ChatGPT in-app browser, tests/viewer/real-scenes.html via python http.server 127.0.0.1, stopped):
desktop 1280 px RM02/RM04/RM05 and viewport override 375×812 (reset after) RM02/RM04/RM05 → all `loading,ready`,
scale=estimated, UNVERIFIED banner shown, scrollWidth = viewport (1280 / 375), at 375 canvas 375×650 CSS px, buttons 44×44
(left 219..right 367), keyboard focus ring visible on Zoom in, no console errors/warnings. Screenshots not saved (derived scene media, gitignored).

## Visual defects

None found in the viewer at 375 px or desktop in the S09j check, so no viewer code changed. Observations, not fixed (not defects / out of scope):
desktop framing leaves the cloud in roughly the central third (bounds-based fit, outlier points widen bounds); the banner is plain
text below the canvas (host page owns styling). tests/viewer/browser-smoke.html prints its one-line JSON result unwrapped, so that
harness page scrolls horizontally after the run — harness only, measurements are taken before printing.

## Known limits

- rAF is vsync-capped (~60 Hz): fps cannot show headroom; only draw JS p95 ~0.3 ms indicates it. GPU completion time not measured.
- No VRAM/GPU memory measurement (browser does not expose it); JS heap is coarse `performance.memory`.
- 375 px is viewport emulation (IAB override / headless device metrics), not a real phone; no real touch, pinch, landscape.
- Real media (evidence/S09/local/) is gitignored: on a fresh clone real-scenes.test.mjs skips (not fails) and real-scenes.html cannot load.
  Verified in S09j with the media junction removed: 46 tests → 43 pass, 3 skipped, 0 fail.
- Points only, main asset only (mobile LOD not loaded), 20k points; larger clouds untested. Viewer not yet mounted by an app route.
- Scale UNVERIFIED for all real scenes; nothing here is Gate R, physics, calibrated or production evidence.
