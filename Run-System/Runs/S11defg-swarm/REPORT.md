# S11defg-swarm — DONE (child implementation only)

## Scope
Implemented a private, simulation-only numerical core for S11d–S11g in
`Build/fitter/`, with isolated tests in `tests/fitter/`. No shared controls,
contracts, deployment, credentials, model/checkpoint download, paid job or
physical result was touched. S11 leaves remain parent-integration dependent;
this report is not a Gate M/P/R/S12 pass.

## Leaf boundary
- **S11d:** local least-squares/residual implementation complete; parent
  acceptance and instrument-contract integration remain pending.
- **S11e:** local AIC/model-selection implementation complete; same prerequisite.
- **S11f:** local QR-derived covariance implementation complete; same
  prerequisite and downstream review remain pending.
- **S11g:** local seeded synthetic regression complete (95/100); this is not
  physical coverage or a parent product/gate result.

These are implementation receipts only. Do not mark S11d–S11g product leaves
accepted until the controller integrates the corrected contract, runs the full
repository checks, and completes independent review.

## Concrete implementation
- Reused the existing measurement lane's numerical posture: stdlib-only,
  finite-input rejection, centered QR rather than normal equations, explicit
  rank/dof and residuals. No duplicate broad math framework or dependency.
- Added linear/quadratic OLS, AIC with `k=rank` and roundoff-perfect-fit `-inf`,
  Jacobian/Gram covariance with honest invalid output for no dof/rank failure,
  and a fixed-seed 100-run coverage regression (95/100, 0.95).
- After the instruments lane exposed its API, `gravity_quantity` imports the
  normal `contracts.fit.quantity.Quantity`; no contract implementation copied.
  Read-only peer-worktree `PYTHONPATH` was used for compatibility verification.

## Fresh checks
`$env:PYTHONPATH=<instruments worktree>; python -m unittest discover -s tests/fitter`
=> **10 tests PASS**. This includes analytic recovery, residuals, degeneracy,
  finite rejection, extreme time origins, AIC, covariance, contract output, and coverage. Direct
coverage output: `CoverageResult(seeds=100, covered=95, coverage=0.95, ...)`.
The contract compatibility test was run with read-only peer `PYTHONPATH`; the
remaining numerical tests are independent of that path. `git diff --check`
passes.

## Limitations / next action
The corrected instruments contract is read through the peer worktree at commit
`ef570b6`; `gravity_quantity` now uses its actual `source.label=simulated` plus
`source.evidence` API. Controller must cherry-pick/integrate that contract and
rerun the full repository suite. Outputs are synthetic and cannot establish
real calibration or any physical gate.

Revision after controller review: replaced absolute-time polynomial evaluation
with span-scaled, twice-reorthogonalized QR; rejected bool/string/overflow
inputs, unsupported degrees/units, empty models and nonfinite predictions;
made AIC roundoff handling scale-aware; computed covariance from QR R inverse;
and made unavailable gravity uncertainty abstain instead of becoming zero.

Independent R-SIM-swarm findings from reviewed head `bc6a7ac` were then fixed
in `9700c3c`: finite huge-time/position arithmetic now catches overflow and
raises `FitError`, and AIC returns `-inf` only for exact `rss == 0.0`; the
reviewer's alternating-`1e-15` nonzero-RSS repro now returns finite AIC.
Fresh fitter suite: **11 tests PASS**; both reviewer repros pass.

Ponytail full/default applied: minimal existing seam, no new dependency,
smallest owned change, fresh targeted checks, explicit skipped external work,
and risks/limitations recorded. OpenCodex-managed usage not polled.
