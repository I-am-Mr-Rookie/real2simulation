# S10e-extension REPORT

- **Status:** DONE — accepted synthetic simulation child; no Gate P/M claim.
- **Lane/model:** CODEX-1, Sol medium, existing managed route; OpenCodex-managed, not polled.
- **Clock:** issued `2026-10-28T18:04:13Z`; nominal deadline `2026-10-28T18:34:13Z`; work stopped at the latest correction stop, recorded in TIMEBOX.json; reported at the actual report time recorded in TIMEBOX.json.
- **Base/branch:** `main` `03d57f6982e21c5d914a53a7a2007c73689b5a5a`; `run/S10e-extension`.
- **Owns changed:** `Build/simulator/extended-templates.mjs`, `tests/simulator/extended-templates.test.mjs`, `evidence/S10/extension-templates/`, this run directory only.

## Result

Added explicit fixed-step RK4 ramp and pendulum APIs. Ramp has explicit length, incline angle, friction coefficient, initial speed, S08-compatible positive acceleration, endpoint stopping, and geometry. It rejects coasting/stalling/static-friction regimes (`a <= 0`) instead of using sign-chatter. Endpoint output stops before the endpoint and exposes a sampled crossing bracket without post-end geometry. Pendulum has explicit length, gravity, initial angle/angular velocity, nonlinear `sin(theta)` dynamics, and pivot-origin geometry. Outputs use consistent SI units, provenance labels, deterministic integer-horizon samples, frozen nested structures, and analytic-comparison metadata. Small-angle comparison is limited to amplitude <= 0.1 rad; nonlinear cases are labelled nonlinear-only.

Review correction commits: `9956c5c` (endpoint/stall/finiteness implementation) and `41f2ba5` (overflow regression test). Derived position/velocity vectors now reject non-finite results after finite RK4 state/input checks.

Added `extendedTrajectoryFromValidatedArtifact(raw)` as the integration entrypoint. It consumes the actual S08 `export_validated_setup.py` envelope, checks the established trusted transport/scene/world -Y/integer-horizon contract, maps schema quantities into the exported API, and leaves Python `validate_setup` authoritative.

## Fresh checks

- `node --test tests/simulator/extended-templates.test.mjs tests/simulator/trajectories.test.mjs`: **13 passed, 0 failed**.
- `PYTHONPATH=tests/spec;tests/simulator python -m unittest test_ramp test_pendulum -v`: **23 passed, 0 failed**.
- Real Python export envelope consumed for both ramp and pendulum.
- `git diff --check`: PASS.\n- Parent `tests/lab/test_regression.py`: **1 passed, 0 failed** after the endpoint/stall/finiteness correction.
- Tests cover analytic ramp, small-angle pendulum, nonlinear convergence/energy, zero horizon, sparse/nonfinite/overflow/provenance rejection, determinism, immutability.

## Ponytail choices / skips / risks

Reused `rk4.mjs` and the existing S08 export envelope; added no dependency, duplicated integrator, schema adapter, lab code, or peer-owned edits. Skipped contacts, real-scene measurements, calibration, Gate P/M/S12, deployment, spend, and cross-language lab integration owned by the parent. Ramp endpoint semantics are sampled: the last emitted sample is before the endpoint and `stop.bracket.after` carries only scalar crossing state. A future stick/slip model would require a separate S08 contract; it is intentionally rejected here. All evidence is synthetic/simulated.

Communication stayed silent; no shared controls were changed. Parent callback: import `extendedTemplateApi` or named exports from `Build/simulator/extended-templates.mjs`; consume `extendedTrajectoryFromValidatedArtifact(raw)` from the existing Python exporter output. See evidence README for exact signature and sample mapping.

