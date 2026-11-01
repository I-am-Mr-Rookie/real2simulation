# S22l-orch248 REPORT

Status DONE. Lane CODEX-2, assigned anthropic/claude-sonnet-5-5/medium (OpenCodex-managed; not polled). Issued 2026-11-01T09:07:44Z, deadline 09:37:44Z, stopped 09:27:30Z. Project Meta AI Hackathon 91e441f8-e40c-4ec4-bea2-de7fa1582d97. Branch run/S22l-orch248 from main 7cd9481d.

## Result
Gate D retest on DEV: 3/3 consecutive fresh flows PASS 3.1 to 3.8 (3.6 N/A), S15bg announcer PASS (no role=alert, title constant), S15bf chips + validated spec PASS, negative check PASS (422 plain message, re-answer without restart after Back), guest library SIMULATED replay PASS. Details: evidence/qa/browser/S22l/RUN.md, run.json.

## Files
evidence/qa/browser/S22l/: RUN.md, run.json, run.mjs (browser script), gen.mjs (RUN.md/run.json generator from per-flow JSON), per-flow json/txt, 20-odd stills (max 224 KB). Run-System/Runs/S22l-orch248/: PLAN.md, TIMEBOX.json, REPORT.md.

## Commands
node run.mjs guest|f1|f2|f3|neg (headed Playwright Chromium); node gen.mjs; python Run-System/worker_timebox.py check.

## Ponytail
Reused S22i/S22h Playwright flow (signup, upload, answer) in one script; one JSON per flow and a generator instead of hand-written tables; no product code, no new dependency. Skipped: HAR files, 375 px, print/download, human timing.

## Findings and limits
- API /version revision e0213a0c (S15bf, ancestor of main 7cd9481d). Web build SHA not observable (no version endpoint); controller-stated af881dce NOT verified. S15bg verified by behaviour only.
- Proposed fixes (P3): U1 invalid answer leaves "All questions answered." with no input until Back; U2 code-prefixed validation alert; V1 expose web build SHA.
- Headless Chromium is blocked by Clerk bot challenge; headed used. Earlier headless attempts for f1 to f3 and an early neg run produced no committed evidence (overwritten by the final runs; the final neg run is the second attempt).
- A mistaken path bug created a stray directory C:/Users/HP/Documents/Hackathon/2026-10-26%20-%20Meta%20Global%20AI%20Developer%20Hackathon (copy of my first test outputs, untracked, outside canonical root). Removal was blocked by policy; controller may delete it.
- Scripted timings exclude human time; Clerk test accounts only; OWN05 only; not the in-app browser. Gate D of record still needs S23.
- Communication: silent; one completion line.

