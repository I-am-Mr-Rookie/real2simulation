# R-P-native — other-vendor Gate-P numeric/replay/contact/service review

Reviewer: CLAUDE lane, native Codex anthropic/claude-opus-5-5 medium (as issued). Source read directly; prior reviews not assumed.
Heads reviewed: main f409018; swarm3-lab-service 11f3159; swarm3-lab-ui 48b0d9d; swarm3-gate-p b5d674a.
Verdict: **analytic RK4/4-template/replay path sound; Gate P NOT fully passed** — contact-time evidence is biased/non-convergent and contact boundary lacks tunnelling guard; Mystery-g g is fixed/public. Simulated, not measured.

## P2 findings

### P2-1 Contact flagged on speculative (prediction-distance) manifold points → early, dt-non-convergent contact time
- Build/simulator/contacts.mjs:36-38 counts `manifold.numContacts()` (includes speculative points with positive distance); :73-75 marks first such sample as contact.
- Repro (run, not read): `node evidence/reviews/R-P-native/repro-contact-convergence.mjs` → [repro-contact-convergence.out.txt](repro-contact-convergence.out.txt). Analytic touch 0.6223824 s.
  | dt | contact_t | err_s | gap at "contact" (m) |
  |---|---|---|---|
  | 0.02 / 0.01 / 0.005 / 0.002 | 0.620 | -0.00238 | +0.01452 |
  | 0.001 | 0.622 | -0.00038 | +0.00233 |
  | 0.0005 | 0.6205 | -0.00188 | +0.01148 |
- Sphere is 14.5 mm ABOVE the floor at reported contact; error does not shrink monotonically with dt. Gate-p b5d674a acceptance (Build/lab/acceptance.py:293-356, evidence/S10/acceptance/README.md) reads "zero sweep spread / no jitter" as stability; it is the fixed prediction margin capturing the same sample, i.e. a systematic bias, not convergence evidence.
- Checked candidate fix (run): `node evidence/reviews/R-P-native/repro-contactdist-fix.mjs` → [repro-contactdist-fix.out.txt](repro-contactdist-fix.out.txt). Filtering to `contactDist(i) <= 0` is ALSO non-convergent and now LATE: +17.6 ms (dt 0.02), +7.6 ms (0.01–0.002), +8.6 ms (0.001), +6.6 ms (0.0005). Teleported-pose Rapier manifolds are not a dt-convergent timing signal in either mode.
- Recommended fix: for sphere-vs-floor, decide touch by exact same-sample geometry (`y - r <= floorY`) and report the [previous, current] sample bracket; keep Rapier as a labelled detector cross-check only. Add a test that bracket width ≤ dt and contains the analytic time for dt down to 5e-4. Do not cite "zero spread" as stability.
### P2-2 No tunnelling guard at contact boundary → silent no-contact through floor
- contacts.mjs:16-17,66-76 accept any RK4 trajectory; contact-runs.mjs:7 builds raw (unvalidated) trajectories. The S08 per-step displacement guard (contracts/experiment/validate_experiment.py:259, speed·dt+½a·dt² ≤ r/2) is not re-enforced here.
- Repro: `node evidence/reviews/R-P-native/repro-tunnel.mjs` → [repro-tunnel.out.txt](repro-tunnel.out.txt): dt=0.1, floor half-thickness 0.1, r=0.1 → 21 samples, firstContact -1, final y = -17.62 m (through floor), returned as a normal trace. dt=0.05 detects only after center is 0.072 m below floor top.
- Fix: reject/fallback when max per-sample |Δpos| > r/2, or when consecutive samples straddle the floor slab without contact (machine-readable fallback, no rebound claim).

### P2-3 Mystery-g hidden g is a constant 9.81 with fixed seed/setup (service peer)
- swarm3-lab-service 11f3159 Build/lab/session-bridge.py:31-36 uses `regression_case` (Build/lab/regression.py:30-31 g=9.81, :40 seed=42) for every start; :68 private g = 9.81. Normal mode returns that same g (:70-71). Observations are identical across sessions.
- Pre-fit public DTO correctly omits private g/seed/setup (session-service.mjs:30) — no field leak — but the "mystery" value is trivially known. Either derive a private g server-side from a seeded range or label UI "fixed demo g (9.81)". Not a privacy/security leak.

