# N58: N57 repairs

Scope: local source and isolated public-sample verification. No DEV deployment, owner clip, N06 data, paid model call or physical calibration was used.
N57 calls the seeded classroom RM02; its actual recorded bundle identifier is RM04.

| Finding | Change | Evidence |
|---|---|---|
| P2-01 FIXED | Seed and repair legacy sample rooms with the hash-verified RM04 reconstruction archive; regenerate the display files in the same gravity-aligned frame used by view/scaling/lifting. Missing user archives return 503, never a substituted sample. | API PNG/ownership/legacy-repair/hash tests; browser `room-view-and-tool-retention`; in-app room screenshot. |
| P2-02 FIXED | Phone toolbar wraps; Add menu is viewport anchored, above sheets, independently scrollable. Its transformed parent no longer clips it. | Browser four editor width/palette variants; in-app 375 px Add scroll reaches Templates. |
| P2-03 FIXED | A snapshot-only project is Saved lab, visible in the full card grid with its snapshot. | Status test; browser `snapshot-only-card`, real saved template snapshot. |
| P2-04 FIXED | Visibility and collision enabling have separate controls. Visibility never changes collider state; loaded raw scan collision remains off by default. | Browser `raw-visibility-and-collisions-independent`. |
| P2-05 FIXED | Room tools remain mounted across tab switches and panel collapse. A4/object controls wait for an actual loaded image. New room IDs reset state. | Browser first A4 mark plus Objects/Room switch; in-app retained first marker and pressed control. No calibration submitted. |
| P2-06 FIXED | Recorded-trace slider selects graph/time samples while paused; live simulation seeking is not implied. Paused simulated traces use the existing CPU fitter. Measured replay shows API quantity, uncertainty, unit and source/clock caveats. | Browser `template-sensor-seek`, `template-cpu-fit`, `public-recorded-experiment-fit-and-seek`; in-app measured seek to index 4. |
| P2-07 FIXED | One workspace header. Palette and Clerk account/sign-out controls move into it. Legacy tools are closed under Advanced single-clip tools; rail shortcuts expand them. | Shell tests/build, browser four workspace variants, fold open/close; actual Clerk account flow not run locally. |
| P3-01 FIXED | Reuse approved light/dark pendulum marks, not R2S text. | In-app and headed screenshots. |
| P3-02 FIXED | Inline rename with Save, Cancel, Escape and retained validation/API error. No native prompt. | Browser PATCH and persisted unique title, no dialogs. |
| P3-03 FIXED | Stored frame pixels overlay only their matching source video. Older results without frame coordinates get a separate labelled relative-path plot, never a fabricated video alignment. Saved editor snapshots still win. No new tracking call. | Owner/latest/bounds tests; actual card rendering test covers matching source, wrong source, snapshot precedence and plot fallback; browser public ST03 plot. |
| P3-04 FIXED | Agent drawer reuses the workspace WAV/transcription hook and fills text without sending a model turn. Add closes on Escape and outside click. | Offline fake-recorder test checks RIFF WAV, route, text, permission error and mic release; browser visible Voice and both dismissal paths. Real mic/transcription not run. |
| P3-05 FIXED | Grid minimums can shrink to available width; prompt picker truncates rather than pushing Send outside its card. | Browser 375 light/dark document widths; in-app light/dark inspection. |
| Snapshot deletion FIXED | Delete removes image bytes and MIME sidecar after owner validation while retaining uploaded files. | API filesystem assertion, wrong-owner denial and preserved detached upload. DEV disk cleanup not inspected. |

No feature was removed. The folded legacy area retains single-clip upload, interview, instruments, run, fit, report, provenance and scene viewer. Duplicate site navigation is hidden only on the private workspace shell, not public pages.

## Required deployment asset

Approved scope extensions: `infra/railway/dev/stage.py` and `Build/pipeline/recorded/RM04-S13l-mapanything.json`.
The existing public archive is 9,330,251 bytes, SHA-256 `1ff2069d346e751e608e0ea5034e278deed6e84d186a5475e5f56eacbb645d6f`.
It stays ignored/local; no NPZ is committed. API staging requires every manifest asset and validates hashes before creating its target. The staging regression exercises successful copy, missing archive and corrupted archive failures.

## Verification limits

These are local code/CPU/public-recording results, not authenticated DEV E2E, physical ground truth or live model readiness. Real microphone permission, hosted transcription, paid object segmentation/SF3D, lab shell generation and a known-size calibration remain untested. The relative-path fallback is not aligned to the video and says so. No provider, model routing, permission policy, credentials or spend settings changed.
