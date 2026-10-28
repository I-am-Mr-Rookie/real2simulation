# S10cd extension contact evidence

`contactAwareTrajectory({ trajectory, geometry, physics, gravity })` uses `@dimforge/rapier3d-compat` 0.21.0, async WASM init, explicit gravity, floor cuboid, dynamic sphere, density, friction, restitution, CCD, and fixed `dt` stepping. It reads actual Rapier narrow-phase manifolds and maps stable collider IDs (`sphere`, `floor`).

The adapter places each supplied S10a/S10b RK4 sample into Rapier, sets `world.timestep` to the same `dt`, runs the actual narrow phase, and stops at the first manifold contact. It adds `contact` plus `contacts[]` to the same `{step,time_s,position_m,velocity_m_s}` sample; it never emits a disconnected post-contact Rapier trajectory. `runContactAwareTrajectory` builds accepted free-fall/projectile RK4 output before attaching contacts. Gravity is mandatory; no hidden default exists.

Fresh check: `node --test tests/simulator/*.test.mjs` — 14/14 pass. Falling sphere produces a real floor manifold; dt 0.005/0.01/0.02 contact timing is within one analytic sample; a short high drop remains no-contact; repeated runs are deterministic; sparse/invalid input rejects; output is deeply immutable. Synthetic only; no physical calibration or S08 real-geometry claim.
