# S09f REPORT — Pause rendering when idle or hidden

- Status: **DONE** (acceptance: idle/hidden viewer stops unnecessary render work; resumes correctly)
- Lane/model: CLAUDE; requested Opus 5.5 medium; actual = orchestrator-delegated Claude-agent session in Codex desktop, exact model/effort not exposed.
- UTC (host clock): start 2026-10-27T19:33:37Z; merge verification end ~19:37Z. Merged SHA c87aab8 (ff, main had not moved; no rebase needed).

## Objective
three renderer does no frame work while the tab is hidden or the host is offscreen, and resumes with a correct single redraw and continuous playback.

## Changes (Owns only: Build/web/src/viewer/, tests/viewer/, evidence/S09/)
- three-renderer.mjs: injectable IntersectionObserverImpl (default global); document visibilitychange listener (doc.hidden);
  paused → invalidate only marks dirty, pending rAF cancelled, playback clock frozen (playStart shifted by paused time on resume);
  resume → one redraw if dirty. Mount-while-hidden waits for visibility. handle.paused getter. Dispose frees listener + observer.
- tests/viewer/three-renderer.test.mjs: fake document is an event target with hidden flag; fake IntersectionObserver; +1 test;
  live-resource counts updated (observers 1→2, listeners 6→7); zero-leak asserts now cover the new resources.
- tests/viewer/browser-smoke.html: real-browser offscreen pause check (pauseOk) folded into ok.
- README section; evidence/S09/S09f.md.

## Commands and results
- node --test tests/viewer/viewer.test.mjs tests/viewer/three-renderer.test.mjs tests/viewer/artifact-loader.test.mjs tests/viewer/scene-overlays.test.mjs tests/viewer/render-budget.test.mjs
  → 41/41 pass, fail 0 (worktree and on main after ff).
- node tests/viewer/browser-smoke.mjs → exit 0, ok true; pausedOffscreen true, pendingWhileOffscreen false, framesWhileOffscreen 0,
  resumed true, framesAfterResume 1, idleFrames 0; overlay/budget checks still true (worktree and main).
- python contracts/scene/validate_scene.py test-data/synthetic/scene/room-v1/scene.json → PASS.
- Mutations (reverted, file restored, suite re-run green): 6/6 caught (list in evidence/S09/S09f.md).

## Skills/plugins
- Superpowers test-driven-development (…/superpowers/7.0.1/skills/test-driven-development/SKILL.md), read before code: test + count
  updates written first → 2 failures (observers 1 vs 2; IntersectionObserver never constructed) → implement → green.
- Superpowers verification-before-completion: full viewer suite + browser smoke + validator fresh in worktree and on main before status claims;
  mutation red-green for each pause branch.
- Ponytail (…/ponytail/5.3.2/skills/ponytail/SKILL.md): ~25 lines in the existing renderer, existing injection pattern, platform APIs, no deps;
  skipped: frame-rate throttling, user-facing pause indicator, real background-tab test.
- Not used: Playwright MCP (existing CDP smoke extended); frontend-design (no UI change); web tools (offline task).

## Limits
- Tab hiding verified with injected fake document only; headless smoke exercises the IntersectionObserver path, not a real background tab.
- No CPU/GPU/battery measurement; synthetic 8-point fixture. Idle no-loop behaviour predates this run (S09b), re-asserted.
- python Run-System/validate_controls.py still has the stale S03 "Product source must not exist" assertion (pre-existing, untouched).

## Communication compliance
Silent workflow followed: no greeting/progress narration in chat; questions: none (fallback unused); final reply one line.

## Cost / quota
Tokens unavailable; Claude quota unavailable; Meta/service/GPU $0. Owner questions: 0. No D1/D2 decisions.

## Next
S09g CLAUDE Opus 5.5 medium (375px reduced-detail viewer layout).
