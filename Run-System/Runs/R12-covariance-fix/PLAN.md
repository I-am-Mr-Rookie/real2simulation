# R12 controller-owned covariance recovery

Actual UTC issue 2026-10-28T20:58:46.012Z; full30m deadline 2026-10-28T21:28:46.012Z;
Dhaka 2026-10-29T03:28:46.012+06:00;
minute25 cutoff 2026-10-28T21:23:46.012Z. Parent CODEX1 Sol/high.
Parent project91e441f8-e40c-4ec4-bea2-de7fa1582d97; isolated run/R12-covariance-fix.

Owns Build/fitter/core.py, Build/fitter/README.md, tests/fitter/test_uncertainty.py, this run directory,
evidence/S11/covariance-recovery/. R12 independent worker owns test_invariants.py
and exact reference evidence; no duplicate implementation/audit.

Fix two reproduced P2s: invalid full covariance from squaring condition before
basis transform, residual-square underflow falsely reported as zero uncertainty.
Ponytail FULL: reuse existing QR Q/R and transform BEFORE forming weighted Gram;
no new math dependency, no arbitrary tolerance relaxation or noise inflation.
Preserve explicit known sigma=0; honest unavailable for underflow.
Fresh exact-invariant/uncertainty/API/core tests, coverage regression, scoped
native Claude re-review before parent acceptance. All physical/spend holds intact.
