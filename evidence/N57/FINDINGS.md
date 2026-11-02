# N57: DEV workspace and full-window editor QA

QA complete, not a release approval. No P1 defect proved. P2/P3 findings below remain unfixed.

## Scope and evidence

- DEV: https://real2simulation.up.railway.app only. The RookieCoders mirror was not visited or inferred equivalent.
- Checkout: `851e9d7a`. Web `fc17545e` and API `ab1c25bd` are controller-provided deployment identifiers, not independently attested from the Railway control plane.
- Primary: headed Playwright Chromium, explicit `ms-playwright/chromium-1248/chrome-win64/chrome.exe`, version `156.0.8078.4`. Initial MCP discovery used installed Chrome; it was abandoned before feature checks.
- Added a ChatGPT in-app browser exploratory pass after Koushik requested it. Public synthetic trials/editor chrome only; did not browse his workspace or projects. Restored its viewport afterward.
- Signed in using the existing DEV test path in `evidence/N46/browser-check.cjs`. New test sign-up stopped at Clerk `protect-check`: "Verification didn't complete. Please try again." No CAPTCHA bypass. Existing account has 0/20 uploads remaining today.
- Forbidden private room and N06 clip were not opened, captured or committed. No deploy, product-code edit, account-setting change, or extra paid retry.
- Main receipt store: [receipts.json](receipts.json). Each `R:` reference below identifies an exact receipt `name`. These contain actual DOM text, responses, timing and geometry, not staged states.
- [network-statuses.json](network-statuses.json), [tests.txt](tests.txt), [template-export.json](template-export.json), [room-collision-traces.json](room-collision-traces.json).
- Eight small JPGs are local-only under this worktree, per the worker contract's no-media-binaries commit rule. JSON/text receipts are committed. Retain this worktree to retain JPG receipts.

## Ranked findings

### P1

None proved in this scope. Unrun paid paths are not evidence of safety or correctness.

### P2-01: Public RM02 Room tools have no usable view image

- Steps: open the seeded classroom room, select Room, wait for its image.
- Expected: a room frame usable by Mark the A4 sheet and Add a real object, or a correctly disabled/unavailable tool state.
- Actual: `GET /api/workspace/rooms/e704985d4073435fb816941a6ab12e82/views/0.png` returns **500 Internal Server Error**. Image width/height are zero; UI says "No view image for this room, so A4 and object clicks are unavailable here." Buttons still arm and overwrite that explanation with click instructions.
- Receipt: `R:room-tools`, `R:sample-room-view-response`, `R:room-tool-state-before-tab`; [07-public-rm02-room-tools.jpg](07-public-rm02-room-tools.jpg).
- Likely fix: `Build/api/storage/sample.py:27` seeds PLY/JSON but not `mapanything.npz`; `Build/api/room/objects.py:58-63` reads that archive and only catches `ValueError`, not missing-file errors. Also `Build/web/src/lab-editor/LabEditor.jsx:183-194` for unavailable controls.

### P2-02: Mobile Add menu is clipped; top actions start outside the viewport

- Steps: editor at 375 x 900, open Add. Also inspect the top bar before horizontally scrolling it.
- Expected: all picture tiles and top actions fit or have an obvious usable mobile presentation.
- Actual: Add menu spans x=96..441 in a 375 px viewport and is clipped by `.le-stage { overflow: hidden }`. Top bar has client width 375, scroll width 532; Export scene is partly outside, Fullscreen and Agent initially outside. Horizontal scrolling does reveal them, so they are not permanently unreachable. Agent loses its accessible name when its text is hidden; Reset retains a title-derived name.
- Receipt: `R:mobile-add-menu-clipping`, `R:mobile-toolbar-horizontal-scroll`, `R:lab-responsive-matrix`, `R:in-app-browser-exploration`; [08-rm02-editor-375-dark.jpg](08-rm02-editor-375-dark.jpg). In-app human-style exploration independently reproduced the clipped right-hand tiles.
- Likely fix: `Build/web/src/lab-editor/lab-editor.css:109-124`; `LabEditor.jsx:583` for Agent's accessible name.

