# Real2Simulation: Concept Notes

Saved October 27, 2026 (Asia/Dhaka). Status: **direction approved Oct 27 (Real2Sim + virtual lab + Mystery-g); nothing built.** The visual version with diagrams and the cost calculator is [Real2Simulation Concept.html](Real2Simulation%20Concept.html). The build plan is [final plan.html](final%20plan.html); owner tasks are in [tasks for the owner.md](../tasks%20for%20the%20owner.md); event rules are in [Event Rules and Participant Guide.md](../Event%20Rules%20and%20Participant%20Guide.md).

This replaces the Measured / 3D pivot in [§000 of the shortlist](../07%20Project%20Reselection/Project%20Shortlist%20and%20Winner%20Patterns.md).

## Google sign-in setup status (Oct 27)

- **Decision (Oct 27):** use Clerk's built-in sign-in only. Google OAuth apps in testing mode admit only listed test users, which would block judges and public visitors, so no custom Google client is used.
- Clerk app `app_3LHWo2Ia88IuLU1EbEccvw7PR01` (Real2Simulation, development instance): Google runs on Clerk's shared credentials ("Use custom credentials" is off) and email sign-up and sign-in use a verification code (OTP). Passwords can be added but are not required. Read back in Clerk on Oct 27.
- The test Google Cloud client was deleted and project `bustling-sunset-512914-j3` was shut down (listed under Resources pending deletion; Google deletes it permanently after 30 days unless restored). Nothing else in Google Cloud was touched.
- Production Google is deferred. Decide it at S22 only if time allows, with a verified or published OAuth app. Judges use guest access (/library) and the demo account.
- Untested: end-to-end Google sign-in and email OTP sign-up on the dev instance.

## Koushik's brain dump (Oct 27, lightly edited from speech-to-text)

- I film a real video of my place and upload it to the web app. The app understands it with its models and builds a 3D world of it.
- An agent asks one or more questions, depending on the situation: what experiment do I want to run with it? It suggests suitable options and also lets me type the experiment's name myself.
- Once confirmed, the simulation world is built. I can simulate in it, run the experiment, and measure values such as the gravitational acceleration.
- Everything runs as a web app, so it works on any platform. Focus: Windows, Mac, Linux, and other landscape or big-screen devices. Nothing runs locally. For phones, find a way around: perhaps an Android APK, or something iOS users can install, so they get the app without browser jitter.
- Hosting: Railway Pro. Login: a simple portal using Clerk and Google Cloud Platform for production-grade auth.
- Users can record and upload their own video, from a phone or a laptop.
- A curated library of demos built from clips on YouTube and the web, viewable by anyone.
- It can be simple: upload a video, answer a few questions, get the 3D world. Then experiment, play around, or ask the sidebar agent to change things. Or describe an idea; the agent searches the library and, if found, the user can customise it.
- Ask real physics questions: how an experiment is done and the logic behind it.
- Create formal outputs such as lab reports.
- Create flowcharts and bar diagrams, using the Meta image model once the Meta Model API is available.

## Decisions proposed (see the HTML for reasons)

1. **Name:** Real2Simulation (chosen by Koushik, Oct 27; earlier working names: Measured, Physics Experimenter). Pitch it as "turn any video into a measurable physics world", never as a tutor.
2. **The circularity problem.** Measuring g inside a simulation only returns the g the simulation was given. Three modes fix this:
   - **Measure:** the video contains real motion, and the system fits real g, friction, and restitution from it.
   - **Real2Sim:** those fitted values become the physics of the 3D world, and the agent predicts the next real trial.
   - **Virtual lab:** a static scene video becomes a lab whose instruments have realistic error. "Mystery-g" hides the world's gravity, and the user has to measure it.
3. **Hosting split:** Railway does not offer GPUs. Railway hosts the web app, API, worker, Postgres, queue, and bucket. GPU work, using Koushik's credits (added Oct 27):
   - **Modal ($30):** live uploads (MapAnything + SAM 3D Objects on an L40S).
   - **AWS ($176.27 left of $200; quota pending):** EC2 g6e.xlarge in us-east-2 only. Spot for batch jobs (library demos, accuracy tests), on demand as Modal failover. See the AWS status below.
   - **Kaggle (30 h/week):** spikes and precompute without SAM 3D.
   - **Baseten (key in the event .env, Oct 27):** Muse Spark Open for the open-weight bonus, model ID `meta-models/muse-spark-open-1026`. Fireworks ($80) is the fallback.

   SAM 3D Objects needs about 32 GB of VRAM, so Kaggle's 16 GB and AWS g5's 24 GB cards can't run it.
