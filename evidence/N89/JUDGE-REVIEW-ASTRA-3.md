# Real2Simulation: strict round-three review

**65.75/100 (6.575/10), up from 61.0.** Reviewed 2026-11-04, main `c378d71d`, against https://real2simulation.rookiecoders.tech. Same rubric; average recorded-voiceover video assumed, not watched. This is an evidence-based improvement, not a reward for following my previous suggestions.

## Scores

| Criterion | Weight | Round 2 | Now | Weighted /100 |
|---|---:|---:|---:|---:|
| Impact | 30% | 5.5 | **5.5** | 16.5 |
| Meta AI tooling | 25% | 7.5 | **8.0** | 20 |
| Technical depth/execution | 20% | 6.0 | **6.5** | 13 |
| Demo | 25% | 5.5 | **6.5** | 16.25 |
| **Total** | | **61.0** | | **65.75** |

**Impact:** The demonstration is more usable, but it still establishes neither learning improvement nor repeat demand. One uncalibrated stock-video example and a simulation playground are a credible educational prototype, not yet proof of a valuable classroom workflow.

**Meta tooling:** The recorded Muse request, tool sequence and numerical reply make orchestration tangible alongside real SAM tracking. This is clearly beyond a chatbot wrapper. However, the Muse example is a separate synthetic drop, not the agent completing the featured ST03 workflow; the page currently blurs that distinction.

**Execution:** Browser-only fitting and pre-impact selection work, and the furnished template now actually loads. Credit is warranted for closing real integration gaps. Mobile scene controls, guest-copy continuity, malformed-link recovery and calibration guidance remain materially unfinished.

**Demo:** I ran the template and obtained approximately -9.81 m/s², loaded ST03, and ran it with changed gravity. The real-to-simulation idea is now demonstrable rather than merely described. Mobile visitors cannot access that gravity change, and an average video still leaves the story short of a compelling finalist presentation.

## Verification and boundaries

- The in-app browser became available after the requested wait. The template showed **38 objects**, resolving the previously observed four-object mismatch in this session. Play → Pause → Fit returned **-9.8100163 +/- 0.0000022 m/s²**, explicitly SIMULATED, using 76 pre-impact samples.
- ST03 loaded at gravity y = -2.33. Desktop editing to -9.81 and Play worked. This is a nominal-scale simulation, not measured terrestrial gravity or independently validated prediction.
- Anonymous HTTP checks: all primary pages, requested odd URLs and library manifest returned 200. All **40 distinct anchor/image targets extracted from the four public HTML pages** returned 200; no broken target found in that scope. README local Markdown targets existed. This does not cover every client-generated link.
- Landing/library had no horizontal document overflow at **320, 375 and 768px**. A 375px editor screenshot and accessibility state confirmed the missing gravity controls. Four public HTML bodies and hydrated landing/library contained **zero em dashes**.
- Featured-result/transcript equality and template/replay tests passed. A direct local run of the browser's Rapier implementation also returned -9.81001634 from the raw drop trace. Test count itself earns no points.
- No sign-in was performed, but the browser already exposed “Private workspace.” Thus browser interactions are not a clean guest-session test. Anonymous HTTP and source inspection establish the guest-path findings below; no copy/save, agent message, upload or paid call was performed.

## Defects found

Severity: **P1** blocks a central task or can mislead a core result; **P2** significant usability/correctness; **P3** polish/documentation. “Source” means the mechanism was inspected, not a live side effect performed.

File aliases, all relative to this checkout:

- **E:** `Build/web/src/lab-editor/LabEditor.jsx`
- **C:** `Build/web/src/lab-editor/lab-editor.css`
- **M:** `Build/web/src/workspace/measure.mjs`
- **F:** `Build/web/src/app/(public)/home/FeaturedRun.jsx`
- **L:** `Build/web/src/app/(public)/library/LibraryClient.jsx`
- **G:** `Build/web/src/app/(public)/guide/guide-data.mjs`

1. **P1, E/C: mobile gravity editing is unreachable.** Repro: open `/lab?editor=1&sample=st03` at 375px. No Gravity inputs appear. CSS hides `.le-right` when `data-sheet='closed'`; that sheet opens only for an object selection or Agent. Object selection shows object properties, not Scene gravity. Deselecting closes it again. There is no Scene-settings opener. Confirmed live and in source; affects widths below 900px.

2. **P1, G plus `Build/pipeline/live_experiment.py`: calibration instructions describe a different operation from the implementation.** Repro: follow the experiment advice to put a ruler/A4 sheet in frame and “Give a known size ... to get metres.” `analyse()` divides that entered length by the tracked object's median box size, not the reference ruler's pixel length. Supplying the ruler length for a tracked apple can therefore produce a wrong metric scale. Source-confirmed; no upload performed. The guide must say to supply the tracked object's own diameter/size unless separate-reference calibration is implemented.

3. **P2, E: guest copies lose non-template edits across authentication.** Repro path: signed-out ST03 replay → change gravity → Make a copy → authentication round trip. The 401 handler stores pending edits only when `origin.kind === 'template'`; a sample or imported scene is not preserved. Returning reloads the original sample. Source-confirmed; authentication/copy deliberately not executed.

