# Virtual-lab fitter (S11d–S11g)

`core.py` is a small standard-library implementation for **synthetic** motion
observations. It fits linear/quadratic OLS models with re-centred QR, returns
observed-minus-predicted residuals, chooses by AIC (`k = rank`), and computes
conditional Jacobian covariance under Gaussian IID residuals. Quadratic
coefficient uncertainty is the Jacobian for `g = 2*c2`.

RMSE uses the residual norm, and AIC evaluates `n*(2*log(norm)-log(n))+2*k`:
neither first squares tiny residuals nor divides an already rounded RSS. The
norm keeps its maximum-residual scale separate through division/logarithms, so
rounding a subnormal norm first cannot erase a representable positive RMSE.
The criterion and exact-zero tie behavior are unchanged. A representable nonzero
residual norm therefore yields finite AIC even if binary64 RSS underflows to zero.
The API marks that rounded RSS with `rss_status="underflow"`, not an exact fit;
`unavailable_exact_zero_rss` AIC metadata is reserved for all-zero residuals.
An unrepresentable residual variance floor is null. Both uncertainty models
retain covariance abstention rather than turning lost variance into known zero;
representable RMSE/AIC do not imply representable covariance or physical evidence.

## Standard uncertainties, not confidence intervals

`jacobian_covariance(fit)` retains residual OLS covariance `RSS/dof * (X'X)^-1`
with clock and scale fixed. `sigma=` remains a known homoscedastic standard
deviation override (including zero); it does not require residual degrees of
freedom. Do not combine it with the new declared-sigma arguments.

The quantity API now defaults to `independent_position_time_first_order`.
For independent standard uncertainties `sy_i`, `st_i`, it uses fitted local-basis
velocity `v_i` and per-observation variance
`max(RSS/dof, sy_i^2 + v_i^2 * st_i^2)`. Covariance is the OLS sandwich
`L diag(variance_i) L'`, with `L=(X'X)^-1 X'` evaluated using existing centred QR.
The residual floor is **not added** to declared variances, avoiding automatic
double counting of noise already present in residuals. Increasing any declared
standard uncertainty cannot decrease a parameter variance for fixed data.

Explicit `iid_fixed_clock_scale` requests remain accepted for existing callers.
They use `max(sqrt(RSS/dof), max(sy_i))` as an IID position-noise floor and do
**not** propagate timing uncertainty. Both API models therefore respect declared
position uncertainty even with noise-free trajectories. Existing response keys
and quantity contracts are unchanged; new metadata identifies the selected model.

If `dof=0`, there is no residual variance estimate: positive declared noise still
permits conditional propagation; without declared noise covariance is unavailable.
An explicit core `sigma=0` remains supported as a known zero-noise assumption.
Rank-deficient designs fail; nonfinite/overflowed covariance is unavailable/null,
not spurious precision. Quantity `uncertainty` and covariance `standard_error`
are **one-standard-deviation uncertainties, never 95% intervals**.

The covariance implementation keeps the existing QR factors and transforms
`R^-1` to physical coefficient coordinates **before** forming a weighted Gram
matrix. Declared-noise influence rows reuse the fitted Q columns; it never
constructs an inverse normal-equation Gram matrix. Every diagonal is checked.
For positive noise, a scaled-design infinity-norm condition estimate above
`1/sqrt(binary64 epsilon)` makes covariance unavailable: this conservatively
retains roughly half the floating-point digits rather than claiming accuracy on
nearly dependent rows. This is not a changed trajectory/coverage tolerance.

Nonzero residuals whose squares underflow cannot establish zero estimated noise;
their covariance is unavailable unless declared noise dominates the rounding
bound (one smallest subnormal per residual, divided by residual dof).
Timing-only declarations at zero fitted velocity do not rescue a lost residual
floor. Explicit known `sigma=0` remains distinct from an underflowed estimate.

Timing propagation is a first-order small-error approximation around the fitted
trajectory, not an errors-in-variables refit or bias correction. It does not
propagate correlated clock-rate errors, common calibration/scale errors, model
misspecification, or validate/calibrate instrument declarations. Residual floors
are conservative safeguards, not an exact confidence-interval construction.

## Synthetic residual-interval coverage regression

`coverage_regression()` retains its fixed 20-observation quadratic design, seeded
Gaussian IID position noise and unchanged observed `>=0.90` diagnostic threshold.
The default **95% residual interval** uses Student-t with 17 residual degrees of
freedom, not 1.96: sigma is estimated from residuals. The fixed-design critical
value is checked against integrated Student-t density and installed SciPy in
generated evidence. This adds no runtime dependency. If the design changes, the
critical value must be recomputed for its new dof.

The existing `interval_z` field/argument is retained as a compatibility name for
the SE multiplier, not a claim that it is a normal z score. Supplying a custom
multiplier clears `nominal_coverage`; zero-noise runs are numerical diagnostics,
not stochastic coverage claims. `interval_method`, `degrees_of_freedom` and
`nominal_coverage` make these distinctions explicit. Individual finite random
batches can still fail the diagnostic even under correct nominal coverage.

Caller integration note: the pipeline's hardcoded blanket non-propagation
limitation should be replaced with these model-specific limits by its owner.
The session bridge explicitly requests the legacy fixed-clock model; it remains
supported, but its blanket non-propagation text should likewise mention the
position floor and remaining timing limitation.

All outputs carry `provenance="simulated"`. They are not live calibration,
physical measurement, Gate M, Gate R, S05c, or S12 evidence.
