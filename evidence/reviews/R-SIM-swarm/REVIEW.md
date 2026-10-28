# R-SIM-swarm independent review

Review scope: read-only review of current peer correction heads; no source or
control edits. This is independent CODEX-1 review evidence, not an other-vendor
gate signoff and not a parent product/gate result.

## Reviewed heads

- S10 simulator: `eb24f12a66397a2bd79858c8028841c6353f97b2`
- S11 instruments: `ef570b63ca12c6bd34bb54ca66aadbe7ae179eef`
- S11 fitter: `bc6a7ac197a71ea30842e571b4c3124048881eef`

## Findings

### P1 — public fitter leaks `OverflowError` for finite huge inputs

File: `Build/fitter/core.py:59` and `:125` in fitter head `bc6a7ac`.

Repro: `python evidence/reviews/R-SIM-swarm/repro_fitter_findings.py <fitter-root>`.
`fit_least_squares((1e308, 1e308-1e292, 1e308-2e292), (1,2,3), 2)` raises
raw `OverflowError: intermediate overflow in fsum`, not the documented
`FitError` boundary. A second family with finite positions around `1e154`
also leaks from RSS/QR arithmetic. The input guards reject non-finite values,
but do not make finite arithmetic overflow fail closed. Catch relevant
`OverflowError`/non-finite intermediate paths and raise `FitError` with a
stable reason; add a regression test.

### P2 — AIC still labels non-zero residual as exact

File: `Build/fitter/core.py:142-146` in fitter head `bc6a7ac`.

The repro creates a quadratic with alternating `1e-15` perturbation. It yields
`rss=1.232595164407831e-29` but `_aic` returns `-inf`, because any RSS below
`64*n*(degree+1)*ulp(y_scale)^2` is treated as exact. This is an arbitrary
absolute machine-epsilon cutoff and makes honest AIC/near-perfect-fit status
depend on output magnitude and rounding. Reserve `-inf` for `rss == 0.0`
(or expose an explicit, documented numerical-status field); add a regression
that requires finite AIC for non-zero RSS.

## Clean areas and fresh checks

- Simulator `node --test tests/simulator/simulator.test.mjs`: **3/3 pass**.
  Reviewed RK4 positive finite `dt`, zero-step validation, sparse-state guard,
  deterministic trace, and the exact Python `validate_setup` producer boundary.
- Instruments `python -m unittest discover -s tests/instruments`: **9/9 pass**.
  Reviewed separate total error vs supplied bias/uncertainty, seeded replay,
  boolean/non-finite/overflow guards, and simulated provenance.
- Fitter `python -m unittest discover -s tests/fitter`: **10/10 pass**, but the
  two independent repros above are outside the existing suite.
- Compatibility setup: for instrument/fitter checks, `PYTHONPATH` was set to
  the corresponding peer roots (fitter first, instruments second); no deps or
  external APIs were added.

## Ponytail application

Applied full Ponytail: reused existing dependency-free ESM/Python seams and
peer tests; made no speculative source changes, new dependencies, framework,
or API. Review evidence is the smallest complete change and keeps source
ownership with S10/S11 peers. Fresh checks and the executable repro are stored
under this review's owned evidence path.

## Limits

No peer edits, merges, control updates, model/checkpoint/media access, paid
jobs, deployment, publication, credentials, or live/browser/hardware checks.
Findings are local numeric-contract defects only; they do not establish Gate
P, Gate M, Gate R/S12, or parent product readiness.
