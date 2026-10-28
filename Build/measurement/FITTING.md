# S07c deterministic free-fall fitter

`from Build.measurement.free_fall import fit_free_fall, evaluate_held_out`

```python
fitted = fit_free_fall(record)  # frozen S07a JSON-compatible record
suffix_errors = evaluate_held_out(fitted, record)  # separate evaluation, no refit
```

Both functions call `inputs.validate_input`. Malformed records raise `ValueError`;
well-formed but metric-ineligible records raise `FitAbstention` (a `ValueError`)
with immutable `.blockers`. No fallback to pixel acceleration, assumed 9.81,
file FPS, inferred slowdown, fabricated scale, or synthetic real-media approval.
Declared evidence remains a review obligation, not authenticated by validation.

## Coordinates, units, fit

- Source image **y down positive**, x unused. A constant in-plane metres/pixel
  scale and verified constant capture-seconds/PTS-second ratio are mandatory.
  Camera/gravity-axis alignment, perspective and calibration applicability must
  be established externally; image-y curvature is not automatically world g.
- Capture elapsed time is `(frame.pts_s - first_training_pts_s) * ratio`.
  No frame-index/FPS substitution: irregular PTS are used directly.
- Model: `y_m(t) = initial_y_m + initial_velocity_m_s*t + 0.5*g_m_s2*t*t`.
  Initial position is measured from the source image's y=0 origin, not a floor;
  initial state is at the first training PTS, not at absolute PTS zero.
  Negative initial velocity is allowed. Nonpositive/unresolved downward curvature
  abstains; this v1 API is not a lunar/projectile classifier.
- Unweighted deterministic least squares uses **only the training prefix**.
  Subtract source position/PTS origins, scale elapsed time to a unit span, center
  it, then solve three columns by reorthogonalized QR. No normal-equation matrix
  inversion or new dependency. Finite conversions/outputs and rank are checked.
  `quadratic_rank_ratio` is the final quadratic QR diagonal / sqrt(sample size);
  <=1e-12 abstains. This numerical threshold is not a physical uncertainty bound.
- At least three distinct samples are required by S07a. Three yield zero residual
  degrees of freedom and cannot establish a noise estimate. All results expose
  `residual_dof = training_count - 3` without inventing an interval.

Raw positions are deliberately **not** Savitzky–Golay filtered: VFR/short prefixes
do not justify a fixed-rate window, smoothing can bias edges and alter residual
covariance, and quadratic LS already estimates a smooth trajectory. Add an
explicit prefix-only noise/smoothing model only when justified by S07d/tracking
evidence, never by viewing/tuning the held-out suffix.

## Residuals and suffix custody

`fitted.training` and `evaluate_held_out` return frozen `Residuals`: frame indices,
signed **observed minus predicted** residuals in metres, RMSE in metres and maximum
absolute error in metres. The fitted record and snapshots are frozen. Local
normalized coefficients are retained to evaluate without large-origin cancellation.
RMSE, residual degrees of freedom and the QR rank ratio are diagnostics, **not**
calibrated confidence/uncertainty intervals or a goodness-of-physics pass.

Evaluation validates the suffix, checks the exact training snapshot and declared
source/calibration/approval identity, then evaluates only suffix observations.
Changing any suffix coordinates cannot affect fit coefficients or train diagnostics.
No suffix coordinates/residuals are stored in the fit. Validation necessarily
checks suffix shape/order, so malformed suffixes reject the whole input record.
An immutable parsed suffix is used within the evaluation call; callers still own
precommitted external suffix custody. This API cannot stop callers replacing
suffix observations or tuning/repeating evaluation outside it.

No arbitrary residual cutoff is imposed: noisy positive-curvature fits expose
their errors; flat/upward/unresolvable fits abstain. S07d must propagate scale,
timebase, tracking/coordinate error, correlations and model adequacy; no current
diagnostic establishes calibrated uncertainty or physical gate eligibility.

## Verification and limits

`python -m unittest discover -s tests/measurement -v`

Synthetic mathematical recovery and error cases only. No real SAM/model call,
footage acquisition/tracking, GPU work, real measured g, Earth/Moon benchmark,
Gate M result or S12 unlock. Current real calibration/approval holds remain.
