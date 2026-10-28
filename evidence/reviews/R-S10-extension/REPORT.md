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

The earlier lab concerns above are **superseded** by parent fixes: the cross-process trajectory contract and successful `validate_quantity` gravity check now pass; `handle` error data is intentionally retained for this internal diagnostic API; instruments are explicitly deterministic with no artificial noise requirement. Fresh parent report says four-template regression is 4/4 PASS.

Replay sibling `run/S10fg-extension` was inspected at `34e324dd45dc155dd7e79c0f7c8ebc6aa5b69d1a` (implementation commit `56b8253`). `replay.mjs` has strong JSON-only canonicalization, sorted keys, hash verification, and runner-output equality. Current `mystery-g.mjs` is not acceptable yet: its `revealFit` contract accepts a caller object shaped only like `{status:'ok', gravity_m_s2}` and labels it `measured`; public observation screening is a substring blacklist that can leak semantically equivalent gravity/seed/setup data; the implementation imports `node:crypto`, so it is not browser-runnable. These are already actionable worker findings: require the real Python S11 fit-result schema/receipt, an allowlisted public DTO with explicit field paths, and WebCrypto or an injected hash implementation. Re-review after the worker's correction; no replay/gate acceptance is claimed.

Templates sibling corrected source `9956c5c` was inspected (the worktree later added documentation commits). `extended-templates.mjs` now runs fixed-step RK4 ramp and nonlinear pendulum, consumes the real validated S08 artifact, and passes 7/7 focused tests. One integration issue remains: canonical main `9e3bb16` at review time had `Build/lab/simulate.mjs` importing `../simulator/extended-templates.mjs` while that file was not yet integrated, so `python -m unittest discover -s tests/lab -p 'test_*.py' -v` failed the 4-template regression with Node exit 1. Integrate the exact template source before accepting the parent 4/4 result.

Contacts corrected source `111ba84` passes 5/5 focused tests. New actionable P2: `checked()` validates RK4 shape but does not validate `t.source`, `t.inputProvenance`, per-sample `step`/time monotonicity, or `time_s == step * dt_s`. A caller can label an arbitrary sparse-in-time trace as an RK4 synthetic trajectory and have Rapier report contacts against it. Add dense sample identity/time checks and explicit simulated/synthetic labels before contact mapping. This is a trust-boundary hardening finding, not a physical Gate-P claim.

Independent repro on integrated main `65e6080`: deleting `source`/`inputProvenance` and changing sample 1 to `{step:99,time_s:99}` was accepted and returned `accepted:true, step:99, time:99`. A second P2 is mutable-input aliasing: `samples.push(Object.freeze({...sample, contacts: ...}))` does not clone/freeze caller-owned `position_m`/`velocity_m_s`; the advertised deep immutability only holds for already-frozen trajectory samples. Clone and freeze vectors before returning.

Fresh integrated checks: `python -m unittest discover -s tests/lab -p 'test_*.py' -v` passed 5/5; `node --test tests/simulator/contacts.test.mjs tests/simulator/extended-templates.test.mjs` passed 12/12. Parent's saved four-template regression reports max relative error `0.00026645` for pendulum, below `0.005`; this remains synthetic regression only. R-P and whole Gate P remain explicitly unrun.

Replay current source advanced to `3f16b63` after `7ca8f3c`; canonical hashing and the real S11-shaped handoff are materially corrected. Focused replay/Mystery-g run: 4/5 pass; the new version/mutation/cross-session test fails before assertions with `SyntaxError: Unexpected end of JSON input` at its inline `spawnSync('python', ['-c', ...])` JSON parse. Fix the test harness (capture/assert `status`, `stderr`, and use the repository `cwd`) or remove the environment-sensitive inline process; do not mark the suite green while this failure remains.

**Follow-up re-review (18:21Z):** contacts `ff91183` now enforce `simulated/synthetic`, exact sample index/time, and clone/freeze returned vectors; focused contacts 5/5 pass. Replay `d16bf0e` now has the corrected actual-observation binding and focused replay/Mystery-g 5/5 pass. The prior contact/replay findings are closed. Integrated canonical main `65e6080` has the extended Node template source; lab 5/5 and contacts/templates 12/12 pass. No new actionable template defect found after the endpoint/overflow fixes.

## Ponytail/application
Used smallest source-only review, reused existing contracts and test seams, isolated owned evidence, avoided dependency/framework expansion, and preserved truthful synthetic-vs-physical boundaries. OpenCodex-managed route was not polled.
