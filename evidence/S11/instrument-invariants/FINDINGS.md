# R14 instrument invariants — one P2 root cause, candidate independently verified

## Audited baseline

`74c886f9b2cc1322dde152f5be5813f813904bc6`; baseline source hashes are in
`probe.json`. No product files were changed by this audit.

### P2: pre-floor `+0.5` changes non-ties and exact lattice points

`Build/instruments/synthetic.py:38–49`, specifically lines43–44, computes
`floor(abs(value)/resolution + 0.5) * resolution`. Binary64 addition can round
before `floor` sees the value. The returned quantity remains schema-valid, so
downstream validation cannot detect the wrong observation.

All inputs below are exact finite binary64 values; bias/noise are zero. The
frozen regressions use dyadic resolutions to exclude decimal-grid ambiguity.

| Case | True input | Resolution | Expected observation | Baseline observed |
|---|---|---|---|---|
| Strictly below half | `0x1.fffffffffffffp-2` = `0.49999999999999994` | `1.0` | `0.0` | `1.0` |
| Exact odd lattice | `0x1.0000000000001p+52` = `4503599627370497.0` | `1.0` | unchanged | `4503599627370498.0` |
| Exact tiny lattice | `0x1.0000000000001p-1022` | `0x0.0000000000001p-1022` = minimum subnormal | unchanged | `0x1.0000000000002p-1022` |

Independent justification:

- Below-half input is `1/2 - 2^-54`. Adding `1/2` yields the exact real
  `1 - 2^-54`, which binary64 rounds to `1.0` before floor. It was never a tie.
- At `2^52+1`, the input/resolution quotient is already an exact integer.
  Adding `0.5` rounds to the next even integer, incorrectly moving one tick.
- Tiny-lattice input equals `(2^52+1) * 2^-1074`, giving the same quotient
  and one-minimum-subnormal error. Correct input, output and resolution are
  representable; this is not an unavoidable result underflow.

`Fraction.from_float` with integer quotient/remainder independently implements
half-away rounding in the **dyadic fixtures**. It does not reuse the product's
division-plus-addition algorithm. All four public instruments reproduce the
defect: stopwatch, light gate, ruler, and camera time/x/y (six quantity channels).
Negative camera coordinates mirror the error away from zero.

Actual caller propagation:

- Instrument call sites: stopwatch75, camera99/102/103, ruler119, light gate133.
- `Build/lab/pipeline.py:71–80` passes light-gate/ruler quantities directly into
  the fitter; units, declared uncertainty and wrong observation values survive.
- `Build/lab/session-bridge.py:70–71` uses the same two instruments with `1e-6`
  resolution. Lines96–97 reconstruct the matching `s`/`m` quantity boundary.
  A wrong quantized value is not corrected by this projection. The exact failing
  inputs above are API counterexamples, not claims about current default demos.

## Semantics decision: preserve the established rounded-quotient contract

The existing `tests/instruments/test_synthetic.py:20–24` explicitly expects
camera time `1.25`, resolution `0.1`, to observe **1.3**. Binary64 division gives
`1.25/0.1 == 12.5`; however, exact rational division of the two stored binary64
numbers is slightly **below**12.5. Therefore an exact binary-grid quantizer would
instead give `1.2000000000000002`, breaking an established observable fixture.

Recommendation, independently assessed: preserve that existing quotient behavior,
not silently introduce exact binary-grid or decimal-string arithmetic. Define
rounding on the binary64 quotient explicitly. The controller's selected split
`whole=floor(ratio); whole+(ratio-whole>=0.5)` removes the premature addition
without changing the already-rounded quotient or signed half-away rule.

For nonnegative finite binary64 quotients below `2^52`, the integer part is
exactly representable and subtracting it preserves the fractional decision.
At larger magnitudes, representable quotients are already integral (or at most
half-integral until `2^52`); integral values do not acquire a spurious increment.
This avoids arbitrary epsilons, new dependencies and a new resolution policy.

The new explicit decimal-tie test covers all public instruments, including
negative camera y; the original one-ULP-below-half regression and all three
frozen exact dyadic regressions remain unchanged. The oracle is **not** asserted
for arbitrary non-dyadic grids. Decimal-string arithmetic is not endorsed.

Preserve the existing conservative ratio-overflow rejection: baseline
`test_synthetic.py:49` expects `1e308 / 1e-308` to reject. This audit does not
expand that envelope or require arbitrary finite-input acceptance.

## Other bounded results

- Every public numeric parameter rejects boolean, NaN, infinities, overflowing
  integer, string and None inputs. Resolutions reject zero/negative; uncertainties
  and noise std reject negative. Negative time/distance/frame identifiers reject;
  signed pixel coordinates remain supported.
- Minimum subnormal, minimum normal and maximum float observations are finite
  when resolution equals the input. Error remains the total observed-minus-true
  float value, distinct from explicit caller-supplied standard uncertainty.
- Seeded stopwatch reaction is replayable; changing seed changes this checked
  sample. Changing declared uncertainty leaves observation/error unchanged.
  No claim that a supplied uncertainty is calibrated or equals reaction std.
- Real S08 export -> Node simulation -> light gate/ruler -> actual fitter passes
  the existing four pipeline tests, plus a new nonzero-bias/nondefault-uncertainty
  test checking **every** sample's units, error, quantization and declared sigma.
- Fitter input boundary rejects swapped time/distance units. Changing only
  diagnostic `error` does not change the result; uncertainty is not inferred from it.
- Existing10 session-bridge tests pass. No new reaction-metadata, units or
  pipeline integrity defect was demonstrated within this bounded audit.

## Evidence and independent candidate verification

- `probe.py` / `probe.json`:18 frozen channel failures and72 mismatches across294
  deterministic dyadic sweep observations (12 scalar input/resolution pairs).
  These counts are not physical/statistical coverage or a gate result.
- `r14-unittest.log`, `all-instruments.log`: baseline remains intentionally red
  only on the three frozen test methods (18 failing instrument/channel subcases).
- `pipeline-unittest.log`, `session-bridge-unittest.log`: real local CPU integration.
- `verify_candidate.py` explicitly loads the **same audit file** against the
  controller's separate source, without writing there. `candidate-unittest.log`
  and `candidate-verification.json`:22/22 tests pass (12 audit +10 existing), and
  all312 frozen+sweep observations match. Source hashes were identical before/after.
- Verified candidate is branch `run/R14-quantizer-fix`, HEAD
  `55a3d2e63dace18539fcd62ff3dbb28c287ab402` **with an uncommitted instrument edit**
  at verification. The product snapshot is pinned by SHA256
  `3f216767bb4d7b16541955d169c699668daf54ef228c1626b37e33fe7c7ba78d`, not claimed
  as part of that HEAD. Parent owns commit/integration and required vendor review.

No covariance/QR/underflow re-audit, physical footage/calibration, UI/deployment,
network/model/GPU job, credentials or gate advancement was performed.
