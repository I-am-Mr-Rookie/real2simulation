# S10hi numeric acceptance

`acceptance.json` is fresh machine-readable evidence from `python -m Build.lab.acceptance`.

- 15 explicit synthetic cases cover all four S08 templates, gravity changes, short/long horizons, upward free-fall, zero-horizontal and tiny-height ballistic cases, supported-positive-acceleration ramp preflight, multiple-period pendulum, and a zero-answer equilibrium guard.
- All 15 cases passed the unchanged `0.005` dimensional characteristic-scale threshold and actual seeded replay check. The measured errors remain per-case in `acceptance.json`; no failing or rejected case was filtered.
- Contact diagnosis installed the pinned dependency with `npm ci --ignore-scripts --no-audit --no-fund`, then measured the existing same-state Rapier adapter at `dt` 0.02/0.01/0.005 for free-fall and projectile. All six contacts were observed at 0.62 s with zero sweep spread; max absolute sampled contact-time error was 0.0023823880 s versus the analytic 0.6223823880 s. No jitter, fallback, or rebound was observed/claimed.
- Fallback policy is machine-readable only: RK4-only and free dragging disabled when contact integration is unsupported/jittery. No UI policy was changed.
- S10g UI integration and required other-vendor R-P review are not claimed; this is simulation-only evidence and not Gate P, Gate M, or a physical result.

Fresh checks: `node --test tests\\lab\\contact-integration.test.mjs` — 2/2 passed; acceptance rerun — 15/15 cases passed; `git diff --check` — passed.
