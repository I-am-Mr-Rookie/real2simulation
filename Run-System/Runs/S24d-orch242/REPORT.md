# S24d-orch242 REPORT

Status: DONE. Lane CODEX-2, model anthropic/claude-sonnet-5-5 medium (OpenCodex-managed; not polled). UTC start 2026-11-01T07:55:33Z, end 2026-11-01T08:15Z. Tokens and cost: unobservable. No deploy, GPU, paid call, secret, publication or upload.

## What was produced
Under media/capture/S24d/: [SHOTS.md](../../../media/capture/S24d/SHOTS.md) (beat table, numbers and sources, video timestamps for S24i), [capture.mjs](../../../media/capture/S24d/capture.mjs), 28 PNG stills (all under 500 KB, largest about 290 KB). Videos abc-flow.webm (1080p), d-viewer.webm (1080p), e-backup-1280.webm (720p) exist locally and are gitignored.
Shots: (a) upload, agent question, known size 20.28 cm; (b) fit curve with 1-sigma band, held-out prediction (dashed) vs recorded held-out points, chi2/dof 2.32/3 p 0.51; (c) g = 8.62 ± 1.29 m/s², report body with caveats; (d) RM04 3D viewer with "Scene geometry: Display only, scale unverified, not a measurement."; (e) 1280x720 rerun of a to c.

## Ponytail use
Reused the S22i/S22h Playwright flow (sign-up code 424242, OWN05, answer text, g wait) as one ~90-line script; no new dependency, playwright-core from the codex runtime. Numbers are scraped nowhere by hand: stills are the product screens. One script for all beats via ONLY env. Skipped: automatic frame trimming, per-shot separate videos, OCR of numbers.

## Checks (fresh)
- Live run on DEV three times for the flow; g = 8.62 ± 1.29 each time; viewer loaded canvas in about 19 s.
- Viewed upload, chart, caveat, report, viewer stills: no owner frame, no email text. CSS hide injected before navigation.
- git check-ignore confirms webm ignored; no em dashes in SHOTS.md.
- worker_timebox.py check run (see commit).

## Limits and risks
- Each video is one 36 to 55 s take with a 12 to 15 s sign-up lead-in, not separate 5 to 20 s clips; use SHOTS.md timestamps.
- The product chart is static: the "reveal" is the dashed prediction vs hollow held-out points on one screen (b1, b2, c1 are identical pixels).
- Owner clip file name "05_repeat_a__035711.mp4" appears in the upload progress line (a2).
- marks.json (untracked) holds only the last run; d and e timestamps were copied into SHOTS.md.
- The held-out PASS is conditional (dof 1, forking-paths caveat, scale unverified); do not present it as accuracy.
- Communication compliance: silent; single completion line sent.

