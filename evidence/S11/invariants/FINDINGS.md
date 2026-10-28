# R12 independent numerical findings — frozen audit record

Audited source `5e0fd65bf24fb38d3d8b4e4426dddf64e293f20d`, simulation-only.
No production fixes or integration performed. Tests intentionally expose defects.
Parent independently confirmed both mechanisms and owns fixes in separate
`swarm12-covariance-fix`. Narrow audit DONE does not close either product defect.

## P2: finite but invalid full covariance advertised as valid

Smallest reproduction (seconds/metres; no large origin or tiny position signal):

```python
fit = fit_least_squares((0., 2.**-28, 1.), (0., 0., 0.))
known = jacobian_covariance(fit, sigma=.125)
declared = jacobian_covariance(fit, position_sigmas=(.125,)*3)
```

Both default to curvature `parameter_index=2`. `known.valid` is True while
`known.covariance[0][0] == -0.00390625`. Declared-noise propagation also returns
True, but `declared.covariance[0][0] == 0.0234375` (50% too large).

Independent proof: this is a full-rank 3-point quadratic interpolation. At t=0,
c0=y0, so Var(c0)=sigma²=0.015625 exactly. Its coefficient influence row is
(1,0,0); no stochastic sample/coverage assumption, residual degrees of freedom,
position subtraction or external reference is needed. The other intercept
covariances are `C01=-sigma²*(1+e)/e`, `C02=sigma²/e` by Lagrange interpolation.
Exact-Fraction normal equations independently agree. Installed NumPy SVD gives
C00≈0.01562500046; it is corroboration only, not a dependency or the oracle.

Positive residual dof does not remove the defect: `(0,e,2e,1)`, four zero
positions, sigma=.125, e=2^-30 returns negative C00 in BOTH modes; at e=2^-36
known-sigma C00=-32 with valid=True. The exact four-point C00≈0.0130208333334.

Root in `Build/fitter/core.py` at the audited source:
- Lines262–263 form `R^-1 R^-T`; lines276–279 evaluate influence polynomials
  from that ill-conditioned Gram inverse for the declared-noise sandwich.
- Lines282–286 transform the already-squared local covariance to the physical
  coefficient basis. Cancellation of very large terms destroys the small,
  well-identified intercept variance. 80-digit algebra on the SAME computed
  float QR factor recovers C00≈0.015625000316 in the 3-point reproduction,
  isolating the covariance algebra rather than a missing time/position bit.
- Lines289–292 validate only the selected diagonal and matrix finiteness;
  another negative diagonal escapes. Merely checking every diagonal would not
  fix the positive-but-wrong declared result.

This is a full-matrix validity defect, not evidence that every reported default
gravity SE is wrong. Default curvature variance in the minimal case remains
close to the exact result. A conservative unavailable result is acceptable when
the implementation cannot resolve the required covariance; returning an invalid
finite matrix as valid is not. No demand to support arbitrarily conditioned data.

## P2: residual-square underflow becomes false zero uncertainty

```python
fit = fit_least_squares((0.,1.,2.,3.), (0.,0.,1e-165,0.))
cov = jacobian_covariance(fit)
```

Residuals are nonzero and representable, but `rss == 0` because individual
residual squares underflow. Both residual-only and all-zero declared-position
sigma modes return an all-zero covariance, standard_error=0, valid=True.
Exact-Fraction OLS proves Var(c2)>0; its conversion to binary64 is zero.

Root: `fit_least_squares` line141 squares residuals without an underflow marker;
`_sigma2` lines217–218 only detects positive-RSS-to-zero division, not information
already lost while forming RSS. The final local-covariance underflow guard cannot
help because local_cov is already all zero. This is a representation-limit case:
the expected behavior is honest unavailable, NOT an impossible positive binary64
variance. Explicit `sigma=0` is a different, supported known-noise assumption and
must remain valid. Existing positive-declared-sigma underflow tests do not cover
residual-estimation underflow.

## Passed boundaries and model limits

Exact-rational expectations / conserved relations cover paired row permutations,
linear and quadratic fits, full covariance at physical time-origin shifts through
2^45 seconds (dyadic observation spacing remains exact), position shifts through
2^20 metres, dimensionally equivalent physical time/length scaling, known sigma
overrides versus residual-floor semantics, and true rank-deficiency rejection.
An independent analytic seven-point full covariance and central finite-difference
fit Jacobian agree for noiseless quadratic motion; a 2^60 time shift that actually
erases spacing is explicitly rejected, not mislabeled an invariance failure.
The scaled problems always use API units s/m; no cm/ms input support is claimed.

Timing covariance remains the documented independent *first-order around the
fitted trajectory* approximation, not an errors-in-variables refit, common clock
calibration model, or exact nonlinear-noise covariance. Extreme origin shifts
that destroy observation spacing or overflow the full covariance are not defects
when rejected/unavailable honestly. No physical calibration/Gate M/S12 claim.

## Reproduce

```powershell
python -m unittest discover -s tests/fitter -p test_invariants.py -v
python evidence/S11/invariants/audit.py
```

`analytic-repro.json`: exact rational, 80-digit same-QR and optional installed
NumPy SVD corroboration. `*-tests.txt`: fresh test outputs.
`near-rank-probe.txt`, `rank-boundary.txt`, `residual-underflow-probe.txt`:
bounded exploratory evidence, not separate defects or product success.
