# R-S10-extension independent review

## Result
PARTIAL under the approved owner-stop exception. The reviewed checkout is exactly `03d57f6982e21c5d914a53a7a2007c73689b5a5a` (main and contacts peer at review start). No S10c Rapier implementation or S10d lab pipeline exists in that source head; Rapier is only pinned in `Build/simulator/package.json` / lockfile. The requested canonical lab files were also absent from canonical main at review time, so no E2E claim is possible.

## Findings
1. **P1 — Rapier/contact scope is unimplemented, not merely unverified.** `Build/simulator/apparatus.mjs` only validates a synthetic transport envelope and returns a sphere plus copied `scene.colliders`; it never imports/initializes Rapier, creates bodies/colliders, steps a world, resolves contact, or reports contact events. `git grep -n -i rapier Build tests` returns no runtime use. The package pin alone cannot support S10c acceptance.
2. **P1 — S10d trusted lab E2E is absent at this head.** `Build/lab/pipeline.py`, `Build/lab/simulate.mjs`, and `tests/lab/test_pipeline.py` were not present in canonical main or any sibling checkout inspected. Therefore the S08->Node->instruments->fitter trust boundary, provenance propagation, and fitter-result authorization remain unreviewed.
3. **P2 — Existing trajectory contract is appropriately conservative.** `Build/simulator/trajectories.mjs` uses fixed-step RK4, freezes validated artifacts, requires `source=simulated` and `inputProvenance=synthetic`, and rejects non-integer duration/time-step horizons rather than flooring. The tests cover determinism, no mutation, finite samples, initial stop-plane, and trusted-artifact identity. This is synthetic/contract evidence only.
4. **P2 — `apparatus.mjs` explicitly documents its envelope as not a security boundary.** Public JSON must not be treated as trusted merely from labels; a future lab/pipeline integration must keep Python validation and artifact identity in the producer boundary and avoid accepting caller-constructed labels.
5. **P2 — Analytic ramp/pendulum templates are separate Python oracles, not integrated into the Node simulator/contact path.** Their tests cover units, bounds, deterministic outputs, and small-angle honesty, but no physical contact or cross-runtime replay equivalence is established.

## Checks
- `python -m unittest discover -s tests/spec -p 'test_*.py' -v`: PASS (completed output; spec suite passed).
- `node --test tests/simulator/*.test.mjs tests/viewer/viewer.test.mjs`: started; source review confirms simulator/viewer contract tests present. Full final output was not retained before owner stop.
- `git grep -n -i rapier Build tests`: no runtime use; only package pin in `Build/simulator/package.json` and lockfile.
- Peer inspection: `swarm2-contacts` and canonical main both at `03d57f6`; `swarm2-replay` and `swarm2-templates` remained at the same base when checked. No peer code was edited or copied.

## Limits / skipped
No physical gate, R-P, real-scene, paid job, deployment, auth, publication, or model/config claim. No generated writeful peer outputs. Canonical lab files were unavailable; parent should re-run this review against their exact integrated heads and add the source-head hashes to the final report.

## Ponytail/application
Used smallest source-only review, reused existing contracts and test seams, isolated owned evidence, avoided dependency/framework expansion, and preserved truthful synthetic-vs-physical boundaries. OpenCodex-managed route was not polled.
