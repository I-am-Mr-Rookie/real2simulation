# N60: N58 DEV re-check

QA report complete; verification is limited as stated below. No application code changed.

## Method and boundaries

- DEV: https://real2simulation.up.railway.app, 2026-11-02. Deployment revisions in the dispatch were not independently attested.
- Requested in-app browser failed once with the exact error `Browser is not available: iab`. Used the worker-contract fallback: headed Playwright Chromium, with incremental click/type/scroll/resize actions and visual screenshot inspection. This is **not** an in-app-browser verification.
- Signed into the existing Clerk DEV fixture from N46, not Koushik's account. No private owner project, prohibited room, or N06 clip was opened. Account menu was inspected only; no settings or sign-out action used.
- Checked 1366 x 900 and 375 x 850; additionally checked the Add menu at 375 x 667. Switched Light/Dark using the visible Colour theme control, not injected theme attributes.
- Free actions only: existing sample/result reads, local simulation, synthetic trial and CPU fitting, one new test project, its rename and preview snapshot. No uploads, paid model calls, measurements/tracking jobs, room builds, object reconstruction, agent turns, microphone/transcription, deploy or purchases.
- Screenshots remain local and uncommitted beside this file. The new test-only project `17f7acaaed9945aab6b782b3c93c91cc`, **N60 QA snapshot-only lab**, remains in the DEV fixture account. It was not deleted under the no-destructive-actions boundary.

## N58 fixes, one line each

`CONFIRMED` means the specified visible behavior was observed on DEV, not every backend/local-test claim in N58. An unperformed check is not honestly classifiable as NOT FIXED.

| N58 fix | DEV result and observed evidence |
|---|---|
| P2-01 | **CONFIRMED, visible path:** seeded RM04 classroom point cloud and real classroom view PNG render; image reports 518 x 294 and both picking controls become enabled after load. No missing-image error. Archive hash, legacy repair and missing-user-archive behavior were not tested on DEV. |
| P2-02 | **CONFIRMED:** phone toolbar wraps inside the viewport; Add menu scrolls to Templates at both 375 x 850 and 375 x 667, Light and Dark. Template trials is reachable, not clipped by the tool container. |
| P2-03 | **CONFIRMED:** new snapshot-only N60 project appears in the main grid, with its image and Saved lab status, without Show empty. Its Open action is separately broken, F02 below. |
| P2-04 | **CONFIRMED:** raw collisions initially unchecked; hiding then showing the scan leaves collisions unchecked; enabling collisions leaves visibility checked. Restored collisions off. This checks controls/state, not physical collider accuracy. |
| P2-05 | **CONFIRMED:** one unsubmitted A4 marker and pressed A4 tool survive Objects/Room switches and panel collapse/reopen. No second point, calibration or real-object step submitted. Different-room-ID reset was not tested. |
| P2-06 | **CONFIRMED:** existing recorded apple slider seeks index 4 to 0.167 s; graph marker/time update while paused. A local simulated trace also seeks index 5 to 0.042 s and CPU Fit trace returns SIMULATED acceleration with +/- uncertainty and covariance/model caveats. Recorded fit shows 2330 +/- 110 px/s^2, 1 sigma, scale-unverified and playback-clock caveats. Phone value visibility remains poor, F03 below. |
| P2-07 | **CONFIRMED:** one visible workspace header; its Colour theme and actual Clerk menu work, including visible Manage account/Sign out choices. Advanced single-clip tools starts folded and opens/closes while retaining the tools. No account action executed. |
| P3-01 | **CONFIRMED:** editor uses the illustrated pendulum mark, not R2S text, in both Light and Dark. |
| P3-02 | **CONFIRMED:** Rename opens inline input with Save/Cancel, blank Save keeps the input and Enter a project name error, Escape cancels without a dialog; N60 title saved and persisted across navigation. Backend-error retention was not deliberately fault-injected. |
| P3-03 | **CONFIRMED, available safety paths:** saved snapshots take precedence over stored paths. No fabricated overlay was shown on another video. The sample's legacy relative path is hidden by its valid snapshot. ST03 has a stored frame track but its matching file has no project association, so its card has no preview at all, F04 below. A visible legacy-plot card and a rendered matching-source frame overlay were not available for full visual confirmation. |
| P3-04 | **CONFIRMED, UI only:** editor Agent drawer exposes Voice; Add closes on Escape and outside-canvas click. Real recording, permissions, WAV/transcription and microphone release were not exercised because this run excludes those calls. |
| P3-05 | **CONFIRMED:** at 375 px the prompt picker truncates, typed text remains in its card, and Send remains visible; no horizontal page overflow in checked Light/Dark workspace or measured replay. No typed prompt was sent. |
| Snapshot deletion | **NOT VERIFIED:** human UI cannot establish removal of underlying image bytes/MIME sidecar. No deletion or remote filesystem inspection performed. N58's local assertion is not DEV evidence. |

