# S09g REPORT — 375px reduced-detail viewer layout

- Status: **DONE** (acceptance: no horizontal scroll at 375px; controls remain usable)
- Lane/model: CLAUDE; requested Opus 5.5 medium; actual = orchestrator-delegated Claude-agent session in Codex desktop, exact model/effort not exposed.
- UTC (host clock): start 2026-10-27T19:38:39Z; end ~19:45Z. Merged SHA fd10ee6 (ff from e1f2c96; main had not moved).

## Objective
Viewer fits a 375px phone without horizontal scroll, uses reduced label detail when narrow, and stays operable by touch.

## Changes (Owns only: Build/web/src/viewer/, tests/viewer/, evidence/S09/)
- three-renderer.mjs: canvas CSS display:block, width/height/maxWidth 100% (fixes pre-existing overflow: gl.setSize(...,false) left CSS size = DPR-scaled buffer → 546px scroll at 375px/DPR1.5);
  host position:relative whenever unset (restored on dispose); banner overflow-wrap:anywhere; toolbar [data-viewer-controls] role=toolbar
  with 44×44 Zoom in / Zoom out / Play camera path buttons (play only with valid path); per-resize layout compact (<480px host: labels 40% max-width, ellipsis, 12px) or full; handle.layout.
- tests/viewer/three-renderer.test.mjs: +1 test (canvas sizing, toolbar, compact truncation, click zoom/play, resize→full, zero-leak dispose); listener count 7→10; ResizeObserver callback exposed in fake env.
- tests/viewer/browser-smoke.html: viewport meta; second full-width host layout check (layoutOk) folded into ok.
- README section; evidence/S09/S09g.md.

## Commands and results
- node --test tests/viewer/{viewer,three-renderer,artifact-loader,scene-overlays,render-budget}.test.mjs → 42/42 pass (worktree and main).
- node tests/viewer/browser-smoke.mjs → exit 0, ok, layoutOk (800px viewport: scrollW 800, full).
- SMOKE_DEVICE=375x667@3 node tests/viewer/browser-smoke.mjs → exit 0, ok, layoutOk: scrollW 375 = viewport, canvas 359 = host, compact, reduced budget DPR 1.5, 3 buttons 44×44 inside viewport and hit-testable, real click zoom changed pixels (worktree and main).
- python contracts/scene/validate_scene.py test-data/synthetic/scene/room-v1/scene.json → PASS.
- Mutations (reverted, suite green after): 5/5 caught (evidence/S09/S09g.md).

## Skills/plugins
- Superpowers test-driven-development (…/superpowers/7.0.1/skills/test-driven-development/SKILL.md), read first: new test + count update written before code → RED (listeners 7≠10; canvas style undefined) → implement → GREEN.
- Superpowers verification-before-completion: fresh unit + both browser smokes + validator on worktree and main before status; mutation red-green.
- Ponytail (…/ponytail/5.3.2/skills/ponytail/SKILL.md): ~35 lines in existing renderer, native buttons/CSS, no deps; skipped pinch zoom, landscape tuning, layout options.
- Not used: frontend-design (functional controls only, no visual design pass); Playwright MCP (existing CDP smoke extended); web tools (offline).

## Limits
- Headless Chromium device emulation, not a real phone; no real touch-event drag test; no pinch zoom; no landscape/short-height check.
- Synthetic 8-point fixture; no measured/simulated numbers. Budget still per mount (S09e), not per resize.
- Worktree used a junction to main's Build/web/node_modules (ignored); junction removed before worktree removal, target intact.
- Process slip: one early apply_patch with a relative path hit main's test file; copied to the worktree and main file restored with git checkout (own edit only) before commit.
- python Run-System/validate_controls.py stale S03 assertion pre-existing, untouched.

## Communication compliance
Silent workflow followed: no greeting/progress narration in chat; questions: none (fallback unused); final reply one line.

## Cost / quota
Tokens unavailable; Claude quota unavailable; Meta/service/GPU $0. Owner questions: 0. No D1/D2 decisions.

## Next
CLAUDE lane: no ready run (S09h waits for S04, S05). CODEX-2 S04e ready on authorization (Codex quota hold per STATE).
