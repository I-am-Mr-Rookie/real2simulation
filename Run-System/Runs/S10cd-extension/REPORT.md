# S10cd-extension report

- **Status:** DONE
- **Lane/model:** CODEX-1 / GPT-6.1 Sol medium, managed route; parent project `91e441f8-e40c-4ec4-bea2-de7fa1582d97`.
- **Timebox:** issued `2026-10-28T18:04:13Z`; nominal deadline `2026-10-28T18:34:13Z`; final work stopped `2026-10-28T18:19:00Z`; reported `2026-10-28T18:19:10Z`.

## Changed paths

- `Build/simulator/contacts.mjs`: Rapier WASM init, finite explicit geometry/physics validation, floor + dynamic sphere, actual narrow-phase manifolds, stable `sphere`/`floor` IDs, and `world.free()` cleanup.
- `Build/simulator/contact-runs.mjs`: settled `runContactAwareTrajectory(input)` API for free-fall/projectile or an existing trajectory.
- `tests/simulator/contacts.test.mjs`: falling-floor contact, no-contact determinism, invalid boundaries.
- `evidence/S10/extension-contacts/README.md`: semantics, limits, fresh evidence.

## P1 correction review

- Removed hidden `gravity ?? 9.81`; gravity is required and positive.
- Set `world.timestep = trajectory.dt_s` before every Rapier step.
- Rapier receives each exact RK4 sample pose with solver velocity zero and gravity scale zero; it cannot free-evolve a disconnected trajectory.
- Output stops at the first actual manifold contact, so no post-floor fictitious samples are returned.
- Contact timing is tested at `dt=0.005`, `0.01`, and `0.02` against analytic impact within one sample. Sparse/empty samples and invalid state reject; output is deeply immutable.

## Parent callback / signature

`import { runContactAwareTrajectory } from './Build/simulator/contact-runs.mjs'`

`await runContactAwareTrajectory({ template: 'free_fall'|'projectile', initialPosition, initialVelocity, gravity, dt, steps, source: 'simulated', inputProvenance: 'synthetic', geometry: { floorY, floorHalfExtents: [x,y,z], sphereRadius }, physics: { friction, restitution, density } })`

For an existing accepted RK4 output: `contactAwareTrajectory({ trajectory, geometry, physics, gravity })` from `contacts.mjs`.

## Checks

- `npm ci --ignore-scripts --no-audit --no-fund` in `Build/simulator` — PASS; Rapier 0.21.0 installed.
- `node --test tests/simulator/contacts.test.mjs` — 5/5 PASS.
- `node --test tests/simulator/*.test.mjs` — 14/14 PASS.
- Official Rapier JS guidance checked: async `init()`, explicit `World`, colliders/body, `world.step()`.

## Limits / skipped

No trajectory, manifest/lock, parent lab, shared control, deployment, spend, media, physical calibration, Gate P, or S08 real-geometry edits. Rapier narrow phase is driven by the same returned RK4 sample state and stops at first contact; no Rapier contact response or post-contact samples are emitted. Parent performs offline lab E2E integration. Worked silently.
