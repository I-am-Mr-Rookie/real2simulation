# S11defg-swarm — DONE

## Scope
Implemented a private, simulation-only numerical core for S11d–S11g in
`Build/fitter/`, with isolated tests in `tests/fitter/`. No shared controls,
contracts, deployment, credentials, model/checkpoint download, paid job or
physical result was touched. S11 leaves remain parent-integration dependent;
this report is not a Gate M/P/R/S12 pass.

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

Ponytail full/default applied: minimal existing seam, no new dependency,
smallest owned change, fresh targeted checks, explicit skipped external work,
and risks/limitations recorded. OpenCodex-managed usage not polled.
