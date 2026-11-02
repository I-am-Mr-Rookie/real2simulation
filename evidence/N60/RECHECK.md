# N60: actual in-app-browser DEV re-check

This reissued UI-only pass supersedes the previous headed-Chromium report. No Chromium or application-code change in this pass. N61 owns the earlier F01 to F04; those are not re-reviewed or certified here.

## Scope and evidence

- Window: 2026-11-02 14:37:36 to 15:07:36 UTC; cutoff 15:02:36 UTC.
- DEV: https://real2simulation.up.railway.app. Controller supplied web deployment 5ad1fa2f at main f7cf60ae; no independent deployment attestation.
- Actual ChatGPT in-app browser, desktop 1366 x 900 and phone 375 x 850. Clicked controls, typed without sending, scrolled with wheel input, resized, switched Light/Dark, and inspected screenshots.
- Signed into the existing N46 fixture n43-mvym1kik+clerk_test@example.com with its approved test code. No new account, owner session, private owner project, prohibited room or N06 clip used. Fixture clarification caused no delay.
- Existing data only. Quota showed 0 of 20 uploads left; no upload attempted. Existing N60 snapshot-only project, classroom sample and ST03 result used. No new test project created in this pass.
- Free synthetic trial, local physics and CPU fit only. No paid model, tracking/measurement job, room build, real-object operation, agent turn, microphone/transcription, sharing, account setting or deployment action.
- Screenshots are local-only, uncommitted JPEGs named iab-*.jpg beside this report. Earlier PNGs are not evidence for this pass.
- Theme restored to its original System choice; temporary viewport override reset. Local-only simulation changes were discarded by leaving the editor.

## N58 re-check, one row per fix

CONFIRMED UI is scoped to the observed visible behavior, not all backend assertions in N58. PARTIAL does not mean a demonstrated regression.

| N58 fix | Actual in-app-browser result |
|---|---|
| P2-01 | **CONFIRMED UI:** classroom point cloud and classroom PNG load at both widths, image natural size 518 x 294. A4/object controls become available with the image. Scale unverified and MODEL-ESTIMATED gravity with +/- 0.3477 deg remain visible. Archive hash, legacy repair and missing-user-archive backend cases not exercised. |
| P2-02 | **CONFIRMED UI:** phone toolbar wraps. Add sits above the room sheet and scrolls to Template trials; desktop and phone Dark screenshots show the bottom reached by wheel scrolling. No menu clipping like the original finding. |
| P2-03 | **CONFIRMED UI:** pre-existing N60 QA snapshot-only lab appears in the main grid with its thumbnail and Saved lab status, without Show empty. Did not test its Open destination, which belongs to N61. |
| P2-04 | **CONFIRMED UI:** loaded room raw collisions initially off. Hide/show scan does not enable collisions; enabling collisions leaves visibility on. Restored scan visible and collisions off. Checked phone and desktop controls; physical collider accuracy not tested. |
| P2-05 | **CONFIRMED UI:** one unsubmitted A4 marker and pressed tool survive Objects/Room tab changes and panel collapse/reopen at phone width; repeated marker/tab retention on desktop. No second mark or calibration request submitted. No second room ID used. |
| P2-06 | **CONFIRMED UI:** existing ST03 recorded trace seeks by keyboard to sample 4, 0.167 s. Local simulated ball trace seeks to sample 5, 0.042 s; paused Fit trace works. Existing result displays 2.71 +/- 0.42 m/s^2, 1 sigma, scale-assumed and playback-clock caveats at both widths. Local fit displays SIMULATED and its covariance/model caveat, not a calibrated gravity claim. |
| P2-07 | **CONFIRMED UI:** single visible workspace header with palette and actual Clerk account menu. Menu shows fixture email, Manage account and Sign out; no account action taken. Advanced single-clip tools starts folded and opens/closes at both widths with stages intact. |
| P3-01 | **CONFIRMED UI:** illustrated pendulum brand mark appears in the editor in Light and Dark, not R2S text. |
| P3-02 | **CONFIRMED UI, read-only subset:** existing N60 test project's Rename opens inline with Save/Cancel. Blank Save retains input and Enter a project name error; Escape and Cancel dismiss correctly. Checked desktop and phone. No valid title change or deliberate backend error was submitted, so persisted-save/API-error retention is not newly certified. |
| P3-03 | **PARTIAL:** normal ST03 card shows its frame-space track on the ST03 video at desktop/phone; saved N57/sample thumbnails take precedence. No fabricated overlay observed. Legacy plot-only and wrong-source fixtures were not manufactured or mutated; these branches are not fully certified. N61's separate F04 regression is not re-reviewed. |
| P3-04 | **PARTIAL:** editor Agent exposes Voice. Add closes on Escape and outside click, including phone. Real recording, WAV/transcription, permission failure and mic release untested under the no-call/read-only scope. |
| P3-05 | **CONFIRMED UI, prompt card:** typed phone prompt and truncated model pill stay inside the card; Send remains visible in Light/Dark, with no horizontal document overflow. The expanded model picker has a separate new defect, F06. |

