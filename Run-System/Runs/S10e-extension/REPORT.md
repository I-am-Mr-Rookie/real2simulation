# S10e-extension REPORT

- **Status:** DONE — accepted synthetic simulation child; no Gate P/M claim.
- **Lane/model:** CODEX-1, Sol medium, existing managed route; OpenCodex-managed, not polled.
- **Clock:** issued `2026-10-28T18:04:13Z`; nominal deadline `2026-10-28T18:34:13Z`; work stopped `2026-10-28T18:09:16Z`; reported at the actual report time recorded in TIMEBOX.json.
- **Base/branch:** `main` `03d57f6982e21c5d914a53a7a2007c73689b5a5a`; `run/S10e-extension`.
- **Owns changed:** `Build/simulator/extended-templates.mjs`, `tests/simulator/extended-templates.test.mjs`, `evidence/S10/extension-templates/`, this run directory only.

## Result

Added explicit fixed-step RK4 ramp and pendulum APIs. Ramp has explicit length, incline angle, friction coefficient, initial speed, signed friction dynamics, and geometry. Pendulum has explicit length, gravity, initial angle/angular velocity, nonlinear `sin(theta)` dynamics, and pivot-origin geometry. Outputs use consistent SI units, provenance labels, deterministic integer-horizon samples, frozen nested structures, and analytic-comparison metadata. Small-angle comparison is limited to amplitude <= 0.1 rad; nonlinear cases are labelled nonlinear-only.

Added `extendedTrajectoryFromValidatedArtifact(raw)` as the integration entrypoint. It consumes the actual S08 `export_validated_setup.py` envelope, checks the established trusted transport/scene/world -Y/integer-horizon contract, maps schema quantities into the exported API, and leaves Python `validate_setup` authoritative.

## Fresh checks

- `node --test tests/simulator/extended-templates.test.mjs tests/simulator/trajectories.test.mjs`: **12 passed, 0 failed**.
- `PYTHONPATH=tests/spec;tests/simulator python -m unittest test_ramp test_pendulum -v`: **23 passed, 0 failed**.
- Real Python export envelope consumed for both ramp and pendulum.
- `git diff --check`: PASS.
- Tests cover analytic ramp, small-angle pendulum, nonlinear convergence/energy, zero horizon, sparse/nonfinite/overflow/provenance rejection, determinism, immutability.

## Ponytail choices / skips / risks

Reused `rk4.mjs` and the existing S08 export envelope; added no dependency, duplicated integrator, schema adapter, lab code, or peer-owned edits. Skipped contacts, real-scene measurements, calibration, Gate P/M/S12, deployment, spend, and cross-language lab integration owned by the parent. Ramp sign reversal is represented explicitly but does not model static-friction sticking; upgrade if the lab requires a stick/slip regime. All evidence is synthetic/simulated.

Communication stayed silent; no shared controls were changed. Parent callback: import `extendedTemplateApi` or named exports from `Build/simulator/extended-templates.mjs`; consume `extendedTrajectoryFromValidatedArtifact(raw)` from the existing Python exporter output. See evidence README for exact signature and sample mapping.