### P2-03: Template-only project snapshots are saved but hidden as Empty

- Steps: open an editor with the new QA project ID, author/play/pause a lab or export it, then return to workspace.
- Expected: the project's saved snapshot appears on its card.
- Actual: snapshot PUT is 200 and the project list returns a snapshot URL, but the project is hidden behind Show empty and its compact `data-small=true` card has no image. This is specific to snapshot-only projects: a completed measurement project correctly displayed its 640 x 689 saved snapshot.
- Receipt: `R:pause-snapshot`, `R:snapshot-only-card-hidden`, `R:ready-project-snapshot-card`; [01-workspace-1366-light.jpg](01-workspace-1366-light.jpg) shows the successful completed-project case.
- Likely fix: `Build/web/src/workspace/live-view.mjs:500,527,537`: snapshot is excluded from non-empty grouping; compact cards suppress media.

### P2-04: Same Show raw scan checkbox state can mean different physics

- Steps: load RM02, inspect its initial checked Show raw scan control; turn it off then on.
- Expected: the same checked state corresponds to the same collision state.
- Actual: initially checked with `room.collision.enabled=false`; after off/on it is checked with `enabled=true`. There are 63 proxy boxes. The same-looking view can therefore have different collision behavior depending on interaction history.
- Receipt: `R:room-raw-collisions-toggle`. Actual collision was independently exercised in `R:room-collision-wall-result` and the exported SIMULATED traces. No metric calibration is claimed.
- Likely fix: `Build/web/src/lab-editor/LabEditor.jsx:209,509-510,615`: independent backdrop state versus collision enabled state.

### P2-05: Room tool selection is discarded by tab switching

- Steps: Room -> Mark the A4 sheet -> Objects -> Room.
- Expected: tool selection and any in-progress clicks remain until canceled or completed.
- Actual: pressed changes `true` to `false`, and the tool instruction disappears. The missing sample image prevents an honest test with a real first click; loss of armed-tool state itself is proved.
- Receipt: `R:room-tool-state-before-tab`, `R:room-tool-state-after-tab`.
- Likely fix: `Build/web/src/lab-editor/LabEditor.jsx:155-159,596-612`: the conditional tab branch unmounts RoomTools and resets local state.

### P2-06: Editor has no timeline scrubber or fitted value/uncertainty card

- Steps: Play/Pause the authored ball; also open the freshly completed measured apple replay.
- Expected: scrubbable recorded timeline and a result card with the computed value and uncertainty.
- Actual: graph/time and SIMULATED labels work, but there is no slider/scrubber. Measured replay shows the tracked line/what-if caveat but no fitted value/uncertainty card, although its backend result has acceleration `-2331.0424081931556` with sigma `103.53609825678797` in px/s^2. Legacy Template trials does show its separate fitted result and 1-sigma explanation; that is not the editor result card.
- Receipt: `R:lab-play-pause-graph`, `R:measured-lab-result-gap`, `R:synthetic-trial-fit-settled`; [06-template-graph-snapshot.jpg](06-template-graph-snapshot.jpg).
- Likely fix: `Build/web/src/lab-editor/LabEditor.jsx:669-697`, replay/result integration near `loadExperiment`.

### P2-07: Workspace retains duplicate chrome and the old single-clip area

- Steps: open workspace, then scroll below Projects/Recent activity.
- Expected: one workspace bar and the new project surface, without a second legacy workspace.
- Actual: site header is above the workspace bar. The old Upload/Interview/Run/Fit/Report stages, empty viewport, "Waiting for an upload" and "No job yet" remain below the new surface. The full-window lab correctly hides site header/footer.
- Receipt: `R:workspace-home`, `R:workspace-responsive-matrix`; [01-workspace-1366-light.jpg](01-workspace-1366-light.jpg), [03-workspace-375-dark.jpg](03-workspace-375-dark.jpg).
- Likely fix: `Build/web/src/shell/PrivateWorkspace.mjs:189-200` mounts both Live.Centre and Workspace; `Build/web/src/app/SiteFrame.jsx` for the outer chrome.

