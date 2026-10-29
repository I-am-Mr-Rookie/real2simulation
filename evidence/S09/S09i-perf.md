# S09i — orbit fps and memory on the target laptop (RM02 / RM04 / RM05)

Evidence class: **real reconstruction bundles (MapAnything nominal), metric scale UNVERIFIED**. Not Gate R, not physics.
Numbers + method: [S09i-perf.json](S09i-perf.json). Bench page: tests/viewer/perf-orbit.html (no product-code change).

## Hardware (read-only Get-CimInstance)

HP 250 G7 Notebook PC · Intel Core i3-1005G1 (2C/4T, 1.2 GHz base) · Intel UHD Graphics (driver 30.0.100.9864) ·
11.8 GiB RAM · Windows 11 Pro 10.0.26200 · 1366x768 @ 59 Hz panel.
Browser: ChatGPT in-app browser (Chrome/156), WebGL = ANGLE Intel UHD **Direct3D11 (hardware GPU, not SwiftShader)**, DPR 1.

## Method

Bundles rebuilt CPU-only in this worktree exactly as S09h (`python Build/gpu/scene_job.py <RM> evidence/S09/local/<RM> --npz <npz>`);
points.ply sha256 prefixes E4681461 / 9F0C0BD9 / 4046FCC2 match S09h. Media gitignored, not committed.
Page mounts each bundle through the existing createArtifactLoader -> createViewerAdapter -> createThreeRenderer, injecting a
timed requestFrame. After load + 500 ms, one fixed 360° orbit at 60°/s for 6 s (orbit.rotate + invalidate every rAF).
Desktop = default IAB viewport 1280x720; 375 = IAB viewport override 375x812 (reset after). python http.server on 127.0.0.1, stopped.

## Results (measured, 20000 points each)

| Scene | View | fps mean | frame ms p50/p95/max | frames >33 ms | draw JS ms p95 | JS heap after orbit |
|---|---|---|---|---|---|---|
| RM02 | 1280 | 59.97 | 16.7 / 16.9 / 18.1 | 0 | 0.3 | 14.3 MB |
| RM04 | 1280 | 59.97 | 16.7 / 17.0 / 19.7 | 0 | 0.4 | 14.3 MB |
| RM05 | 1280 | 59.97 | 16.7 / 17.1 / 22.9 | 0 | 0.4 | 14.9 MB |
| RM02 | 375 | 56.32 | 17.8 / 18.2 / 19.5 | 0 | 0.3 | 15.0 MB |
| RM04 | 375 | 56.40 | 17.7 / 18.3 / 18.7 | 0 | 0.3 | 15.0 MB |
| RM05 | 375 | 56.31 | 17.7 / 18.4 / 22.2 | 0 | 0.3 | 15.0 MB |

All six: states `loading,ready`, scale `estimated` (UNVERIFIED banner). Budget tier full (1280) / reduced, no AA (375).
**Acceptance met: all three scenes orbit >= 30 fps on identified hardware** (min 56.3 fps, worst frame 22.9 ms).

## Limits

- rAF is vsync-capped (~60 Hz); headroom only indicated by draw JS time (~0.3 ms), GPU completion time not measured.
- GPU/VRAM memory not exposed by the browser: not measured. JS heap is Chromium `performance.memory` (coarse, GC-noisy).
- 375 px is viewport emulation on this laptop, not a real phone. 20k-point bundles only; larger clouds untested.

