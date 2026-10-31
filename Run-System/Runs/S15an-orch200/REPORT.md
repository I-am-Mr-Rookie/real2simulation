# S15an-orch200 REPORT — PARTIAL

- Lane/model: CLAUDE, anthropic/claude-opus-5-5 high. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). No Meta/GPU/paid call, no deploy, no Chrome, no secrets.
- UTC: issued 10:05:38Z; work 10:06–10:17Z; stopped/reported at the 10:35:38Z deadline (PARTIAL rule). Base main 09cf0fcc -> rebased onto e2b55cfc (controls-only change).
- Why PARTIAL: all seven defects fixed and my Owns' tests green, but 1/159 tests in `tests/web-private` (S15ao's Owns) asserts the removed native `<select>`. One-line fix is ready in [evidence/S15an/OUT-OF-OWNS-TEST.md](../../../evidence/S15an/OUT-OF-OWNS-TEST.md). The controller should apply it when merging S15an + S15ao. No controller-messaging tool was available, so this is recorded here.

## Fixes (a–g)
| # | Root cause → change | File(s) |
|---|---|---|
| a | `main:has(> .r2s-shell)` never matched: the shell sits at main > section[data-private-content] > .r2s-shell. → `main:has(.r2s-shell)`. Probe: main width 1280/1280, no side gutters. | workspace.css |
| b | Two controls → ONE: the S15am swatch menu (System + 6 modes) moved into the global `ThemeToggle` (rendered by SiteFrame on every page). The workspace `<details class="r2s-theme">`, its CSS, and the PrivateWorkspace theme state were deleted. System-follows-OS effect moved with it. | ThemeToggle.jsx, styles.css, workspace-shell.mjs, PrivateWorkspace.mjs, workspace.css |
| c | At 375px the rail (z 31) sat over the open drawer (z 30). → open drawer z 32. Screenshot *-375-right: drawer unclipped. | workspace.css |
| d | The global marketing rule `h1 { max-width: 16ch }` capped the app title. → `.r2s-top h1 { max-width: none }`. h1 is now 954px wide at 1280 (was about 190px). | workspace.css |
| e | Display only: unit `m/s^2` → `m/s²` via a string replace of the stored unit (numbers untouched). Source path moved into a collapsed `<details>Source</details>` and kept verbatim. Skipped stages show a dash icon, dashed pill and `title="Not run"`; the "(not run)" text stays in the DOM in an `r2s-sr` span (layout.mjs label unchanged). Also fixed the invisible done tick (ok-on-ok colour). | view.mjs, workspace.css |
| f | When `.ws[data-phase^="report"]`, the empty host becomes a 4rem strip with the art at left and the EMPTY · NO SCENE pill kept. `.ws-status` changed from monospace to the body font. | workspace.css |
| g | Live notices became `<details class="r2s-chip">` chips: "Connected" and "Instruments off", each with an (i) icon. The full LIVE_NOTICE / INSTRUMENTS_UNAVAILABLE text is unchanged and sits in the detail with `role="note"` (DESIGN_QA 9). Fixture/unavailable notices remain plain notes. | PrivateWorkspace.mjs, workspace.css |

Unchanged: controller.mjs, workflow.mjs, API routes, Build/api, layout.mjs labels, rail/agent/interview behaviour, and the label wording for RECORDED/SIMULATED/what-if/owner clip/FIXTURE/Held-out/scale.

## Ponytail (applied)
- Reuse: kept the existing S15am swatch menu markup and tokens, the existing `r2s-sr` class, `icon()`, the existing `data-phase` / `data-status` hooks, the existing SiteFrame slot and the S15am static-render pattern. Added no dependencies, state or options.
- Smallest change: (a) was one selector and (c) and (d) were one rule each. (e) and (f) render or style the existing data with no new layout state. (g) uses native `<details>`, so it needs no JS state.
- Deleted: about 25 lines of workspace theme-menu markup, CSS and state, which removed the second control.
- Skipped: Escape / outside-click closing for the menu (native details, same as S15am). Also skipped (out of row scope): a metric-xl g value, mono-middle-truncated job ids and a copy affordance (DESIGN_QA 11–12).

## Checks (fresh, this worktree; Build/web/node_modules junction -> canonical, removed afterwards)
- `node --test "tests/workspace/*.test.mjs" "tests/shell-workspace/*.test.mjs" "tests/web-private/*.test.mjs" "tests/web-workspace-api/*.test.mjs"`: 159 tests, 158 pass, 1 fail (public-chrome select regex, out of Owns; see above). Updated tests in my Owns: owner-clip and spec-body now expect m/s² and the Source detail; shell-toggle now asserts the shell renders NO theme control.
- `npm run build` (next build --webpack): passed twice, after the JS change and after the final CSS.
- `python evidence/ui/design-direction/contrast.py`: 6 modes x 27 pairs, 0 failures.
- Static SSR harness [evidence/S15an/static_render.mjs](../../../evidence/S15an/static_render.mjs). It uses the real renderShell/renderWorkspace, mirrors the header markup, shows the owner-clip report.owner state and is labelled FIXTURE; values come from tests/workspace/spec-body.test.mjs. It was served with python http.server and captured with Playwright MCP.
  - Screenshots (dark/paper/contrast): `evidence/S15an/<mode>-1280.png`, `-1280-right`, `-1280-menu`, `<mode>-375.png`, `-375-right`.
  - Probe in all modes and widths: docScroll equals the width (no horizontal scroll), main is full width, and the 1280 title is 954px.
  - Computed contrast at 1280: chip 6.9 / 7.2 / 15.1, skipped stage 7.4 / 6.4 / 15.1, Source 6.9 / 7.2 / 15.1 (dark/paper/contrast). The title probe read about 1 in paper/contrast because it misparsed the color-mix() background; the screenshots show black on white.
- Clerk-gated /workspace was not walked live. Proof comes from the static render only, and the controller DEV walk after merge is the end-to-end check.

## DESIGN_QA self-score (applicable items)
1 pass: labels are DOM text and visible; the EMPTY pill is CSS content and visible. 2 pass: contrast.py. 3 pass on no-scroll; the theme summary and chips are 44px and 32px tall, but the chips sit in the centre flow and do not cover anything. 4: unchanged pre-paint script, not re-verified across reload. 5: focus ring not re-shot. 7 pass. 8: title is a single line but still the fixture copy (not in scope). 9 pass (chips). 13 pass (icons and tooltip, sr text). 14 unchanged. 15 pass (one icon set, 14/16/18). 16: the strip is not a dashed box and keeps the label. 17 pass (dark screenshot). 19 pass: the native select was replaced by a styled menu in every mode. 11–12: not in this row.

## Risks / next
- Merge: apply the one-line test update from OUT-OF-OWNS-TEST.md together with S15ao, then redeploy DEV once. Re-walk /workspace live in dark, paper and contrast at 1280 and 375.
- The header theme menu does not close on Escape or an outside click (native details).
- Communication: silent; no messages sent and no other chats touched.
