# S15j-orch29 REPORT
Lane/model: anthropic/claude-sonnet-5-5 medium (OpenCodex-managed; not polled). Start 2026-10-29T15:37:08Z, end 2026-10-29T15:38:43.4181824Z. Result: DONE (fixtures only; no gate/real-scene/physical claim).
## Change
- Build/web/src/workspace/workspace.css: in the existing `@media (max-width: 860px)` block, areas now "nav" "viewport" "panel" "job" "side" (was side above viewport). One line; existing grid reused.
- tests/workspace/stack.test.mjs: asserts single-column minmax(0,1fr), area order ends with side below viewport, and no fixed width/min-width > 343px in the stylesheet.
## Checks
- node --test tests/workspace/*.test.mjs: 77 pass (includes new stack test), 0 fail.
- In-app browser (iab only), local static preview evidence/S15/stack-preview.html (made by existing nav-ssr-check.mjs, React 19.3.1 SSR, synthetic report fixture), served by temporary python http.server (stopped):
  - 375: scrollWidth 360 == clientWidth 360 (no horizontal scroll); tops: stages 40, viewport 82, panel 473, job 1065, sidebar 1205 (below viewport).
  - 1280: scrollWidth 1265 == clientWidth 1265; desktop layout unchanged (sidebar row above viewport, panel/job right).
- Screenshots: evidence/S15/stack-375.png, evidence/S15/stack-1280.png.
## Skips / risks
- Ponytail: reused workspace.css grid, existing SSR preview script, no new deps; one stylesheet line + one small test.
- Sidebar DOM order is unchanged (still before viewport), so screen-reader/tab order precedes the viewport at narrow width; only visual order changed. Not changed (reordering DOM is outside the smallest change).
- Preview shows report phase only (viewport empty, no scene); other phases not measured at 375 in this run. No Chrome used. Communication: silent apart from the one final line.