### P3-01: Lab logo is text, not the pendulum mark

- Steps: open either editor context; inspect top-left badge.
- Expected: approved pendulum logo.
- Actual: orange badge containing literal "R2S", matching Koushik's reported screenshot.
- Receipt: `R:template-editor-initial`, `R:sample-room-open`; [05-template-editor-1366-dark.jpg](05-template-editor-1366-dark.jpg).
- Likely fix: `Build/web/src/lab-editor/LabEditor.jsx:567` and `.le-logo` styling.

### P3-02: Rename still uses the browser prompt dialog

- Steps: project ... -> Rename.
- Expected: in-product rename interaction.
- Actual: native dialog type `prompt`, message "Rename project". **The PATCH BFF fix works:** HTTP 200 and the new title persists.
- Receipt: `R:native-rename-prompt-proof`, `R:rename-patch`.
- Likely fix: `Build/web/src/workspace/live-view.mjs:515`. No backend rename defect reproduced.

### P3-03: Experiment card preview has no automatic tracked-path overlay

- Steps: inspect completed experiment card before saving an editor snapshot.
- Expected: preview includes the measured trajectory/path.
- Actual: type art/video/snapshot fallback only, no automatic tracked path. Fresh measured replay itself does show its line. A manually saved replay snapshot can include that rendered line, so "no path anywhere" would be false.
- Receipt: `R:project-preview-path-gap`, `R:measured-lab-result-gap`.
- Likely fix: `Build/web/src/workspace/live-view.mjs:406-411,487-501`.

### P3-04: Agent drawer has no voice control; Add does not dismiss naturally

- Steps: open Agent; inspect controls. Open Add, press Escape, then tap blank canvas.
- Expected: voice input in the drawer; menu dismisses on Escape/outside click.
- Actual: drawer has text input/Ask/suggestions but no voice button. In-app exploration left Add expanded after both Escape and outside tap; selecting an item or toggling Add closes it.
- Receipt: `R:lab-agent-drawer`, `R:in-app-browser-exploration`.
- Likely fix: `Build/web/src/lab-editor/AgentPanel.jsx`; `LabEditor.jsx:625-634` for menu dismissal.

### P3-05: Workspace has a narrow-screen horizontal overrun

- Steps: workspace at 375 px, light or dark, collapsed rail.
- Expected: project grid remains within the viewport.
- Actual: document width 380 px, with project-grid/card right edges at 380; horizontal overflow is hidden, clipping the overrun. Vertical scrolling still reaches the bottom.
- Receipt: `R:workspace-responsive-matrix`; [03-workspace-375-dark.jpg](03-workspace-375-dark.jpg).
- Likely fix: `Build/web/src/workspace/workspace.css`, `.lv-pgrid`/card min-content sizing and the rail/centre width calculation.

## Requested-check verdicts

PASS means observed behavior, not merely matching source. NOT RUN is not PASS. A known gap marked FAIL means it was confirmed.