4. **P2, E: malformed links lack useful public recovery.** `/lab?editor=1&sample=x` silently becomes an empty lab with “Add an object, then press Play,” without identifying the bad sample. `?template=nope` says “Pick Blank lab or Physics lab from the workspace,” without public template links. Both confirmed live. `?project=garbage` correctly returned “Saved lab not loaded: project not found” in the existing session; its empty editor likewise offers no direct recovery action. Anonymous project access should remain protected.

5. **P2, F: a separate synthetic agent demonstration reads as step five of the real run.** Repro: read “One real run, start to finish” through “5. Muse runs the lab for you.” The displayed request is a new 5cm-ball/1.2m synthetic drop, not ST03. Separately, “The agent kept the 19 frames” attributes deterministic `moving_segment()` selection to the agent. The recordings are genuine; their causal relationship is misleading. Verified from the rendered copy and source records.

6. **P2, M/E: the replay baseline omits the fitted horizontal acceleration.** Repro: compare ST03's fitted x trajectory with `trajectoryScene()` plus `loadSample()`. Both axes were fitted quadratically, but only vertical acceleration is applied; initial position is the first noisy observation rather than the fitted intercept. The current setup predicts terminal x about **-0.01654** versus the final dot **-0.003** in nominal scene units. This is an alignment defect, not a physical-accuracy claim. The regression checks only terminal y within 0.03, so it misses this mismatch. Locally reproduced from the committed data.

7. **P3, E: Reset contradicts the still-visible measured result.** Repro: ST03 → Play → Reset. The message becomes “Everything here is SIMULATED,” while the measured track graph and measured fit remain. Confirmed live. The initial nominal-scale explanation also disappears on Play/Reset; keep provenance attached to the specific layers instead of a transient whole-scene statement.

8. **P2, L: a stalled manifest request has no bounded recovery.** Repro condition: `/api/library/manifest` never settles. The fetch has no timeout and “Loading library…” persists indefinitely. A rejected request has fallback copy but no Retry control. Source-confirmed failure path, not an outage observed today.

9. **P3, L: empty catalog recovery is a no-op.** Repro condition: a valid manifest with `demos: []`. The UI says “No clips match” and offers “Clear filters”; clearing cannot create entries. Distinguish an empty catalog from a filter mismatch and link to the working template. Source-confirmed, not the current live manifest.

10. **P3, G: unsupported pendulum fitting is softened to “less reliable.”** Repro: compare guide section 6 with `live_experiment.py`, which explicitly reports no pendulum model and no period/g. Tracking may work; fitting support should be stated separately. The old 2330 +/- 100 guide example also differs from the new featured +/-110 result; identify it as a different snapshot or update it.

11. **P3, README.md: stale evidence scope.** “All numbers live in BENCHMARK.md” and blanket “Meta dollar cost is UNAVAILABLE” no longer describe the public N07 run and its price-derived cost estimate. Distinguish old benchmark availability from the newer estimate; do not call an estimate a reconciled bill. Three judging-gate bullets contain em dashes, contrary to the project's visible-text rule. These are not a major score deduction.

12. **P3, L: stale scope footer.** The live library ends with “accepted synthetic traces ... no raw media or real-scene physics,” despite the real-run panel and extracted stock frames above. Scope this sentence to the synthetic catalog, not the entire page.

No P0 security/data-exposure defect was established. The generic application error boundary already provides a library fallback; I did not count an imaginary missing error boundary. Empty blank labs appropriately disable Play until an object is added.

## Top eight fixes by expected score gain/hour

Estimates are subjective weighted points out of 100, overlapping and not guaranteed. Small copy-only fixes do not earn implementation-sized credit.

| Rank | Concrete change | Time | Gain/hour |
|---|---|---:|---:|
| 1 | **E/C:** add an always-reachable Scene/Gravity sheet opener, independent of selection and Agent; test 320/375/768px. | 30m | ~3 |
| 2 | **G**, `Build/web/src/workspace/live-view.mjs`: require the tracked object's own known dimension; explicitly separate room A4 calibration and unsupported pendulum fitting. No new calibration system tonight. | 30m | ~2 |
| 3 | **E:** preserve validated pending scene/name/source context for every guest copy, not just templates; restore without automatically creating a project. | 45m | ~1.7 |
| 4 | **E:** validate sample/template/project selectors and show direct public “Physics lab,” “Blank lab,” and “ST03 replay” recovery links. Preserve auth boundaries. | 30m | ~1.5 |
| 5 | **F/E/L/README.md:** separate the two recorded examples, correct frame-selection attribution, persist layer-specific units/provenance, and reconcile scope/cost copy. | 30m | ~1 |
| 6 | **`media/demo/voiceover.md`** (new), `media/capture/S24e/capture.mjs`, **README.md:** script one question → real track → fit → replay → changed outcome; publish the finished link only when available. Keep the assumed average production quality. | 60m | ~1 |
| 7 | **M/E**, `tests/web-private/featured-run.test.mjs`: initialize the baseline from both fitted axes and intercepts; compare the full timed path, not only final y. Keep physical gravity distinct from image-plane fitted acceleration. | 60m | ~0.75 |
| 8 | **L:** add bounded loading, Retry, and a distinct zero-entry state with a working-template link. Retain the featured static result during catalog failure. | 45m | ~0.7 |

Only this report was written. No paid inference, account changes, saved copies or production changes. Not checked: a fresh signed-out browser, authenticated upload/reconstruction, actual video, or every device/browser. The remaining copy-loss and network-failure paths are source findings, not claimed end-to-end reproductions.
