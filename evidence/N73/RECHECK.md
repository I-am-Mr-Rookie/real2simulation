# N73 DEV human-style recheck

QA completed, not a readiness sign-off. No product code changed. DEV: https://real2simulation.rookiecoders.tech. In-app ChatGPT browser only; existing approved fixture session. Controller-declared deploy: main `be52ddeb`, API `093b5ac4`, web `0712a39f`; runtime revision not independently verified. Source pointers below are likely owners in this checkout (`d4735eb6`).

## Eight requested checks

1. **Model picker: PASS with routing observation.** At 1366x900 and 375x850, Recommended Spark Standard / Cheapest Contributor / Fastest Open / Smartest Wonder and relative intelligence/speed/cost bars are present. Contributor confirmation canceled. Phone picker x=64..348 with navigation closed, clear of the rail. Wonder's relative-cost details and guide daily-budget note are present. One actual classroom Wonder response confirmed `muse-wonder-1.0`; first selection did not persist once, see O1.
2. **N59 SF3D sample showcase: NOT PRESENT.** Approved classroom sample has 20,000 scan points, 0 objects and no SF3D meshes; conditional in-editor Stability attribution therefore absent. One `Powered by Stability AI` appears in the public footer. Cannot sign off mesh appearance or the single in-room attribution without meshes. See F1.
3. **N63/N65/N67/N68: MIXED.** Reset now reads Ready and t=0.00 on desktop/phone; picker clears the left rail; replay summary clears floating navigation by 10 px and is not clipped. N63 mesh-quality coverage unavailable (item 2). N67 paid quota/concurrency enforcement was not exercised; this is not a backend guard revalidation.
4. **N69 storage / N72 limits copy: PASS for display.** Fixture sidebar shows 26 MB of 1 GB and 20 uploads/day; guide states up to 3 new room builds/day plus 3 shell rebuilds. Backend limits were not consumed or tested.
5. **GPU indicators: PARTIAL COVERAGE.** Red sleeping state observed. No deliberate wake; yellow starting, green running and green-only idle countdown not observed. Zero GPU jobs initiated.
6. **Lab tools/editor: PASS for safe interactions.** A4 helper, real-object pick helper and shell-build button present; no image point selection or rebuild. In an unsaved standalone scene: added ball, moved x=0.5/y=2, resized all axes to 0.2, Play/Pause/Reset, deleted only this new ball, Undo restored it. Phone canvas 375x646.03, desktop outside-canvas scroll did not trap/overflow. At 1920x1080, header/timeline span 1920 and canvas 1552x904.22. Native Ctrl+- did not change browser zoom: true zoom check remains unverified. See F5.
7. **Voice / sample redo: PASS with voice limitation.** Voice button responds but remains disabled `Transcribing` while microphone acquisition is unresolved; no completed recording/transcript observed. Existing approved ST03 replay shows 2.71 +/- 0.42 m/s^2 (1 sigma), assumed user size and unverified capture clock. Changed only unsaved what-if gravity y=-4 and played/reset SIMULATED replay; original fit unchanged. Phone replay canvas 375x497.53; summary bottom 476.53, navigation top 486.53. See F4.
8. **Guide and public copy: MOSTLY PASS.** All 10 sections/anchors inspected, all 16 walkthrough screenshots loaded, no broken image observed, visible guide text contains no em dash. Room-tool/model/menu labels and limits match tested UI; public library opens a labeled synthetic replay. System, Paper, Light, Dark, Midnight, Graphite and High contrast inspected; original System restored. Signed-in phone header overflows and home abstention copy is stale, see F2/F3.

## Findings, ranked

### F1 [P2] Classroom sample has no SF3D showcase objects
- Repro: fixture workspace > Open classroom room and falling apple > lab Objects/Room. Observed at 1366x900 and 375x850: 20,000 points, 0 objects; Play initially disabled and no mesh attribution.
- Impact: current approved sample cannot demonstrate N59 meshes or validate their appearance/licensing display. This does not prove the SF3D renderer or generation endpoint is broken.
- Likely owner: `Build/api/storage/sample.py` `_room` seeds `objects: []`; `Build/web/src/lab-editor/LabEditor.jsx` mesh attribution is conditional. Existing fixture migration may also matter; not investigated by mutating data.
- Local evidence: `classroom-room-panel.jpg`.

