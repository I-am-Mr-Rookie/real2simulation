# N83: DEV recheck after N81 and N82

**DONE, with two concrete follow-up rows.** QA only; no product code or guide assets changed.

- Site: https://real2simulation.rookiecoders.tech
- Date: 2026-11-03 UTC. In-app ChatGPT browser, actual authenticated DEV fixture, inherited dark theme.
- Signed out an unrelated test session before signing in with the explicitly supplied fixture email and test code. No auth-screen captures were saved.
- Viewports were verified from `innerWidth`: 1366 and 375. The guide used its own tab-scoped CDP viewport/capture because the browser-wide override did not resize older tabs. These were still in-app browser checks, not external Playwright QA.
- Created rooms/projects/uploads: 0. Deleted rooms/projects/files: 0. Paid model/GPU calls: 0; cost $0. No private owner room or N06 clip opened. No deployment, push or account-setting changes.

## Requested checks

| Item | 1366px | 375px | Evidence / result |
|---|---|---|---|
| 1. SAMPLE has no Delete | PASS | PASS | SAMPLE menu contains only Open and Open experiment; no project or room Delete. |
| 1. Own room confirmation and Cancel | PASS functional | PASS functional; FAIL label contrast | Fixture-owned Not in a project exposes Delete room 82f05b85. Exact warning: Delete this room? Its 3D files and lab edits are removed. This cannot be undone. Cancel closes it and restores menu focus. The room remains after reload, storage stays 52 MB and uploads left stay 20. No destructive confirmation button was pressed. See F1. |
| 2. SAMPLE SF3D shape and labels | PASS visual + regression | PASS visual + regression | Opened only the classroom SAMPLE through its card. Current textured meshes are thin/fragmentary rather than the old inflated silhouettes in the guide. One visible Powered by Stability AI line in the expanded provenance list; no repeated per-object attribution labels. SIMULATED, MODEL-GENERATED, MODEL-ESTIMATED and scale unverified remain explicit. Physical accuracy/model completeness is not certified. |
| 3. Guide matches current workspace/lab | FAIL: two stale images | FAIL: same stale room imagery | Room-tab and A4 screenshots retain the pre-N81 inflated GLB proportions. The Room controls themselves still match. Model-picker and Files/storage layouts reviewed against live controls still match; 26 MB in the guide versus current 52 MB is normal snapshot data, not a UI defect. See F2. |
| 4. GPU status | PASS, sleeping | PASS, sleeping | Red dot / GPU sleeping / Queue empty agrees with the separately rendered GET /api/workspace/gpu/status response: state red, queue_length 0, your_position null, source modal+jobs. A brief gray unavailable state while the Files view mounted resolved to sleeping; no job was started. |
| 4. Console errors / visible em dashes | PASS | PASS | No captured console errors in the checked workspace, SAMPLE lab or guide. Clerk development-key warnings were present, not hidden. Rendered DOM copy contained zero U+2014 characters on all three views. No horizontal document overflow at either width. |

## Concrete fix rows

| ID | Priority | Owns / change | Reproduction and acceptance |
|---|---|---|---|
| F1 | P2 | Build/web/src/workspace/workspace.css, room-delete danger button | In inherited dark theme, open a real fixture room's Delete confirmation at 375px. Enabled Delete room text is rgb(248,113,113) on rgb(255,138,76), approximately 1.184:1 contrast, visibly hard to read. Cancel uses readable dark text. Give the danger button a coherent contrasting foreground/background pair, then recheck desktop/mobile and Cancel. Both touch controls are already 44px high. |
| F2 | P2 | Build/web/public/guide/room-tab.webp and room-a4.webp | Compare /guide#room with the current SAMPLE Room tab. Old guide GLBs include inflated black and curved silhouettes; current uniformly fitted models are much thinner. Refresh only these two screenshots from the approved SAMPLE, preserving honest labels and private-data exclusions. No guide assets were retaken or replaced in this QA run. |

F1 was not patched: this is a QA row, and the existing functional test does not assert rendered color/contrast. F2 is an asset-refresh row, not a one- or two-line product fix.

## Regressions and supporting measurements

`node --test tests/lab-editor/sf3d-fit.test.mjs tests/lab-editor/sf3d-shape.test.mjs tests/workspace/room-delete.test.mjs`: **12 passed, 0 failed, 0 skipped**.

The fit tests verify one equal world scale on all axes across four yaw orientations, centering/bottom alignment, safe degenerate bounds, and unchanged proxy dimensions. This supports the visual N81 check; it is not a browser scene-graph measurement or physical calibration. The room-delete test covers SAMPLE exclusion, all grouped own-room targets, exact warning and Cancel. Dependencies were reused via a junction to existing node_modules; nothing installed.

| View | innerWidth | clientWidth / scrollWidth | Other measured facts |
|---|---:|---:|---|
| Workspace desktop | 1366 | 1351 / 1351 | Cancel restores Project actions for Not in a project. |
| Workspace mobile | 375 | 360 / 360 | Cancel and Delete room: 44px high, both enabled before confirmation. |
| SAMPLE lab desktop | 1366 | 1366 / 1366 | Powered by Stability AI visible count: 1. |
| SAMPLE lab mobile | 375 | 375 / 375 | Powered by Stability AI visible count: 1. |
| Guide desktop | 1366 | 1351 / 1351 | Room section and screenshot remain within the document. |
| Guide mobile | 375 | 360 / 360 | Room section width 320px, computed font 16px, visual scale 1. |

## Local-only screenshots

All JPEGs are excluded by evidence/N83/.gitignore. See screenshot-manifest.json for dimensions and SHA-256 digests.
Workspace captures omit the scrollbar: their pixel widths are 1351/360 while the verified browser viewports were 1366/375. SAMPLE lab captures use the full viewport; guide comparison clips are 720px high.

- sample-menu-1366.jpg, sample-menu-375.jpg: SAMPLE protection.
- delete-cancel-1366.jpg, delete-cancel-375.jpg: exact confirmation and mobile contrast defect.
- sample-lab-1366.jpg, sample-lab-375.jpg: live SAMPLE meshes and single expanded attribution.
- guide-room-1366.jpg, guide-room-375.jpg: stale room imagery in the guide. Native-resolution tab captures avoid a browser screenshot rescaling artifact.
- files-1366.jpg: live Files layout, settled sleeping GPU and unchanged storage.
- console-check.json: empty error lists plus explicit development-warning note.

## Limits / cleanup

No room deletion, rebuild, model selection, new tracking, microphone or paid inference was exercised. Yellow/green GPU states were not forced; the observed sleeping state alone was checked. The guide's paid measurement workflow and every illustrative replay/trace screenshot were not rerun. Existing generated geometry is incomplete in places; uniform rendering does not make it a faithful classroom reconstruction. All run-created tabs were closed and viewport overrides cleared. No browser-only instrumentation or helper service was left running.
