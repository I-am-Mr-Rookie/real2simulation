# S07h-orch172 REPORT — DONE (contract scope OWN02–OWN06)

- Lane CLAUDE, step S07; assigned anthropic/claude-opus-5-5/high; coding quota OpenCodex-managed; not polled. Tokens/cost: unknown (not observable); $0 API/GPU (no Modal/GPU/Meta call).
- UTC: issued 2026-10-30T23:44:12Z; worker start 23:44:52Z; work stopped 2026-10-30T23:49:12+00:00; deadline 00:14:12Z. Branch run/S07h-orch172 from main daffaee2; worktree .worktrees/S07h-orch172.
- Parent project Meta AI Hackathon 91e441f8-e40c-4ec4-bea2-de7fa1582d97; canonical root unchanged; canonical controls not edited.

## Outcome
Frozen S07i pipeline on OWN02–OWN06 → MEASURED g per clip (user-declared scale, phone clock unverified): 9.29±0.32, 9.54±0.63, 10.39±0.46, 8.62±1.28, 7.12±1.02 (OWN06 premise violated);
with OWN01 10.96±0.77: 9.79 inside 1u 2/6, 2u 5/6; **held-out PASS 0/6** (RMSE 13–119 px vs 6 px threshold). 05a vs 05b 1.51±1.63 (05b invalid; 05c/d pending).
Full table + failure modes: [evidence/S07/S07h/README.md](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/S07h-orch172/evidence/S07/S07h/README.md); data/ledger with per-track SHA-256: evidence/S07/S07h/results.json.
Failure modes: impact frame inside the colour-rule window (OWN02/03/06), systematic later-fall deficit + book rotation (OWN01–04), late colour release with scale frames in motion (OWN06), short window (OWN05), SAM loss (OWN04).

## Pre-registration / no-tuning evidence
PLAN.md with all rules committed 815c59d3 BEFORE the script existed; script committed before its first run; results produced by one run; no rule/parameter edit after results (README/REPORT text only).

## Files (Owns only)
evidence/S07/S07h/measure_heldout.py, results.json, README.md; Run-System/Runs/S07h-orch172/PLAN.md, REPORT.md, TIMEBOX.json.

## Checks (fresh)
- `python -B evidence/S07/S07h/measure_heldout.py --self-check` → "self-check OK" (frozen S07i check, OWN01 reproduces) + "S07h self-check OK".
- `python -B evidence/S07/S07h/measure_heldout.py` → table above; results.json written.
- `python -B -m unittest discover -s tests/measurement -t tests/measurement` → Ran 86, OK (skipped=1).
- `python Run-System/worker_timebox.py check Run-System/Runs/S07h-orch172/TIMEBOX.json` → see commit.

## Ponytail (full) — applied
- Reuse: imports measure_own01 (record/window/assume/run) and Build/measurement; frozen m.run() fed a truncated track via a 4-line read_bytes shim instead of copying fit/uncertainty code; constants asserted unchanged; globals restored in finally.
- Smallest complete: one script (plan parse, truncate, run, table); no new deps, no Build/ or tests/ edits.
- Skipped: OWN07–OWN11 (no valid tracks, CUDA OOM → S07j), OWN12 (excluded), any post-hoc sensitivity re-fit (would be tuning), weighted mean g.
- Risks: track inputs are untracked canonical files (SHA recorded, not committed); scale plane/clock unverified; held-out fails everywhere so no g here is a validated measurement; OWN06 number must not be used.

## QUEUE note / next
QUEUE S07h row also lists 05c/05d and 06 robustness clips: remain open until S07j re-tracks OWN07–OWN11; then rerun this script after adding them to CLIPS (rules unchanged) — but new window fixes (end before impact, SAM-y release check) need a fresh pre-registration first.

Communication: silent; one completion message to controller only.

