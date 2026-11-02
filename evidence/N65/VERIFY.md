# N65: F05/F06 regression and in-app verification

## Code checks
- Base `882da5c5`; implementation commit `de03c263`, branch `run/N65-orch308`.
- Before production edits, `node --test tests/workspace/measure.test.mjs tests/workspace/home.test.mjs` returned 14 pass, 2 fail. Both new regressions failed: picker used `.75rem` instead of rail-safe inset; assumed metric result claimed known-size MEASURED.
- After edits, targeted checks returned 16 pass, 0 fail. Full requested `node --test tests/workspace/*.test.mjs tests/lab-editor/*.test.mjs` returned 200 pass, 0 fail.
- `npm run build` in `Build/web` passed, including compilation, TypeScript and page generation. `git diff --check` passed.
- Provenance coverage: quantity-label known size; assumed size via quantity label and legacy top-level label; pixel/unverified track; metric track without verified provenance. No fitting or measurement numbers changed.

## Actual browser session
- Actual ChatGPT in-app browser, local `http://localhost:3065`, running this worktree's `next dev --webpack` against the existing DEV API. No DEV deployment.
- Existing fixture `n43-mvym1kik+clerk_test@example.com`, approved test code, existing projects only. Initial local-origin mode gate retained its default Standard mode. No model selected in the picker.
- Controller-approved Railway web-variable export went directly to gitignored `Build/web/.env.local`, never printed. Railway-private API DNS was unreachable locally; read-only domain lookup supplied the existing DEV public API domain for this local file only. File removed after QA; server stopped.
- Initial 127.0.0.1 proxy/navigation trouble resolved by restarting on localhost. Browser attachment failure from the first window was not treated as visual evidence.
- Used product controls to close sidebar, open model pill, choose Light/Dark, open the existing ST03 project and its 3D replay, collapse the editor panel, and return to workspace. Did not upload, run tracking, request agent/model inference, fit, simulate, share, save or change account settings.

| Width / theme | F06 model picker | F05 replay summary |
|---|---|---|
| 375x850 / Dark | PASS: names, Standard/Contributor, bar labels and pros/cons visible right of rail | Correct assumed-size copy in DOM and visible summary; floating nav overlaps part of text |
| 375x850 / Light | PASS: same clearance and readable contents | Same corrected copy and pre-existing overlap |
| 1366x900 / Dark | PASS: original absolute desktop placement remains readable | PASS: summary explicitly says `Track in metres, scale assumed (user size).` |
| 1366x900 / Light | PASS: same desktop behavior | PASS: same summary and matching footer |

- Phone DOM geometry: viewport 375; rail right 52; picker left 64, right 348. This checks actual rail overlap, not only document width.
- Desktop DOM geometry: viewport 1366; picker left 389.6875, right 879.6875; computed position `absolute`.
- Existing ST03 result remained 2.71 +/- 0.42 m/s^2, 1 sigma, with assumed-size and playback-clock caveats. These are existing fitter output, not a new run or a physical calibration claim.
- Replay retains SIMULATED what-if ball and the original uncertainty/footer. Phone floating navigation partly overlaps the summary even with the panel collapsed; this layout issue predates the copy-only F05 fix and was not expanded into this run.
- QA tab browser error log: empty. Theme restored to original System (confirmed pressed); viewport override reset.

## Local-only screenshots
No media binaries committed, per worker contract. Files are under `C:/Users/HP/.codex/visualizations/2026/11/02/01a19cc7-44e3-74e1-a6e3-149eb6ee41d0/`:
- `N65-picker-375-light.jpg`, `N65-picker-375-dark.jpg`
- `N65-picker-1366-light.jpg`, `N65-picker-1366-dark.jpg`
- `N65-replay-375-light.jpg`, `N65-replay-375-dark.jpg`
- `N65-replay-1366-light.jpg`, `N65-replay-1366-dark.jpg`

Paid calls: 0. Deploys: 0. Live known-size/pixel visual fixtures were not manufactured; their summary branches are unit-tested.