## New findings

No P1 observed within these free paths. These are QA findings only, not implemented repairs.

### F01, P2: classroom room card opens only the apple result

1. Sign into the DEV fixture and click **classroom room and falling apple**, shown with a Room lab icon and a classroom snapshot.
2. The URL remains the workspace. Recent activity loads **SAMPLE (RECORDED): falling apple**, with only **3D replay, redo with changes**.
3. That action opens the experiment replay, not the room. No room choice is offered on the card or its Open menu.

The sample room itself works when reached directly at `/lab?editor=1&room=e704985d4073435fb816941a6ab12e82`; that URL was obtained from the sample metadata loaded by the page, not from a private project. Ordinary card navigation does not expose it.

Likely files: `Build/web/src/workspace/projects.mjs:33` (`groupStatus`, newest-job selection) and `Build/web/src/workspace/live-view.mjs:474-482` (`ProjectCard` single Open destination). The sample room list row lacks a created/created_at timestamp, while its companion experiment has created, so the experiment wins the status selection.

Local screenshot: `sample-card-opens-apple-not-room-1366-light.png`.

### F02, P2: Saved lab cannot reopen its editor

1. Create an experiment project through the free mode card, rename it **N60 QA snapshot-only lab**.
2. Visit `/lab?editor=1&project=17f7acaaed9945aab6b782b3c93c91cc`, run/pause a local simulated scene and wait for the preview save. Observed snapshot PUT returns 200.
3. Return to workspace. The main-grid card correctly says **Saved lab** and shows a snapshot.
4. Click the card (or its Open menu). It opens the generic agent drawer and stays in workspace; no editor opens. Reproduced at 375 and 1366 px.

Likely file: `Build/web/src/workspace/live-view.mjs:478-482`. The editor href requires ready status plus a job ID. Snapshot-only saved status has no job, so Open falls through to openAgent rather than a project editor route. This is distinct from N58's repaired visibility/status.

Local screenshots: `snapshot-only-card-375-dark.png`, `snapshot-only-open-opens-agent-375-dark.png`, `snapshot-only-open-opens-agent-1366-light.png`.

### F03, P3: phone trace seeking hides the actual numerical reading

1. Open the existing recorded apple replay and pause/seek the Recorded trace slider.
2. At 375 px the time and graph marker update, but the value caption is entirely absent. At index 4 the DOM caption is **Tracked object reading (px): -49.500 at t = 0.17 s. MEASURED**, but its computed display is none and its box is zero-sized.
3. Desktop also ellipsizes the caption, with no title exposing the full text. A first-time phone user cannot read the selected y value or its MEASURED label from the graph.

Likely file: `Build/web/src/lab-editor/lab-editor.css:70,111`; phone media rule hides `.le-graph figcaption`. Keep a compact wrapping/stacked readout rather than removing it.

Local screenshots: `recorded-seek-375-light.png`, `recorded-seek-1366.png`.

### F04, P3: existing ready ST03 experiment has no video or track preview

1. In the DEV fixture workspace, inspect **Experiment: ST03-trim.mp4**, marked Ready.
2. Its card is just a generic graph icon, unlike the snapshot cards. There is no trajectory or video preview.
3. The page's loaded metadata includes a frame-space track for file `42fcf3760e5742efa729285887bbbe13`. Its files response contains that exact video as ST03-trim.mp4, but with project_id null. The experiment references the same file ID.

Likely file: `Build/web/src/workspace/live-view.mjs:519-520`. Project-card files are selected only by file.project_id, ignoring a room/experiment's file_id. This affects pre-existing/detached-source data; not a newly uploaded-video test. It must not be fixed by overlaying a path on an unrelated file.

Local screenshot: `fresh-session-cards-1366-light.png`.

## Numbers, text and remaining limits

- Quota display was consistent with the loaded API: 20 used, 0 of 20 uploads remaining. No inference that the account was newly empty.
- Synthetic template trial's actual reveal was 9.810 +/- 0.0000737 m/s^2, explicitly simulated, with 1 sigma and the independent position/time uncertainty model. These are app/fitter outputs, not physical accuracy claims.
- No em dash found in checked workspace, room, replay or synthetic-trial visible text. No claim about unchecked pages or untriggered errors.
- The long session saw one sample snapshot 500 and one older N57 snapshot 404. Both loaded normally at natural width 640 in a fresh signed-in session, with no failed responses there. Treat these as transient observations, not a reproducible ranked defect. No JavaScript page error was captured in the monitored session. Empty agent-report GETs returned 404; no report had been generated.
- Room scale remains unverified and geometry/gravity remain MODEL-ESTIMATED. No known-size measurement, physical calibration, hosted-model readiness or paid end-to-end claim is made.
- Backend deletion cleanup, the unavailable in-app browser, actual voice behavior and the P3-03 fixture permutations above remain unverified. No source tests/build were run because no application source changed.
