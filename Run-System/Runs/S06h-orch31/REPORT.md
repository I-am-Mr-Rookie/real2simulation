# S06h-orch31 REPORT — DONE

Lane CODEX-1; model anthropic/claude-opus-5-5 medium; coding quota OpenCodex-managed; not polled. UTC start 2026-10-29T15:47:41Z, end 2026-10-29T15:52:39+00:00. Base main 1c83bc1, branch run/S06h-orch31.

## Result
[evidence/S06/CHECKPOINT.md](../../../evidence/S06/CHECKPOINT.md) + [CHECKPOINT.json](../../../evidence/S06/S06h/CHECKPOINT.json). Acceptance "record measured cost, timings and chosen renderer/reconstruction path": met.
- Chosen: MapAnything (Apache-2.0) on Modal A10G via s06d-scene-job; primitive colliders, SAM3D off (<32 GB, no access receipt); Gate R FAIL -> Fallback 2 planes+boxes, scale UNVERIFIED; R-R recheck cited PENDING (not CLEAR); AWS adapter gated, never launched.
- Per scene (measured): RM02 39.6 s round-trip / RM04 43.6 s (63.3 s whole command); ~30 s cold start+model load, inference ~1.5 s.
- Billed: S06 total $0.05786; RM02 $0.01135 (est $0.01032), RM04 $0.00955 (est $0.01001). Modal month-to-date $0.59959 of $30 (read 15:49:15Z, lagging).
- Finding: S06d ledger $0.00661 was a lagging partial read; fresh billing $0.00955 (+$0.00294). Canonical ledger not edited (recorded as ledger_lag_usd).

## Files (all new, evidence/S06/ + run dir)
evidence/S06/CHECKPOINT.md; evidence/S06/S06h/{checkpoint.py, CHECKPOINT.json, billing-month.json, billing-today-hourly.json, RM02-scene-log.reconciled.json, RM04-scene-log.reconciled.json, tests.txt}; Run-System/Runs/S06h-orch31/{PLAN.md, TIMEBOX.json, REPORT.md}.

## Commands / fresh checks
- `uv run --no-project --python 3.11 --with modal==1.6.3 --env-file .env modal billing report --for "this month" --json --show-resources` and `--for today -r h` (read-only; run from canonical root for .env path; output only into worktree).
- `python Build/gpu/cost_log.py <copy-of-scene-log> billing-today-hourly.json` x2 → billed values identical to S06e/S06f (originals untouched).
- `python evidence/S06/S06h/checkpoint.py` → asserts pass (billing >= every ledger, scenes <=300 s, 0 < S06 <= MTD <= 30).
- `python -m unittest discover` in Build/gpu → 29 OK.
- `python Run-System/worker_timebox.py check` on TIMEBOX.json.

## Ponytail (full) applied
- Reuse: Build/gpu/cost_log.py reconcile (on copies, not originals) instead of new billing parser; existing ledgers/scene logs/GATE_R.json/S06c gate-default.json read directly.
- Smallest complete: one ~70-line generator with assert self-check + one Markdown table doc; no Build/gpu or infra/modal code changes (none needed).
- Skipped: new GPU/Modal jobs, editing canonical ledgers/controls, reservation re-audit across workers, AWS calls, SAM3D.

## Limits / risks
Billing hourly lag: MTD can rise. Not gate/real-scene/physical/calibrated evidence. R-R recheck pending. Spend this run: $0 compute (billing CLI read only). Communication: silent; one completion message to controller.

