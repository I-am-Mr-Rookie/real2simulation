# S21c-orch135 REPORT — DONE

- Lane/model: CODEX-2 (army: Claude), anthropic/claude-opus-5-5 high. Coding quota: OpenCodex-managed; not polled.
- UTC issued 2026-10-30T11:15:35+00:00; work stopped/reported 2026-10-30T11:19:56+00:00. Branch run/S21c-orch135 from main e9e226f.
- Tokens/cost: unknown (unobservable). No GPU/API/network runs; no installs; no secrets read.

## Changed
- Build/benchmark/predictions.py — held-out error rows; writes evidence/S21/S21c-predictions.json; `--md` table.
- Build/benchmark/test_predictions.py — regeneration/BENCHMARK drift, gates/classes, leak, recompute-mismatch,
  non-null-unavailable and tampered-pin fail-closed tests.
- evidence/S21/S21c-predictions.json — generated (2 measured, 0 simulated, 4 unavailable).
- BENCHMARK.md — new "Results: held-out prediction errors (S21c)" section; table is verbatim `--md` output.

## Results (all from evidence; no authored numbers)
- ST03 suffix normalized RMS 0.1982 and max abs 0.3334 (image-height fraction), n=7 scored of 466 sealed,
  frames 77-83 > last training frame 76; recomputed from prediction-ST03-v2 trace vs ST03-f58-83 track and
  asserted equal (1e-12) to gate-rs.json recorded values; diagnostic only (scored=false). Uncertainty = max
  prediction 1-sigma OLS band (0.01822), labelled model band only.
- UNAVAILABLE with evidence reasons: st03_range_error, bounce_height_error, pendulum_period_error,
  gate_rs_median_heldout_error (Gate RS NOT_MET; S12f VIRTUAL_LAB_ONLY).

## Fresh checks
- `python -B -m unittest discover -s Build/benchmark -p "test_*.py"` -> Ran 16 tests, OK (S21a/b tests still green).
- `python -B Build/benchmark/manifest.py check` -> exit 0 (freeze + leakage).
- `python Run-System/worker_timebox.py check Run-System/Runs/S21c-orch135/TIMEBOX.json` -> TIMING PASS, exit 0.

## Ponytail (full) applied
- Reused errors.py `ref` and `markdown` (imported, not copied), manifest `check`/`_load`/`resolve`/`leakage`
  and the S21b add()/null() fail-closed shape; stdlib only.
- Smallest complete change: S12f-fallback.json (accepted after the S21a freeze) is sha-pinned in predictions.py
  EXTRA instead of editing the frozen manifest, which would have changed S21b's manifest_sha256 and forced
  regenerating S21b evidence. Build also asserts S12f was decided on the same gate_rs sha.
- Recompute-and-compare (like S21b angle recheck) instead of copying the recorded RMS.
- Skipped: Build/web/src/about/ (no consumer needed for S21c), first-5 diagnostic RMS row, simulated rows
  (no simulated held-out error exists in accepted S12 evidence; synthetic pendulum is "not applicable").

## Limits / risks
- Only one real clip (ST03) has any held-out error; 1.5% coverage, not gate-eligible; no physical/metric claim.
- EXTRA pin lives outside the frozen manifest; a future re-freeze (S21d+) should fold it in and regenerate S21b/S21c.
- Communication: silent; single completion line to controller only.

Next: S21d per QUEUE; controller merge after acceptance.
