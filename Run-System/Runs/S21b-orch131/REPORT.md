# S21b-orch131 REPORT — DONE

- Lane/model: CODEX-2 (army: Claude), anthropic/claude-opus-5-5/high. Coding quota: OpenCodex-managed; not polled.
- UTC issued 2026-10-30T11:08:17+00:00; started ~11:09:25Z; stopped 2026-10-30T11:12:57+00:00. Branch run/S21b-orch131 from main 392683f.
- Tokens/cost: unobservable (unknown). No GPU/API/network calls, no dependency installs, no secrets read.

## Delivered
- [Build/benchmark/errors.py](../../../Build/benchmark/errors.py): runs the S21a `check` (sha pins + leakage) first, then builds rows only via
  `manifest.resolve` pointers into pinned evidence. Each row: class, value, unit, uncertainty+kind, n, sources, reason. Fails closed if a
  value expected unavailable is non-null; recomputes RM02/RM04 floor-normal vs camera-down-prior angle from pinned vectors and asserts it
  matches the recorded angle (tol 0.01 deg, recorded has 3 decimals). `--md` prints the BENCHMARK table.
- [evidence/S21/S21b-errors.json](../../../evidence/S21/S21b-errors.json): deterministic output; 8 measured, 8 UNAVAILABLE; gates
  gate_m=NOT_MET_INPUT_READINESS, gate_rs=NOT_MET (resolved, not asserted).
- [Build/benchmark/test_errors.py](../../../Build/benchmark/test_errors.py): 4 tests (committed JSON == regeneration and BENCHMARK table current;
  class/reason invariants; non-null "unavailable" fails closed; tampered sha rejected).
- [BENCHMARK.md](../../../BENCHMARK.md): "Results: gravity and scene-scale errors (S21b)" = generated table pasted verbatim.

## Honest result
- UNAVAILABLE: gravity magnitude error m/s^2 (Gate M NOT_MET; S05d magnitude null for RM02/04/05); RM02/RM04 gravity direction error vs
  truth (no independent ground-truth vertical; basis = floor assumed horizontal); RM05 gravity (clip not under gravity); metric scale
  error RM02/RM04/RM05 (S05d abstain, no source-backed known-size reference) and ST03 (image-height units).
- Measured (precision/consistency only, NOT accuracy): ST03 image-space g relative 1-sigma (n=19 training frames); RM02/RM04 floor-normal
  bootstrap 1 sd (+max over 50 resamples, n=inliers); RM02/RM04 floor-normal vs camera-down-prior disagreement (recomputed);
  RM02/04/05 floor-plane RMS residual (p95, model units, n=inliers).
- NOT_MET is not reinterpreted as a result; no number authored (all from pointers or arithmetic on pinned values).

## Fresh checks
- `python -B Build/benchmark/errors.py` -> {"measured": 8, "unavailable": 8}.
- `python -B -m unittest Build/benchmark/test_manifest.py Build/benchmark/test_errors.py` -> Ran 10, OK.
- `python -B Build/benchmark/manifest.py check` -> exit 0.

## Ponytail
Reuse: manifest.check/_load/resolve/_num (sha pins, pointers, leakage) instead of new loaders; stdlib math only. Smallest complete: one
script + one test + generated JSON; BENCHMARK table generated, not hand-typed, with a drift test. Skipped: adding rows to the frozen
manifest.json (would change the S21a freeze sha; spec lives in errors.py instead), Build/web/src/about/ (S21e), camera-height spread
(reflects camera motion, not error), MapAnything self-reported scale factor as a "result" (no reference). Risks: `_load`/`_num` are
private helpers of manifest.py (same package); bootstrap 1 sd and residuals are precision, readers must not quote them as accuracy;
evidence edits break sha pins (intended: refreeze).

## Communication
Silent; one completion message to controller chat as authorized.
