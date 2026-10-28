# R-S10-extension independent review

## Result
PARTIAL under the approved owner-stop exception. The reviewed checkout is exactly `03d57f6982e21c5d914a53a7a2007c73689b5a5a` (main and contacts peer at review start). No S10c Rapier implementation exists in that source head; Rapier is only pinned in `Build/simulator/package.json` / lockfile. Parent later exposed uncommitted S10d lab files in canonical main; their 3/3 offline tests pass, with the boundary findings recorded below. No physical or gate claim is possible.

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
No physical gate, R-P, real-scene, paid job, deployment, auth, publication, or model/config claim. No generated writeful peer outputs.

## Fresh parent lab and replay review (18:14Z)

Parent's uncommitted canonical lab files were then reviewed. `python -m unittest discover -s tests/lab -p 'test_*.py' -v` passed 3/3 (the direct `python tests/lab/test_pipeline.py` form is not runnable because its import path omits the repository root; the documented module/discovery form works). Source hashes at observation: `Build/lab/pipeline.py` `703FAA6F3BD6CA64CF3F7CA634F8FD52AE29B04A0CB806915EBB82065F4E62B9`; `simulate.mjs` `D8052B254D3A2E5CC6B5471E097B6A8C506D502300B7DC84B237213BA1E47F07`; `test_pipeline.py` `36AE2202256A31119ABBA778159FB2569B2E11A25A8CE99B887CC90434C0201F`.

Actionable lab findings:

1. **P1 — fitter binding is real and passes, but the returned fit boundary is not independently allowlisted.** `run_lab` parses whatever JSON the local Node process emits and passes observations to `Build.fitter.api.handle`; it returns the whole fit object without checking `status == 'ok'`, the required quantity schema, `source.label == 'simulated'`, or that gravity is the fitted quadratic coefficient. Add a narrow response validator before exposing `fit`; reject extra/unknown status shapes and require the actual S11 quantity fields. This is defense-in-depth for the trusted-fit boundary, not a physical-g claim.
2. **P2 — seed is validated upstream but is not carried into the lab result or instrument provenance.** `pipeline.py` invokes deterministic instrument functions without the experiment seed and omits seed from its result. If seeded replay is intended, include the canonical seed in the returned provenance and derive any stochastic instrument stream from it; otherwise explicitly declare this lab deterministic/non-seeded and test that changing seed is intentionally irrelevant.
3. **P2 — `simulate.mjs` emits a generic error and `pipeline.py` trusts only exit status plus JSON parse.** Add an explicit trajectory contract check at the Python boundary (kind/template, finite samples, `source='simulated'`, `inputProvenance='synthetic'`, and requested horizon) so a future runner cannot silently return a different valid-looking JSON object.

Replay sibling `run/S10fg-extension` was inspected at `34e324dd45dc155dd7e79c0f7c8ebc6aa5b69d1a` (implementation commit `56b8253`). `replay.mjs` has strong JSON-only canonicalization, sorted keys, hash verification, and runner-output equality. Current `mystery-g.mjs` is not acceptable yet: its `revealFit` contract accepts a caller object shaped only like `{status:'ok', gravity_m_s2}` and labels it `measured`; public observation screening is a substring blacklist that can leak semantically equivalent gravity/seed/setup data; the implementation imports `node:crypto`, so it is not browser-runnable. These are already actionable worker findings: require the real Python S11 fit-result schema/receipt, an allowlisted public DTO with explicit field paths, and WebCrypto or an injected hash implementation. Re-review after the worker's correction; no replay/gate acceptance is claimed.

Templates sibling `run/S10e-extension` was inspected at `ab2d60ab47cca893e11ebc5ae067bef3d9d088c10`. Ramp and pendulum are honest analytic, simulation-only Python oracles with no integrator/contact/replay integration. Keep that boundary. No additional P1 found in the fresh template source; S10e must not be presented as Rapier or cross-language E2E evidence.

## Ponytail/application
Used smallest source-only review, reused existing contracts and test seams, isolated owned evidence, avoided dependency/framework expansion, and preserved truthful synthetic-vs-physical boundaries. OpenCodex-managed route was not polled.
