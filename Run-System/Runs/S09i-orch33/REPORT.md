# S09i-orch33 REPORT — DONE

Lane CLAUDE · anthropic/claude-opus-5-5/medium · UTC 2026-10-29T15:53:11Z – 2026-10-29T15:59:41Z · base main f15f180 · branch run/S09i-orch33.
Coding quota: OpenCodex-managed; not polled. Cost: $0 (no Modal/GPU/API). Tokens: unobservable.

## Result
All three real scenes orbit >= 30 fps on identified hardware: HP 250 G7, i3-1005G1, Intel UHD (ANGLE D3D11 hardware WebGL), 11.8 GiB RAM.
Desktop 1280: 59.97 fps each (vsync cap); 375 px: 56.3–56.4 fps; 0 frames > 33 ms; worst frame 22.9 ms; draw JS p95 <= 0.4 ms; JS heap ~12–15 MB.
Evidence: evidence/S09/S09i-perf.md, evidence/S09/S09i-perf.json. Scale stays UNVERIFIED (estimated).

## Files
- tests/viewer/perf-orbit.html (new bench page)
- evidence/S09/S09i-perf.md, evidence/S09/S09i-perf.json
- Run-System/Runs/S09i-orch33/{PLAN.md,TIMEBOX.json,REPORT.md}
- Gitignored, not committed: evidence/S09/local/RM0{2,4,5}/ rebuilt bundles.

## Commands / checks (fresh)
- scene_job.py RM02/RM04/RM05 --npz (S09h paths) -> PASS x3, 20000 pts; points.ply hashes match S09h.
- Get-CimInstance (CPU/GPU/system/OS), read-only.
- IAB (ChatGPT in-app browser, not Chrome): perf-orbit.html?scene=RM0x&secs=6 at 1280x720 and 375x812 override (reset after) -> 6 RESULT JSONs, states loading,ready.
- node --test "tests/viewer/*.test.mjs" -> 46/46 pass (with temporary node_modules junction; without it three-renderer test cannot resolve three — env, not code).
- python http.server 127.0.0.1:8719 started and stopped (no LISTEN after).

## Ponytail
Reused createArtifactLoader/createViewerAdapter/createThreeRenderer and its injectable requestFrame for timing, plus the S09h converter; one ~60-line HTML page, zero product-code change, no new deps. Skipped: GPU timer queries, VRAM measurement, a reusable bench module, screenshots in git.
Worktree lacked Build/web/node_modules: used a temporary directory junction to main's existing install (no install), removed afterwards (main install verified intact).

## Limits / risks
- rAF vsync-capped; GPU completion time and VRAM not measured (browser does not expose VRAM). Heap is coarse/GC-noisy.
- 375 is emulation on the laptop, not a real phone. Only 20k-point clouds tested.
- S09h noted SwiftShader; this run's IAB used hardware ANGLE D3D11 — results are hardware GPU numbers.

## Next
S09j: checkpoint viewer evidence (375 + perf), keep fixture vs real-scene evidence separate.

## Communication
Silent; one completion message to controller chat only.

