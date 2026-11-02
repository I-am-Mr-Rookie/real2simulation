# N68 verification

- Branch `run/N68-orch312`, base `31c10cfa`.
- Both Reset buttons share `stop()`. It now clears the stale Running/Paused message to a ready SIMULATED message, alongside the existing time, cursor, trace-fit and physics cleanup.
- Inspected every `stop()` caller. Scene/history/source/agent callers retain their following contextual status messages. `LabClient.jsx` already resets status to idle, resets its message, aborts pending requests and invalidates stale responses; no change needed there.
- Phone replay summary (`.le-status`) now sits 112px plus the bottom safe area above the stage bottom, clearing the floating rail's 56px bottom inset and 46px height. Its existing scrolling and height limit remain. Desktop positioning is unchanged.
- Before production edits, the two new regression tests failed: stale Running message and insufficient rail clearance (5 other targeted tests passed).
- After fixes: `node --test tests/lab-editor/*.test.mjs tests/workspace/*.test.mjs`: 204 passed, 0 failed.
- `npm run build` in `Build/web`: passed compilation, TypeScript, page generation and route output.
- Local production server `next start --hostname 127.0.0.1 --port 3068`: ready; HTTP `/lab` returned 200 and SIMULATED content. This is only an HTTP smoke check, not browser or interaction verification.
- DEV `railway variables --kv` export went directly to gitignored `Build/web/.env.local`, never printed. Temporary file removed; local production listener stopped, both verified.
- `git diff --check`: passed.
- Initial connection and its single retry both returned `Browser is not available: iab`. Original deadline passed and was recorded PARTIAL. Koushik subsequently attached the browser; controller reissued 19:18:52 to 19:48:52 UTC. Final status DONE.
- No private N06 room or owner clip accessed. No uploads, inference, paid jobs, deployments or account changes. Paid calls: 0.

## Actual in-app browser QA after attachment

- Rebuilt the same worktree with `npm run build`: PASS. `next start --hostname localhost --port 3068` served the production build, not `next dev`. Final checks below all used `http://localhost:3068`.
- Existing approved DEV fixture account confirmed through its visible account menu before workspace QA. Kept default Standard mode; did not choose a new model or alter account settings. No real email appears in screenshots.
- Used the fixture's existing synthetic virtual lab, the explicitly labelled RECORDED classroom sample, and the existing public ST03 experiment. Opened ST03 via its visible workspace card and `3D replay, redo with changes` result link. Did not open unrelated projects or private owner recordings.
- Desktop 1366x900: clicked Play, confirmed Running SIMULATED status and advancing time (3.42 s observed), clicked the top Reset. Status became `Ready. Press Play to start again. Everything here is SIMULATED.`; time became 0.00 s; Play enabled, both Reset controls disabled. Scene remained visible.
- Phone 375x850: collapsed the Objects panel, clicked Play, then Pause. Confirmed Paused status and 7.07 s. Clicked timeline Reset; status became Ready SIMULATED, time 0.00 s, Play enabled and Reset disabled. Screenshot visually inspected.
- Phone ST03 replay: all summary text, assumed-size provenance, SIMULATED what-if warning, fitted result, 1 sigma uncertainty and playback-clock caveat remained readable. No overlap with floating navigation. Actual DOM bounds: summary bottom 476.53125px; navigation top 486.53125px, a 10px gap. Summary clientHeight/scrollHeight both 62px, so it was not silently clipped.
- Phone result bounds: y=740.625px to bottom=844px in an 850px viewport. Existing fitter output remains 2.71 +/- 0.42 m/s^2; this is not a new fit or a calibrated measurement claim.
- Used visible replay slider Home/End controls: time displayed 0.00 s then 0.67 s. Restored the last recorded sample.
- Desktop ST03 replay: summary fully visible, computed bottom inset still 10px. Summary clientHeight/scrollHeight both 48px. Result and uncertainty visible, without phone-specific displacement.
- Actual screenshots inspected, not only DOM assertions. Browser error log empty. Existing theme retained, viewport override reset, temporary tab closed.
- Railway-exported `.env.local` used only for this local production process. Its local workspace API route used the existing DEV public endpoint instead of Railway-private DNS; no remote configuration changed. Environment file removed and production listener stopped, both verified after QA.
- No new implementation changes were needed. Physical-device/safe-area hardware testing and live inference were not performed.

## Screenshots

- [Desktop Reset](reset-desktop.jpg), [375px Reset](reset-375.jpg)
- [Desktop ST03 replay](replay-desktop.jpg), [375px ST03 replay](replay-375.jpg)
- Four JPGs saved under this directory and committed as explicitly requested in the controller's follow-up. Only synthetic/public sample data is shown.
