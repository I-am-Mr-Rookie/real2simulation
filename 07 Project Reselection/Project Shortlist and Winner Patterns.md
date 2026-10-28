# Project Reselection: Shortlist and Winner Patterns

Prepared October 27, 2026 (Asia/Dhaka) for Koushik Sadhak Jeet. Indie developer track, solo. Strategy only: no code, accounts, or submissions were touched.

**Status:** this is a proposal waiting for your pick. AttemptLens remains the accepted application idea. Switching projects after selection is your call; check that the Official Rules allow it.

## 000. Pivot: Measured becomes Physics Experimenter (Oct 27, proposal; awaiting approval)

> **Superseded the same day** by the full product concept, renamed **Real2Simulation**, in [08 Real2Simulation](../08%20Real2Simulation/Real2Simulation%20Concept.html) (video → 3D world → agent interview → experiment → measurement → report).

Koushik asked to rename Measured and shift it toward physics experiments reconstructed in 3D from a video.

### Name

- **Recommended: Physics Experimenter.** Tagline: *"Film any experiment. Get it back in 3D: measured, explained, simulated."* The spelling is "Experimenter"; "Experimentor" is a misspelling.
- **Avoid "Physics Professor".** It reads as an AI tutor, and simple "AI for Education" chatbots are on the guide's anti-project list.
- **Avoid "Physics Simulator" or "Experiment Simulator".** Judges would expect a simulation toy and miss the point: the product measures *real* motion. Simulation becomes a feature (the digital twin), not the name.

### Concept

A phone video of a real experiment becomes a measured 3D digital twin:

1. **Calibrate.** SAM 3.1 finds an A4 sheet on the table. With the principal point at the image centre, one plane homography gives the focal length; PnP then gives the camera pose and the table plane, so "down" and metres are known.
2. **Track in 3D.** SAM 3.1 tracks the object (ball, bob, cart) through the clip. Each mask gives a sub-pixel centre and an apparent diameter. Known object size gives depth: Z = f·D/d.
3. **Physics-constrained reconstruction (the technical core).** Monocular depth from apparent size is noisy, so the system does not trust it frame by frame. It fits a small bundle adjustment: unknown launch position, velocity, and g (plus drag or damping where needed). The fit minimises reprojection error of the centre and the size residual over every frame. The physics model *is* the 3D prior. Model choice uses AIC; uncertainty comes from the Jacobian.
4. **Digital twin.** A three.js scene shows the table plane, the camera frustum, the fitted 3D trajectory with error bands, and the real video projected alongside. Optional: SAM 3D Objects (Meta open weights, GPU on Modal) meshes the object from a keyframe so the replay uses the real object's shape.
5. **Simulate and predict.** The fitted parameters drive a simulator. The Muse Wonder agent (the experimentalist) states a prediction *before* the next trial, e.g. "launch at 30° from the same spot: it lands 1.42 ± 0.04 m away". The user marks the spot, films the throw, and the system overlays sim against reality.
6. **Report.** LaTeX report with provenance to the raw frames. The hard gate stays: the agent can never report a number the fitter didn't compute.

**Experiments that need 3D:**

- a projectile thrown at an angle toward or away from the camera;
- a conical pendulum (a circle in 3D, an ellipse in 2D);
- a bouncing ball (coefficient of restitution);
- a spring-mass system;
- a cart on an incline (on the table plane, which the homography maps directly).

Keep everything lab-style. Never film basketball or cricket throws, because sports analyzers are on the anti-project list.

**Demo beat:** the agent predicts the landing spot, a coin marks it, the real ball lands on it, and the 3D twin replays both paths. That beat is "working within 90 seconds" plus a clip that can go viral.

### Meta tooling

