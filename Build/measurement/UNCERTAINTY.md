# S07d: conditional uncertainty, not physical verification

```python
from Build.measurement.uncertainty import classify_clock, propagate_uncertainty
clock = classify_clock(record)
result = propagate_uncertainty(record, assumptions)
```

Both use accepted S07a validation; propagation calls the actual S07c
`fit_free_fall`. No shared schema, fitter, tracking, dependency or caller changes.
Malformed inputs raise `ValueError`. Scientific/permission insufficiency raises
`FitAbstention` with explicit `.blockers`; no partial metric fallback.

## Clock declaration

`classify_clock` returns an immutable classification, declared ratio and evidence
reference. A validated timebase maps capture elapsed seconds = PTS elapsed
seconds * ratio: `<1` slow_motion, `==1` real_time, `>1` sped_up. This is a
classification of the **declared mapping**, NOT proof of camera acquisition,
uniform cadence, unedited footage or even statistically distinguishable slowdown.
Ratio uncertainty spanning 1 does not establish an acquisition category.
Null/missing/unverified timebase returns unknown and no ratio; propagation
abstains. Delivered/container FPS and Earth-g never determine scale or clock.
Evidence is caller-declared and must be independently reviewed; code cannot
authenticate it. Other input blockers still prohibit metric propagation.

## Owned-module input schema

The second argument is a separate dictionary with exactly these fields, frozen
before inspecting held-out observations:

| Field | Required meaning |
|---|---|
| `detection_std_px` | List/tuple, **training count only**, finite nonnegative absolute one-standard y-coordinate errors in original source pixels. Must cover tracking/localization uncertainty, not just quantization. |
| `timestamp_std_pts_s` | Same length; finite nonnegative absolute one-standard per-frame timestamp errors in **PTS seconds**, not capture seconds. Common clock-rate error belongs to timebase, not here. |
| `scale_clock_correlation` | Explicit finite correlation [-1,1] between scale and capture-ratio errors. Zero is an explicit independence declaration, not a default. |
| `independent_frame_errors` | Must be boolean true: all per-frame y and timestamp errors mutually independent, including same-frame y/time cross-error. Correlated tracking/smoothing/rolling shutter errors require a future full covariance model; false abstains. |
| `calibration_independent_of_frames` | Must be true: scale/ratio errors independent of all frame errors. Prefix-derived calibration sharing observations generally violates this. |
| `small_error_linearization` | Must be true, externally justified: first-order propagation adequate, negligible higher-order terms; positive scale/ratio not near zero relative to their uncertainty. No automatic threshold or guaranteed bound is invented. |
| `remaining_systematics_negligible` | Must be true with evidence: any systematic not represented by scale/ratio/frame errors negligible. Unknown camera motion, perspective, plane/alignment, acceleration-model mismatch, timing edits, tracking bias, etc. require abstention. Not permission to ignore known bias. |
| `evidence` | Nonempty reviewable reference supporting **every** precision, correlation and assumption, including justified exact zero components. Synthetic references are not real-media evidence. |

No numeric defaults, residual-based estimates or suffix precision arrays. Missing
or null fields abstain as unknown; false required assumptions abstain as
unsupported; malformed fields and extra keys reject. No hidden RNG/noise model.
The existing scale uncertainty (`uncertainty_m_per_px`) and capture-ratio
uncertainty (`uncertainty_factor`) are **absolute one-standard uncertainties**,
not percentages, bounds, or 95% intervals. Their evidence remains mandatory.

## Mathematics and units

Image y down positive; g is the S07c fitted positive acceleration in m/s². Let
scale be s, ratio r. Calibration sensitivities are
`dg/ds = g/s`, `dg/dr = -2*g/r`. For scale/ratio standard errors us, ur,
calibration variance is `(g*us/s)^2 + (-2*g*ur/r)^2 +
2*rho*(g*us/s)*(-2*g*ur/r)`. The implementation factors this PSD form to
avoid catastrophic cancellation near perfect correlation.

Observation sensitivities differentiate the **unweighted OLS estimator** on the
training prefix, NOT a reweighted fit. For the fitter's fixed centered normalized
times z and duration D, residualize z² against [1,z] by two-pass QR to obtain q;
let B be the coefficient of z in that projection and H=sum(q²). Then
`dg/dy_m[i] = 2*q[i]/(H*D²)`. Pixel sensitivities multiply by s.
Writing fitted polynomial coefficients as [a,b,c], and signed metre residual e,
`dg/dPTS[i] = 2*r/(H*D³) * ((2*z[i]-B)*e[i] - q[i]*(b+2*c*z[i]))`.
The residual/design-matrix term is retained even on imperfect quadratic data.
Independent component standard errors are Euclidean norms of sensitivity times
declared standard precision. Their variances add to calibration variance.

Output is frozen: fitted record, total `standard_uncertainty_m_s2`, separate
detection/timestamp standard components, signed scale/clock sensitivities,
correlation and assumption evidence. **No confidence/coverage interval** exists.
Residual RMSE is still only a residual diagnostic; a perfect quadratic does not
make uncertainty zero unless all relevant errors are explicitly justified zero.

## Insufficiency, conditioning and custody

At least four training observations (positive residual degrees of freedom) are
required here. Three exact points still permit S07c interpolation but never an
S07d uncertainty result. Four points do not establish empirical coverage either:
the noise model is external, not estimated from residual degrees of freedom.
The fitter's <=1e-12 rank-ratio abstention is preserved and checked in the
Jacobian construction; output fit exposes rank and sample diagnostics. A tiny
time span can amplify errors greatly: no clamping or silent interval narrowing.
Nonfinite numerical propagation and nonzero error products rounding to zero
abstain instead of silently claiming exact uncertainty.

Only the fixed prefix enters fit, Jacobians and error propagation. No held-out
residual tunes filtering, noise, bounds or assumptions. Whole-record validation
still rejects malformed suffixes; valid suffix coordinate/time changes cannot
change the result. Caller must enforce real external custody and calibration
freeze; this function cannot prevent a caller leaking suffix data into supplied
assumptions or fabricating evidence.

Synthetic verification: `python -m unittest discover -s tests/measurement -v`.
No real footage, live model/GPU calls, physical measurements, Gate M pass,
S07e/S12 unlock, empirical uncertainty calibration or guaranteed coverage claimed.
