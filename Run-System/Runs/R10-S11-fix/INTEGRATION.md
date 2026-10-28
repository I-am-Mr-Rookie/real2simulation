# Parent-owned integration / targeted rereview

No fitter caller signature or quantity contract change. Default API uncertainty
model is now `independent_position_time_first_order`; explicit
`iid_fixed_clock_scale` remains supported with a declared-position noise floor.
Exact response metadata (additive, no quantity contract change):
- `uncertainty.model`: chosen request/default model above.
- `uncertainty.assumptions`: model-specific independence, first-order, scale,
  calibration and bias limitations (or fixed-clock legacy limits).
- `uncertainty.quantity_uncertainty`: `standard uncertainty (one sigma), not a 95% interval`.
- `uncertainty.residual_degrees_of_freedom`: actual fit dof.
- `uncertainty.residual_variance_floor`: RSS/dof, or null when no residual dof.
- `covariance.model`, `covariance.assumptions`: same model/assumptions.
- `covariance.interval`: null; no adapter confidence interval claimed.
- Existing covariance SE is for c2; existing `gravity_scale_factor=2.0` converts
  it to gravity SE. `gravity.uncertainty` is already twice that coefficient SE.

`coverage_regression` alone evaluates a synthetic residual interval: its existing
`interval_z` compatibility field is now a t multiplier by default; additive
`interval_method`, `degrees_of_freedom=17`, `nominal_coverage=.95`. Custom multiplier
or zero-noise diagnostic clears nominal coverage. It does not turn the API's
instrument-propagated SE into a 95% confidence interval.

Three old fitter assertions intentionally changed: blanket non-propagation text
is obsolete, and a 3-point fit with positive declared noise now has valid known-
noise covariance despite having no residual dof. Zero declarations + zero dof
still abstain.

Outside Owns: `Build/lab/pipeline.py` has a blanket
`input instrument uncertainty not propagated` limitation, and
`tests/lab/test_pipeline.py` asserts it. The pipeline defaults into the new model,
so its owner should replace that limitation/assertion with model-specific
first-order/independence/calibration limits, ideally forwarding fitter metadata.
`Build/lab/session-bridge.py` explicitly requests the legacy model; its separate
blanket non-propagation text should mention the position floor / fixed clock.
No edits made to these files. Existing caller suites remain required checks.

Parent must obtain the required **native Claude targeted rereview** of these two
numeric findings before gate acceptance; implementation DONE is not that review,
nor physical M/S12, deployment or gate unlock. Parent owns integration/FF, not this
worker. No extra worker or broad review launched here.

Controller timing correction acknowledged: UTC issue/deadline unchanged;
correct Dhaka deadline is 2026-10-29T02:29:19.659+06:00, not 06:59.