- **SAM 3.1** (Model API): calibration target, 3D tracking, and size-based depth.
- **Muse Wonder:** experimentalist agent that chooses models, diagnoses residuals, and designs the next trial.
- **Muse Spark:** per-trial checks.
- **Voice Transcribe:** hands-free logging ("trial 3, launch angle 30°").
- **SAM 3D Objects:** Meta open weights, not on Model API; runs on Modal GPU credit. It is optional.
- **Muse Spark Open** on Baseten or Modal for one real component, for the $10K open-weight bonus. Whether SAM 3D also counts for that bonus is **unverified**: the guide names Muse Glimmer and Spark Open.

### Scores (official rubric; previous Measured in brackets)

| Criterion | Weight | Score |
|---|---:|---:|
| Impact | 30% | 7 (7) |
| Meta tooling | 25% | 8.5 (8) |
| Technical depth | 20% | 9 (8) |
| Demo | 25% | 9.5 (9) |
| **Weighted** | | **84 (80)** |
| Risk adjustment (monocular accuracy, scope) | | −3 |
| **Final** | | **81 (80)** |

The weighted gain is small. The real gain is the **ceiling**: a live 3D replay plus a prediction that comes true is the kind of demo that reaches the top 5 and does well in the viral and community votes.

### Risks and gates

- **Gate A, end of day 2:** 10 throws with a measured landing spot. The landing prediction must fall within 5 cm (median), and g within 3%. If the gate fails, ship the 2D table-plane experiments (pendulum, incline, collisions, which need only a homography) with the 3D viewer as visualisation only. The 2D version is the old Measured, so the fallback is still an 80-point project.
- **Gate B:** SAM 3D Objects running on Modal by day 4. If it isn't, use a primitive sphere or cylinder in the replay. Nothing else depends on SAM 3D.
- **Optional stereo validation:** a second phone, synchronised by cross-correlating the two audio tracks, gives ground truth for the benchmark ("monocular vs. stereo: median error X cm"). Treat it as a stretch goal.

### Cost delta

- **Coding agents:** about +$60–100 for the reconstruction module, the three.js twin, and the simulator, for **≈$300–430 total** (±40%).
- **Meta API:** about $76, unchanged, covered by the $150 credit.
- **SAM 3D on Modal:** within the $100 Modal credit, if requested.

## 00. Re-rank on the official rubric (Oct 27, from the signed-in CV Details page; supersedes §0 and §3)

### Official Stage-2 rubric

Each criterion is scored 0–10; the top 5 per track are then re-ranked live in the final round.

| Criterion | Weight | What judges ask |
|---|---:|---|
| Impact | 30% | Real-world potential, who benefits, could it become something people use, does it fit a problem statement |
| Use of Meta AI tooling | 25% | Creative use beyond basic integration; "surface capabilities that surprised even us" |
| Technical depth and execution | 20% | Sound, refined engineering with real craft |
| Demo | 25% | Working and impressive, holds up live, a genuinely cool 3-minute video |

### Prizes

- **Indie track:** $150K / $100K / $75K / $50K / $25K for places 1–5.
- **Bonus prizes:**

| Bonus | Amount | How it's won |
|---|---:|---|
| Most Viral | $20K | Engagement on X up to Nov 8 |
| Best Build on Meta Open-Weight Models | $10K | Must run Muse Glimmer or Spark Open on your own hardware or partner inference |
| Community Vote | $10K | Public gallery votes |
| Best Agentic Use-Case | $5K | Agent autonomy and usefulness |
| Best Creative Build | $5K | Built with Muse Image or Wonder |

### Ranking on the official weights

Scores are my 0–10 judgments, with Demo marked down where the build might not hold up live.

