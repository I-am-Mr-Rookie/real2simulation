# S15f-orch23 REPORT
Status: DONE. Lane CLAUDE, anthropic/claude-sonnet-5-5/high; OpenCodex-managed, not polled. Parent project Meta AI Hackathon 91e441f8-e40c-4ec4-bea2-de7fa1582d97. Branch run/S15f-orch23 (worktree .worktrees/S15f-orch23, base f37121c).
UTC: issued 2026-10-29T14:33:09, started 14:33:41, work stopped 2026-10-29T14:46:17+00:00 (deadline 15:03:09; verified fully DONE, finishing early is allowed). Tokens/cost: unobservable.

## Result
Run, pause/resume/cancel and seeded replay controls for the workspace, following the S10 replay contract (Build/simulator/replay.mjs, s10-replay-v1). Fixtures only.
- `Build/web/src/workspace/runcontrol.mjs` (new): playback model `reduceRun`, `prepareRun`, `verifyReplay`, `completionEvent`, `runView`.
- `Build/web/src/workspace/run-view.mjs` (new): `renderRun`; wired via one optional `run` prop (react.mjs, view.mjs); CSS in workspace.css; README section; fixture runner in fixtures.mjs.
- `tests/workspace/run.test.mjs` (new, 7 tests); `evidence/S15/`: react-ssr-check.mjs S15f block + .out, workspace-tests-s15f.out.txt, run-preview.html, run-375-paused.png, run-375-done.png.

## Behaviour (as tested)
- Pause only freezes a playback cursor; the trace is computed once up front. Paused-run and unpaused-run give identical observations and replayHash; ticks while paused/idle return the same reference.
- Same-seed replay: two independent `prepareRun` calls give deep-equal traces and equal traceHash/replayHash; `verifyReplay` (real `replayRecord`) -> verified. Other seed: same trace, different replayHash (replay.md: seed = identity, not randomization). Drifting runner and tampered record -> visible `mismatch` (alert), never swallowed.
- Guards: R_LOAD only in run.running with matching seed; replay only in run.done and once at a time; RUN_START/CANCEL/EDIT_SPEC/RESET clear stale record/replay; a trace with a hidden_g key still fails the run via the S15a leak guard.

## Checks (fresh)
- `node --test tests/workspace/*.test.mjs`: 54/54 pass (47 existing + 7 new) -> evidence/S15/workspace-tests-s15f.out.txt.
- `node evidence/S15/react-ssr-check.mjs <Build/web/node_modules>` with React 19.3.1 SSR: S15b-S15f blocks pass -> react-ssr-check-s15f.out.txt. (Re-running it regenerated the four older *-preview.html files; only the shared CSS changed.)
- 375px, in-app browser only (ChatGPT in-app browser, viewport override 375x812, reset afterwards, tab closed): no horizontal overflow (scrollWidth 360 <= 375), 0 overflowing .ws-run elements, buttons 50-79px tall (>=44px). The page was served through a temporary 127.0.0.1 python http.server (the browser refuses file: URLs); it was stopped and port 48151 verified free.

## Ponytail (full) choices
Reused S15a RUN_* edges, S15c "host supplies payload" pattern, S15d/e injected-h view style, `Workspace` prop pattern and the real `replay.mjs` (injected, so no new cross-package import or dependency). No new reducer edges, timer, store or config. Skipped: a timer/host component, persistence, speed control, scrubbing. Kept in tests: real replay.mjs with an exact (dyadic) fixture runner so equality is bit-exact.

## Limits / risks
- Fixture runner is deliberately non-physical; no real simulator trace, lab session-service, gate, real-scene or physical evidence is claimed. A verified replay shows consistency, not authentication or accuracy.
- The S04 page does not yet host the loop (timer, prepareRun call, R_* dispatch); README documents it. Run-System/Runs is gitignored, so these three files need `git add -f` (done on the branch).
- Canonical controls untouched; nothing merged. Not reviewed by the other vendor (gate review is the controller's).
- Communication compliance: silent; one final line to controller.
