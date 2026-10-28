# S10cd-extension report

- **Status:** DONE
- **Lane/model:** CODEX-1 / GPT-6.1 Sol medium, managed route; parent project `91e441f8-e40c-4ec4-bea2-de7fa1582d97`.
- **Timebox:** issued `2026-10-28T18:04:13Z`; nominal deadline `2026-10-28T18:34:13Z`; work stopped `2026-10-28T18:08:30Z`; reported `2026-10-28T18:08:45Z`.

## Changed paths

- `Build/simulator/contacts.mjs`: Rapier WASM init, finite explicit geometry/physics validation, floor + dynamic sphere, actual narrow-phase manifolds, stable `sphere`/`floor` IDs, and `world.free()` cleanup.
- `Build/simulator/contact-runs.mjs`: settled `runContactAwareTrajectory(input)` API for free-fall/projectile or an existing trajectory.
- `tests/simulator/contacts.test.mjs`: falling-floor contact, no-contact determinism, invalid boundaries.
- `evidence/S10/extension-contacts/README.md`: semantics, limits, fresh evidence.

## Parent callback / signature

`import { runContactAwareTrajectory } from './Build/simulator/contact-runs.mjs'`

`await runContactAwareTrajectory({ template: 'free_fall'|'projectile', initialPosition, initialVelocity, gravity, dt, steps, source: 'simulated', inputProvenance: 'synthetic', geometry: { floorY, floorHalfExtents: [x,y,z], sphereRadius }, physics: { friction, restitution, density } })`

For an existing accepted RK4 output: `contactAwareTrajectory({ trajectory, geometry, physics, gravity })` from `contacts.mjs`.

## Checks

- `npm ci --ignore-scripts --no-audit --no-fund` in `Build/simulator` — PASS; Rapier 0.21.0 installed.
- `node --test tests/simulator/contacts.test.mjs` — 3/3 PASS.
- `node --test tests/simulator/*.test.mjs` — 12/12 PASS.
- Official Rapier JS guidance checked: async `init()`, explicit `World`, colliders/body, `world.step()`.

## Limits / skipped

No trajectory, manifest/lock, parent lab, shared control, deployment, spend, media, physical calibration, Gate P, or S08 real-geometry edits. Rapier detects contacts beside RK4; it does not replace analytic state or claim physical truth. Parent performs offline lab E2E integration. Worked silently.