| # | Project | Impact | Meta tooling | Tech | Demo | Weighted | Risk adjustment | Final |
|---|---|---:|---:|---:|---:|---:|---|---:|
| 1 | **Measured** | 7 | 8 | 8 | 9 | 79.5 | none | **80** |
| 2 | **Circuit Witness** | 7 | 8 | 9 | 7 | 76.5 | none (1-day test gate) | **77** |
| 3 | Shohoj (Bangla e-government agent) | 9 | 8 | 7 | 4 | 71 | −5: personal data, CAPTCHAs, the ban on legal or ethical violations | 66 |
| 4 | Sightline Dhaka | 8 | 8 | 7 | 5 | 70.5 | −7: safety claims can't be backed in a week | 63 |
| 5 | Glimmer offline tutor | 7 | 7 | 8 | 5 | 67 | −5: close to the education-chatbot anti-project | 62 |
| 6 | ProblemForge | 5 | 6 | 8 | 5 | 58.5 | none | 59 |
| 7 | Viva | 6 | 5 | 5 | 6 | 55.5 | −5: education-chatbot anti-project | 50 |

**What the official weights change:** Impact is the heaviest weight (30%), and ProblemForge falls from 3rd to 6th. Its audience is niche, and a text-only agent won't "surprise" Meta on tooling. Shohoj's impact pulls it up to 3rd, but its live demo can't hold up honestly. **Measured stays first.**

**How to push Measured's two weakest scores:**