4. **Library rights:** no ripping YouTube. Use public-domain NASA footage (the Apollo 15 hammer-and-feather drop, confirmed PD-USGov-NASA on Oct 27), Wikimedia Commons (PD, CC0, CC BY, CC BY-SA, credited) and Pexels or Pixabay clips. No NC or ND licences. The rules ban rights-less data.
5. **Phones:** an installable PWA on Android and iOS first. An Android APK can wrap that PWA (a Trusted Web Activity) later. A native iOS app is out of scope. Jitter comes from the rendering budget; a wrapper doesn't fix it.
6. **Charts:** charts and flowcharts are drawn deterministically from the data. Muse Image makes illustrations only, never images carrying numbers.

## Open questions for Koushik

1. AWS: tell me when the two quota requests are approved. Until then the plan treats AWS as unavailable.
2. Should the agent and UI support Bangla? Muse Voice Transcribe covers 25 languages, and Bangla is unverified.

## AWS status (Oct 27, from Muse's console check and Koushik's side chat)

**Treat AWS as "quota pending" until Koushik confirms approval.**

| Item | Status |
|---|---|
| Credits | $200 total, **$176.27** estimated remaining ($23.73 used). Six credits, all expiring **2027-05-25**: five $20 credits plus a $100 Free Tier credit. EC2 is in the eligible-services list of the credits checked; the lists of 3 of the $20 credits were not opened. |
| October bill | About $23.73 spent month to date, covered by credits; $0.00 billed so far. |
| Existing budgets | Two $25/month budgets, already past their alert thresholds (actual above 85%, forecast above 100%). They alert; they never block spending. A separate $50 GPU budget is still to be created before the first GPU session. |
| GPU quota | 0 vCPUs for G/VT on demand (L-DB2E81BA) and spot (L-3819A6DF) in us-east-1, us-west-2 and us-east-2 at the time of the check. |
| Quota requests | Per Koushik, Muse was then told to submit two 8-vCPU requests in **us-east-2**: "Running On-Demand G and VT instances" and "All G and VT Spot Instance Requests". **Pending.** Muse's check report says no request had been submitted when it ran, so the requests came after it. Not independently verified here. |
| Instance type | g6e.xlarge is offered in us-east-2: 4 vCPU, 32 GiB RAM, L40S GPU, $1.861/h Linux on demand. Fallback g6e.2xlarge (8 vCPU) at about $2.24/h was priced in us-east-1. 8 vCPUs of quota covers either. |
| Capacity | About 95 hours of g6e.xlarge on the remaining credit, before other spend. |
| Running instances | None launched for this project. In us-east-2, `dcv-gaming-test-2` and `rookiebot-agent-vm` (the Run System VM) were stopped, not terminated, at 16:42 +06. **Not needed any more:** Koushik decided on Oct 27 that the Run System runs on his own PC, so the VM stays stopped and costs nothing. |

Plan rules: us-east-2 only; spot for batch jobs; once the quota is approved, create a $50 EC2 budget alert before the first GPU session (it warns by email, it never stops spending); stop every GPU instance after each session.

## Pivot: public clips instead of filming (Oct 27)

Koushik's reasons: his phone records at most 60 fps with modest quality, setting up and measuring 8 clips is slow, an Algorithm course presentation video is due before Nov 3, and semester finals start Nov 5 (Statistics first).

Decisions:

- **Koushik films nothing.** An agent assembles about 10 licensed public clips (S02) with `clips.csv`: source, licence, credit line, frame rate, and a known-size object for scale. Koushik approves the list (about 10 minutes).
- **Ground truth comes from known physics, not a tape measure.** Earth clips should read g = 9.81 m/s², the Apollo 15 clip 1.62 m/s². Scale comes from standard object sizes (ball diameter, A4, door height). Gate M loosens from 3% to 5%, Gate R from 5% to 10%.
- **Prediction vs reality uses held-out frames.** The app watches the first part of a clip, predicts the rest, then overlays the prediction on the real frames it never saw. This replaces "film the next throw".
- **Slow-motion detection** becomes a feature: a clip that reads g ≈ 9.81/k² is reported as k-times slowed, not as a wrong g.
- **Upload stays.** Any user can still upload their own clip; the demo just doesn't depend on Koushik filming one.
- **Owner time ≈ 4 hours in total**; stop-work moved from Nov 4 22:00 to 18:00 Dhaka. The demo video is screen-recorded by an agent; Koushik adds an optional voice-over.

Rights: "almost any sample" is not safe. The participant guide bans footage without rights, so random YouTube or stock clips without a reuse licence stay out.

Risk: public clips have weaker ground truth (ledger L22). The Direct Measurement Videos collection, designed for this kind of measurement, moved to the commercial Pivot Interactives site, so it is not used.

## Model routing for the Run System (Oct 27, by measured cost per task)

Price per token is misleading: models differ hugely in how many tokens they burn per task. The numbers below are Artificial Analysis Intelligence Index scores with the measured cost per task at list prices (read Oct 27; ledger L28 in the final plan). This is a general index, not coding-only; the coding-specific check below overrides it where they disagree.

