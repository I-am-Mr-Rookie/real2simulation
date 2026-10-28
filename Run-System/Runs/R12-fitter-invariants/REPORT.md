# R12-fitter-invariants — DONE (bounded AUDIT only)

**Two reproducible P2 numerical defects remain open in the audited product.**
Parent independently confirmed both and owns fixes in `swarm12-covariance-fix`.
DONE uses the direct narrow acceptance clarification saved in ACCEPTANCE.md;
it is not a product pass, fix verification, queue advancement or physical gate.

## Source, scope and clock

- Assigned: CODEX1 / managed `gpt-6.1-sol` / HIGH, as supplied. No routing change
  or independent model-identity attestation. `OpenCodex-managed; not polled`.
- Source head: `5e0fd65bf24fb38d3d8b4e4426dddf64e293f20d`.
  Unmodified fitter core blob: `b2dc16ed683b2ede9725b11e4d44c161a9baec64`.
- Branch/committed handoff pointer: `run/R12-fitter-invariants`, one scoped commit
  above that base. Parent owns cherry-pick, core fixes and integration.
- Canonical root and parent project are recorded in PLAN.md. Required inherited
  project ID is `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; parent discovery identified
  `Run Ponytail swarm to 10:00`, thread `01a1840d-7310-7991-8cb8-8ec4cfb149a7`,
  but its app metadata returned `projectId=null`. Therefore UI project association
  was not verified; no project membership was changed or falsely claimed.
- Issued 2026-10-28T20:46:38.309Z; first observed execution clock
  20:46:47.4163940Z. Original cutoff21:11:38.309Z, deadline21:16:38.309Z
  (Oct29 03:16:38.309+06:00) unchanged. Scientific/task work stopped
  **2026-10-28T20:59:25.1053625Z** after final evidence/scope/whitespace checks.
  Report/timebox/commit administration follows; reported_at is in TIMEBOX.json.
- Only owned test, `evidence/S11/invariants/`, and this run folder changed.
  No core/API/product/config/control/merge changes.

## Findings and completed audit

Root mechanisms, smallest fixtures, severity, independent derivations and limits:
`evidence/S11/invariants/FINDINGS.md`.

1. Known and declared covariance can be materially incorrect / contain a negative
   unselected diagonal while `valid=True` on near-rank-deficient full-rank inputs.
   Three-point interpolation proves intercept variance independently. Exact
   rational, 80-digit same-QR algebra and optional installed NumPy SVD corroborate.
2. Four-point residual-square underflow yields valid zero estimated uncertainty
   despite nonzero residuals. Exact variance is positive but unrepresentable:
   honest unavailable is acceptable; impossible positive floats are not demanded.

Meaningful regression coverage completed: paired row permutation (degree1/2),
full declared covariance under time-origin shifts through2^45, exact dyadic
position shifts through2^20, algebraically scaled physical problems in s/m,
explicit known sigma vs residual-floor semantics, near/exact rank deficiency,
full analytic timing sandwich and independent central-difference fit Jacobian.
Collapsed spacing at2^60 is correctly rejected and separated from invariance.
No unsupported cm/ms API conversion or stochastic seed-coverage duplication.

Tolerances: ordinary exact-rational full covariance3e-11 relative to marginal
scales (avoids arbitrary dimensional absolute floors); non-centred position
offset2^20 allows2e-8 for QR arithmetic on a large, exactly represented offset;
finite-difference timing derivatives use1e-7 relative /1e-8 absolute for division
of rounded coefficients by h=2^-18. Near-rank regressions allow a deliberately
loose0.1% error or explicit rejection/unavailable, yet expose10%/50%/negative
variance errors. Reference helper self-checks exact interpolation identities and
normal-equation residual moments; expected values do not come from production QR.

## Fresh verification

Python3.14.5; optional already-installed NumPy2.4.6 used only in evidence, never
required by tests/runtime. No installation.

| Command | Observed result / evidence |
|---|---|
| `python -m unittest discover -s tests/fitter -p test_core.py -v` |13/13 PASS; core-tests.txt |
| `python -m unittest discover -s tests/fitter -p test_uncertainty.py -v` |7/7 PASS; uncertainty-tests.txt |
| `python -m unittest discover -s tests/fitter -p test_api.py -v` |9/9 PASS; api-tests.txt |
| `python -m unittest discover -s tests/fitter -p test_invariants.py -v` |13 methods; nine passing, four failing methods / seven failing (sub)test events; invariants-tests.txt |
| `python -m unittest discover -s tests/fitter -v` |42 methods; exactly those seven intentional failure events, unittest exit1; fitter-final-tests.txt |
| `python evidence/S11/invariants/audit.py` |exit0; analytic-repro.json, five exact known-noise fixtures plus residual-underflow proof |
| JSON/source/hash assertions |PASS; exact audited head, five fixtures, positive exact-underflow variance and frozen regression SHA verified |
| `git diff --exit-code 5e0fd65 -- Build/fitter/core.py Build/fitter/api.py` |PASS, unchanged product |
| `git diff --cached --check` |PASS after trimming only five unittest progress-line trailing spaces in logs; no test/repro semantics changed |

All `.txt` evidence above is under `evidence/S11/invariants/`. Exploratory bounded
logs are retained separately; they are not extra independent defect counts.
No failures were marked expectedFailure, skipped or weakened to produce green.

Frozen tests SHA256: `DC3EBF3D96EA6D31F0D6CD9483B4EA35E9DD6742900DFDB6FD72AFDFAAA85703`.
Git normalized test blob: `62b8f59c259b137280e7e03738bbfbda34cfa4c6`.

## Applied skills, skips, risks and next

- Ponytail FULL: read exact installed marketplace skill; reused unittest and
  existing public fitter calls; smallest disjoint test/evidence-only change.
  Fractions/Decimal use standard library; no production abstraction, dependency,
  API/unit feature, stochastic seed search or unrelated cleanup.
- Verification-before-completion: fresh full targeted suite and immutable
  source/test hashes precede completion. TDD application is RED reproduction
  only; GREEN belongs to parent core owner, not falsely claimed here.
- No wider repository/build/UI/physical/real-scene/GPU/paid/deploy/publication/
  account/terms/credentials checks/actions. No physical M/S12 or gate success.
- Timing model remains independent first-order about the fitted trajectory;
  this does not prove errors-in-variables bias correction, common clock/scale
  uncertainty, nonlinear-noise covariance or real instrument calibration.
- Parent must verify core fixes against frozen regressions and baseline tests,
  then perform required targeted review/integration. Open product defects remain
  the material limitation of this AUDIT DONE receipt.
- Communication: mandatory opening skill update and concrete nonterminal defect
  notices only, not repeated report narration. Authorized parent callback through
  app tool was rejected: `cannot send to your native ancestor`; no bypass/retry
  workaround. Parent subsequently sent direct acceptance clarification. Discovery
  of the parent UI project metadata mismatch is retained above, not repaired
  outside Owns. Final communication is one report-pointer line.
- Observable token usage unavailable; coding/API monetary cost unknown. No paid
  job or external model/API call initiated by this audit.
