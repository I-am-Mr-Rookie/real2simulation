# S10hi numeric acceptance

`acceptance.json` is fresh machine-readable evidence from `python -m Build.lab.acceptance`.

- 15 explicit synthetic cases cover all four S08 templates, gravity changes, short/long horizons, upward free-fall, zero-horizontal and tiny-height ballistic cases, supported-positive-acceleration ramp preflight, multiple-period pendulum, and a zero-answer equilibrium guard.
- All 15 cases passed the unchanged `0.005` dimensional characteristic-scale threshold and actual seeded replay check. The measured errors remain per-case in `acceptance.json`; no failing or rejected case was filtered.
- Contact diagnosis attempted the existing same-state Rapier adapter at `dt` 0.02/0.01/0.005 for free-fall and projectile. This checkout lacks the existing `@dimforge/rapier3d-compat` runtime, so the result is explicitly `unavailable`, not a jitter pass or rebound claim.
- Fallback policy is machine-readable only: RK4-only and free dragging disabled when contact integration is unsupported/jittery. No UI policy was changed.
- S10g UI integration and required other-vendor R-P review are not claimed; this is simulation-only evidence and not Gate P, Gate M, or a physical result.

Fresh checks: `python -m unittest tests\\lab\\test_regression.py tests\\lab\\test_acceptance.py` — 3/3 passed; `git diff --check` — passed.
