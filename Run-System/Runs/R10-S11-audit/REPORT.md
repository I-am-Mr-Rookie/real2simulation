# R10-S11-audit — S11 numeric/uncertainty gate audit

Status: DONE (narrowed per owner update: required numeric gate audit only; no fixes, no broad review).
Lane/model: native Claude reviewer (inline). Issued 2026-10-28T19:50:37.036Z; deadline 2026-10-28T20:20:37.036Z. Work stopped 2026-10-28T19:55:07.757Z.
Head audited: f82ed85fd96c38f8fcee23322657e92e5f4f8e92 (branch run/R10-S11-audit). Costs unknown; coding quota OpenCodex-managed; not polled.
Ponytail full applied: audit only, smallest evidence (stdlib repros, existing tests), no implementation edits.

## Fresh checks
- `python -m unittest tests.fitter.test_core tests.fitter.test_api tests.instruments.test_synthetic tests.instruments.test_quantity_contract tests.lab.test_pipeline` → Ran 33, OK. (pytest not installed.)
- Repros below; all simulation-only. No physical evidence.

## Findings

### P2-1 Coverage gate uses normal z with residual-estimated sigma; pass is seed-dependent
- Build/fitter/core.py:286-290 (`interval_z=1.96`, threshold 0.90) with sigma from `_sigma2` rss/dof (core.py:217), dof=17. Correct quantile is Student-t (t_0.975,17 ≈ 2.110); expected coverage with 1.96 ≈ 93.4%, not 95%.
- Repro: `coverage_regression(seed=k)` for k=0..199 → mean 0.93645; **10/200 seeds FAIL** (<0.90), e.g. seed=7 → 0.88. Default seed=0 → 0.95 PASS.
- tests/fitter/test_core.py:72-75 asserts one fixed seed only, so "100-seed coverage PASS" is partly seed luck and silently undercovers.
- Fix (Codex): use t quantile for fit.dof in the interval (or document z as asymptotic and test aggregate over several seeds against expected ~0.934).

### P2-2 Valid gravity reported with uncertainty far below declared input uncertainty
- Build/fitter/api.py:116-131 → core.py:217 (residual-only sigma) and core.py:299: noise-free positions each declaring uncertainty 0.05 m (times 0.01 s) return `covariance.valid=True`, `gravity.uncertainty=3.35e-15 m/s^2`.
- The "input quantity uncertainty not propagated" assumption is documented (api.py:112,127; pipeline.py:92), so propagation absence is a known limit; but returning status "available"/valid with machine-epsilon uncertainty is an unsound positive result (overconfident, would pass any coverage check by luck of value).
- Fix (Codex): use declared input sigma via existing `jacobian_covariance(sigma=...)` as a floor (e.g. max(residual sigma, declared position sigma)), or mark gravity unavailable when residual sigma << declared input sigma.

## Concrete no-findings (checked)
- QR rank: rank-deficient/zero-span designs raise (core.py:42-43,67-68). Rank always degree+1 when returned; AIC k=rank consistent.
- AIC roundoff: noiseless linear data (two cases) select degree 1; quadratic gains penalty 2 at equal rss. Exact-zero rss → -inf handled and serialized as null with status (api.py:137-147).
- Jacobian transform local→physical (core.py:243-249) consistent with coefficient back-transform (core.py:82); underflow guard core.py:258.
- Non-finite/bool inputs rejected at quantity and fitter boundaries.

## Not checked / risks
- Constant time/position instrument bias assumed absorbed by c0/c1 (reasoning only, not repro'd). Clock-rate/scale errors fixed by design (documented). Sessionbridge/JS UI not audited (owner narrowed scope). No implementation edits.

Communication: silent; single final line.

