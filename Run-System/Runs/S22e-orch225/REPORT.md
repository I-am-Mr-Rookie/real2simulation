# S22e-orch225 REPORT (claude-sonnet-5-5/medium, OpenCodex-managed; not polled)
Start 2026-10-31T16:06:46Z, end ~2026-10-31T16:11Z. Status: DONE.
Result: Gate D run 3 PASS vs <5 min (1280 px result at 24 s scripted; Report 48 ms). Details: evidence/qa/browser/S22e/RUN.md.
Defects: P3-1, P3-2, P3-4 FIXED; P3-3 not reproduced; P2-1 (Run/Fit not executed, recorded replay) STILL PRESENT. No new defects.
Commands: node %TEMP%/s22e/r.mjs 1280 and 375 (headed Chromium, two new Clerk test accounts, kept).
Ponytail: reused S22d script (copied/parametrised by width), existing evidence format; no code changes, no deps. Skipped: RM04 recheck, human-eye Report body check, 3D interaction. Risks: Report body render not verified; scripted timings exclude human time; result card appears before the answer.
Communication: silent; one completion line to controller.

