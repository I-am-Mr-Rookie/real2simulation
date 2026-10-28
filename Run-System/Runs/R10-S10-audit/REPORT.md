# R10-S10-audit — native Claude Gate P numeric re-audit

Status: DONE (narrow numeric gate audit; findings only, no implementation edits).
Lane/model: native Claude (Codex desktop inline), not Claude Code. Coding quota: OpenCodex-managed; not polled. Costs: unknown.
Issued 2026-10-28T19:50:36.537Z; deadline 2026-10-28T20:20:36.537Z; work stopped 2026-10-28T20:00:41.8194288Z.
Head reviewed: f82ed85 (branch run/R10-S10-audit). Owner mid-run update applied: narrow numeric audit only, no fanout.

## Ponytail (full) applied
Reused existing tests/acceptance diagnostics and one-line node repros; no new deps (Rapier via existing lockfile `npm ci --ignore-scripts` in worktree only); no implementation edits; skipped broad design review.

## Findings

**P2-1 contacts.mjs:19 / :56 — floor centre can overflow to non-finite; accepted silently.** Validation checks `floorY` and `floorHalfExtents` finite separately, but the collider translation `g.floorY - g.floorHalfExtents[1]` is never checked. Repro: floorY=-1e308, halfExtents[1]=1e308 → centre -Infinity; call returns 11 samples, `contact:false`, zero Rapier manifolds, no error. Fix: after line 19, `if (!finite(g.floorY - g.floorHalfExtents[1])) fail('floor centre must be finite');` + one test.

**P2-2 contacts.mjs:77–78 — initial penetration reported as contact at t=0 with bracket [0,0].** If sample 0 already has `y - r <= floorY` (repro: y=0.05, r=0.1, floorY=0, depth 0.05 m) output is `contact:true, contactBracket_s:[0,0]`. True first-touch time lies before the trajectory; [0,0] is a fabricated exact bracket, conflicting with the "time bracket" semantics and trajectories.mjs:58 which labels this case `at_initial_sample`. Fix: reject start-penetration (`index===0 && touch` → fail('initial state penetrates floor')) or emit an explicit `at_initial_sample` label with null bracket; add test.

No P1 found.

## Checked, no defect
- Contact jitter/bounds: acceptance `_contact_diagnostic` fresh run — analytic 0.62238 s inside every sampled bracket for dt 0.005/0.0025/0.001, both templates; `contact_jitter_observed:false`; spread 0.0025 s is step quantisation, correctly not called jitter. Displacement guard (line 71) and footprint guard (line 69) present.
- Oracle/step consistency: acceptance.py:225–230 enforces exact `step==index`, `time_s==index*dt` and sample-count bound; endpoint clamp limited to 4 ULP and recorded (237–253). Characteristic-scale zero guard present. Extended templates' ramp stop excludes post-endpoint sample (extended-templates.mjs:59–62) consistent with bound.
- Replay identity: canonical hash rejects non-finite/sparse/accessor/cyclic; replayRecord re-verifies both hashes then rerun; replay-check confirms seed binds hash.
- Mystery privacy: session-service.mjs:45 omits `gravity` for mystery; `private` kept server-side only; reveal requires WeakMap-bound fitter handoff with matching observation hash; single reveal. Fresh bridge run: mystery start internal result includes gravity but service strips it (test line 17 asserts).

## Fresh checks (worktree, head f82ed85)
- `node --test tests/simulator/*.test.mjs tests/lab/contact-integration.test.mjs`: 28/28 pass.
- Bridge start all four templates (normal): ok, finite, non-negative observations (201/201/201/1001 samples).
- `node --test tests/lab/session-service.test.mjs`: 1 failure observed once — "aborting an active bridge settles and releases its capacity" got status 'ok' (expected 'error'); likely race (bridge may finish before abort). Rerun of that test alone did not return within tool window: NOT confirmed flaky vs deterministic. Routine test-reliability item for Codex, not a numeric gate defect.
- `python -m unittest tests.lab.test_acceptance tests.lab.test_regression tests.simulator.test_s10_adapter`: acceptance/regression pass; test_s10_adapter import error (`test_experiment_schema` not on sys.path under plain unittest) — invocation/path issue, pytest not installed; not evaluated further.
- Repro commands for P2-1/P2-2: inline `node --input-type=module -e` in worktree (output quoted above).

## Skipped / risks
UI, fitter internals, physical Gate M/S12 not in scope. node_modules installed in worktree only (ignored, uncommitted). Communication: silent; this report is the only output.


## Commit
Findings commit af90244 on run/R10-S10-audit (owned paths only; not merged). worker_timebox.py check: TIMING PASS.