### F2 [P2] Signed-in public header overflows at 375 px
- Repro: signed-in fixture > /guide > wait for account navigation; phone 375x850. Header nav right edge 391.15625, document scrollWidth 391 vs innerWidth 375. User-menu control sits beyond the viewport; screenshot shows it missing at the right edge. Repeated after restoring System; not theme-specific.
- Likely owner: `Build/web/src/app/SiteFrame.jsx` mobile FRAME_CSS, `Build/web/src/app/styles.css` mobile header rules, `Build/web/src/shell/AccountNav.jsx` signed-in extra avatar.
- Local evidence: `guide-header-overflow-375.jpg`, `restored-system-theme-375.jpg`. Lab header/timeline at 1920 px did not show this problem.

### F3 [P3] Home still promises abstention for unverified scale
- Repro: / > visible honesty strip, phone 375x850 (also source): `We abstain when scale is unverified.` Actual sample flow allows explicitly assumed scale and labeled what-if use. This contradicts the current imperfect-input product direction and guide.
- Likely owner: `Build/web/src/app/(public)/page.jsx`, honesty-strip paragraph.

### F4 [P3] Voice says Transcribing before microphone acquisition resolves
- Repro: classroom > Agent > Voice input; desktop. Button immediately becomes disabled `Transcribing`, with no completed recording/transcript observed before tab closure. Permission-pending behavior is acceptable for this QA, but this label suggests work that has not started and offers no cancel.
- Source confirmation: `Build/web/src/workspace/voice.mjs` sets `working` before awaiting getUserMedia; `Build/web/src/lab-editor/AgentPanel.jsx` maps working to disabled Transcribing. Root permission outcome and full transcription are unverified; do not treat this as proof the service fails.

### F5 [P3] Turning off real-object pick leaves its instruction active
- Repro: classroom > Room > Add a real object > press Add a real object again without clicking the image; desktop. Tool becomes unpressed and image returns to normal but helper still says `Click a real object, for example a chair or table.`
- Likely owner: `Build/web/src/lab-editor/LabEditor.jsx` `pickTool` updates note from requested tool even when toggling it off.

### O1 [P3, once observed, not persistent] First Wonder selection reverted
- First picker selection displayed Wonder, but subsequent classroom turn used Spark and returning to workspace displayed Spark. Re-selected Wonder, reloaded workspace to confirm persistence, then classroom returned actual `muse-wonder-1.0` successfully. Two turns total; no repeated persistent routing failure established.
- Likely investigation points: `Build/web/src/workspace/live-view.mjs` ModelPicker / selection persistence in live.mjs and `Build/web/src/lab-editor/AgentPanel.jsx` user-key/model read. Do not claim a root cause from this single event.
- Local evidence: `wonder-selected-but-spark-response.jpg`, `wonder-turn-classroom.jpg`.

## Spend / safety / verification limits

- Two confirmed paid agent turns, no tool calls: Spark 2026-11-02T20:54:43.466Z, 2481 input / 398 output tokens, code estimate USD 0.004471; Wonder 2026-11-02T20:57:07.554Z, 2409 / 306 tokens, code estimate USD 0.015756. Total USD 0.020227 from `Build/agent/core.py` token prices, not billing receipts. Machine-readable ledger: `paid-turns.json`.
- No room build, shell rebuild, real-object generation or GPU job initiated. No third agent turn. Voice billing was not independently inspected; no completed transcript observed.
- Only approved fixture sample and ST03 were opened, plus unsaved local scenes/public pages. No private owner room/clip, upload, account mutation, persistent-data deletion, deployment, push or product-code edit. Deleted ball was created within this unsaved QA scene and recovered via Undo. Spark Standard and System appearance restored, viewport override reset, own tabs closed.
- True browser zoom, awake GPU states/countdown, paid enforcement, new upload/tracking/fitting, SF3D generation/mesh appearance, microphone/transcription end-to-end and full screen-reader/contrast audit remain unverified. Wide viewport is not browser zoom. Existing fit was inspected, not recomputed or physically calibrated.
- No application tests/build run: application code unchanged. Report/receipt JSON, named staged paths and timebox checked separately.

## Local-only screenshots

Not committed or uploaded. Directory: `C:/Users/HP/.codex/visualizations/2026/11/02/01a19dda-5200-73a2-8e88-b2ec3eaae909/N73/`.

Primary views: `picker-1366.jpg`, `picker-375-dark.jpg`, `picker-375-light.jpg`, `wonder-limit-375.jpg`, `classroom-room-panel.jpg`, `wonder-turn-classroom.jpg`, `reset-desktop.jpg`, `reset-375.jpg`, `replay-375.jpg`, `editor-outside-scroll.jpg`, `editor-wide-1920.jpg`, `guide-limits-375.jpg`, `guide-midnight.jpg`, `guide-contrast.jpg`, `guide-header-overflow-375.jpg`, `restored-system-theme-375.jpg`.
