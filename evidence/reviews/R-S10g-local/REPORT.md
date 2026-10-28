# R-S10g-local independent review

## Status
IN PROGRESS — peer source located and reviewed; earlier pre-integration absence is superseded. Browser validation remains pending parent reconciliation.

Resumed at 2026-10-28T18:51:06.9989541Z; original deadline remains 2026-10-28T19:04:55Z.

## Baseline and scope
- Branch un/R-S10g-local, clean rebased HEAD d5df5fcfa502433fd5df4d0ec24010efb604d2b.
- Owns only this report/evidence and run metadata; no peer files or controls edited.
- Ponytail full applied: reused existing pipeline, contracts, and tests; no dependency/framework/build expansion.

## Fresh checks
- python -m unittest discover -s tests/lab -p 'test_*.py' -v: **5/5 PASS**.
- 
ode --test tests/lab/*.test.mjs tests/simulator/*.test.mjs: **28/28 PASS**.
- python Build/web/src/shell/test_contract.py: **7/7 PASS**.
- 
ode Build/web/src/shell/smoke.mjs: **FAIL/environment-limited**; Build/web/node_modules/next is absent. No install attempted.
- source-audit.txt records current source facts and exact UTC observation.

## Findings / required integrated-head recheck
1. **P1 candidate — hidden gravity still crosses the viewer model boundary.** Build/web/src/viewer/scene-model.mjs:106 copies m.gravity into the viewer DTO. The shell contract at lines 78–81 explicitly says no secret-safe payload exists and Mystery-g must remain disabled until one exists. Before accepting S10g, the final integrated UI must feed public Mystery-g only a redacted DTO; successful fitter/reveal must be the sole path that returns the trusted numeric result. Do not rely on CSS/conditional rendering to hide it.
2. **P1 candidate — no live service/UI route is in this review head.** Build/web/src/app has no lab route/API, so actual fit-before-reveal, session binding/expiry, bounded concurrency, stale/error/history/cache, and localhost-only behavior are untestable here. Recheck the final integrated peer head; acceptance requires a real loopback request sequence, not source presence or fixture tests.
3. **P2 — offline numeric boundary is strong but not an auth boundary.** Build/lab/pipeline.py:40–53 uses JSON stdin, repository cwd, a 30s timeout, and checks source=simulated, inputProvenance=synthetic, fixed-step RK4 and dt_s; lines 80–92 validate fitter gravity units and label output synthetic. The eventual HTTP route must keep this producer-side validation and must not accept caller-supplied labels/fit DTOs as provenance or authentication.
4. **P2 — analytic evidence is simulation-only.** The four-template regression passes and the max error is recorded in the existing swarm verification, but this proves neither calibrated g nor Gate M/P physical acceptance. Keep UI labels and gate packets explicitly simulated/synthetic; do not promote these numbers to measured evidence.

## Deferred integrated repro matrix
Run after parent integration, without changing this checkout's scope:
- public initial payload contains no gravity, seed, private setup, or fitter internals;
- fit request is bound to an unguessable expiring session and rejects cross-session/replayed reveal;
- malformed/timeout/bridge errors clear prior result and do not expose stderr, setup, or numeric secrets;
- toggle cannot reveal before successful fit; failed/new runs clear stale reveal/history/cache;
- concurrent requests are bounded and route binds only to 127.0.0.1/localhost dev surface;
- final evidence includes actual request/response captures plus numeric producer provenance.

## Limits
No server/browser E2E, no peer edits, no deployment/auth/credentials/spend/publication, and no physical or Gate M claim. Parent must rerun this matrix against the integrated final heads.

## Timing
Issued 2026-10-28T18:34:55Z; nominal deadline 2026-10-28T19:04:55Z; observed report write UTC $now.


## Fresh review of intended service branch — run/S10g-service-fixed @ 476338d

The intended branch currently still contains the original d9466d7 implementation; no corrective commit is present yet. Fresh static review confirms parent-returned issues remain open:
- session-service.mjs:15: done() is called from both child rror and close; timeout/abort kills the child but does not kill a possible descendant process tree. Output is appended before the cap check, so a large stdout chunk is accepted into memory before rejection.
- session-service.mjs:32–42: two concurrent fits can both observe no session.result and run bridges/reveal; response puts it (including gravity) in Mystery-g result, while UI expects/reads body.fit. Fit response has only nested session metadata, not a top-level sessionId.
- session-service.mjs:13: eviction/TTL pruning happens only at request entry and evicts oldest entries at capacity; add deterministic expiry/capacity tests and avoid races around read/fit.
- session-bridge.py:14–17,50–65: INSTRUMENTS is unused and observations are direct raw RK4 positions with authored gravity; this is a synthetic trace, not an instrument reaction. Remove the unused constant or implement/document the bounded instrument transform; keep the UI/gate evidence labelled simulated.
- oute.js:6–8: Origin is optional and Host/Origin checks are not socket binding; exact same-origin and explicit loopback server startup remain required.

No acceptance claim is made until the worker's corrective commit and parent's IAB browser run are available. This review is nonterminal and remains within the original 19:04:55Z window.

## Final deadline review — actual current heads

Stopped at $now after the original deadline. Reviewed service un/S10g-service-fixed @ 11f3159 and UI 48b0d9d; no browser/IAB evidence was available in this worker because parent owns that step.

### Closed by current service fix
- bridge completion is guarded by a settled gate, active count cleanup is single-shot, fit calls are coalesced per session, expiry is checked after bridge, and insertion/pruning is bounded.
- bridge now applies the synthetic light-gate/ruler adapters and returns private seed/setup only to the server-side session.

### Remaining acceptance blocker
- **P1 remains:** session.result still returns raw it alongside eveal (11f3159, fit path). Raw it.gravity, uncertainty internals, and fitter metadata therefore cross the Mystery-g API boundary; UI 48b0d9d deliberately parses ody.fit, so this is not merely dead data. The public response must be redacted to reveal/session metadata only, with a regression proving no raw fitter/private setup/seed in Mystery-g responses.
- **P2:** abort/timeout calls child.kill() but does not explicitly kill a descendant process tree; route still relies on Host and optional Origin checks, so parent must prove explicit loopback binding and exact same-origin behavior in IAB.
- **P2:** INSTRUMENTS remains duplicated/unused beside hard-coded adapter values; remove it or make it the single source of truth. Numeric result remains synthetic, not measured/gate evidence.

Final status is PARTIAL at the actual deadline: source review complete, live browser validation and final parent reconciliation not performed here. No new implementation was made.

## Deadline noncompliance addendum
The worker stopped/reported at the actual 2026-10-28T19:09:38.0936212Z, after the original 2026-10-28T19:04:55Z deadline. This is recorded as noncompliance; the deadline was not backdated or extended by this worker. No further work was performed after finalization.
