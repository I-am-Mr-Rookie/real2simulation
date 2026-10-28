# R-SIM-swarm independent review

Review scope: read-only review of current peer correction heads; no source or
control edits. This is independent CODEX-1 review evidence, not an other-vendor
gate signoff and not a parent product/gate result.

## Reviewed heads

- S10 simulator: `eb24f12a66397a2bd79858c8028841c6353f97b2`
- S11 instruments: `ef570b63ca12c6bd34bb54ca66aadbe7ae179eef`
- S11 fitter: `bc6a7ac197a71ea30842e571b4c3124048881eef`

## Findings and re-review status

### P1 — public fitter leaks `OverflowError` for finite huge inputs

File: `Build/fitter/core.py:59` and `:125` in the previously reviewed fitter
head `bc6a7ac`; the peer currently has uncommitted corrective edits.

The corrective commit `9700c3c` (final head `57027a3eff25d3f0bf7c8f966c2e9cfa45f71f5b`)
now makes the primary repro raise `FitError`
(`time_arithmetic_overflow`) and add a regression test. A second family with
finite positions around `1e154` also fails closed as `FitError`. **P1 is fixed
in the committed final source.**

### P2 — AIC still labels non-zero residual as exact

File: `Build/fitter/core.py:142-146` in fitter head `bc6a7ac`.

The corrective commit removes the arbitrary epsilon cutoff, so the `1e-15` repro now
has finite AIC. However, the existing exact-fit tests fail: ordinary exact
quadratic data has a small floating residual (`rss > 0`) and now returns finite
AIC instead of the expected `-inf`. **P2 is not accepted:** preserve honest
nonzero-RSS behavior while revising exact-fit handling/tests so the full suite
passes (prefer a numerically justified exactness status, not the removed
absolute cutoff). The peer revised exact-fit tests to use an exactly representable
linear case; final suite is green.

## Clean areas and fresh checks

- Simulator final head `e16810e4de1ff5e2e4d14f370995a07442ae12c1`: **3/3 pass**
  with `node --test tests/simulator/simulator.test.mjs`; the added recursive
  freeze and sparse-vector guards pass. The actual Python S08 adapter test is
  **2/2 pass** with `PYTHONPATH=tests/spec;tests/simulator`, and the synthetic
  scene validator passes.
  Reviewed RK4 positive finite `dt`, zero-step validation, sparse-state guard,
  deterministic trace, and the exact Python `validate_setup` producer boundary.
- Instruments final head `f261e91dcef7d1fa74652847e433352e94b55057`: **10/10
  pass** with `python -m unittest discover -s tests/instruments`; unit allowlist,
  source error validation, mutability, uncertainty and total-error checks pass.
  Reviewed separate total error vs supplied bias/uncertainty, seeded replay,
  boolean/non-finite/overflow guards, and simulated provenance.
- Fitter final head `57027a3eff25d3f0bf7c8f966c2e9cfa45f71f5b` with compatibility
  `PYTHONPATH=<fitter>;<instruments>`: **11/11 pass**; independent repro shows
  P1 `FitError` and P2 finite AIC for nonzero RSS. The final `_aic` source uses
  `rss == 0.0` only; no unsupported exactness claim is made for nonzero RSS.
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
