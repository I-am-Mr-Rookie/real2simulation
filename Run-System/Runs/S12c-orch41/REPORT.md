# S12c-orch41 REPORT — DONE

Lane CODEX-1 · anthropic/claude-opus-5-5/high · coding quota OpenCodex-managed; not polled · tokens/cost unknown · no GPU/Modal/Meta/paid calls, no installs.
UTC issue 2026-10-29T21:26:43Z · started 21:27:07Z · work stopped 2026-10-29T21:32:37+00:00 (verified DONE, early finish) · base main 03e6c2f.

## Result
Gate M **NOT_MET** in every output. Units image-height fraction (scale-free, Q15=A); no calibrated-g / physical-accuracy claim. Scoring is S12e.

- **Build/real2sim/predict.py** (new): `Prediction` frozen dataclass (trace = tuple of tuples, sha256 over [kind, model, trace]); `check()` re-hashes.
  `_identities()` takes only row[0], row[1] of the sealed suffix and verifies training + suffix-identity seals.
  `projectile()`: S12a `fit_prefix` (AIC) -> `fit.predict` at suffix PTS, 1-sigma band from fitter `jacobian_covariance` full matrix (J C J^T).
  `bounce()`: prefix quadratic + validated restitution record, analytic floor reflection v -> -e v (1-D vertical; friction irrelevant), sigma not propagated.
  `st03_record()`: orch14 record + **ST03 errata frame_map** (S07b-param-orch40) applied in memory; checks errata_for path, source sha, frame set, and agreement with presentation map. Accepted orch14 untouched.
- **evidence/S12/prediction-ST03.json** (real, image-derived): errata-corrected boundary (training sha eb4f9cbc..., 19 frames 58-76; suffix 466 identities 77-542),
  prediction sha **c81e0f94c110eb229502b37d03c29ec36b11621ed8ca97015f9e671508c9d1b0**, `suffix_observations_read: false` (suffix not tracked at all).
  With the errata the prefix fit no longer abstains: AIC degree 2; g = 1.846 ± 0.136 image-height/s^2, speed = 0.171 ± 0.042 image-height/s (from_fit, 'image-derived'); friction/restitution still abstain (no ST03 bounce observation).
  Records `supersedes_s12a_seal` (old suffix sha 0f2a1562..., 465 ids): frame-77 quarantine lifted because errata f76 2.535867 < f77 2.569233.
- **Simulator F1 (smallest change)**: `INPUT_PROVENANCE = ['synthetic','image-derived']` exported in Build/simulator/trajectories.mjs, reused by contacts.mjs; source must still be 'simulated'. extended-templates (ramp/pendulum) unchanged (synthetic-only).
  params.simulate now passes one provenance label through (mixed or unknown refused, never relabelled). F2 (*_m field names carry image heights) documented, not refactored.
- **Bounce**: SYNTHETIC fixture only — no approved bounce clip has tracking (rg 'bounce' in evidence/S07 hits only audit/readiness docs). Finding: the existing Rapier contact layer does not produce rebound positions (RK4 samples pass through the floor; contacts are candidate manifolds), so bounce uses the analytic reflection above.

## Acceptance: predictions generated without reading held-out observations
1. Spy rows log any index>=2/slice/iteration access: `projectile()` and `bounce()` -> zero reads; then `verify()` (scoring stage) does read -> spy proven live.
2. Same prefix, different held-out values ([500,520,540] vs [1,2,3]) -> identical trace and sha.
3. Frozen dataclass / tuple rows reject mutation; truncated trace fails `check`; dropped suffix identity fails the seal.
4. Committed ST03 prediction re-hashes and regenerates byte-identical sha from sources; gate_m NOT_MET; g/speed present.

## Fresh checks (Python 3.14.5, Node v24.18.0, this worktree)
- `python -m unittest discover -s tests/prediction -v` -> 18 OK (7 S12a + 6 S12b incl. updated image-derived assertion + 5 S12c) -> evidence/S12/tests-prediction-S12c.txt.
- `python -m Build.real2sim.predict` -> "evidence/S12/prediction-ST03.json gate_m=NOT_MET suffix=466 sha256=c81e0f94...".
- node --test tests/simulator/*.test.mjs (10 files) + tests/lab/contact-integration + browser-simulator: 134 tests, 130 pass, 4 fail -> evidence/S12/tests-simulator-S12c.txt.
  Canonical main 03e6c2f same files: 133 tests, 129 pass, **same 4 fail** (pre-existing: R14 pendulum frequency-step-boundary, pendulum negative-phase, ramp + pendulum replay hash oracle; untouched extended-templates path). New test passes.
- tests/simulator/test_s10_adapter.py: pre-existing ImportError (needs tests/ on sys.path for test_experiment_schema); not run, unrelated.
- Env: local junction Build/simulator/node_modules -> canonical node_modules (gitignored, not committed; delete with worktree).

## Ponytail (full)
- Reused: S12a split/_sha/fit_prefix/record_json/GATE_M/LIMITS; S12b from_fit/parameter/ROOT; fitter jacobian_covariance + FitResult.predict (no new fit/uncertainty math); simulator validation lines (one shared constant, two call sites).
- Smallest complete: one new module (~150 lines) + one test file; frozen dataclass + sha instead of a storage layer; ST03 errata applied in memory instead of re-writing accepted evidence.
- Skipped: horizontal x prediction (S12a boundary carries y only); sigma propagation for bounce; multi-object/real bounce; regenerating params-ST03.json (S12b artifact left as historical; current real params are inside prediction-ST03.json); extended-templates provenance; F2 rename; scoring (S12e).

## Risks
- Errata scope is timestamps only (centroids/masks unchanged per S07b-param-orch40); if the f76 centroid itself came from a shifted image, the prefix tail is off by one frame.
- Ballistic extrapolation has no floor: ST03 suffix predictions run far past y=1 (out of frame) after ~2.7 s; S12e must score only meaningful/visible frames and track exactly the sealed 466 identities.
- Uncertainty OLS residual-based, clock/scale fixed. Gate M/RS not run; cross-vendor review of S12 path still required.

Communication: one completion line to controller (authorized). No canonical controls edited.

