# R12-fitter-invariants

- Objective: independently audit existing simulation-only QR coefficients and
  declared independent-position/first-order-time covariance; preserve reproductions
  of genuine numerical defects, not add fitter features.
- Assigned route: CODEX1, managed `gpt-6.1-sol`, HIGH; runtime routing not changed.
- Parent project: `91e441f8-e40c-4ec4-bea2-de7fa1582d97` (owner-supplied inline
  Swarm exception; not claiming a newly verified desktop project binding).
- Canonical: `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`.
- Isolated worktree source: `5e0fd65bf24fb38d3d8b4e4426dddf64e293f20d`;
  created `run/R12-fitter-invariants` from detached clean checkout.
- Issue: 2026-10-28T20:46:38.309Z; implementation cutoff:
  2026-10-28T21:11:38.309Z; deadline: 2026-10-28T21:16:38.309Z
  (2026-10-29T03:16:38.309+06:00). First observed clock 20:46:47.4163940Z.
- Owns only: `tests/fitter/test_invariants.py`, `evidence/S11/invariants/`,
  `Run-System/Runs/R12-fitter-invariants/`. No core/API/control/merge edits.
- Checks: deterministic analytic exact-rational and metamorphic coefficient and
  full covariance comparisons; row permutations; time/position origins;
  algebraically scaled physical problems still expressed in seconds/metres;
  explicit sigma versus residual floor; near-rank-deficiency and precision limits.
- Ponytail FULL applied: reuse unittest + existing public functions; standard
  library rational reference, no dependency installation, API or unit extension.
- Verified narrow DONE may finish early only if no genuine bug remains. A genuine
  bug requires failing regression + root-cause/severity evidence, continued useful
  scoped investigation and terminal PARTIAL at deadline unless controller changes
  acceptance. Minute25 starts no new implementation. No filler or expanded scope.
- All physical M/S12/real-scene/GPU/deployment/publication/auth/terms gates stay shut.
