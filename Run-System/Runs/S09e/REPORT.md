# S09e REPORT — Implement pixel-ratio and detail budgets

- Status: **DONE** (acceptance: DPR cap and reduced detail are deterministic per device budget)
- Lane/model: CLAUDE; requested Opus 5.5 medium; actual = orchestrator-delegated Claude-agent session in Codex desktop, exact model/effort not exposed.
- UTC (host clock): start 2026-10-27T19:23:35Z; merge verification end ~19:29Z. Merged SHA d31bc76 (ff after rebase on S04d f55330d).

## Objective
One pure, deterministic device budget (DPR cap, detail tier, point cap, antialias) applied by the three renderer once per mount.

## Changes (Owns only: Build/web/src/viewer/, tests/viewer/, evidence/S09/)
- Build/web/src/viewer/render-budget.mjs (new): renderBudget(device) → frozen { tier, pixelRatio, maxPoints, antialias };
  full = DPR ≤ 2, ≤ 2 M points, antialias; reduced (viewport < 768 px, memory < 4 GiB or < 4 cores) = DPR ≤ 1.5, ≤ 250 k points, no AA.
  probeDevice() (width = min(innerWidth, screen.width)); decimatePoints (every ceil(n/max)-th point).
- three-renderer.mjs: option device (replaces pixelRatio); budget → createGLRenderer(canvas, budget), setPixelRatio, decimated geometry;
  handle.budget, handle.pointCount.
- Tests: render-budget.test.mjs (8), three-renderer.test.mjs (+2, fake GL records pixel ratio/options); browser-smoke.html budgetOk check;
  browser-smoke.mjs optional SMOKE_DEVICE=WxH@DPR CDP emulation. README section; evidence/S09/S09e.md.

## Commands and results
- node --test tests/viewer/viewer.test.mjs tests/viewer/three-renderer.test.mjs tests/viewer/artifact-loader.test.mjs tests/viewer/scene-overlays.test.mjs tests/viewer/render-budget.test.mjs
  → 40/40 pass, fail 0 (worktree, after rebase on f55330d, and on main after ff).
- node tests/viewer/browser-smoke.mjs → exit 0, ok/overlaysOk/budgetOk true at default (800 px @1 → full, DPR 1, canvas 320×240),
  SMOKE_DEVICE=375x667@3 (→ reduced, DPR 1.5, no AA, canvas 480×360), SMOKE_DEVICE=1440x900@3 (→ full, DPR 2, canvas 640×480); after rebase too.
- Mutations (reverted): reduced cap 1.5→2 fail 3; <768→<=768 fail 1; ceil→floor stride fail 2; probe without screen.width fail 1;
  renderer setPixelRatio(1) fail 2 → 5/5 caught.
- python contracts/scene/validate_scene.py test-data/synthetic/scene/room-v1/scene.json → PASS.

## Skills/plugins
- Superpowers test-driven-development (…/superpowers/7.0.1/skills/test-driven-development/SKILL.md + writing-good-tests.md), read before code:
  render-budget tests written first vs empty exports → 7 fail (feature missing) → implement → 7/7; renderer tests first → 2 fail
  (pixel ratio 1 vs 1.5/2) → wire → pass; phone-smoke bug (innerWidth 981 under 375 px emulation without viewport meta) → failing
  probeDevice test (981 vs 375) → fix → pass. Hand-derived literal expectations; full viewer suite run, not just new file.
- Superpowers verification-before-completion (…/verification-before-completion/SKILL.md): fresh full suite + 3 browser smokes + validator
  after rebase and on main before any status claim; red-green mutations; acceptance checklist in evidence/S09/S09e.md.
- Ponytail (…/workspace-directory/ponytail/5.3.2/skills/ponytail/SKILL.md): one small pure module, existing injection pattern, no new deps;
  skipped mobile_asset_id loading, resize re-evaluation, point-size compensation (named in limits).
- Not used: Playwright MCP (existing CDP smoke extended instead); frontend-design (no UI design change); web tools (offline task).

## Limits
- Heuristic budget from device facts, not measured fps; emulated DPR/width on headless SwiftShader, no real phone/GPU.
- Browser fixture has 8 points, so decimation is proven by node tests only. mobile_asset_id still not loaded; budget fixed per mount.
- First ff attempt failed because S04d merged meanwhile; worktree was removed early, re-added on run/S09e, rebased, rechecked, then ff.
- python Run-System/validate_controls.py fails on its stale S03 assertion "Product source must not exist" (Build/ exists since S04); pre-existing, not changed here.
  node_modules junction (ignored) removed non-recursively before each worktree removal; main install intact.

## Communication compliance
Silent workflow followed: one brief pre-skill note only (before reading skills), no other narration; questions: none (fallback unused); final reply one line.

## Cost / quota
Tokens unavailable; Claude quota unavailable; Meta/service/GPU $0. Owner questions: 0. No D1/D2 decisions.

## Next
S09f CLAUDE Opus 5.5 medium (pause rendering when idle or hidden).