| Model and effort | Index | Cost per task | Verdict |
|---|---|---|---|
| GPT-6.1 Sol, medium | 47.8 | $0.21 | **Default for CODEX-1** |
| GPT-6.1 Sol, high | 50.2 | $0.32 | Gate code; beats Astra medium at about 1/5 the cost |
| GPT-6.1 Sol, xhigh | 51.0 | $0.39 | Escalation (replaces Astra) |
| GPT-6.1 Sol, max | 51.8 | $0.72 | Not used: +0.8 points for 1.85x |
| GPT-6 Astra, medium / max | 49.6 / 52.7 | $1.54 / $3.26 | At most 1 run in the build, with Koushik's go-ahead |
| GPT-6.1 Terra, high | 43.9 | $0.13 | **Default for CODEX-2** (fast, computer use) |
| GPT-6.1 Terra, xhigh / max | 45.4 / 48.1 | $0.19 / $0.40 | Not used: Sol medium is better at the same cost |
| GPT-6 Luna, high / max | 32.9 / 38.1 | $0.03 / $0.07 | Mechanical subtasks with a deterministic check only (reliability score near 0) |
| GPT-5.6 Luna, max | 37 | $0.18 | Not used: worse and 2.6x pricier than GPT-6 Luna |
| Claude Opus 5.5, medium | 51.2 | $1.34 | **Default for CLAUDE**: viewer, workspace UI, Gate D, script |
| Claude Opus 5.5, max | 57.6 | $5.98 | Not used |
| Claude Sonnet 5.5, high | 46.8 | $0.88 | PWA, report, cross-vendor review |
| Claude Sonnet 5.5, xhigh / max | 51.9 / 56.0 | $2.01 / $5.46 | Not used: Opus medium scores about the same for less; Sonnet max burns about 193K output tokens per task |

Rules: about 75% of build time on Codex. Each gate's code is reviewed by the other vendor. Switch model instead of raising effort past the table. On Oct 28–29, S03 logs tokens and quota per task for each lane; re-route if real costs differ from the table by more than 2x. Codex quota is counted in messages, not dollars; on Plus, Luna gets about 20x Sol's allowance and Astra about a third of it (L27, L30). Still unknown: Koushik's plan tier and Terra's allowance.

### Coding-specific check (Vals AI and Cognition, read Oct 27)

Cost per task at API list prices. Vals doesn't state effort settings; Cognition ran everything at medium in each vendor's own tool.

| Model | Terminal-Bench 4.0 (terminal agent, 66 tasks) | Vibe Code Bench (build a web app) | SWE-bench Multimodal (visual bugs) |
|---|---|---|---|
| Opus 5.5 | 65.2% · $13.20 | 90.3% · $57.92 | **70.2% · $3.63** |
| Sonnet 5.5 | 64.1% · $16.51 | **92.4% · $31.25** | 58.3% · $3.26 |
| Haiku 5.5 | 36.4% · $3.12 | 90.4% · $6.07 | 44.0% · $0.70 |
| GPT-6 Astra | 59.6% · $9.58 | 89.6% · $38.51 | 43.3% · $1.81 |
| **GPT-6.1 Sol** | 55.1% · **$1.72** | 88.9% · $6.23 | 43.5% · **$0.35** |
| GPT-6.1 Terra | 49.5% · $2.04 | 84.0% · $6.00 | — |
| GPT-6 Luna | 13.6% · $0.35 | 81.7% · $1.35 | 37.5% · $0.03 |
| GPT-5.6 Luna | 11.6% · $0.73 | 77.1% · $0.73 | — |

Cognition FrontierCode 1.1 at medium: Sol in Codex 50.2% at $0.36 per run; Opus in Claude Code 54.6% at $0.80.

What changed because of it:

- **Terra stops writing code.** On coding it costs about the same per task as Sol, or more, and scores lower. It keeps only browsing and screen work: clip sourcing, Playwright QA runs, video capture.
- **Sol does all Codex coding:** CODEX-1 for physics and gates, CODEX-2 (Sol at medium) for app plumbing. That's about 56 hours of Sol, the main quota risk.
- **Opus keeps the 3D viewer:** it leads visual-bug fixing by 27 points over Sol, so it earns its 10x price there.
- **Sonnet takes the workspace UI:** first at building web apps, at about half of Opus's cost.
- **Haiku 5.5 takes the PWA and lab report:** 90.4% at building web apps for about a fifth of Sonnet's cost. Koushik confirmed on Oct 27 that Haiku 5.5 is in his Claude Code.
- **Astra and GPT-5.6 Luna:** nothing changes. Astra is beaten on cost on every coding board; GPT-5.6 Luna scores lower than GPT-6 Luna on all three.
