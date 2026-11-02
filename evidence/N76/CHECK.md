# N76 DEV QA and guide-image audit

DEV: https://real2simulation.rookiecoders.tech. Fixture account only, in-app ChatGPT browser. Controller-declared main `d764b2ce`, API `e1546d11`, web `a4030a5d`; deployed revisions were not independently exposed/verified. Audited Nov 3 Dhaka (Nov 2 UTC).

## Requested checks
- CONFIRMED: signed-in public header at 320, 375 and 1366 CSS px has no horizontal overflow; account panel opens and identifies the fixture at every width. `header-widths.json` records DOM measurements. Screenshots were captured after dismissing the panel, with no email visible.
- CONFIRMED: home says `Imperfect inputs are welcome. Results show uncertainty and a "scale unverified" or "scale assumed" label when needed.` See `home-honesty.jpg`.
- CONFIRMED: lab Voice changes from `Voice input` to disabled `Waiting for microphone`. Stopped at permission request; did not grant microphone access, record, transcribe or send an agent turn. See `voice-permission.jpg`.
- CONFIRMED: `Add a real object` shows its click-helper when enabled; toggling off removes the helper (matching DOM count 0). No image click or reconstruction request.
- CONFIRMED: existing classroom SAMPLE opens a shell, not a point-cloud-only scene: floor, inferred walls/window openings, furniture and 23 scene objects. Room panel says SAMPLE / RECORDED, MODEL-ESTIMATED and scale unverified. It reports 0 observed walls, 4 scan-edge walls, 3 openings, 9 furniture retained and 130 detections dropped; these are UI output, not physical validation.
- CONFIRMED: four SF3D assets (`room-object-1`, `2`, `4`, `7`) render; all four GLB responses and room PLY were HTTP 200. See `sample-assets.json`. Expanded honesty contains one `Powered by Stability AI` credit, SIMULATED explanation and unverified-scale warning. See `sample-honesty.jpg`.
- CONFIRMED: Play becomes Pause and enables Reset; Reset returns t to 0.00 s and the ready/SIMULATED state. A browser-local ball with its default trajectory sensor produced the guide's SIMULATED graph; reset and navigated away without saving/exporting/fitting. Reloaded sample returned to 23 objects.
- NOT FIXED: Files at 375 px still cramps metadata into a very narrow column, wrapping `34 KB, 1.0 s, no project` almost word/character by character. Preview, Measure and actions remain present. See `files-375.jpg`.

## All 16 guide assets
| Image | Decision and live comparison |
| --- | --- |
| what-it-is.webp | Refreshed: requested post-N74 signed-in public-header baseline, same home hero and honest labels. |
| sign-in.webp | Retained, NOT REVERIFIED: visiting `/sign-in` while signed in redirects to workspace. Did not sign out or change authentication to expose the anonymous form. |
| models.webp | Retained: four model choices, tags, relative bars and Standard details match live picker. No model selection changed. |
| models-wonder.webp | Retained: keyboard-focus preview shows high intelligence, low speed, high cost and the same caveats; Standard remains selected. |
| first-question.webp | Retained: live New project panel has the same question, two options, Other field and Continue. |
| filming-tips.webp | Retained: default My experiment Continue shows the same five local filming tips. This created one empty fixture `New experiment` project, left intact; no upload or paid agent call. |
| room-tab.webp | Refreshed: old point-cloud-only screenshot is stale against the N75 shell and four meshes. |
| room-a4.webp | Refreshed: same A4 helper over the new shell; did not mark a length or change scale. |
| experiment-result.webp | Retained: existing result UI still has value +/- uncertainty, scale/playback labels, caveats and fit chart. Live stored ST03 example is 2.71 +/- 0.42 m/s^2 with assumed user size; retained screenshot's 2330 +/- 100 px/s^2 is a DIFFERENT recorded example, not this current result. No refit or measurement. |
| experiment-replay.webp | Refreshed: current replay has the wrapped, separate fit-result region below its trace. Uses the existing ST03 result and keeps MEASURED/scale-assumed warnings. |
| editor-add.webp | Refreshed: open Basics/Apparatus/Mass set menu over the new sample shell. |
| editor-play.webp | Refreshed: running browser-local simulated ball and actual sensor graph over the shell, not a fabricated trace. |
| agent.webp | Retained: idle Agent panel, Standard mode, Message, Voice, Send and Tools match live. |
| files.webp | Retained: desktop Files header, sleeping GPU indicator and Upload video match. Phone-row defect is separate. |
| storage.webp | Retained: same storage meter and quota layout; old illustrative 26 MB vs current fixture 52 MB is changing usage data, not stale UI. Alt text still describes its existing 26 MB example. |
| library.webp | Retained: live public simulated-demo filters/cards and honesty copy match. |

Six replacements preserve exact names and original dimensions. Ten others are byte-identical. `image-audit.json` records before/after hashes for replacements; `all-image-dimensions.json` checks all 16 against git HEAD. No resampling, invented UI or fabricated numbers: browser JPEG captures were exported to WebP.

## Findings, report only
- P2, NOT FIXED, Files phone layout: cramped metadata at 375 px. Likely `Build/web/src/workspace/workspace.css` (`.lv-frow` / `.lv-fname`, around 714-717), with row structure in `live-view.mjs` around 575-582.
- P2, existing quality limitation: SF3D meshes are visibly coarse/fragmented (blob/strips rather than recognizable furniture); HTTP success is not reconstruction-quality acceptance. Likely upstream crop/shape-generation/placement pipeline, not guide images.
- P3, lab honesty badge: at 1280 px the centered transform/Add toolbar overlaps the right side of the collapsed honesty badge, hiding part of the scale warning / `+1`. Expanded credit is readable. Likely `Build/web/src/lab-editor/lab-editor.css` (`.le-honesty` and transform toolbar positioning). See room screenshots.
- P3, guide copy/alt now needs follow-up outside image-only Owns: `guide-data.mjs` room intro and `room-tab.webp` alt still call the example a point cloud, while the refreshed screenshot correctly shows the shell. Do not claim copy was updated.

## Verification and boundaries
- PASS: `node --test tests/web-guide/guide.test.mjs`, 2/2 after replacements.
- PASS: `npm run build` with existing canonical environment loaded in-process; exit 0. No env values copied or printed. Next.js compiled and generated pages successfully.
- PASS: all 16 image names/dimensions unchanged; exactly 6 changed and 10 identical; `git diff --check` clean; browser error-log query returned no entries.
- No paid calls, new measurements, tracking, fits, GPU jobs, room/shell builds, deployment, push, account-setting changes, deletion, sharing, submission or private owner-project access. Anonymous sign-in form remains the explicit verification limitation.
