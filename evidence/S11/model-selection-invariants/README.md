# R14 independent model-selection/residual audit

Baseline: `74c886f9b2cc1322dde152f5be5813f813904bc6`. No product edits.

## Exact expected oracle

For `t=(-2,-1,0,1,2)`, let `h=t²-2`, `e=(1,-4,6,-4,1)` and
`y=s*(c*h+e)`. Exact arithmetic gives `sum(h)=sum(t*h)=0`,
`e` orthogonal to `1,t,t²`, `sum(h²)=14`, and `sum(e²)=70`.
Thus the degree-1 RSS is `s²*(14*c²+70)`, degree-2 RSS is `s²*70`.
These are least-squares optima by exact residual orthogonality, not production QR.

The implemented AIC convention is `n*log(RSS/n)+2*(degree+1)`. Omitting the
common Gaussian constant and common estimated-noise parameter does not change
which candidate wins. At `c=1` the expected winner is degree1; at `c=4` it is
degree2. For `c=4`, the score difference is `5*log(70/294)+2 < 0`, independent
of any nonzero common scale. Compute expected scores in log scale, never by
squaring a tiny float. Expected RMSE is `abs(s)*sqrt(RSS_unscaled/5)`.

## Confirmed counterexample and scope

At exact dyadic `s=2**-600`, positions are finite, distinct from zero, and exact
binary multiples. Both true RSS values are positive but below binary64 range;
RMSE and AIC remain representable. Production returns degree1, both AIC `-inf`,
both RMSE zero, and API `unavailable_exact_zero_rss` for nonzero residuals.
The covariance correctly abstains here; this finding concerns residual/AIC/API
metadata only. Tests permit explicit FitError/API error instead of false success.

`audit.json` preserves actual responses, exact-rational RSS, independent finite
expected scores/RMSE, baseline source hashes and an intermediate `2**-540` case.
That intermediate case raises a readable API error (RSS/n underflows in log),
which is fail-closed, not an additional fail-open defect.

Additional observation, not a contract-strength failing regression: six exact
linear float pairs `t=1+i/10`, `y=1+2*t` favor degree2 from roundoff-only RSS.
Fraction arithmetic proves exact linearity. No exact-fit tie/resolution policy
is specified, so no arbitrary numerical tolerance/new feature is mandated.

## Frozen checks

`python -m unittest discover -s tests/fitter -p test_r14_model_selection.py -v`

The test file covers independent AIC scores, both winners, residual sign/RSS/
RMSE, sample/rank/dof metadata, 30 ordinary common-scale/permutation cases,
degree/sample-count matrix, strict invalid degrees/options, rank deficiencies,
exact-zero JSON handling and the three underflow observables. No expectedFailure,
skip decorators, fixture tuning, external package, covariance/QR audit or physical
calibration claim. Explicit numerical abstention remains acceptable.

API `degree` currently controls the returned fit/quantity; `select_model` is
diagnostic metadata and does not replace it. Two-point degree1 fitting is valid,
but requesting the fixed `(1,2)` candidate set fails for insufficient quadratic
samples. Both behaviors are recorded, not invented as new defects. No AICc or
positive-residual-dof requirement is imposed on an API that permits interpolation.