- **Impact (7 → 8+).** Pitch it beyond school labs: "measure any moving physical system from a phone video". Show one real-world case beyond the textbook, such as a ceiling fan's wobble frequency, the damping of a hanging structure, or a machine's vibration. Back the Bangladesh lab-access argument with sourced numbers (still to be verified; don't invent figures).
- **Meta tooling (8 → 9).** Make each model essential, not decorative:
  - **SAM 3.1** as a precision instrument: sub-pixel centroids from masks, scale from a reference object. This is the "surprised even us" angle.
  - **Muse Wonder** as the experimental scientist: model selection, error diagnosis, next-trial design.
  - **Muse Spark** sub-agents: cheap checks on each trial.
  - **Muse Voice Transcribe:** hands-free trial logging ("trial 3, length 50 centimeters").
  - **Muse Spark Open** on Baseten or Modal credits for one real component, such as the report writer. That qualifies for the **$10K open-weight bonus**.
- **Bonus prizes it can also chase:** Best Agentic Use-Case ($5K), Most Viral ($20K; "I measured g with my phone in 10 seconds" is a shareable clip), and Community Vote ($10K).
- **Demo (25%):** deploy a live web app with bundled sample videos, so a judge can rerun a measurement without filming anything.

**Checks:** the CV gallery for this event is still empty (checked Oct 27). Discord is **not** signed in inside the browser pane; only Cerebral Valley is. The crowding check in #intros wasn't possible.

## 0. Re-rank after the Participant Guide (Oct 27; superseded by §00)

Source: the participant guide Koushik pasted on Oct 27. Its judging-rubric and prize tables came through empty (`[table]`), so the exact criteria and weights are **still unknown**.

### Guide rules that change the ranking

- **Anti-projects:** the guide names "sports analyzers or coaches", "simple 'AI for Education' chatbots", "simple image analyzers", "basic RAG", and anything giving medical advice. **Gully Hawk-Eye is dropped** (it's a sports analyzer). Viva and the Glimmer tutor sink, because they're close to the education-chatbot entry.
- **Stage 1 pass/fail:** the project has to fit a theme and make real use of the Meta Model API or Meta's open-weight models.
- **Stage 2:** scored 0–10 on a rubric we don't have yet. **Stage 3:** the top 5 per track are ranked live from their videos.
- **New work only:** the repo must be public, and the 3-minute demo may show only what was built during the event (from Oct 27). AttemptLens's planning docs are fine; any reused code isn't. Every option below starts from scratch.
- **Judged on three things:** the video, the code, and **the live product**. So the project needs to be deployed.
- **$150 in Meta API credits** (claim by Nov 4, 9 PM ET; a payment card is required, and credits arrive in batches). This covers the Meta-side running cost of every option except ProblemForge's high end.
- **The workshop on Oct 28 is "Agents 102: Best Practices for Verifiable Agents".** That's a strong hint about what Meta values, and it rewards the "model suggests, code checks" designs.

### New ranking

| # | Project | Score (was) | Change | Coding-agent cost | Meta API cost |
|---|---|---:|---|---:|---:|
| 1 | **Measured** | **83** (81) | Matches the verifiable-agents emphasis and Push the Frontier ("accelerate a scientific experiment"). Must be pitched as a measurement instrument, never as an "AI for education" tool or an image analyzer. | $240–335 | ≈$76 (covered by credit) |
| 2 | **Circuit Witness** | **79** (79) | Avoids "simple image analyzer" because the photo goes through circuit reconstruction, SPICE simulation and a diff. Pitch it as a hardware-debugging instrument. The 1-day test gate stands. | $330–470 | ≈$120 (covered) |
| 3 | **ProblemForge** | **75** (73) | Every step is checked by running code, which is the clearest fit with verifiable agents. Not an education chatbot. Still the weakest video. | $265–355 | $100–160 (use Spark for sub-agents to stay under $150) |
| 4 | Shohoj (Bangla e-government agent) | 62 (65) | Personal data on government sites risks the "legal, ethical, platform policies" ban, and CAPTCHAs can't be bypassed. | $290–400 | ≈$180 (over the credit) |
| 5 | Glimmer offline tutor | 58 (65) | Close to the education-chatbot entry, and the stack is heavy. | $290–400 | Fine-tuning compute via Modal credits |
| 6 | Sightline Dhaka | 58 (63) | Its safety claims would be hard to back up, and the medical-advice ban could be read broadly for an assistive device. | $270–380 | ≈$100 |
| 7 | Viva | 55 (67) | Most likely to be read as a "simple AI for Education chatbot". | $180–245 | ≈$15 |
| — | ~~Gully Hawk-Eye~~ | out | Explicit anti-project (sports analyzer) | — | — |

The coding-agent column uses the §5 assumptions (≈$2.25 blended per 30-minute run, plus ≈$40 for planning and review), at API list prices. With the Meta credit claimed, Meta-side spend should be $0 cash for #1–#3.

**Recommendation unchanged:** Measured, with an optional 1-day Circuit Witness test.

Measured's pitch has to say explicitly: "an instrument that turns any phone video into a verified measurement of a physical system." The LaTeX lab report is one output among several, not the product.

**Still missing:** the rubric table and the indie prize table. Paste their rows, because the weights could reorder #1–#3.

## 1. What the official pages actually say (checked Oct 27)

- **Indie track judging:** "creativity, technical ambition, and whether it works." No weights published.
- **Themes:** *Build for Your World* (a problem you know firsthand) and *Push the Frontier* (software, robotics, energy, materials; "accelerate a scientific experiment… understand and control a physical system").
- **Deadline:** Nov 4, 9:00 PM ET = **Nov 5, 8:00 AM Dhaka**. That leaves about 8.5 build days.
- **Official Rules:** promised before Oct 26, but not public: `/rules` returns 404 on both sites. They are probably in the participant portal or Discord. **Unverified: whether pre-existing code is allowed, plus the repo, video and license requirements.**
- **Meta models on Model API** ([docs](https://dev.meta.ai/docs/models)):

| Model | What it does | Price |
|---|---|---|
| Muse Wonder (`muse-wonder-1.0`) | Frontier agentic and coding model. Long-running agents, sub-agents, computer use, Active Memory. 1M context. Text, image, video, audio and PDF in. | $4 in / $0.20 cached / $20 out per Mtok |
| Muse Spark 1.3 | Cheap agentic workhorse | $1.25 / $4.25 (Contributor mode: $0.10 / $0.20) |
| SAM 3.1 | Text prompt in; boxes, masks and identity-preserving video tracking out | $2.50 per 1k images, $0.20 per 1k frames |
| Muse Voice Transcribe | Streaming speech-to-text, diarization, 25 languages. **No text-to-speech.** | Not checked |
| Muse Image | Image generation and editing | Not checked |
| Muse Spark Open / Muse Glimmer | Open weights; can be fine-tuned; Glimmer runs on ExecuTorch | Self-hosted, or partner credits (Baseten $100, Modal $100, Fireworks $25) |

## 2. Winner patterns: what separates winners from everyone else

Sources: Built with Opus 4.6 and 4.7 (Cerebral Valley + Anthropic, virtual, 20k applicants → 500 builders; **the closest structural match to this event**), the LlamaCon Hackathon (Meta), the Gemini Live Agent Challenge (1,536 entries), the Gemini API Competition, the GitLab AI Hackathon on Devpost, lablab.ai recent winners, the CV AI Engineer World's Fair gallery, and a JetBrains judges' panel.

1. **The builder is the person closest to the problem.** Opus 4.6: 4 of 5 winners were not professional developers (a lawyer, a cardiologist, a roads specialist, a musician). Opus 4.7: a doctor, a former micro-soldering technician, and a CS teacher. Winning entries open with a specific person ("my dad is a master carpenter in Chiloé…").
2. **The sponsor's newest headline capability carries real weight in the project.** Opus 4.7's winners (MedKit, Wrench Board, MaestrIA, ARIA) were all built on the newly launched Managed Agents. Geo-ML won "Best Llama API usage" because it needed Maverick's long context and multimodality. For Meta today, the headline capabilities are **Muse Wonder's long-running agents and computer use** and **SAM 3.1 video tracking**, which no rival API offers on the same key.
3. **The AI acts on a real artifact, in that artifact's own medium.** Wrench Board draws the diagnosis onto the circuit board. Askable links every answer to the exact second of a video. ViddyScribe writes audio descriptions into the video. TARA appraises roads from dashcam footage. Chat-in-a-box projects rarely place.
4. **A model proposes; deterministic code checks.** lablab trading winners: "Claude proposes and fifteen deterministic gates dispose." MedKit's system prompt doubles as a citation allowlist. DocSync opens a PR only when it is confident and files an issue otherwise. Trust is designed in, not claimed.
5. **Measured numbers, not adjectives.** "183 of 200 unseen tables set completely." "−36% TTFT on MI300X." "+5.1% over the judged week." "43 tests (in a hackathon project)." "$556 → $18 per month." Judges quote these numbers back.
6. **One flow that shows "this is possible now" within 90 seconds.** Every judge on the JetBrains panel said a version of: show something working in about 90 seconds, do one thing well, mock anything slow, and be honest about what doesn't work yet.
7. **Simulation, role-play and grading against published standards are a strong pattern.** MedKit (AI patient, graded against guidelines) and Maieutic (explain before you code). This is also the most crowded lane: expect hundreds of "AI tutor" entries out of 20k builders.
8. **Physical-world and multimodal work stands out in virtual events.** Drone-copilot, ORION (surgery), TARA (dashcam), the SO-101 robot arms, and the edge fall-detector all placed because they leave the browser.

**Cross-check against your 2nd Brain vault.** The vault is `2026-07-01 - IUT ICT Fest/Tools/2nd Brain/`: 767 Devpost projects (2023–2026, 227 flagged winners) plus about 7.4k lablab notes. I ran a keyword-category match on the Devpost notes:

| Category | Projects | Win rate |
|---|---:|---:|
| All projects (baseline) | 767 | 30% |
| Agent | 179 | 48% |
| Hardware / physical | 160 | 40% |
| Computer vision | 114 | 39% |
| Chatbot / RAG | 141 | 29% |

The sample is curated and the categories overlap, so read this as correlation only. It agrees with patterns 2, 3 and 8. A search of both collections found **no project resembling Measured, Circuit Witness, Gully Hawk-Eye or ProblemForge**. The few keyword hits were incidental.

**Implication for 20,000 builders:** a generic agent, tutor, or "self-improving loop" will drown; the AIEWF gallery alone has about 25 self-improvement loops. Pick a physical or measurable domain where you are an insider, make SAM 3.1 or Wonder essential to the project, and prove it with ground-truth numbers.

## 3. Ranked shortlist (original Oct 27 ranking, before the guide; see §0 for the current one)

Scoring is my judgment, not an official rubric. The weights follow the indie criteria:

| Criterion | Weight |
|---|---:|
| Creativity | 25 |
| Technical ambition | 25 |
| Works solo by Nov 5 | 25 |
| Meta-model weight in the project | 10 |
| Insider story and theme fit | 10 |
| 90-second demo impact | 5 |

| # | Project | Theme | Score | Build risk | API-equivalent cost |
|---|---|---|---:|---|---:|
| 1 | **Measured**: phone video → physics measurement with error bars | Frontier + Your World | **81** | Medium | **$320–420** |
| 2 | **Circuit Witness**: breadboard video → netlist → SPICE → errors drawn on the board | Your World + Frontier | **79** | High | **$450–600** |
| 3 | **Gully Hawk-Eye**: single-phone cricket ball tracking | Your World | 73 | Very high | $400–510 |
| 4 | **ProblemForge**: autonomous, stress-tested CP problem packages | Your World (software) | 73 | Low–medium | $350–480 |
| 5 | **Viva**: voice lab-viva examiner grounded in your lab manual | Your World | 67 | Low | $190–260 |
| 6 | Shohoj: Bangla computer-use agent for government e-services | Your World | 65 | High (legal, CAPTCHA, can't submit for real) | $500–600 |
| 7 | Glimmer Offline Tutor: fine-tuned Bangla tutor on a cheap Android | Frontier | 65 | High | $380–570 |
| 8 | Sightline Dhaka: hazard narration for visually impaired walkers | Your World | 63 | High (safety-critical) | $390–500 |

### 1. Measured: "Your phone is now a physics lab instrument" (recommended)

- **Core idea:** Record any mechanics experiment on a phone (slow-motion if possible): free fall, pendulum, spring, projectile, or a cart collision. You type "the red ball" and SAM 3.1 tracks it across frames. A known object in the frame (an A4 sheet or a ruler, also found by SAM) calibrates pixels to meters. Deterministic Python extracts the trajectory and fits candidate models: free fall, damped oscillation, projectile with drag, and momentum conservation. A Muse Wonder agent then works like a real experimentalist. It picks the model, reads the residuals, diagnoses systematic errors (parallax, rolling shutter, dropped frames, damping), **proposes the next trial that would cut the uncertainty most**, and writes a LaTeX lab report with full uncertainty propagation and a provenance trail back to the raw frames.
- **Demo (90 s):** Drop a ball. Fifteen seconds later the screen shows *g = 9.79 ± 0.06 m/s²*, a track overlay on the video, a residual plot, "your camera was 12° off-axis, redo from here", and a compiled PDF.
- **Impact:** Most labs in Bangladesh, SUST included, run mechanics with stopwatches and rulers; motion sensors and photogates are rare. This turns a ৳15k phone into a data-logging instrument. Beyond school it is a general "measure a physical system from video" capability, which is the *Push the Frontier* brief almost word for word.
- **Technical depth:** SAM 3.1 video tracking → camera calibration and homography → numerical differentiation with noise handling (Savitzky–Golay) → nonlinear least squares with model selection (AIC) → an agent loop with deterministic gates (the agent may never report a number the fitter didn't produce) → uncertainty propagation → LaTeX generation.
- **Why it can win:** It has ground truth. You can publish a benchmark such as "36 recorded trials, known g / k / L, median error 1.4%, versus 6.8% with a manual stopwatch." That covers the "whether it works" criterion with numbers. You are the user: you write physics lab reports in LaTeX.
- **Risks and mitigations:**
  - Small, fast objects blur. Use 120/240 fps slow-motion and large, brightly colored objects.
  - It could be seen as an academic-integrity hazard. Frame it as an instrument: the report exposes raw data and every agent decision, and a teacher mode is planned.
  - Prior art is Tracker (Open Source Physics), which is manual and has no reasoning. **Novelty:** zero-click tracking from a text prompt, plus an agent that designs the next experiment.
- **Cost breakdown:** 90–130 worker runs ≈ $200–295, Muse Wonder evaluation ≈ $70, SAM frames ≈ $6, and planning/review with Opus at high effort ≈ $40.

### 2. Circuit Witness: the lab TA that sees your breadboard (most ambitious)

- **Core idea:** Photograph or film a breadboard circuit and the lab-manual schematic. SAM 3.1 segments components and jumper wires. A homography fitted to the breadboard's hole grid maps every wire end to a hole. Muse Wonder reads resistor color codes and part markings. The system builds the as-built netlist, diffs it against the intended netlist, runs both through ngspice, and **draws the mistake onto the photo**: "R3 is in row 14, should be 15; with this miswire Vout will read 0.0 V instead of 4.3 V." It also predicts the multimeter reading at every node, so the student can confirm with a real probe.
- **Impact:** EEE and CSE first-year labs everywhere lose hours to a single misplaced wire, and you lived this in OrCAD/PSpice labs. One TA for 40 students becomes a TA per student.
- **Technical depth:** The highest on this list: vision → graph reconstruction → electrical equivalence (node-merging through breadboard strips) → SPICE simulation → diff → visual overlay.
- **Risks:** Wire-endpoint detection on a cluttered breadboard is a genuinely unsolved hackathon-scale problem. Wrench Board (Opus 4.7, second place) already used "overlay diagnosis on a board", so judges may have seen that motif, although the user and the problem differ. Schematic-to-netlist already exists (SINA, CircuitVision); a physical breadboard does not.
- **Gate:** A day-1 spike. If SAM 3.1 plus the homography can't map 90% of wire endpoints correctly on 5 photos of a constrained kit, switch to Measured.
- **Cost breakdown:** 130–190 runs ≈ $290–430, Wonder vision evaluation ≈ $120, plus planning.

### 3. Gully Hawk-Eye

- **Core idea:** A single phone on a tripod behind the stumps. SAM 3.1 tracks ball and batter. The pitch is a known 20.12 m with standard crease markings, so a homography from crease lines gives real-world coordinates. Output: speed, line, length and bounce point, a predicted path for an LBW-style call, and Bangla coaching commentary from Muse.
- **Impact:** Hawk-Eye costs broadcasters a fortune; every para team in Bangladesh plays with nothing.
- **Depth:** High. Single-camera 3D estimation from known geometry plus ball-flight physics.
- **Risk:** A 7 cm ball at 120 km/h makes about 30 cm of blur per frame even at 120 fps, which pushes SAM's tracking to its limit. This idea has the best demo and the worst chance of working well by Nov 5. The Measured architecture covers about 70% of it, so it could become a stretch demo for Measured instead.

### 4. ProblemForge

- **Core idea:** A long-running Muse Wonder agent turns a theme into a contest-ready problem package: statement, reference solution, brute force, generator, validator and checker. An adversarial sub-agent writes plausible wrong solutions (greedy shortcut, int overflow, O(n²)), and the system **proves that its tests kill each one**. Exports to Polygon and DOMjudge.
- **Impact:** Bangladesh's IUPC and NCPC circuit (SUST hosts) and every university club are short on problem setters.
- **Depth:** High, and the verification is fully deterministic.
- **Weakness:** The AutoCode paper (2025) and Olympath AI already exist, and a judge without a CP background won't feel the demo. It fits your expertise perfectly but has the lowest visual impact.

### 5. Viva

- **Core idea:** Upload your lab manual. Muse Voice Transcribe plus Spark runs an oral viva: adaptive follow-ups, perturbed questions that expose a memorized answer, and grading with citations to the manual. A teacher dashboard shows class-wide misconceptions.
- **Assessment:** Feasible and personal, since vivas are central to Bangladeshi labs. But it is the MedKit and Maieutic pattern again, in the most crowded lane. Meta has no text-to-speech, so voice output would come from browser speech synthesis.

### 6–8. Briefly

- **Shohoj.** Muse Wonder's computer use carries real weight here and the social impact is high. But real government sites mean personal data, CAPTCHAs (which must not be bypassed), and no way to submit for real, so the demo becomes a mock and "whether it works" suffers.
- **Glimmer Offline Tutor.** The deepest technically, through fine-tuning plus on-device deployment. It needs Bangla data and a GPU budget, and fine-tuning plus ExecuTorch in 8 days, solo, is the riskiest stack here.
- **Sightline.** High impact, but safety-critical claims need user studies you can't run in a week.

### Considered and rejected

- Paper-to-simulator (Mobius did it at Opus 4.7).
- Self-improving agent harnesses (about 25 in one CV gallery).
- Home-repair diagnosis (MaestrIA).
- Generic RAG or study tutors.
- Robot-arm simulation (crowded on lablab, and outside your background).

## 4. Recommendation

Pick **Measured**. It has the best balance of all three judging criteria, the strongest "Push the Frontier" fit, an essential use of SAM 3.1 (unique to Meta), a Muse Wonder agent that does real scientific reasoning rather than chat, and a ground-truth benchmark you can produce at home with a ball, a string and a spring.

If you want the maximum-ambition bet instead, start with a **one-day Circuit Witness spike** under the hard gate in §3.2, with Measured as the fallback. That costs one day, not the whole hackathon.

Next step after your pick: The Thinker produces `final plan.html` (architecture, an 8-day timeline mapped onto your Run System lanes, validation gates, a v2 Executor handoff).

## 5. How the costs were estimated (API-equivalent, not cash)

| Item | Assumption |
|---|---|
| Opus 5.5 | $4 / $20 per Mtok, $0.20 cached reads |
| Sonnet 5.5 | $2 / $10 |
| GPT-6.1 Sol | $2 / $10 |
| GPT-6.1 Terra | $1 / $5 |
| GPT-6 Astra | $10 / $50 (not used in these estimates; it would roughly double them) |
| One 30-minute Run System worker run (Opus, high effort) | ≈ 2.5M cached input + 0.25M fresh input + 60k output ≈ **$3.00** |
| Same run on Sol | ≈ **$1.50** |
| Blended across both lanes | **≈ $2.25 per run** |
| Muse orchestrator on Spark Contributor | Under $5 total |
| Firecrawl, TinyFish and Mobbin | Treated as existing subscriptions ($0 marginal) |

- Product evaluation spend uses Meta list prices from §1.
- Your Claude and Codex subscriptions mean the real cash cost is far lower. **Meta API spend is real money unless event credits arrive.**
- These are planning estimates with roughly ±40% uncertainty; nothing has been metered.

## 6. Open items for you

1. Paste the **Official Rules and submission requirements** from the participant portal or Discord, especially on pre-existing code, video length, repo and license.
2. **Muse API key:** has it arrived? Do you have Muse Code with Wonder Full? Wonder Full needs the $50/month Power plan; it is optional.
3. **Hardware:** does your phone shoot 120/240 fps slow-motion? Can you reach a SUST physics lab (pendulum, springs, a track), or an EEE breadboard kit with a multimeter?
4. **Partner credits:** have the Baseten, Modal or Fireworks credits been granted?
5. **Mobbin** needs authorization via `/mcp` in a terminal before it can be used for UI research.
6. **The VM and Run System:** are they live? Their files still target AttemptLens.