## P3 findings
- mystery-g.mjs:12 error text "actual successful S11 fitter response required" but check is shape-only; any in-process caller can mint a handoff. Label as in-process trust, not authentication.
- gate-p acceptance.py:359-363 runtime-unavailable branch reports `contact_jitter_observed: False`, `fallback_observed: False`; should be null/unknown.
- session-service.mjs:35 shared in-flight fit uses first caller's abort signal; one client abort fails concurrent waiters (recoverable: inFlightPromise reset). :16 child.kill() is not a tree kill on Windows (bridge's own node child is bounded by its 20 s communicate).
- session-bridge.py:58 `position_m < 0` rejects pendulum near half period; pendulum duration 1 s vs half-period ≈1.003 s leaves 3 ms margin (not reachable now; fragile).
- regression.py:74 `zip` silently truncates on length mismatch (lengths currently equal by construction).

## Verified sound (fresh runs)
- rk4.mjs / trajectories.mjs / extended-templates.mjs: finite/dense checks, integer horizon (ε-ratio, no truncation), sample time = step·dt matches Python pipeline check exactly.
- `python -m Build.lab.regression` (run): passed, threshold 0.005 unchanged; rel err free_fall 7.9e-15, projectile 5.6e-15, ramp 3.0e-15, pendulum 2.66e-4 (small-angle oracle at 0.05 rad, model mismatch dominates; amplitude >0.1 rad labelled nonlinear-only). Errors normalized by characteristic scale, not pointwise near zero.
- Ramp: kinetic friction only; non-positive acceleration rejected (no stick/slip/coast claim); endpoint reported as sampled bracket.
- Replay: canonical JSON + WebCrypto SHA-256; replay-check.mjs drives the real four template engines; seed binds identity only (stated).
- Route: non-dev/test 403; loopback Host + same-origin; 1 MB cap streamed; TTL 10 min; 64 sessions; 4 bridges. UI parseFitReveal strict; request-version stale guard; "simulated, not calibrated" copy.
- `node --test` tests/simulator/*.mjs tests/lab/*.mjs: 28/28 pass. `python -m unittest tests.lab.test_pipeline tests.lab.test_regression tests.simulator.test_s10_adapter`: 7 OK. (pytest not installed; unittest used.)



## Addendum 19:16Z — final heads re-review
- main 1650652 (UI 48b0d9d + service 8bc2c6b + gate-p acceptance) — service 8bc2c6b is a pure rebase of reviewed 11f3159 (0-line diff in Build/lab, route, service tests); acceptance.py/Build/simulator unchanged vs reviewed b5d674a. All P2s above still apply at 1650652.
- Fresh at run/R-P-native rebased on 1650652: NODE_ENV=test `node --test` tests/simulator+tests/lab 37/37; unittest pipeline/regression/adapter/session_bridge/acceptance OK.
- P3 new: tests/lab/session-service.test.mjs:40-43 route test needs NODE_ENV=test; plain `node --test` gives 403≠200 (4/5). Set env in the test or document the command.
- Canonical UNCOMMITTED controller diff (session-service.mjs ROOT-from-cwd + stopTree; next.config.js turbopack.root=Build; abort test) reviewed, not committed by me:
  - Run: NODE_ENV=test session-service tests 6/6; import from Build/web cwd resolves root; mystery start DTO keys = status,sessionId,template,mode,observations,observationHash,source,units,limitations (no gravity/seed/setup) ✓; post-fit reveal 9.80999887 m/s² — fit reveal after fit is contract-allowed (NOT a finding); it also confirms P2-3 fixed 9.81.
  - turbopack.root absolute path per bundled Next 16.4.3 docs (turbopack.md:49,90-94) ✓; config loads (CJS, no "type":"module").
  - P3: stopTree Windows — taskkill nonzero exit (not 'error') leaves no fallback; add `killer.on('exit', c => c && child.kill())`. Grandchild cleanup not independently observed (only capacity release asserted).
  - P3: module-level throw when cwd lacks the bridge makes the route import fail → 500 instead of production 403; resolve lazily inside bridge().
- Not verified by me: browser/IAB UI, next dev/build bundling, Unix process-group path.



## Addendum 2 (19:20Z) — re-review of the parent's uncommitted canonical fixes (main 5989604 + working tree; not committed by me)
- P2-1 contact: RESOLVED in the uncommitted fix. contacts.mjs now decides touch by sample geometry `y-r<=floorY` and records the before/after time bracket; Rapier manifolds are kept only as labelled candidates. Run: dt 0.005 → [0.62,0.625], 0.001 → [0.622,0.623], 0.0005 → [0.622,0.6225]. Each contains the analytic 0.6223824.
- P2-2 skipping through the floor: RESOLVED in the uncommitted fix. A step longer than r/2 is now rejected: dt 0.02/0.01/0.1 fail with INVALID_CONTACTS. The touch test checks a half-space, so the floor's thickness can no longer be skipped. The floor-footprint guard is strict and honest.
- P2-3 Mystery-g: RESOLVED in the uncommitted fix. Mystery sessions get a private crypto seed and g from 4 to 16; normal mode stays at 9.81 with seed 42. Run: two Mystery sessions revealed 13.957 and 4.563. Before the fit, the start response contained neither gravity nor a seed.
- Also confirmed in the uncommitted fix: taskkill exit fallback, root resolved lazily, the regression length guard, unavailable branch now null, LabClient shows uncertainty with toPrecision(3) plus model and assumptions. The parser guarantees the values are finite and the assumptions are strings.
- Fresh runs on the canonical working tree: NODE_ENV=test node --test tests/simulator+tests/lab 38/38; unittest session_bridge, regression and acceptance all OK.
- P3 remaining: acceptance.py:341-351 still calls the spread of sampled contact times across dt "jitter" and reports error as sample time minus analytic time. With geometric touch, that spread equals sampling resolution. Assess containment of the analytic time in the bracket instead. evidence/S10/acceptance/acceptance.json is stale until regenerated; the old "zero jitter" claim is superseded.
- Still not verified by me: browser/IAB at 375px, next build, the Unix process-group path, and observed grandchild kill.



## Addendum 3 (19:21Z): final read-only acceptance review (canonical uncommitted state)
- Ran `_contact_diagnostic()` from acceptance.py. All 6 brackets (free_fall and projectile × dt 0.005/0.0025/0.001) contain the analytic 0.6223824. Fallback was not observed. The raw spread of 0.0025 s is recorded separately and is not called jitter. The earlier jitter P3 is resolved.
- unittest test_acceptance and test_session_bridge: OK. Node 38/38, run by the parent and by me at 19:19.
- P3 naming: `contact_jitter_observed` now means "analytic time outside a bracket". Rename it, e.g. `bracket_miss_observed`. With zero measured rows, `any()` gives False; `fallback_observed` covers that case. Regenerate evidence/S10/acceptance/acceptance.json before citing it.
- Acceptance verdict, simulation-only: the numeric, contact-bracket, replay and Mystery privacy checks I reviewed have no P1 or P2 open. I can't call Gate P passed until main has the committed integrated head and the browser and 375px evidence exist. No contact response, rebound or dragging is claimed.



## Addendum 4 (19:22Z): test-env fix
- tests/lab/session-service.test.mjs now sets `NODE_ENV ??= 'test'` in the test file only and adds a production-403 test. The route file is unchanged (no diff under Build/web/src/app). Run: plain `node --test tests/lab/session-service.test.mjs` 7/7. This resolves the NODE_ENV P3.
- Open items, all P3 and non-blocking: rename `contact_jitter_observed`; regenerate acceptance.json; the browser at 375px, next build, Unix process-group path and grandchild-kill observation remain unverified by me. No P1 or P2 is open.



## Addendum 5 (19:24Z): integration head fd10a19, read-only
- Read in the diff: the contact bound is now `|v_prev|·dt + ½g·dt² ≤ r/2`. This is a conservative upper bound on per-step displacement under constant gravity and covers upward and downward motion; the bracket and geometric-touch logic match what I verified in Addendum 2. Minor P3: the bound uses `input.gravity`, not the trajectory's own gravity, so a caller passing mismatched values would get a mismatched bound.
- I did not rerun the tests at fd10a19 myself. The parent reports Node 39, Python lab 11, contact 7 and oracle 15 passing. The parent also reports the IAB 375px Mystery reveal (7.821 ± 1.27e-5, with model and assumptions, no hidden params before the fit); `evidence/S10/ui/lab-375.jpg` exists, but I did not inspect it.
- No P1 or P2 is open in my review scope. Remaining P3s: the `contact_jitter_observed` name, regenerating acceptance.json if it is cited, and the input.gravity bound note. Physical gates stay locked; all evidence is simulated, not measured.