Snapshot disk deletion/MIME cleanup remains outside this read-only UI pass and unverified. No deletion performed.

## New findings only, not N61 F01 to F04

No new P1 found in the exercised free paths.

### F06, P2: phone model picker is behind the permanent rail

1. At 375 px, close the expanded sidebar, then click the Muse Spark model pill in the workspace prompt.
2. The model dialog opens across x=12 to x=348, but the permanent left rail covers its left portion up to about x=50.
3. Model names, Standard/Contributor labels, Intelligence/Speed/Cost labels and leading pros/cons text are visibly cut off. Reproduced in Light and Dark. The page has no horizontal overflow, so a document-width check misses this.
4. Desktop picker is readable. No model choice was changed.

Likely file: Build/web/src/workspace/workspace.css:294,631,744. Mobile rail is z-index 31; fixed .lv-pickpop is z-index 30 and starts at .75rem instead of respecting the rail or rendering above it. ModelPicker is in Build/web/src/workspace/live-view.mjs:400.

Local screenshots: iab-model-picker-375-light.jpg, iab-model-picker-375-dark.jpg, iab-model-picker-1366-dark.jpg.

### F05, P3: replay summary promotes an assumed size to a known size

1. Open the existing Experiment: ST03-trim.mp4 result, then 3D replay, redo with changes.
2. Workspace correctly labels scale assumed (user size): apple width assumed for QA 8 cm. Editor fit footer also correctly retains scale assumed (user size).
3. The editor's large scene summary instead says Track MEASURED in metres from your known size. The input is an assumption, not a verified known size. This is contradictory provenance copy, not evidence that the numerical fitter is wrong.
4. Seen at desktop; the same summary exists in the phone view, where the sheet can obscure it.

Likely file: Build/web/src/workspace/measure.mjs:152,160. trajectoryScene chooses the stronger wording solely from trajectory.unit === m, without inspecting the scale provenance. Preserve the assumed-scale caveat in the summary.

Local screenshot: iab-measured-replay-1366-light.jpg, also iab-measured-replay-375-light.jpg for the narrower layout.

## Numbers and limits

- Synthetic Free fall trial actually returned 9.810 +/- 0.0000737 m/s^2, labelled simulated, 1 sigma, with independent position/time uncertainty and not-calibrated caveats.
- Local ball trace CPU summary actually returned 2.76 +/- 0.16 m/s^2, explicitly SIMULATED and a quadratic summary not necessarily gravity or a valid model for collisions/oscillation. This trace included floor interaction, so it is not a gravity-calibration result.
- No em dash found in inspected workspace, room, recorded replay, synthetic trial or fit text. No claim about untriggered errors or unchecked pages.
- On first opening an already completed experiment, Queued/Processing briefly appeared before Done. It did not persist on repeat; no new tracking action was invoked. Treat as an unranked status-copy observation, not proof of a new paid job.
- No actual voice/transcription, destructive cleanup, physical calibration, provider-readiness or full backend regression verification. No code tests/build needed for report-only changes.
