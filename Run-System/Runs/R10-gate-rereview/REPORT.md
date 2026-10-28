# R10-gate-rereview — DONE

**Gate verdict: RESOLVED / PASS for all three targeted decisions. No P0–P2 open. One P3 note (no observed defect).**
Pinned source `72b1cbf55b4cdf914496dde644dd3aec745885fa` (branch run/R10-gate-rereview; source HEAD unchanged). Native review chat (Claude, medium; not Claude Code). UTC start 2026-10-28T20:18:20Z, work stopped 2026-10-28T20:23:36.334Z. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable). No GPU/API/model spend.

Scope: targeted only (owner: no broad re-audit). Read original audits (R10-S10-audit, R10-S11-audit), fix reports (R10-S10-fix, R10-S11-fix, R10-lab-contract) and actual `git diff main...72b1cbf` of contacts.mjs, mystery-g.mjs, fitter core/api, session-service/bridge, LabClient and tests.

## 1 Gate P (S10 P2-1, P2-2) — RESOLVED
- Code: Build/simulator/contacts.mjs:5-7 (`rapierFinite` = finite after `Math.fround`; `positive` rejects f32 zero/overflow); derived `floorCenterY` checked finite in f64 and f32 and reused for the collider; strict `y - r < floorY` initial-penetration reject, equality (exact touch) allowed. Analytic/replay loop unchanged except per-sample f32 position check.
- Fresh repro [gatep-repro.txt](../../../evidence/reviews/R10-gate-rereview/gatep-repro.txt): audit f64 overflow → reject; f32-only overflow (centre −3.5e38) → reject; audit penetration y=0.05 and 1-ulp penetration → reject; exact touch → contact t=0 bracket [0,0]; +EPSILON → no contact; analytic impact within 0.005 s and inside bracket for dt 0.005/0.0025/0.001 (err 2.6e-3, 1.2e-4, 6.2e-4 s).
- P3 note (non-blocking): touch/penetration decided in f64 while Rapier narrow phase is f32; far from origin sub-f32-ulp gaps are precision-limited. Probe +1e-5 m at floorY=1000 returned no contact (correct); scenes use floorY≈0.

## 2 S11 (P2-1, P2-2) — RESOLVED
- Formula read: Build/fitter/core.py:316-339 fixed 20-pt quadratic, dof 17, multiplier 2.1098155778333156 (== scipy `stdtrit(17,.975)` exactly), threshold ≥0.90 unchanged; custom multiplier / zero-noise labelled with `nominal_coverage=None`. core.py:226-297 declared-sigma sandwich, per-row v_i = max(RSS/dof, σy² + (v̂_i σt)²) at fitted velocity; non-finite/underflow → `valid False`. api.py:106-132 default `independent_position_time_first_order`; explicit legacy `iid_fixed_clock_scale` = homoscedastic max(max σy, residual σ). One-SE label api.py:120 and LabClient.jsx reveal.
- Independent NumPy/SciPy reference [s11_rereview.txt](../../../evidence/reviews/R10-gate-rereview/s11_rereview.txt): 200 batches → 3 FAIL, mean 0.95095 (binomial P(fail)=1.15%/batch ≈ 2.3/200 expected; honestly retained). Sandwich u matches reference ≤3.6e-15 rel on 3 cases incl. audit noise-free σy=0.05/σt=0.01 (now 0.196 m/s², was 3.35e-15); legacy matches ≤3.4e-15.
- Edges: dof0 σ=0 → covariance unavailable; dof0 declared σ → available from declared inputs only (residual floor null, labelled); σ 1e200 (position or time) → unavailable; σ 1e-200 → residual floor dominates (honest); repeated times → rejected; unknown model → error.

## 3 S10 session guards (R10-lab-contract) — RESOLVED
- Code: Build/lab/session-service.mjs:37-42 sticky `stopped` makes abort/timeout/stdin/spawn-error + close(0) reject; slot freed only in `finish` on close; `activeBridges += 1` after synchronous spawn (throw consumes none). :20-24 `assertCurrent` (Map identity, TTL, abort) after bridge and after handoff hashing; :69 aborted caller cannot receive cached success. Build/simulator/mystery-g.mjs:12 allowlist = exactly the two API models; reveal only via WeakMap-bound handoff of the fitted value.
- Fresh: session-service + mystery-g tests 29/29 PASS ([tap](../../../evidence/reviews/R10-gate-rereview/session-mystery-tests.tap)). Real-process repro ([session-repro.txt](../../../evidence/reviews/R10-gate-rereview/session-repro.txt)): 6× real async ENOENT → bounded error, slots 0; real abort mid-fit → error, not cached; real TTL expiry mid-fit → `session_expired_during_fit`, not cached; real Mystery fit → new model, reveal == fitted g, start payload has no gravity/seed/setup, slots 0.
- Not claimed: OS process-tree death (taskkill /T outcome not verified).

## Fresh commands
- `cd Build/simulator; npm ci --no-audit --no-fund` (own worktree, lockfile) → added 1 package.
- `node --test tests/simulator/*.test.mjs tests/lab/*.test.mjs` → 66/66 PASS.
- `python -m unittest tests.fitter.test_core tests.fitter.test_api tests.fitter.test_uncertainty tests.lab.test_pipeline tests.lab.test_session_bridge` → 37 OK.
- `node evidence/reviews/R10-gate-rereview/gatep-repro.mjs`; `python evidence/reviews/R10-gate-rereview/s11_rereview.py`; `node evidence/reviews/R10-gate-rereview/session-repro.mjs`.

## Ponytail / skipped / risks
- Applied full: reused existing tests/helpers; three small repro scripts; no source edits.
- Skipped: broad re-audit; instruments/acceptance and S10 Python adapter suites (controller ran); Windows process-tree kill verification.
- Risk: sandwich is first-order, independent errors, no clock-rate/scale correlation (labelled); all synthetic — not physical Gate P/M evidence.
- Communication: silent; one final line. Only owned paths committed; no source/shared-control edits.
