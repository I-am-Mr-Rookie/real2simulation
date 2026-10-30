# S21d-orch136 REPORT — DONE

Lane CODEX-2 (army: Claude); model anthropic/claude-opus-5-5 medium (assigned; OpenCodex-managed, not polled). Tokens/cost: unobservable. No GPU/API/billing-console calls, no secrets read.
UTC: issued 2026-10-30T11:21:21+00:00; work stopped 2026-10-30T11:25:14+00:00; deadline 11:51:21Z. Branch run/S21d-orch136 from main 65a829d.

## Changed
- Build/benchmark/costs.py — 24 rows from pinned evidence. Classes billed/estimated/reservation/measured/simulated/unavailable; never summed together (no totals computed; month-to-date billed is read directly from S06h checkpoint).
  - RM02/RM04 (S06h reconciled scene logs): billed USD, estimated USD, billed GPU-s, cold start, model load, inference, round trip as separate rows.
  - ST03 tracking job: billed USD + billed GPU-s (already-pinned cost_st03_job).
  - Modal month-to-date billed and S06 jobs billed, S06e reservation (checkpoint_s06h; asserts /jobs/3 is S06e).
  - Meta S16e: tokens + latency measured; cost_usd UNAVAILABLE (null asserted; reason from /cost_basis, Q17).
  - S20d: caps as SIMULATED, only if provider_calls==0 and mode SIMULATED_ONLY.
  - Fail closed: billed rows require /cost/billed/status=="billed"; non-numeric values raise; non-null unavailable raises.
- New pins (EXTRA, sha256): evidence/S06/S06h/RM02-scene-log.reconciled.json, RM04-scene-log.reconciled.json, evidence/S16/S16e-orch108-live.json, evidence/S20/S20d-regression.json.
- Build/benchmark/test_costs.py — regeneration + BENCHMARK drift, class separation, null-cost fail-closed, unbilled/live-sim rejection, tampered pin.
- evidence/S21/S21d-costs.json (generated); BENCHMARK.md S21d subsection (verbatim --md) + unavailable bullet.

## Ponytail (applied)
- Reuse: manifest.py check/_load/resolve/_num; S21c EXTRA-pin pattern instead of re-freezing manifest; errors.py add/markdown/CLI shape.
- Smallest: one rows() function, no new deps, no aggregation code (avoids cross-class sums by construction).
- Skipped: Build/web/src/about/ (S21e owns About data); S05/S07 ledger jobs and S13 cost-logs not included (S06h reconciled logs are the accepted per-scene runtime source; adding more is extendable via EXTRA); per-row uncertainty.

## Checks (fresh)
- python -B -m unittest discover -s Build/benchmark -p "test_*.py" -> Ran 21 tests OK (5 new in test_costs.py).
- python Run-System/worker_timebox.py check Run-System/Runs/S21d-orch136/TIMEBOX.json -> TIMING PASS.

## Risks / limits
- Billing reads are point-in-time (Modal report lags); month-to-date value is from 2026-10-29 read, not current.
- Pinned hashes are of this Windows checkout bytes (same as S21a manifest behaviour).
- Per-scene cost covers RM02/RM04/ST03 only; RM05 and other clips have no accepted per-scene cost record here.
- Communication: silent; one completion message to controller.

Next: S21e About data + BENCHMARK prose.
