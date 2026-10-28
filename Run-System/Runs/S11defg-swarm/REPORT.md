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
=> **6 tests PASS**. This includes analytic recovery, residuals, degeneracy,
finite rejection, AIC, covariance, contract output, and coverage. Direct
coverage output: `CoverageResult(seeds=100, covered=95, coverage=0.95, ...)`.
With no peer `PYTHONPATH`, the five core-only tests pass and the contract import
test correctly fails because the contract is not yet integrated into this
worktree. `git diff --check` passes.

## Limitations / next action
Controller must integrate/cherry-pick the instruments contract commit before
running the full repository suite. Parent should review API compatibility and
serialize integration. Outputs are synthetic and cannot establish real
calibration or any physical gate.

Ponytail full/default applied: minimal existing seam, no new dependency,
smallest owned change, fresh targeted checks, explicit skipped external work,
and risks/limitations recorded. OpenCodex-managed usage not polled.
