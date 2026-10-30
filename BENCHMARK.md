# Real2Simulation benchmark

Status: **inputs and method frozen (S21a)**. Numbers are not written here by hand.
Every reported number is a JSON pointer into sha256-pinned accepted evidence,
listed in [Build/benchmark/manifest.json](Build/benchmark/manifest.json) and resolved by
`python Build/benchmark/manifest.py check` (frozen output: [evidence/S21/check.json](evidence/S21/check.json)).

## Gates (honest status)

- **Gate M: NOT_MET** (no calibrated scale or capture clock). No metre or m/s^2 claim.
- **Gate RS: NOT_MET** (no category reaches 80% scored coverage; median unavailable).
- Both statuses are read from evidence pointers, not asserted here.

## Method

1. **Inputs.** Only accepted evidence from S05d (floor/gravity/scale), S06e/f/h (scene runtime and
   billed cost), S07b orch14 (ST03 prefix tracking), S11 (fitter, simulated), S12 (Gate RS, ST03
   prediction). Library UI is not an input (controller decision: S18 dependency relaxed).
   No new GPU or API runs.
2. **Clips.** ST03 (projectile, Pexels License), BN01 (bounce, not scored), PD02/PD03/PD04/PD06
   (pendulum, not scored), RM02/RM04/RM05 (scene). Licence and approval receipts via pointers.
3. **Metric for S12 (Q15=A).** Scale-free error: per-clip RMS of |y_pred - y_obs| divided by image
   height over the sealed held-out suffix; Gate RS uses the median over categories. Units:
   image-height fraction. Not a physical accuracy claim.
4. **Split.** ST03 training prefix = tracked frames up to the sealed last training frame;
   held-out = the sealed suffix in the committed prediction trace. Scored frames = tracked
   suffix frames after the boundary.
5. **Automated leakage check** (`leakage()` in manifest.py), fails if any of:
   train/held-out overlap; max(train) >= min(held-out); boundary, prediction and Gate RS disagree on
   the last training frame; counts differ from the seal; scored frames fall outside the sealed suffix;
   training or prediction sha256 differ across evidence; the prediction records reading suffix
   observations at fit time.
6. **Classes.** *measured* = real run on approved licensed input (image-derived or billed);
   *simulated* = synthetic/analytic; *unavailable* = evidence value is null/abstained, with an
   evidence-backed reason. The validator rejects any literal number in gates/clips/split/metrics.
7. **Estimates vs billed.** Cost rows are labelled `USD (billed)` or `USD (estimate, not billed)`;
   cold start and inference are separate timing rows. One run each: no variance claimed.

## What is unavailable (and why, per evidence)

- Calibrated gravity magnitude and gravity error in m/s^2 (Gate M).
- Metric scene scale for RM02/RM04/RM05 (S05d abstained: no source-backed known-size reference).
- Gate RS median; bounce and pendulum normalized RMS (no prefix tracking / sourced records).
- The ST03 normalized RMS is measured but **diagnostic only** (coverage below 80%; `scored=false`).

## Next (not done here)

S21b-f measure/extend, write About data under Build/web/src/about/, cross-check pitch numbers.
Re-run `python -m unittest Build/benchmark/test_manifest.py` after any evidence change; a sha
mismatch means the freeze must be redone, not edited.
