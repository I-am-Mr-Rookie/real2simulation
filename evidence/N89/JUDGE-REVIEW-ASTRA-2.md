# Real2Simulation: strict re-judging

**Weighted total: 61.0/100 (6.10/10), previously 54.5/100.**

Reviewed 2026-11-04 against main `469f43a4` and the supplied DEV host. Same rubric: Impact 30%, Meta tooling 25%, execution 20%, demo 25%. Average recorded-voiceover video remains an assumption, not a reviewed artifact. No bonus for internal process, test counts or labels alone.

## Scores

| Criterion | Before | Now | Weighted points /100 |
|---|---:|---:|---:|
| Impact | 5 | **5.5** | 16.5 |
| Meta AI tooling | 7 | **7.5** | 18.75 |
| Technical depth and execution | 6 | **6** | 12 |
| Demo | 4 | **5.5** | 13.75 |
| **Total** | **54.5/100** | **61.0/100** | **61.0** |

**Impact:** The students/teachers positioning and real worked example make the intended use substantially clearer. However, a stock apple clip and a generic physics lab still do not demonstrate a completed learning task, user adoption or an advantage users would repeatedly choose. Better explanation is not new impact evidence.

**Meta tooling:** Judges now see an actual hosted-SAM output, frame count, fitted result and recorded processing cost. This establishes a meaningful perception-to-analysis integration. Muse's orchestration and the room workflow remain less observable publicly; a static tracking example is useful, but not yet a surprising agent capability.

**Execution:** Reusing the existing chart machinery and enabling a default sensor improve coherence. The public fit action still crosses into authenticated workspace infrastructure, and the new instructions omit the required pause. Source changes are not proof that the previous live template mismatch is fixed. Provenance equality establishes faithful copying, not calibrated accuracy or generalization.

**Demo:** The previous central objection, no public real-video result, is materially addressed. The new panel presents frames and a readable quantitative result without an account. But “start to finish” stops before an interactive replay; the displayed what-if infers scale assuming Earth gravity rather than letting a judge change physics and compare outcomes. Average narration will help comprehension, not supply the missing interaction.

**Verdict:** A credible improvement, not a cosmetic rescore. Still below a convincing finalist demonstration: the visitor can inspect evidence more readily than complete the advertised transformation.

## What was actually verified

- Anonymous HTML fetches returned 200 for [landing](https://web-dev-cd80.up.railway.app/), [library](https://web-dev-cd80.up.railway.app/library), [lab](https://web-dev-cd80.up.railway.app/lab), [guide](https://web-dev-cd80.up.railway.app/guide) and the template URL.
- Landing/library expose the ST03 panel: 543 tracked frames, 19 selected frames, 0.70 s, **2330 +/- 110 px/s²**, $0.1086 and 40 s. These are recorded outputs, not measurements independently repeated here. The audience line, drop-first advice and 3D entry links are live.
- Source verifies readable card-title mapping, first-sensor ordering and template instructions. The featured-result equality/geometry test and template tests passed. These checks do not establish hydrated browser behavior or live inference reliability.
- `LabEditor.jsx` sends Fit trace to `/api/workspace/fit`. The proxy requires sign-in before forwarding; an anonymous GET returned **401**. No fitting POST was made. The button is disabled while playing.
- Main has a pre-existing uncommitted change in `FeaturedRun.jsx` removing a code-path suffix from copy. Live HTML still contains that suffix. It was excluded from shipped credit and left untouched.

## Top five remaining fixes, ranked by expected score gain/hour

Paths are checkout-relative. Estimates are subjective weighted points out of 100, not promises or additive forecasts.

1. **Make the public fit genuinely public.** About **45m; +2 points; 2.7/hour**. In `Build/web/src/lab-editor/LabEditor.jsx`, use existing `polyFit` from `Build/web/src/workspace/measure.mjs` for local simulated sensor traces, including its covariance and invalid-input handling. Keep private workspace authentication intact. Add the guest-fit regression in `tests/lab-editor/editor-ui.test.mjs`. A visitor should get acceleration without creating an account, not “Sign in required.”

2. **Demonstrate one actual Muse action/result.** About **45m; +1.5 points; 2/hour**. Extend `Build/web/src/app/(public)/home/FeaturedRun.jsx` with a sanitized, already-recorded Muse request → tool action → visible result. Identify deterministic frame selection as pipeline logic, not evidence of agent reasoning. Keep required Stability credit in `Build/web/src/app/SiteFrame.jsx`, but make Meta's distinct roles visible. Do not fabricate a transcript if no approved recording exists.

3. **Finish the drop lesson, not just its graph.** About **45m; +1.25 points; 1.7/hour**. In `Build/web/src/lab-editor/LabEditor.jsx`, explicitly guide Play → Pause → Fit, select ball-drop and fit only its pre-contact window. `scene.mjs` currently forwards every supplied sample; browser `physics.mjs` records ongoing motion. Validate the window against scene gravity with one regression. This avoids a confusing disabled button and a whole-collision quadratic being mistaken for free-fall acceleration.

4. **Connect the measured example to its own replay.** About **2h; +3 points; 1.5/hour**. Add a public recorded-sample entry in `Build/web/src/lab-editor/LabEditor.jsx`, reusing `trajectoryScene` in `Build/web/src/workspace/measure.mjs`; link it from `Build/web/src/app/(public)/home/FeaturedRun.jsx`. Load only the approved bundled ST03 result. Keep measured dots fixed while a simulated gravity change visibly diverges, with assumed scale explicit. The current generic-lab link does not complete that story.

5. **Make the average video show an answered question.** About **1h; +1 point; 1/hour**. Add `media/demo/voiceover.md`, adapt `media/capture/S24e/capture.mjs`, and put the finished video link in `README.md`. Follow one student question through recorded input, SAM track, fit, replay and a changed prediction. Mark processing skips. Avoid spending the three minutes touring menus or listing models.

Not checked: sign-in, paid inference, hydrated editor/playback, screenshots or the actual video. No claim that the old template-loading defect is resolved. Only this report was written; existing changes were preserved.
