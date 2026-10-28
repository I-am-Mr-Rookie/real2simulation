# S07b verification boundary

Synthetic transport/array fixtures exercised real adapter parsing, immutable
source-index/PTS mapping, centroid computation, missing-data handling, documented
request construction, local factory wiring and S07a validator integration.
They are **not** captured model output or proof of SAM inference/accuracy.

- Initial RED: `red.txt`, 10 missing-feature assertion failures before implementation.
- GREEN: `green.txt`, 23/23 (13 adapter + 10 frozen S07a regressions).
- UNC/URL regression RED: `local-path-red.txt`, 3 failures showed filesystem
  probes preceded local-path rejection; fixed before probes. Same green suite passes.
- Malformed stream RED: `stream-red.txt`, unexpected TypeError for `None`; now
  raises boundary ValueError. Provider iterator/runtime exceptions still propagate.
- First implementation check exposed synthetic fixture height80 vs source
  metadata height100; traced to fixture setup, aligned dimensions, did not weaken
  production shape checking.
- `import-check.txt`: fresh process imports no NumPy, Torch or SAM.
- `python -m compileall -q Build/measurement/tracking.py tests/measurement/test_tracking.py`: exit0.

Broader repository verification (independent unittest discovery in all eight
tracked test directories, including the new measurement tests):

| Directory | Result | Log |
|---|---|---|
| tests/measurement |23 PASS|green.txt; suite-tests-measurement.txt|
| tests/spec |91 PASS|suite-tests-spec.txt|
| contracts/scene |11 PASS|suite-contracts-scene.txt|
| Build/api/health |15 PASS, 1 ERROR|suite-Build-api-health.txt|
| Build/reconstruction/spike |3 PASS|suite-Build-reconstruction-spike.txt|
| Build/web/src/shell |7 PASS|suite-Build-web-src-shell.txt|
| Run-System/tests |25 PASS|suite-Run-System-tests.txt|
| infra/railway/dev |7 PASS|suite-infra-railway-dev.txt|

The health error is `test_postgres_probe_uses_read_only_query_and_bounded_connection`:
`ModuleNotFoundError: No module named 'psycopg'` during patch import. Test files and
dependencies are unchanged; no out-of-scope installation/fix attempted. Health
suite also emits installed websockets deprecation warnings; no product failure
inferred from warnings.

`node --test` on every Git-tracked `*.test.mjs`: 39 PASS, 1 file-load failure,
exit1 (`node-suite.txt`). `tests/viewer/three-renderer.test.mjs` cannot import absent
worktree `Build/web/node_modules/three/build/three.module.js`; unchanged viewer
and dependency paths, no install attempted. Whole-repository checks are NOT green.

Primary-source inspection: official SAM repository HEAD observed
`f1647e8d0c1d280991f4d1b7d974c2704537fe66`; README/release/builder/shared predictor/
video inference/example notebook/custom licence read. Exact permalinks and derived
interface assumptions are in Build/measurement/TRACKING.md. Public SAM3.1 model-card
fetch denied restricted access; no auth or bypass. This host has NumPy but lacks
Torch/SAM. No checkpoint fetched, provider inference, CUDA/GPU, remote footage,
real clip processing, account/terms action or physical gate performed.

Scientific holds: original source/licence/approval/scale/timebase declarations are
preserved, not independently attested. Explicit local prefix custody is required;
filename/count validation alone cannot prove image contents/PTS/hash. Mask centroid
is not centre-of-mass metrology. Real identity stability, segmentation uncertainty,
capture clock, geometric calibration and actual model/runtime remain unverified.
