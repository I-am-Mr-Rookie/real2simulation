# R10-S11-fix — DONE (scoped implementation)

**Code/evidence commit:** `3f913b7f6ee5ac49626b0aa8c08ac6bbd98281f8`.
Branch `run/R10-S11-fix`, base `3fa80eb4985779f8b913ce1d9cdbd932f1b65468`.
Only assigned checkout used; no main merge/rebase, shared-control edits or publish.
Parent still owns caller-label integration and mandatory native Claude targeted
rereview before acceptance. Neither is claimed completed by this worker.

## Identity / truthful timing

- Assigned CODEX1 / managed `gpt-6.1-sol`, HIGH; runtime identity not independently observable.
- Parent project contract: `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; inherited inline
  simulation-only owner exception. No new chat/project/worker/schedule created.
- Issued **2026-10-28T19:59:19.659Z**; first recorded worker clock
  **2026-10-28T19:59:36.0394572Z**.
- Original cutoff **2026-10-28T20:24:19.659Z**; deadline
  **2026-10-28T20:29:19.659Z** (full 1,800 seconds, never reset/extended).
- Controller correction acknowledged: correct Dhaka deadline is
  **2026-10-29T02:29:19.659+06:00**, not the handout's 06:59.
- Task work/checks stopped **2026-10-28T20:13:01.0389264Z**. All owned fix/check
  criteria verified DONE early; no padding or early incomplete exception.
  Report/receipt finalization follows; actual report timestamp is in TIMEBOX.json.

## Findings reproduced / smallest complete fix (Ponytail full applied)

Read supplied full marketplace skill; inspected fitter/core/API/exports, quantity
contract, all matching code callers and fitter/instrument/lab tests; canonical
instructions, current controls, timebox policy and native audit report consulted.
Original reviewer checkout was archived: audit recovered first via `git show
e63e31f:Run-System/Runs/R10-S11-audit/REPORT.md`, then verified at canonical path
(controller identifies rebase `def3aa5`).

1. **Residual interval:** same fixed 20-point quadratic experiment now uses
   `t(.975,17)=2.1098155778333156`, not 1.96, because RSS/dof estimates sigma.
   Existing seed, random generator and **>=90/100** gate are unchanged. New
   interval-method/dof/nominal-coverage metadata distinguishes t intervals,
   explicit custom multipliers and zero-noise numerical diagnostics.
2. **Declared input noise:** reuse existing centred QR/inverse-R and physical
   Jacobian transform. Default API model `independent_position_time_first_order`
   uses OLS sandwich covariance with independent per-observation variance
   `max(RSS/dof, sy_i^2 + fitted_velocity_i^2 * st_i^2)`.
   Explicit legacy `iid_fixed_clock_scale` remains supported with sigma
   `max(residual_sigma, max(position_sigma))`; timing remains fixed there.
   Residual noise is floored, not automatically added/double counted.
3. **Honest precision:** API quantity uncertainty is explicitly one standard
   uncertainty, not a 95% interval (`covariance.interval=null`). Known declared
   noise can support covariance at zero residual dof; absent known noise cannot.
   Preserve `sigma=` override including explicit zero; reject invalid declarations
   and abstain on overflow or positive-sigma underflow instead of reporting zero.

No new runtime dependency, fitter abstraction, EIV optimizer, quantity-schema or
export change. NumPy/SciPy are installed **reference checks only**. Fixed-design
t critical value avoids a new general quantile implementation; tests require
recomputation if the experiment's dof changes.

## Fresh generated evidence

Under `evidence/S11/uncertainty-hardening/`:

| Actual check | Observed result |
|---|---|
| `reproduce.py` before, same audit population (200 batches x 100) | coverage **0.93645**; **10** batches fail unchanged gate |
| Same generator after fix | coverage **0.95095**; **3** batches still fail (finite sampling, not hidden) |
| Default batch, unchanged seed 0 | **96/100**, PASS; t interval / 17 dof / nominal .95 |
| Noise-free 20-point API fixture, declared position .05 m / time .01 s | gravity standard uncertainty before **1.627815429422649e-15**, default after **0.19626533680225153 m/s^2** |
| Same fixture, explicit fixed-clock legacy model after | **0.07547223547528771 m/s^2** |
| `reference_checks.py` | quantile equals installed SciPy; full covariance matches independent NumPy reference at ordinary and 1e9-shifted times (relative errors ~1e-15); timing derivative finite-difference reference passes |
| Fresh final unittest command below | **47 tests PASS** |
| `git diff --check` / staged Owns assertion | PASS; product stage contains only 14 owned files |

JSON numbers above come from actual `before.json`, `after.json`, `reference.json`;
not physical measurements or model-authored experimental results. Individual
batch failures remain visible in raw evidence; no seed search or threshold change.

```powershell
python evidence/S11/uncertainty-hardening/reproduce.py
python evidence/S11/uncertainty-hardening/reference_checks.py
python -m unittest tests.fitter.test_core tests.fitter.test_api tests.fitter.test_uncertainty tests.instruments.test_synthetic tests.instruments.test_quantity_contract tests.lab.test_pipeline tests.lab.test_session_bridge
```

New checks cover integrated Student-t density, aggregate coverage, closed-form
heteroscedastic covariance, per-observation position/timing monotonicity, residual
floor preservation, known-sigma/zero-dof/zero-noise, rank/nonfinite declarations,
overflow/underflow and JSON-safe unavailable covariance. Baseline 33 tests passed;
three old adapter assertions changed intentionally for the new model/known-noise
semantics. Existing pipeline and session-bridge behavior tests pass unchanged.

## Handoff / limits / communication

Exact additive API fields and parent-owned stale pipeline/bridge label locations
are in `INTEGRATION.md`; parent acknowledged ownership of those caller changes.
Unchanged caller tests passing does not validate their now-stale blanket text.
Parent must obtain **native Claude targeted rereview of these two findings** and
serialize integration/FF. No gate acceptance or cross-vendor approval claimed.

Communication exceptions: higher-priority required pre-tool update and finding
update, plus requested actionable API handoff; no optional recurring narration,
cross-chat messages or duplicate chat report. Final reply is one report pointer.
Costs/tokens unknown; **OpenCodex-managed; not polled**. No paid job, GPU, real
scene, physical Gate M/S12, deploy, publication, account/terms/credential/provider
or policy action; no secret values read. Shared controls and other reports untouched.

Skipped: general-purpose quantile engine, full errors-in-variables/bias correction,
correlated calibration propagation, UI/bridge edits, broad vendor review.
Risk: first-order independent-error approximation and declared noise are not
calibrated physical coverage; correlated clock-rate/scale errors remain excluded.
