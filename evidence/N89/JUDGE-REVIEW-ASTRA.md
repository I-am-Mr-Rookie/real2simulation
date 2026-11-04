# Real2Simulation: strict Indie-track review

Reviewed 2026-11-04, branch `run/N89-templates`, revision `2ab555c8`. Rubric: main-checkout Event Rules, lines 130–150. Evidence: source, README/BENCHMARK, HTTP responses and hydrated in-app-browser pages. Browser already had a signed-in session; only public routes were visited. Live copy changed during inspection. Average recorded-voiceover video assumed, not watched.

## 1. Scores

| Criterion | Score | Weighted points /100 |
|---|---:|---:|
| Impact | 5/10 | 15 |
| Meta AI tooling | 7/10 | 17.5 |
| Technical depth/execution | 6/10 | 12 |
| Demo | 4/10 | 10 |
| **Total** | **5.45/10** | **54.5/100** |

**Impact:** A phone-to-physics teaching tool has credible educational value. But the public experience demonstrates neither a completed student task nor a compelling advantage over an ordinary simulation playground. Room reconstruction and experiment measurement compete for attention; adoption and learning benefits remain unproven.

**Meta tooling:** SAM 3.1 tracking, Muse tool orchestration and reconstruction are meaningfully connected, not merely a chatbot wrapper (`Build/measurement/hosted_sam.py`, `Build/agent/core.py`, `Build/pipeline/live_experiment.py`). However, judges cannot readily see that chain working publicly. Model breadth alone is not a surprising capability.

**Technical execution:** Video timestamps, tracking, fitted curves, covariance and editable physics constitute substantial engineering. But live experiment fitting still explicitly lacks a pendulum model; BENCHMARK does not establish reliable held-out prediction. The observed template/project scene mismatch further weakens confidence in integration, regardless of test counts.

**Demo:** All five supplied URLs returned HTTP 200, and the editor initialized. Yet the main demo library contains only two playable synthetic traces and one practice setup, not the promised real-to-simulation transformation. An average voiceover will not compensate for an unconvincing public proof path.

**Verdict:** Ambitious implementation, weakly demonstrated product. Not finalist-ready on the evidence available; private capabilities may be stronger than this score can justify.

## 2. Highest-leverage six-hour changes

Paths below are relative to this checkout. `W = Build/web/src/`. Gains are subjective weighted percentage-point estimates, overlapping, not additive. Budget: 340 minutes implementation plus 20 minutes smoke checks. No new paid inference required; deployment needs the applicable owner approval.

1. **Expose one real result, not another simulator** (65m; +4–6). Change `W/app/(public)/library/LibraryClient.jsx` and `W/app/(public)/page.jsx`. Promote an existing approved recording/result into a featured input → tracking → fit → replay panel, reusing public `/guide` assets where necessary. Explicitly recorded, no private uploads. Judges immediately see the actual transformation.

2. **Make the template URL deterministic** (50m; +3–5). Inspect `W/lab-editor/LabEditor.jsx`, `W/lab-editor/AgentPanel.jsx`, `W/lab-editor/templates.mjs`. The live URL twice displayed “Scene loaded from the project.” and four objects; checkout specifies a furnished lab. Reconcile deployed assets and scene initialization before adding code: N89 already contains a template load guard. Verify both guest and signed-in entry.

3. **Show Meta's causal contribution** (45m; +2–4). Add a compact recorded trace beside the featured result in `W/app/(public)/library/LibraryClient.jsx`; update `W/app/SiteFrame.jsx`. Show SAM's tracked object and Muse's actual tool action/result, not model logos. Retain required Stability attribution but explain its narrower mesh role.

4. **Give the average video a complete story** (40m; +2–3). Add `media/demo/voiceover.md`; adapt `media/capture/S24e/capture.mjs`. Show one learner question, real input, extracted result, one changed parameter and the answer. Cut model-picker tours and internal-process material; mark elapsed processing rather than implying instantaneous reconstruction.

5. **Start with a runnable lesson** (35m; +1–3). Change `W/lab-editor/templates.mjs` and `W/lab-editor/LabEditor.jsx`: select one apparatus, enable its sensor and show a specific experiment instruction. First Play should produce a useful graph, not require discovering sensor settings.

6. **State who benefits** (25m; +1–2). Change `W/app/(public)/page.jsx`: lead with a concrete student/teacher task and its completed output. Replace generic illustration-led explanation with the featured real result; do not invent learning or time-saving statistics.

7. **Unify the lab entrance** (25m; +1–2). Change `W/app/(public)/lab/page.jsx` and `W/lab/LabClient.jsx`: foreground the guided 3D template; keep Mystery-g as a clearly separate challenge. Visitors should not have to infer which of two labs delivers the promise.

8. **Make library cards understandable** (20m; +0.5–1.5). Change `W/app/(public)/library/LibraryClient.jsx` and `library-copy.mjs` in that directory: use task titles and distinct previews; move machine IDs into details. Preserve essential caveats without making them the card's entire story.

9. **Finish the judge's repository entry** (20m; +0.5–1). Update `README.md`: replace stale deployment placeholders with verified live/sample links and a 60-second walkthrough. Add the video link only when available. Judges should not encounter “Judging URL: PENDING S23”.

10. **Match filming advice to supported fitting** (15m; +0.5–1). Change `W/app/(public)/page.jsx` and `W/app/(public)/guide/guide-data.mjs`: recommend a simple drop first; explain that filmed pendulum fitting is currently unsupported. Avoid leading users into an advertised experiment that cannot return its expected quantity.

## 3. Five first-minute problems

1. [Landing](https://real2simulation.rookiecoders.tech/): “Film Physics” alongside “Illustration only, not scene evidence.” Promise without visible proof.
2. [Library](https://real2simulation.rookiecoders.tech/library): “2 playable”, “1 practice setup”; all three entries SIMULATED. No public real-video payoff.
3. Library: “SIMULATED projectile: baseline-short (display-only)” reads like a fixture, not a compelling experiment.
4. [Lab](https://real2simulation.rookiecoders.tech/lab): “Set parameters and run” initially replaces the result; “Fit & reveal” is disabled. Another setup task before any reward.
5. [Template](https://real2simulation.rookiecoders.tech/lab?editor=1&template=physics-lab): “Physics lab” but “Scene loaded from the project.” and “4 objects.” In this signed-in session, the promised furnished template was not what appeared.

Not checked: paid/live uploads, actual video, guest-only browser state or simulation playback. Screenshot capture failed; visual-layout quality remains unverified. Template root cause and production revision are not established.
