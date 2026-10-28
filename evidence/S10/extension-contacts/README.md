# S10cd extension contact evidence

`contactAwareTrajectory({ trajectory, geometry, physics, gravity })` uses `@dimforge/rapier3d-compat` 0.21.0, async WASM init, explicit gravity, floor cuboid, dynamic sphere, density, friction, restitution, CCD, and fixed `dt` stepping. It reads actual Rapier narrow-phase manifolds and maps stable collider IDs (`sphere`, `floor`).

The adapter preserves the supplied S10a/S10b RK4 sample state and adds `contact` plus `contacts[]` to each same `{step,time_s,position_m,velocity_m_s}` sample. Rapier is a detector beside RK4, not a replacement integrator or physical Gate-P result. `runContactAwareTrajectory` builds accepted free-fall/projectile RK4 output before attaching contacts.

Fresh check: `node --test tests/simulator/*.test.mjs` — 12/12 pass. Falling sphere produces a real floor manifold; a short high drop remains no-contact; repeated runs are deterministic; invalid geometry/physics rejects. Synthetic only; no physical calibration or S08 real-geometry claim.
