# N84 verification

## Result
- F1: the room-delete danger button now uses the existing danger foreground on the theme surface, with a matching border. Cancel and the 44px height are unchanged. The existing room-delete test asserts the scoped danger/surface token pair.
- F2: only room-tab.webp and room-a4.webp were retaken from the designated fixture's classroom SAMPLE on the requested DEV domain. Both are native browser WebP captures, 1280x720, dark theme, full-window Room panel / canvas / properties / timeline framing, same camera between the pair. The A4 image only enters marking mode; no sheet points were selected and scale was not changed. The assets retain SAMPLE / RECORDED, MODEL-ESTIMATED, SIMULATED and scale unverified labels. No private content or auth UI appears.
- Added Objects-panel finding: constrain the outline grid and rows, let names shrink with ellipsis, reserve fixed 32px action controls, and remove inherited global button margins from rows and panel tabs. Existing stable scrollbar gutter is retained. No JS behavior or keyboard semantics changed.

## Browser proof and its boundary
All UI work used the in-app browser. No deploy was authorized. F1 used the exact scoped rule preview recorded in contrast.json. sidebar.json records interim selected-rule Objects previews, not final compiled stylesheet-order proof. A final audit caught equal specificity between the new 32px rule and the later 28px base rule; the selector is now .lab-editor .le-outline .le-mini, and the test requires it. Fresh final checks injected the entire emitted Lab stylesheet through documented CDP, preserving all its internal rule order. full-built-sidebar.json records its path, byte count, SHA-256 and four valid layouts. These are browser-local checks with DEV's existing global CSS, not a deployment. Navigation/closing removed previews; the original System theme choice was restored and the viewport override reset.

### F1 contrast
At both verified widths, 1366px and 375px, the enabled danger button was 44px high:

| Palette | Foreground / background | Measured ratio |
|---|---|---:|
| Dark | #f87171 / #18181b | 6.405:1 |
| Light | #b91c1c / #ffffff | 6.470:1 |
| Paper | #a3191b / #fffcf5 | 7.557:1 |
| Midnight | #fca5a5 / #111831 | 9.229:1 |
| Graphite | #ff8f8f / #26282c | 6.734:1 |
| High contrast | #8b0000 / #ffffff | 10.011:1 |

All 12 computed-style cases exceed the requested 4.5:1. Only Cancel was clicked. Four local-only JPEGs show Dark/Light at both widths. Source selectors do not target Cancel.

### Objects before / after
- Before, 1366px in both Dark and Light: panel clientWidth 244, scrollWidth 312, horizontal overflow 68px; 28px eye controls extended beyond the content edge, reproducing the report.
- Before, 375px: panel clientWidth and scrollWidth were both 360, so horizontal overflow did not reproduce at this wider bottom-sheet panel; eye targets were still only 28px.
- The first preview fixed rows but left 5px of desktop overflow in the tab header. DOM inspection traced this to inherited 16px button margins. The final patch removes those margins as well; intermediate data is explicitly labelled after-initial, not final proof.
- Final full-built stylesheet, Dark and Light at 1366px: clientWidth = scrollWidth = 244. At 375px: clientWidth = scrollWidth = 360. All 23 eye controls stay inside the content edge, clear of the stable gutter, with width/height 32px and tabIndex 0. Light navigation initially mounted a collapsed panel; zero-size readings were rejected, then the visible Objects button opened it before measurement.
- Keyboard Tab from wall-1-1's native row button focuses the native Hide wall-1-1 button in both palettes with the full built CSS. Nothing was hidden, deleted or otherwise edited. Before/after and final full-build JPEGs are local-only.
- Full emitted stylesheet: Build/web/.next/static/css/34569f794e50d3ae.css, 13745 bytes, SHA-256 1719b4b5f13a282135d23c21aa5b5b75e98b4c4ec0db2f4103cb7a8a637ca462. The 32px selector precedes the 28px base selector and wins by specificity.

## Automated and artifact checks
- `node --test tests/workspace/*.test.mjs tests/web-guide/*.test.mjs tests/lab-editor/*.test.mjs`: 218 passed, 0 failed, 0 skipped, after the final CSS/test patch.
- The literal `node --test tests/workspace tests/web-guide` invocation is not supported by installed Node v24.18.0: directory arguments are treated as module paths and raise MODULE_NOT_FOUND. The explicit file globs above exercise every test in all three requested directories.
- `npm --prefix Build/web run build`: PASS after the final CSS/test patch. No dependency installation; reused existing node_modules through a junction.
- Generated-data assertions: 12 contrast cases >=4.5, four full-built panel layouts with zero horizontal overflow, all eye controls >=32px and in bounds, native keyboard focus, F1 preview/source equality and full-built stylesheet hash, two changed WEBPs at exactly 1280x720. assets.json records before/after SHA-256 digests. Other guide assets are untouched.
- Both retaken WEBPs were visually inspected. browser-check.json and full-built-sidebar.json record zero captured console errors. Final staged Owns/credential/path and whitespace audits are recorded in the completion report.

## Safety / limits
Paid calls 0, cost $0. No delete confirmation, rebuild, paid tracking, purchases, deployment, push, private owner room or N06 access. No backend files changed. Existing fragmentary model geometry remains honestly labelled; this work does not establish physical accuracy. Screenshots beyond the two explicitly owned guide assets remain local-only. All run-created tabs closed; no helper service started.
