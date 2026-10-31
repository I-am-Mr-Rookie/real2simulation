# S24c-orch211 REPORT

Status: PARTIAL (all five beats and 5b captured; product viewer, fit overlay and prediction overlay do not exist as capturable screens, listed in SHOTS.md).
Lane/model: CODEX-2 lane run by anthropic/claude-sonnet-5-5 medium; OpenCodex-managed; not polled. UTC start 2026-10-31T12:43:10+00:00, end 2026-10-31T12:57:31+00:00.
Branch run/S24c-orch211 (worktree .worktrees/S24c-orch211).

## Delivered
- [SHOTS.md](../../../media/capture/S24c/SHOTS.md): per-shot table (file, duration, source, numbers and their origin, gap).
- PNG stills (all under 500 KB) for beat1, 2, 3, 4, 5, 5b, plus DEV site-library, site-lab, site-lab-fit; webm videos (1280x720, not committed, gitignored) in media/capture/S24c/.
- [capture.mjs](../../../media/capture/S24c/capture.mjs): reproducible script (playwright-core chromium from codex runtime, headless, not Chrome).
- .gitignore: two video lines; DEMO_SCRIPT_DRAFT.md: PENDING S24c line now points to SHOTS.md.

## Ponytail choices
Reused existing evidence JSON (PD02 result.json stream, ST03 stream, S05d RESULT, gate-rs.json, S07n table.md, BENCHMARK rows) and the deployed DEV site instead of building a viewer harness; one script, overlay pages generated at run time so no number is typed by hand. Skipped: point-cloud render, parabola/prediction overlay, mask pixels, mp4 transcode, 1920x1080.

## Fresh checks
- Viewed stills for beats 2 to 5b and /lab; box format verified (x+w/2 range 408.0 to 1294.5 px equals PD02-summary x_range_px 407.9 to 1294.3).
- Numbers on screen come from JSON/BENCHMARK reads; labels verbatim (ABSTAINED (unverified), Gate RS: NOT_MET).
- No owner-clip (OWN*) frames; beat 5b is table only. git add -f only named files; videos not staged.

## Gaps and risks
- Beat 3: cloud.py renders the real RM02 MapAnything cloud (matplotlib orbit + S05d floor-normal arrow, beat3-cloud); not the product viewer (private /workspace/[sceneId] only), no floor plane.
- Beat 4: overlay has track points only; plots.py adds a real Build/fitter parabola + residual-RMSE band (beat4-fit). Local OLS rel. uncertainty 0.07444 differs from BENCHMARK 0.07367, so it is NOT drawn; use the BENCHMARK number as caption. No product fitter screen.
- Beat 5: beat5-predict is a plain extrapolation illustration, not the sealed prediction file; no error meter; beat5 card title says "sealed prediction vs suffix" but shows values only.
- Beat 5b: no OWN07 track plot; scale 20.28 cm / phone-clock labels must be added in edit.
- DEV /lab returns local_lab_disabled: no lab/fitter screen is capturable on the deployed DEV build.
- Videos start with 1 to 3 s page-load lead-in (trim in S24f). Pexels frames shown under owner Q19 = A; people-depicted rights review (ST03, PD02) still noted in the script.
- Not run: deploy, GPU, Meta, secrets, uploads: none. Communication compliance: silent; one completion line.