| Item | Check | Verdict | Receipt / limitation |
|---|---|---|---|
| 1 | Prompt editing | PASS | `R:home-prompt-draft`; draft cleared, not sent |
| 1 | Attach picker successful upload | NOT RUN | Disabled by real 0/20 quota; fresh sign-up protect-check failed |
| 1 | Drop stages a real public MP4 and Remove clears it | PASS | `R:home-drop`; upload not submitted |
| 1 | Recommended Spark standard / Cheapest Spark contributor / Fastest Muse Open | PASS | `R:model-picker`; relative low/medium/high bars, no Sol or numeric bar scores |
| 1 | Contributor warning and model persistence | PASS | `R:contributor-consent`, `R:fastest-persisted`; Standard restored |
| 1 | Both mode cards answer the right first question and show filming tips | PASS | `R:room-flow-settled`, `R:experiment-first-question`; real project POST 201 |
| 2 | Preview fallback, Ready/Empty status and relative time | PASS | `R:project-previews`, `R:ready-project-snapshot-card`; snapshot-only defect P2-03 |
| 2 | Rename through PATCH | PASS | `R:rename-patch` 200; native prompt remains P3-02 |
| 2 | Project-card Download execution | NOT RUN | Available account's ready projects reference jobs whose source files have no project_id; their menus have no Download. No upload capacity to create a file-backed project |
| 2 | File-menu Download and BFF range stream | PASS | `R:file-download`: 410461 bytes, HTTP 206 bytes 0-1023/410461 |
| 2 | Delete confirmation and Cancel preserve project | PASS | `R:delete-confirm-cancel`; native confirm, GET remains 200, no DELETE sent |
| 2 | Confirmed permanent deletion | NOT RUN | Waiting for Koushik's action-time approval for only the newly created QA project |
| 3 | Files list, upload limits text, loaded preview | PASS | `R:files-limits-storage`, `R:file-preview-loaded`: 1280 x 720, duration 6 s, readyState 4 |
| 3 | Rail storage meter | PASS | `R:storage-meter-expanded`; visible in expanded sidebar, 1.2 MB/1.0 GB and real quota |
| 4 | Progress pop-up during a real measurement | PASS | `R:real-job-progress-files`, `R:real-job-progress-home`; POST 202, "Processing 1 item", hosted SAM tracking; [04-real-job-progress.jpg](04-real-job-progress.jpg) |
| 4 | Private GPU red/sleeping state | PASS | `R:gpu-live-observation`: API red, queue_length 0, UI "GPU sleeping Queue empty" |
| 4 | Live yellow/green transitions and sleep countdown | NOT RUN | Hosted measurement did not wake Modal; no second job to manufacture states. Local mapping/countdown tests passed, not live proof |
| 5 | Duplicate site/workspace chrome and legacy single-clip view absent | FAIL | P2-07 |
| 5 | Rename is in-product, not browser prompt | FAIL | P3-02 |
| 5 | Automatic tracked experiment card preview | FAIL | P3-03 |
| 6 | Full-window editor hides site header/footer | PASS | `R:lab-responsive-matrix`: fixed viewport-sized editor in both sources, all six display variants |
| 6 | Top bar, Objects/Room tabs, floating transforms, illustrated Add/Templates, Properties, Agent drawer | PASS | `R:template-editor-initial`, `R:lab-add-menu`, `R:lab-add-ball`, `R:lab-agent-drawer`; mobile limitations P2-02 |
| 6 | Live graph and honesty chip expansion | PASS | `R:lab-play-pause-graph`, `R:lab-honesty`; labels retained |
| 7 | Add/move/rotate/resize/delete and undo/redo, editor sandbox AND RM02 | PASS | `R:lab-rotate-gizmo`, `R:lab-move-resize`, `R:lab-undo-redo`, `R:lab-delete-undo`, `R:room-transform-history-roundtrip` |
| 7 | Play/Pause/Reset | PASS | `R:lab-play-pause-graph`, `R:lab-reset`, `R:room-collision-drop`, `R:room-collision-wall-result` |
| 7 | Actual room collisions | PASS | Exported SIMULATED zero-gravity wall probe bounced before the actual proxy face. Scale unverified; not a calibrated room measurement |
| 7 | Show raw scan toggle | PASS | Control works; state/physics inconsistency is FAIL P2-04 |
| 7 | Mark A4 end-to-end | NOT RUN | Sample image HTTP 500; only arming/state-loss tested |
| 7 | Add a real object end-to-end | NOT RUN | Missing sample image and no extra paid operation allowed |
| 7 | Build lab shell execution | NOT RUN | Additional hosted SAM/SF3D paid operation outside the one-job allowance |
| 7 | Scene import/export, both contexts | PASS | `R:lab-export-import`, authoritative settled `R:lab-import-settled`, `R:room-transform-history-roundtrip`; traces exported too |
| 7 | Agent suggestion selection | PASS | `R:lab-agent-suggestion-selected`; fills the input |
| 7 | Agent executes a suggestion | NOT RUN | Would add a paid model call; not sent under this run's one-job restriction |
| 7 | Legacy Template trials, fit and uncertainty | PASS | `R:synthetic-trial-fit-settled`, `R:in-app-browser-exploration`; Free fall and Projectile, no paid call |
| 8 | Pause/Export snapshot writes | PASS | `R:pause-snapshot`; owner-scoped PUT 200 and snapshot URL |
| 8 | Snapshot appears on completed-project card | PASS | `R:ready-project-snapshot-card`: loaded 640 x 689 JPEG |
| 8 | Snapshot appears for template-only project | FAIL | P2-03 |
| 9 | Approved logo instead of R2S text | FAIL | P3-01 |
| 9 | Two actual fullscreen buttons | PASS | Refuted: `R:lab-fullscreen` proves one Fullscreen and one distinct Fit view control. Fullscreen enters `.lab-editor` |
| 9 | Top bar fits 375 px without cutoff | FAIL | P2-02; horizontal scrolling is a workaround |
| 9 | Timeline scrubber and value/uncertainty result card | FAIL | P2-06 |
| 9 | Voice in Agent drawer | FAIL | P3-04 |
| 9 | Room tool state survives tabs | FAIL | P2-05; a real first-click state could not be tested without a view image |
| 9 | Deleting project removes snapshot bytes | NOT RUN | DEV snapshot filesystem not inspected in this UI QA; source-only cleanup gap below, not a claim about observed disk contents |
| Both | Light/dark at 1366, 1920, 375 | PASS | 6 workspace + 12 editor layout observations. `R:room-loaded-responsive-recheck` additionally verifies actual RM02 data loaded in all 6 variants |
| Both | No vertical scroll trap | PASS | Workspace reaches its bottom; Add menu reaches Templates; editor intentionally fixed, not a long document. Horizontal clipping defects remain |
| Both | No visible em dashes in checked states | PASS | Matrix DOM text scans and tested trial/replay text. Untested model replies not covered |
| Both | No console errors | FAIL | `R:console-network-summary`: natural RM02 image HTTP 500; old test-file thumbnail 404/500 and missing report 404 also observed |
| Both | No uncaught page JS errors | PASS | None captured. Initial rapid reload sweep had two PLY 401s; subsequent settled six-variant RM02 recheck loaded all six successfully |

### Snapshot deletion: source evidence, not runtime disk proof

`Build/api/storage/files.py:286-292` deletes the project row and clears file associations but never removes `_snapshot(owner, project_id)` (`files.py:237-238`). This is a concrete missing cleanup path in the checked-out implementation. A post-delete GET 404 would only prove access denial, not physical erasure. DEV disk retention therefore remains NOT RUN, even if a disposable-project delete is later authorized.

## Spend and verification

- Exactly one live measurement job, no retries: [PAID_CALLS.md](PAID_CALLS.md). API result reports **120 frames, USD 0.024**. Hosted SAM 3.1, no Modal job. No paid agent, real-object, shell or room build call.
- Existing targeted tests: **20 passed, 0 failed**. These include GPU mapping/countdown and editor source contracts; passing those tests did not hide the browser defects above.
- No build: no product source changed. No production/judging deploy, credentials, billing, private clip/room access, or public submission.
- Test-created projects are named `N57 QA room`, `N57 QA measured apple`, plus the empty experiment created by the mode card. Automatic Pause/Export also updated the test account's seeded sample-card snapshot. Existing projects/files were not deleted; reconstruction/measurement source data was not edited. Model selection restored to Standard. Screenshots remain local-only.
