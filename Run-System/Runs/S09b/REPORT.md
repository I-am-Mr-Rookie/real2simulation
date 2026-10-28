# S09b report — DONE

- Objective: render the synthetic fixture geometry with an orbit camera; mount → orbit → unmount without leaking resources.
- Lane CLAUDE; planned Opus 5.5 / medium. Actual: orchestrator-delegated Claude-agent session in Codex desktop; exact model ID/effort not exposed (not verified).
- UTC start 2026-10-27T18:42:54Z; merge/verification end 2026-10-27T18:47:54Z (host clock as observed). Merged SHA 2a632f1474e698e4529c28c89389ca9ad80f82e1 (ff after rebase on 47875e7).

## Changes
- Build/web/src/viewer/three-renderer.mjs — createThreeRenderer (injectable THREE/GL/rAF/ResizeObserver): THREE.Points + vertex colours, camera framed from bounds_m, spherical orbit (drag, wheel, arrows/+/-; pole + zoom clamps), render-on-demand, synthetic banner via textContent, full dispose (frame, listeners, observer, geometry, material, WebGLRenderer, context loss, DOM nodes); partial-construction failure frees itself.
- Build/web/src/viewer/three-viewer.mjs — browser entry createThreeViewer() wiring real three into the S09a adapter.
- Build/web/src/viewer/README.md — renderer section, checks, dependency request closed.
- tests/viewer/three-renderer.test.mjs (6 tests), tests/viewer/browser-smoke.{mjs,html} (allow-listed 127.0.0.1 server + raw CDP on chrome-headless-shell; no new dependency).
- evidence/S09/S09b.md.

## Commands and results
- node --test tests/viewer/viewer.test.mjs tests/viewer/three-renderer.test.mjs → 17/17 pass (worktree, after rebase, on main).
- node tests/viewer/browser-smoke.mjs → ok=true on worktree, after rebase, on main: loading→ready, WebGL2, 19 lit px, drag orbit changed pixels, after abort canvas/banner gone, geometries 0, context lost.
- Mutations (drop geometry dispose / listener removal / frame cancel / partial dispose) → 3/2/1/1 failures; restored.
- python contracts/scene/validate_scene.py …/room-v1/scene.json → PASS (not Gate R); python Build/web/src/shell/test_contract.py → OK.

## Decisions (routine)
- Own ~30-line orbit instead of three/addons OrbitControls: Node-testable, exact listener accounting, no addon DOM assumptions.
- Render on demand, no continuous loop (GPU/battery). Only +Y-up scenes; others → RENDER_FAILED.
- Browser smoke uses raw CDP over Node's WebSocket with Playwright's cached headless shell; --dump-dom snapshotted before the module finished, so it was replaced.

## Limits
- SwiftShader software GL, not a real GPU/driver; no mobile/touch/pinch, heap/GPU-memory profiling, fps or large clouds. Leak proof is resource accounting (Node) + three renderer.info/DOM/context checks (browser), not a profiler.
- Not mounted by any app route (S04/S15 composition). Synthetic fixture only: not reconstruction, physics or Gate R evidence.
- Smoke needs Build/web/node_modules and a Playwright-cached chrome-headless-shell (or CHROME_BIN); worktree used a temporary ignored junction to main's node_modules, removed before worktree removal.
- Started with tests written after the renderer (not strict TDD red); compensated with mutation checks.

## Next
- S09c CLAUDE Opus 5.5 medium: artifact loader validation; real artifacts wait for S05.

## Skills/plugins
- Original run (18:42–18:48Z): no Superpowers SKILL.md was read, contrary to Run-System/SKILLS_AND_PLUGINS.md. Checks were rerun in worktree, after rebase and on main, and mutations were used instead of TDD red (see Limits); that was practice, not documented skill use.
- Correction after orchestrator acceptance hold (2026-10-27, finished 18:51:07Z): read Superpowers verification-before-completion
  (C:/Users/HP/.codex/plugins/cache/openai-curated-remote/superpowers/7.0.1/skills/verification-before-completion/SKILL.md; only other file agents/openai.yaml, which is UI metadata; no further references). Applied its gate function on main 82cb673, with fresh full commands and exit codes read:
  - VCS check ("agent completed" requires a diff): 2a632f1 is an ancestor of HEAD (exit 0); 7 files, +455/-5, all within S09b Owns paths; viewer/tests/evidence tree clean.
  - Tests: node --test tests/viewer/viewer.test.mjs tests/viewer/three-renderer.test.mjs → tests 17, pass 17, fail 0, exit 0.
  - Real browser: node tests/viewer/browser-smoke.mjs → exit 0; ok=true, states loading,ready; WebGL2; 19 lit px; orbit changed pixels; after abort canvas and banner removed, geometries 0, context lost.
  - Red-green revert (regression-test pattern): removed geometry dispose → three-renderer tests 3 pass / 3 fail, exit 1; restored → git diff clean, 17/17 pass, exit 0.
  - Others: scene validator PASS, exit 0; shell test_contract OK, exit 0.
  - Requirements checklist (QUEUE acceptance "loads, orbits, unmounts without leaking resources"): loads = loading→ready + lit pixels (verified); orbits = Node camera position change + browser pixel change (verified); no leaks = Node zero live GL/geometry/material/DOM/listener/frame/observer counts after dispose and 100 mount→abort cycles, plus browser geometries 0/context lost/DOM removed (verified within these measures). Gaps: browser shader programs/textures and JS heap not measured; SwiftShader is not a real GPU.
- Not used: test-driven-development (strict RED was not observed; not claimed), Playwright MCP (direct CDP sufficed), other plugins/MCP (offline task).

## Cost / quota
- Tokens: unavailable. Claude quota: unavailable. Meta/service/GPU $0. Owner questions: 0.
