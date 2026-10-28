# Virtual-lab fitter (S11d–S11g)

`core.py` is a small standard-library implementation for **synthetic** motion
observations. It fits linear/quadratic OLS models with re-centred QR, returns
observed-minus-predicted residuals, chooses by AIC (`k = rank`), and computes
conditional Jacobian covariance under Gaussian IID residuals. Quadratic
coefficient uncertainty is the Jacobian for `g = 2*c2`; clock and scale are
held fixed. `coverage_regression()` uses one fixed seeded generator and reports
the observed 100-seed result without tuning to it.

All outputs carry `provenance="simulated"`. They are not live calibration,
physical measurement, Gate M, Gate R, S05c, or S12 evidence.
