# NORMAL-only browser transport

Scope: synthetic/simulated local S10 DTO boundary, not physical accuracy, browser mounting, contact acceptance or an other-vendor gate review.

## Contract

`handleLab({action:'start', template, mystery:false})` returns:

```js
browserSimulation: { mode: 'normal', validatedSetup: artifact }
```

`artifact` is the SAME complete export already produced once by Python `export_validated_setup.export` after real S08 `validate_setup`; it is not reconstructed from observations or model-authored numbers. Supported fixed templates: free_fall/projectile/ramp/pendulum. Actual current normal observation counts: 201/201/201/1001. Both transports enforce a fixed-step horizon of at most 2000 points including the initial point.

- Bridge omits this DTO and authored public gravity for every Mystery start, irrespective of seed; its existing `private` object remains server-only transport.
- Service adds the DTO only in its explicit `!request.mystery` response branch, after checking the normal envelope, matching synthetic scene/template, fixed normal seed/gravity and bounded horizon.
- Service constructs its public response by allowlist, never spreading the bridge result/private object. Mystery responses do not inherit an earlier normal DTO. Existing matched-fit gravity reveal remains unchanged and does not include the setup or seed.
- Request allowlists still reject caller-supplied artifacts, seeds and setup editing. Labels are NOT producer authentication. Trust comes from the fixed local subprocess invoking the actual Python validator; no arbitrary artifact-input interface was added.
- Normal seed42/gravity9.81 checks intentionally describe the current fixed authored demo; an approved future setup editor would require revisiting them.

## Evidence

- `actual-normal-dtos.json`: four freshly generated public DTOs from actual `handleLab` calls. Synthetic/public NORMAL inputs only; no Mystery private payloads saved.
- `python-tests.txt`: full lab Python suite (actual pipeline/regression/acceptance plus boundary tests).
- `node-tests.txt`: targeted service tests, including actual bridge/fitter, all four DTO/export comparisons, pre-fit privacy, normal-to-Mystery transition, fixed request allowlists, invalid/bounded horizons, redacted errors, and existing abort/TTL/eviction/stale-fit/capacity guards.
- Seed cases for each ballistic template: 0, 1, 2^31, 2^32-1. These exercise boundary/representative seeds, not an exhaustive 2^32 enumeration; unconditional mode branches enforce the invariant independent of seed.
- `node-all-tests.txt`: additional simulator/lab regression attempt. Two contact test files cannot load because this fresh worktree lacks existing `@dimforge/rapier3d-compat`; no dependency installation or contact-source change was performed. This is NOT a whole-suite pass.

## Verification commands

```powershell
python -m unittest discover -s tests/lab -p 'test_*.py'
node --test tests/lab/session-service.test.mjs
$nodeFiles = @((Get-ChildItem -LiteralPath 'tests/simulator' -Filter '*.test.mjs').FullName; (Get-ChildItem -LiteralPath 'tests/lab' -Filter '*.test.mjs').FullName)
node --test @nodeFiles
git diff --check
```

No API-route, UI, fitter, simulator, config or canonical controls changed. Parent owns browser-child integration, LabClient mounting, IAB 375px verification and native-Claude targeted gate review. No physical M/S12, real scene, paid GPU, deploy, publish, account, terms or credential action.
