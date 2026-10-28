# R12 covariance recovery — DONE

CODEX1 / assigned managed Sol high, controller-owned implementation. Full clock
in PLAN/TIMEBOX, original30m unchanged. Canonical root/project ID in plan;
assigned project is not independent UI membership proof (see controller receipt).

## Findings fixed

- Retain the existing two-pass QR Q/R. Transform R inverse into physical
  coefficient coordinates BEFORE forming the covariance Gram; declared-noise
  influence rows reuse Q. No inverse normal-equation Gram or copied fitter.
- Validate every diagonal, not only the selected coefficient. Conservative
  scaled-QR condition bound returns unavailable before unreliable full-matrix
  precision; no trajectory/coverage threshold or noise inflation.
- Nonzero residuals whose squares vanish cannot imply zero estimated noise.
  Declared variances must dominate a conservative lost-square rounding bound;
  stationary timing declarations cannot mask it. Explicit known sigma=0 retained.
- Private Q field is not serialized by the existing explicit public API.
  Extra retained Q storage is O(n*rank), rank<=3; lab samples remain capped2000.

## Fresh verification / independent acceptance

Final product pin9d240b0. Frozen exact-Fraction/metamorphic audit was originally
red, now45/45 fitter methods PASS, including13 independent invariant methods.
Final Python lab17/17 PASS. Node84/84 PASS on same JS/bridge sources; Python-only
follow-up guard then verified by final45/17 and actual browser.
Coverage96/100 with the SAME Student-t critical2.1098155778333156 and90/100 floor.
No measured/calibrated claim.

Native targeted Claude review at7708494 resolved both P2s, noP0-P2. Parent also
fixed its one actionable subnormal-floor P3; short same-window re-review at
9d240b0 confirms resolved/no newP0-P2. Exact reports/probes retained unchanged in
R12-covariance-review/REPORT.md and FOLLOWUP.md. Other P3s are explanatory notes,
not actionable gate failures. No broad repetitive Claude audit.

Actual ChatGPT IAB375x812 normal fresh Run->Fit->reveal and Mystery Run->Fit:
clientWidth360==scrollWidth360, finite fitter-only simulated reveal with explicit
one-standard-uncertainty/model labels. Mystery has no reveal before fit and no
browser compute before/after fit. Saved DOM and PNGs in covariance-recovery;
parent visually inspected final Mystery screenshot. Initial tab attach timed out;
inventory recovered actualtab3, no Chrome or alternate browser used.

R13 independent real Windows lifecycle sidecar: actual unchanged service,
controlled Python->Node fixtures. Worker combined33/33 and parent NEW OS test1/1
PASS; four occupied slots/fifth rejected, abort+replacement, five real trees dead,
zero fallback cleanup, no successful sessions. Not universal/reparented/process
timeout-path or actual simulation success proof. Source/cleanup code inspected;
only exact owned PIDs and validated temporary roots can be removed.

## Smallest complete change / limits

Reused stdlib math/QR, current API and independent audit tests; no deps, general
editor, calibration, real scene, physicalM/S12, paidGPU, deployment/publication,
account/terms/credential work. Known-noise/ill-conditioned availability is more
conservative; no impossible positive float variance manufactured.
OpenCodex-managed; not polled. Tokens/cost unknown.
Worker reports/timeboxes checked; parent owns rebase/FF/shared controls only.
Communication: mandatory updates and material findings only; no duplicated logs.
