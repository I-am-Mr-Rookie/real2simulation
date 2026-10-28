# R10-S11-fix

Issued 2026-10-28T19:59:19.659Z; implementation cutoff 20:24:19.659Z;
deadline 20:29:19.659Z (Dhaka 2026-10-29T02:29:19.659+06:00).
Handout's Dhaka 06:59 is inconsistent; UTC issue/deadline govern the 1800s window.
CODEX1 / managed Sol HIGH. Parent project 91e441f8-e40c-4ec4-bea2-de7fa1582d97.
Branch run/R10-S11-fix; base 3fa80eb4985779f8b913ce1d9cdbd932f1b65468.

Objective: fix residual-interval nominal coverage and misleading API precision
without changing gate thresholds or unrelated simulation/physical gates.

Owns: Build/fitter/{core.py,api.py,README.md,__init__.py}, tests/fitter/,
evidence/S11/uncertainty-hardening/, this run directory; contracts/fit only if needed.
No shared controls, lab bridge, UI, instruments, other reports or main merge.

Ponytail full: inspected fitter exports, contracts, tests, pipeline and session
bridge callers; reuse centred QR and covariance transform, no new dependency.
Preserve explicit legacy conditional model and sigma override; default adapter
will use declared independent position/time uncertainty with first-order timing.
Coverage uses Student-t for the fixed 20-observation / 17-dof experiment.

Acceptance: reproduce both reviewer findings; quantile-reference and aggregate
coverage checks without seed selection; declared-sigma monotonicity, independent
sandwich reference, nonfinite/rank/dof/zero-residual checks; existing caller suites.
Generate evidence from actual runs. Native Claude targeted rereview is parent-owned.
