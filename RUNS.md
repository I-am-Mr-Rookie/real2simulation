# Runs checklist

Updated Oct 31, 14:18 Dhaka from QUEUE.md by `Run-System/runs_view.py`. Agents regenerate this file; don't edit it by hand.

**How to run one:** open the tool and model shown, then say `Complete run S05a` (or `Complete the next run`).
All lanes run inside Codex; CLAUDE uses the existing native Claude route, not Claude Code (owner correction Oct29). Manual runs: no fixed agent cap; independent isolated shards only, serialized shared controls/heavy builds (PARALLELISM_POLICY.md).

Progress: **238 / 270** runs done · 2 in progress · 0 blocked · 0 waiting for Koushik · 0 open reviews

## Reviews for Koushik

None open. Routine decisions proceed; necessary owner inputs come from STATE.md.

## Ready now

**CODEX-1**
- [ ] **S13j** — Codex (native Claude) · Opus 5.5, effort high — OPTIONAL/CUT-FIRST: re-capture RM04 geometry bytes into private dev bucket via existing e2e.py under guardrails (30 min)

**CODEX-2**
- [~] **S02f** — Codex · GPT-6.1 Sol, effort high — Find licensed calibrated Earth-fall replacements (30 min) *(partial: resume it)*
- [~] **S18c** — Codex · GPT-6.1 Sol, effort medium — Precompute projectile and bounce demos (30 min) *(partial: resume it)*
- [ ] **S22c** — Codex (native Claude) · Sonnet 5.5, effort medium — Capture fresh-account full flow run 1 (30 min)
- …and 1 more ready in this lane

**CLAUDE**
- Nothing ready yet: check dependencies and retry holds below.

## In progress

- [~] **S15af** — Codex (native Claude) · Sonnet 5.5, effort medium — Left rail polish after S15ae DEV walk (Q21 spec section 6) (30 min) *(in progress)*
- [~] **S15ag** — Codex · Sol, effort high — Logo per owner Oct31 direction: generated with the best available image model and a proper prompt (30 min) *(in progress)*

## Waiting for Koushik

Nothing right now.

## All runs by step

Legend: [x] done · [~] in progress or partial · [!] blocked · [ ] to do

<details><summary><b>FILLER</b> —  (6/6)</summary>

- [x] **F-CODEX-1-1** — Codex · GPT-6.1 Sol, effort medium — Document owned-module edge cases (15 min)
- [x] **F-CODEX-1-2** — Codex · GPT-6.1 Sol, effort medium — Review owned-module test coverage gaps (15 min)
- [x] **F-CODEX-2-1** — Codex · GPT-6.1 Sol, effort medium — Document owned-module edge cases (15 min)
- [x] **F-CODEX-2-2** — Codex · GPT-6.1 Sol, effort medium — Review owned-module test coverage gaps (15 min)
- [x] **F-CLAUDE-1** — Codex (native Claude) · Opus 5.5, effort medium — Document owned-module edge cases (15 min)
- [x] **F-CLAUDE-2** — Codex (native Claude) · Opus 5.5, effort medium — Review owned-module test coverage gaps (15 min)

</details>

<details><summary><b>S01</b> — Finish keys and approvals (3/3)</summary>

- [x] **S01a** — Review Meta access evidence and billing balance (30 min)
- [x] **S01b** — Verify Google, email OTP and guest access when S04 is available (30 min)
- [x] **S01c** — Reconcile service readiness and dev-deploy approval (30 min)

</details>

<details><summary><b>S02</b> — Build the licensed public clip set (7/7)</summary>

- [x] **S02a** — Codex · GPT-6.1 Terra, effort high — Source free-fall and Apollo 15 candidates (30 min)
- [x] **S02b** — Codex · GPT-6.1 Terra, effort high — Source projectile, bounce, pendulum and room candidates (30 min)
- [x] **S02c** — Codex (native Claude) · Opus 5.5, effort high — Acquire licensed clips and record attribution (30 min)
- [x] **S02c1** — Codex (native Claude) · Opus 5.5, effort high — Independently assess NASA real trajectory sources (30 min)
- [x] **S02c2** — Codex (native Claude) · Opus 5.5, effort high — Independently assess non-sports stock Earth physics (30 min)
- [x] **S02d** — Codex (native Claude) · Opus 5.5, effort high — Inspect metadata and known-size references (20 min)
- [x] **S02e** — Approve the clip list (10 min)

</details>

<details><summary><b>S03</b> — Retarget the Run System to Real2Simulation (5/5)</summary>

- [x] **S03a** — Codex · GPT-6.1 Sol, effort medium — Initialize fresh local repository and control policy (20 min)
- [x] **S03b** — Codex · GPT-6.1 Sol, effort medium — Decompose and validate the complete handoff queue (20 min)
- [x] **S03c** — Codex · GPT-6.1 Sol, effort medium — Implement and verify Windows dispatcher on harmless runs (20 min)
- [x] **M-ROOT** — Codex · GPT-6.1 Sol, effort medium — Consolidate event-root repository and merge context (30 min)
- [x] **M-PROMPTS** — Codex · GPT-6.1 Sol, effort medium — Short-prompt self-serve dispatcher and event-root verification (30 min)

</details>

<details><summary><b>S04</b> — App skeleton on Railway with sign-in and guest access (18/18)</summary>

- [x] **S04a** — Codex · GPT-6.1 Sol, effort medium — Define shell interfaces and fixture mount points (30 min)
- [x] **S04b** — Codex · GPT-6.1 Sol, effort medium — Create Next.js shell and isolated route layout (30 min)
- [x] **S04c** — Codex · GPT-6.1 Sol, effort medium — Wire Clerk shared-Google and OTP configuration (30 min)
- [x] **S04d** — Codex · GPT-6.1 Sol, effort medium — Add guest library route and authorization boundary (30 min)
- [x] **S04e** — Codex · GPT-6.1 Sol, effort medium — Create FastAPI and worker health skeletons (30 min)
- [x] **S04f** — Codex · GPT-6.1 Sol, effort medium — Configure dev Postgres, Redis and bucket integration (30 min)
- [x] **S04g** — Codex · GPT-6.1 Sol, effort medium — Deploy the dev skeleton via Railway (30 min)
- [x] **S04g1** — Codex · GPT-6.1 Sol, effort medium — Harden dev deployment verifier semantic checks (15 min)
- [x] **S04g2** — Codex · GPT-6.1 Sol, effort medium — Preserve staging destination guards under Python optimization (15 min)
- [x] **S04h** — Codex (native Claude) · Sonnet 5.5, effort high — Verify sign-in, guest route and dev health (30 min)
- [x] **S04i** — Codex · GPT-6.1 Sol, effort high — Connect private scene repository and mount workspace route (30 min)
- [x] **S04j** — Codex (native Claude) · Opus 5.5, effort high — Wire guest library page to manifest and simulated replay (30 min)
- [x] **S04k** — Codex (native Claude) · Opus 5.5, effort high — Serve guest library from build-time snapshot (30 min)
- [x] **S04l** — Codex (native Claude) · Opus 5.5, effort medium — Polish guest library page copy and UI (30 min)
- [x] **S04n** — Codex (native Claude) · Opus 5.5, effort medium — Web BFF proxy /api/workspace/[...path] (Clerk auth, capped body, private-network forward) (30 min)
- [x] **S04m** — Codex (native Claude) · Opus 5.5, effort high — Mount workspace routers, extend API image (+jsonschema pin), set var names, deploy API to dev (30 min)
- [x] **S04o** — Codex (native Claude) · Opus 5.5, effort medium — PrivateWorkspace mounts controller; deploy web to dev (30 min)
- [x] **R-W** — Codex (native Claude) · Opus 5.5, effort high — Cross-vendor review: private workspace auth boundary and proxy (15 min)

</details>

<details><summary><b>S05</b> — Gate R spike: metric 3D scene from public clips (7/7)</summary>

- [x] **S05a** — Codex · GPT-6.1 Sol, effort medium — Check reconstruction licences and freeze scene artifact contract (30 min)
- [x] **S05b** — Codex (native Claude) · Opus 5.5, effort high — Probe MapAnything on the first licensed scene (30 min)
- [x] **S05c** — Codex (native Claude) · Opus 5.5, effort high — Reconstruct remaining scene clips (30 min)
- [x] **S05d** — Codex (native Claude) · Opus 5.5, effort high — Fit floor, metric scale and gravity orientation (30 min)
- [x] **S05e** — Codex (native Claude) · Opus 5.5, effort high — Run Gate R and inspect reconstruction failures (30 min)
- [x] **S05f** — Codex (native Claude) · Opus 5.5, effort high — Apply the named fallback and checkpoint Gate R (30 min)
- [x] **R-R** — Codex · GPT-6.1 Sol, effort high — Cross-vendor review: Gate R implementation and failure thresholds (15 min)

</details>

<details><summary><b>S06</b> — GPU container on Modal (AWS-ready) (9/9)</summary>

- [x] **S06a** — Codex (native Claude) · Opus 5.5, effort high — Define reproducible GPU image and dry-run contract (30 min)
- [x] **S06p** — Codex · GPT-6.1 Sol, effort medium — Verify existing Modal allocation and pre-reset GPU readiness (20 min)
- [x] **S06b** — Codex (native Claude) · Opus 5.5, effort high — Package MapAnything runtime (30 min)
- [x] **S06c** — Codex (native Claude) · Opus 5.5, effort high — Add optional SAM 3D Objects path (30 min)
- [x] **S06d** — Codex (native Claude) · Opus 5.5, effort high — Add Modal scene job entry point (30 min)
- [x] **S06e** — Codex (native Claude) · Opus 5.5, effort high — Add cold-start timing and cost instrumentation (30 min)
- [x] **S06f** — Codex (native Claude) · Opus 5.5, effort high — Exercise one licensed room clip on Modal (30 min)
- [x] **S06g** — Codex (native Claude) · Opus 5.5, effort medium — Verify CPU dry-run and disabled AWS adapter (30 min)
- [x] **S06h** — Codex (native Claude) · Opus 5.5, effort medium — Checkpoint GPU runtime and fallback evidence (30 min)

</details>

<details><summary><b>S07</b> — Gate M spike: measure g from public free-fall clips (20/21)</summary>

- [~] **S02f** — Codex · GPT-6.1 Sol, effort high — Find licensed calibrated Earth-fall replacements (30 min) *(partial: resume it)*
- [x] **S02g** — Codex · GPT-6.1 Sol, effort high — Verify original FF01/FF02 calibration sources (30 min)
- [x] **S02h** — Codex · GPT-6.1 Sol, effort high — Resolve RP03 capture mapping and geometric identifiability (30 min)
- [x] **S02i** — Codex · GPT-6.1 Sol, effort high — Audit RP01 side-view metric trajectory segments (30 min)
- [x] **S07r** — Codex · GPT-6.1 Sol, effort high — Reconcile input readiness and approved small-sample fallback (20 min)
- [x] **S07a** — Codex · GPT-6.1 Sol, effort medium — Define scale, timestamps and held-out tracking inputs (30 min)
- [x] **S07b** — Codex (native Claude) · Opus 5.5, effort high — Implement SAM 3.1 tracking adapter (30 min)
- [x] **S07c** — Codex · GPT-6.1 Sol, effort medium — Implement deterministic free-fall fit (30 min)
- [x] **S07d** — Codex · GPT-6.1 Sol, effort medium — Detect slow-motion and propagate measurement uncertainty (30 min)
- [x] **S07e** — Codex · GPT-6.1 Sol, effort high — Run Earth Gate M measurements (30 min)
- [x] **S07f** — Codex · GPT-6.1 Sol, effort high — Evaluate Apollo stretch and record Gate M decision (30 min)
- [x] **S07g** — Codex (native Claude) · Opus 5.5, effort high — Owner clips: register in clips.csv and measure g on 01_demo_hero with the real pipeline (30 min)
- [x] **S07i** — Codex (native Claude) · Opus 5.5, effort high — OWN01 measured g from the real SAM 3.1 track; prepare one batched track for OWN02-OWN12 (30 min)
- [x] **S07j** — Codex (native Claude) · Opus 5.5, effort high — Fix batch-track CUDA OOM and add an explicit reviewed second standalone GPU envelope (30 min)
- [x] **S07k** — Codex (native Claude) · Opus 5.5, effort high — Pre-registered fall-window/release rule v2 from SAM tracks; re-measure owner clips (30 min)
- [x] **S07l** — Codex (native Claude) · Opus 5.5, effort high — Diagnose why held-out prediction fails on every owner clip (v1 0/9, v2 0/6) (30 min)
- [x] **S07m** — Codex (native Claude) · Opus 5.5, effort high — Pre-registered v3 predictive check (chi-square with extrapolation leverage) on all owner clips (30 min)
- [x] **S07n** — Codex (native Claude) · Opus 5.5, effort medium — System-derived fall time and drop height (+/- u) for OWN01 from existing tracks (no stopwatch, no tape) (30 min)
- [x] **S07h** — Codex (native Claude) · Opus 5.5, effort high — Owner clips 02-06: held-out and robustness evaluation with the S07g pipeline (30 min)
- [x] **R-M** — Codex (native Claude) · Opus 5.5, effort medium — Cross-vendor review: Gate M fitting, timebase and uncertainty (15 min)
- [x] **R-M2** — Codex (native Claude) · Opus 5.5, effort medium — Review S07f summary-boundary fixes and honest fallback (15 min)

</details>

<details><summary><b>S08</b> — Experiment spec, validator and 4 templates (9/9)</summary>

- [x] **S08a** — Codex · GPT-6.1 Sol, effort medium — Define versioned experiment schema and units (30 min)
- [x] **S08b** — Codex · GPT-6.1 Sol, effort medium — Validate numeric ranges and dimensional consistency (30 min)
- [x] **S08c** — Codex · GPT-6.1 Sol, effort medium — Validate geometry and numerical stability (30 min)
- [x] **S08d** — Codex · GPT-6.1 Sol, effort medium — Add free-fall template and analytic answer (30 min)
- [x] **S08e** — Codex · GPT-6.1 Sol, effort medium — Add projectile template and analytic answer (30 min)
- [x] **S08f** — Codex · GPT-6.1 Sol, effort medium — Add ramp template and analytic answer (30 min)
- [x] **S08g** — Codex · GPT-6.1 Sol, effort medium — Add pendulum template and analytic answer (30 min)
- [x] **S08h** — Codex · GPT-6.1 Sol, effort medium — Run schema and ten-bad-spec regression checks (30 min)
- [x] **S08i** — Codex · GPT-6.1 Sol, effort medium — Reject unrepresentable fall displacement and extreme sample times (30 min)

</details>

<details><summary><b>S09</b> — 3D world viewer with a rendering budget (11/11)</summary>

- [x] **S09a** — Codex (native Claude) · Opus 5.5, effort medium — Define viewer adapter and synthetic fixture scene (30 min)
- [x] **S09b** — Codex (native Claude) · Opus 5.5, effort medium — Render fixture geometry and orbit camera (30 min)
- [x] **S09c** — Codex (native Claude) · Opus 5.5, effort medium — Load real point-cloud or splat artifacts (30 min)
- [x] **S09d** — Codex (native Claude) · Opus 5.5, effort medium — Add colliders, camera path and scene labels (30 min)
- [x] **S09e** — Codex (native Claude) · Opus 5.5, effort medium — Implement pixel-ratio and detail budgets (30 min)
- [x] **S09f** — Codex (native Claude) · Opus 5.5, effort medium — Pause rendering when idle or hidden (30 min)
- [x] **S09g** — Codex (native Claude) · Opus 5.5, effort medium — Add 375px reduced-detail viewer layout (30 min)
- [x] **S09h** — Codex (native Claude) · Opus 5.5, effort high — Integrate three measured scene artifacts (30 min)
- [x] **S09i** — Codex (native Claude) · Opus 5.5, effort medium — Measure fps and memory on target laptop (30 min)
- [x] **S09j** — Codex (native Claude) · Opus 5.5, effort medium — Checkpoint viewer evidence and visual fixes (30 min)
- [x] **S09k** — Codex (native Claude) · Opus 5.5, effort medium — Add simulated-trajectory replay to viewer (30 min)

</details>

<details><summary><b>S10</b> — Builder and in-browser simulator; Gate P (19/19)</summary>

- [x] **S10a** — Codex · GPT-6.1 Sol, effort medium — Build validated-spec apparatus placement (30 min)
- [x] **S10b** — Codex · GPT-6.1 Sol, effort medium — Implement fixed-step RK4 core (30 min)
- [x] **S10c** — Codex · GPT-6.1 Sol, effort medium — Integrate Rapier contacts (30 min)
- [x] **S10d** — Codex · GPT-6.1 Sol, effort medium — Implement free-fall and projectile runs (30 min)
- [x] **S10e** — Codex · GPT-6.1 Sol, effort medium — Implement ramp and pendulum runs (30 min)
- [x] **S10f** — Codex · GPT-6.1 Sol, effort medium — Implement seeded replay (30 min)
- [x] **S10g** — Codex · GPT-6.1 Sol, effort medium — Hide Mystery-g until fit/reveal (30 min)
- [x] **S10h** — Codex · GPT-6.1 Sol, effort medium — Run four-template Gate P regression (30 min)
- [x] **S10i** — Codex · GPT-6.1 Sol, effort high — Resolve contact jitter with RK4-only fallback if needed (30 min)
- [x] **S10j** — Codex · GPT-6.1 Sol, effort high — Checkpoint Gate P and review packet (30 min)
- [x] **S10k** — Codex · GPT-6.1 Sol, effort high — Harden lab session cancellation and stale reveal boundaries (30 min)
- [x] **S10l** — Codex · GPT-6.1 Sol, effort medium — Preserve complete plotted traces and honest mobile lab labels (30 min)
- [x] **S10m** — Codex · GPT-6.1 Sol, effort high — Reject nonrepresentable contact geometry and initial penetration (30 min)
- [x] **S10n** — Codex · GPT-6.1 Sol, effort high — Run validated normal-mode synthetic trials in the real browser (30 min)
- [x] **S10o** — Codex · GPT-6.1 Sol, effort high — Repair independent valid-domain RK4 and analytic model findings (30 min)
- [x] **S10p** — Codex · GPT-6.1 Sol, effort high — Stabilize replay canonicalization and initial snapshot consistency (30 min)
- [x] **S10q** — Codex · GPT-6.1 Sol, effort high — Correct local bridge byte decoding and output ceiling (30 min)
- [x] **S10r** — Codex · GPT-6.1 Sol, effort high — Harden exported fit-reveal and finite plotting helpers (30 min)
- [x] **R-P** — Codex (native Claude) · Opus 5.5, effort medium — Cross-vendor review: Gate P analytic comparison and replay (15 min)

</details>

<details><summary><b>S11</b> — Virtual instruments and the fitter service (12/12)</summary>

- [x] **S11a** — Codex · GPT-6.1 Sol, effort medium — Define instrument and fitter API contracts (30 min)
- [x] **S11b** — Codex · GPT-6.1 Sol, effort medium — Model stopwatch reaction error (30 min)
- [x] **S11c** — Codex · GPT-6.1 Sol, effort medium — Model camera, ruler and light-gate error (30 min)
- [x] **S11d** — Codex · GPT-6.1 Sol, effort medium — Implement least-squares fitter (30 min)
- [x] **S11e** — Codex · GPT-6.1 Sol, effort medium — Add AIC model selection and residuals (30 min)
- [x] **S11f** — Codex · GPT-6.1 Sol, effort medium — Add Jacobian uncertainty (30 min)
- [x] **S11g** — Codex · GPT-6.1 Sol, effort medium — Run hundred-seed coverage regression (30 min)
- [x] **S11h** — Codex · GPT-6.1 Sol, effort medium — Finalize tool-only numeric API and evidence (30 min)
- [x] **S11i** — Codex · GPT-6.1 Sol, effort high — Correct finite-sample coverage and declared uncertainty overconfidence (30 min)
- [x] **S11j** — Codex · GPT-6.1 Sol, effort high — Stabilize full covariance and reject lost residual variance (30 min)
- [x] **S11k** — Codex · GPT-6.1 Sol, effort high — Correct virtual-instrument half-step and lattice rounding (30 min)
- [x] **S11l** — Codex · GPT-6.1 Sol, effort high — Preserve residual scale in RMSE and AIC model selection (30 min)

</details>

<details><summary><b>S12</b> — Real2Sim bridge and prediction; Gate RS (7/7)</summary>

- [x] **S12a** — Codex (native Claude) · Opus 5.5, effort high — Define calibration and withheld-frame boundary (30 min)
- [x] **S12b** — Codex (native Claude) · Opus 5.5, effort high — Transfer measured parameters into simulator (30 min)
- [x] **S12c** — Codex (native Claude) · Opus 5.5, effort high — Predict held-out projectile and bounce motion (30 min)
- [x] **S12d** — Codex (native Claude) · Opus 5.5, effort high — Predict pendulum continuation and overlay contract (30 min)
- [x] **S12e** — Codex (native Claude) · Opus 5.5, effort high — Run Gate RS on public motion clips (30 min)
- [x] **S12f** — Codex (native Claude) · Opus 5.5, effort high — Label outputs and choose honest prediction fallback (30 min)
- [x] **R-RS** — Codex · GPT-6.1 Sol, effort high — Cross-vendor review: Gate RS held-out boundary and error normalization (15 min)

</details>

<details><summary><b>S13</b> — Upload and reconstruction job pipeline (10/11)</summary>

- [x] **S13a** — Codex (native Claude) · Opus 5.5, effort high — Define resumable upload and job-stage contracts (30 min)
- [x] **S13b** — Codex (native Claude) · Opus 5.5, effort high — Implement bucket upload validation (30 min)
- [x] **S13c** — Codex (native Claude) · Opus 5.5, effort high — Extract ffmpeg keyframes and metadata (30 min)
- [x] **S13d** — Codex (native Claude) · Opus 5.5, effort medium — Add Redis job lifecycle and retry handling (30 min)
- [x] **S13e** — Codex (native Claude) · Opus 5.5, effort high — Connect Muse Wonder understanding (30 min)
- [x] **S13f** — Codex (native Claude) · Opus 5.5, effort high — Connect SAM masks and Modal reconstruction (30 min)
- [x] **S13g** — Codex (native Claude) · Opus 5.5, effort medium — Stream job progress to shell integration interface (30 min)
- [x] **S13h** — Codex (native Claude) · Opus 5.5, effort high — Measure dev upload-to-scene path (30 min)
- [x] **S13i** — Codex (native Claude) · Opus 5.5, effort high — API upload + job routes with RECORDED-replay executor (approved-clip sha gate) (30 min)
- [ ] **S13j** — Codex (native Claude) · Opus 5.5, effort high — OPTIONAL/CUT-FIRST: re-capture RM04 geometry bytes into private dev bucket via existing e2e.py under guardrails (30 min)
- [x] **S13k** — Codex (native Claude) · Opus 5.5, effort medium — RM04 replay: stitch recorded S14g-fix3 live understand spec + owner-scoped scene resolver (30 min)

</details>

<details><summary><b>S14</b> — Scene-understanding and interview agent (11/11)</summary>

- [x] **S14a** — Codex (native Claude) · Opus 5.5, effort high — Define scene, question and tool-output contracts (30 min)
- [x] **S14b** — Codex (native Claude) · Opus 5.5, effort high — Integrate Muse Wonder scene understanding (30 min)
- [x] **S14c** — Codex (native Claude) · Opus 5.5, effort high — Implement one-to-three-question interview (30 min)
- [x] **S14d** — Codex (native Claude) · Opus 5.5, effort high — Add bounded validator-retry loop (30 min)
- [x] **S14e** — Codex (native Claude) · Opus 5.5, effort high — Connect Muse Spark trial check (30 min)
- [x] **S14f** — Codex (native Claude) · Opus 5.5, effort high — Enforce tool-only numbers in replies (30 min)
- [x] **S14g** — Codex (native Claude) · Opus 5.5, effort high — Run Gate A fixture and thirty-turn suite (30 min)
- [x] **S14h** — Codex (native Claude) · Opus 5.5, effort high — Checkpoint Gate A and template-card fallback (30 min)
- [x] **S14i** — Codex (native Claude) · Opus 5.5, effort high — API workspace analysis routers: internal-token auth, interview questions, spec validate, fit, HTML report (30 min)
- [x] **S14j** — Codex (native Claude) · Opus 5.5, effort high — Workspace spec route: owner Q16 'scale unverified, not setup-validated' path for recorded scenes (30 min)
- [x] **R-A** — Codex · GPT-6.1 Sol, effort high — Cross-vendor review: Gate A tool-number enforcement (15 min)

</details>

<details><summary><b>S15</b> — Workspace UI (31/35)</summary>

- [x] **S15a** — Codex (native Claude) · Sonnet 5.5, effort high — Define workspace states and consume module contracts (30 min)
- [x] **S15b** — Codex (native Claude) · Sonnet 5.5, effort high — Build workspace layout and viewport mount (30 min)
- [x] **S15c** — Codex (native Claude) · Sonnet 5.5, effort high — Build upload status and failure surfaces (30 min)
- [x] **S15d** — Codex (native Claude) · Sonnet 5.5, effort high — Build interview chips and free-text panel (30 min)
- [x] **S15e** — Codex (native Claude) · Sonnet 5.5, effort high — Build experiment template controls (30 min)
- [x] **S15f** — Codex (native Claude) · Sonnet 5.5, effort high — Build run and replay controls (30 min)
- [x] **S15g** — Codex (native Claude) · Sonnet 5.5, effort high — Build virtual instrument controls (30 min)
- [x] **S15h** — Codex (native Claude) · Sonnet 5.5, effort medium — Build fit table and residual chart (30 min)
- [x] **S15i** — Codex (native Claude) · Sonnet 5.5, effort medium — Build sidebar and report navigation (30 min)
- [x] **S15j** — Codex (native Claude) · Sonnet 5.5, effort medium — Stack workspace at 375px (30 min)
- [x] **S15k** — Codex (native Claude) · Sonnet 5.5, effort high — Walk full workflow on dev (30 min)
- [x] **S15l** — Codex (native Claude) · Sonnet 5.5, effort medium — Checkpoint workspace accessibility and evidence (30 min)
- [x] **S15m** — Codex (native Claude) · Opus 5.5, effort high — Plan end-to-end workspace wiring (upload to report) (30 min)
- [x] **S15n** — Codex (native Claude) · Opus 5.5, effort high — Workspace controller: reduce() state + fetch adapters + upload control (30 min)
- [x] **S15o** — Codex (native Claude) · Sonnet 5.5, effort high — Re-walk upload-to-report on dev (successor to S15k) (30 min)
- [x] **S15p** — Codex (native Claude) · Opus 5.5, effort medium — Wire workspace run (browser simulator), honest instruments and API report shape (30 min)
- [x] **S15q** — Codex (native Claude) · Opus 5.5, effort medium — Fix live workspace spec 422 + surface errors and RECORDED labels (S15o controller walk defects) (30 min)
- [x] **S15r** — Codex (native Claude) · Opus 5.5, effort high — Owner Q20=A: labelled what-if Run on Q16 recorded scenes (API artifact + simulator mode + labels) (30 min)
- [x] **S15s** — Codex (native Claude) · Opus 5.5, effort medium — Reach Fit and Report from a finished run in the live workspace (30 min)
- [x] **S15t** — Codex (native Claude) · Opus 5.5, effort high — Fix live Fit display rejection and report 422 on DEV (30 min)
- [x] **S15u** — Codex (native Claude) · Sonnet 5.5, effort medium — Fit view polish: 375px overflow, truthful what-if source note, compact residuals (30 min)
- [x] **S15v** — Codex (native Claude) · Opus 5.5, effort high — Product: accept 30 fps phone clips, ask for a known size, report uncertainty instead of failing (30 min)
- [x] **S15y** — Codex (native Claude) · Opus 5.5, effort high — Owner clip flow without failure: known-size interview and g +/- u result on DEV (30 min)
- [x] **S15w** — Codex (native Claude) · Opus 5.5, effort high — One UI pass: myfront 1.2.0 round-3 + make-interfaces-feel-better (30 min)
- [x] **S15x** — Codex (native Claude) · Sonnet 5.5, effort medium — Propose 6 Mobbin references for the owner to pick 3 (20 min)
- [x] **S15z** — Codex (native Claude) · Sonnet 5.5, effort medium — Owner clip result card shown once (stage panel or job panel, not both) (30 min)
- [x] **S15aa** — Codex (native Claude) · Opus 5.5, effort medium — Owner clips OWN02-OWN12 in product: stored frozen-v1 result + v3 predictive-check verdict, or abstain (30 min)
- [x] **S15ab** — Codex (native Claude) · Opus 5.5, effort high — Workspace shell per Q21 owner spec: collapsible left icon rail, center project, top-right toggle for a right agent/tools panel (30 min)
- [x] **S15ac** — Codex (native Claude) · Opus 5.5, effort high — Interview as right-panel agent questions (O1 live preview + O2/P4 question card + P1 waiting state) per Q21 owner spec (30 min)
- [x] **S15ad** — Codex (native Claude) · Sonnet 5.5, effort medium — Workspace centre polish after S15ab/S15ac: no overflow and no cramped centre when the right panel is open (30 min)
- [x] **S15ae** — Codex (native Claude) · Opus 5.5, effort medium — Left rail as activity bar per owner addendum (Q21 spec section 6): toggle current pane, icon click toggles/opens, hover temporarily opens, click pins (30 min)
- [~] **S15af** — Codex (native Claude) · Sonnet 5.5, effort medium — Left rail polish after S15ae DEV walk (Q21 spec section 6) (30 min) *(in progress)*
- [~] **S15ag** — Codex · Sol, effort high — Logo per owner Oct31 direction: generated with the best available image model and a proper prompt (30 min) *(in progress)*
- [ ] **S15ah** — Codex (native Claude) · Opus 5.5, effort high — Workspace modern-SaaS restyle + dark mode per evidence/ui/OWNER-UI-DIRECTION-2026-10-31.md (30 min)
- [ ] **S15ai** — Codex (native Claude) · Opus 5.5, effort medium — Public pages (home, library, lab, about, sign-in chrome) restyled with the S15ah tokens/icons + dark mode (30 min)

</details>

<details><summary><b>S16</b> — Sidebar agent tools and the open-weight component (8/8)</summary>

- [x] **S16a** — Codex · GPT-6.1 Sol, effort medium — Define sidebar tool-call and search contracts (30 min)
- [x] **S16b** — Codex · GPT-6.1 Sol, effort medium — Implement validator-first spec patch tool (30 min)
- [x] **S16c** — Codex · GPT-6.1 Sol, effort medium — Implement rebuild and tool-output plumbing (30 min)
- [x] **S16d** — Codex · GPT-6.1 Sol, effort medium — Connect Baseten Spark Open library search (30 min)
- [x] **S16e** — Codex · GPT-6.1 Sol, effort medium — Verify real dev search inference (30 min)
- [x] **S16f** — Codex · GPT-6.1 Sol, effort medium — Add Fireworks fallback (30 min)
- [x] **S16g** — Codex · GPT-6.1 Sol, effort medium — Test patch safety and search failures (30 min)
- [x] **S16h** — Codex · GPT-6.1 Sol, effort medium — Checkpoint open-weight evidence and fallback claims (30 min)

</details>

<details><summary><b>S17</b> — Lab report and charts (6/6)</summary>

- [x] **S17a** — Codex (native Claude) · Sonnet 5.5, effort high — Define report data contract and numeric assertions (30 min)
- [x] **S17b** — Codex (native Claude) · Sonnet 5.5, effort high — Build deterministic report tables and charts (30 min)
- [x] **S17c** — Codex (native Claude) · Sonnet 5.5, effort high — Build TeX/HTML report rendering (30 min)
- [x] **S17d** — Codex (native Claude) · Sonnet 5.5, effort high — Compile reports for all four templates (30 min)
- [x] **S17e** — Codex (native Claude) · Sonnet 5.5, effort high — Automate numeric report-to-fitter diff (30 min)
- [x] **S17f** — Codex (native Claude) · Sonnet 5.5, effort medium — Checkpoint report accessibility and fallback evidence (30 min)

</details>

<details><summary><b>S18</b> — Demo library with licensed footage (12/13)</summary>

- [x] **S18a** — Codex · GPT-6.1 Sol, effort medium — Define library manifest and immutable artifact format (30 min)
- [x] **S18b** — Codex · GPT-6.1 Sol, effort medium — Precompute free-fall demos (30 min)
- [~] **S18c** — Codex · GPT-6.1 Sol, effort medium — Precompute projectile and bounce demos (30 min) *(partial: resume it)*
- [x] **S18d** — Codex · GPT-6.1 Sol, effort medium — Precompute pendulum and scene demos (30 min)
- [x] **S18e** — Codex · GPT-6.1 Sol, effort medium — Prepare Apollo and Mystery-g entries (30 min)
- [x] **S18f** — Codex · GPT-6.1 Sol, effort medium — Implement guest manifest and artifact endpoint (30 min)
- [x] **S18g** — Codex · GPT-6.1 Sol, effort medium — Implement library loading integration (30 min)
- [x] **S18k** — Codex · GPT-6.1 Sol, effort medium — Publish playable demo assets for guest library (30 min)
- [x] **S18l** — Codex (native Claude) · Opus 5.5, effort medium — Fix R-L P2: Mystery-g answer recoverable from public trace/repo (30 min)
- [x] **R-L** — Codex (native Claude) · Opus 5.5, effort medium — Cross-vendor review: guest library exposure and Mystery-g answer withholding (15 min)
- [x] **S18h** — Codex · GPT-6.1 Sol, effort medium — Verify licences and approved clip list (30 min)
- [x] **S18i** — Codex · GPT-6.1 Sol, effort medium — Measure library load times (30 min)
- [x] **S18j** — Codex · GPT-6.1 Sol, effort medium — Checkpoint minimum-library fallback (30 min)

</details>

<details><summary><b>S19</b> — Installable PWA and phone layout (4/4)</summary>

- [x] **S19a** — Codex (native Claude) · Sonnet 5.5, effort high — Add PWA manifest and icons from owned assets (30 min)
- [x] **S19b** — Codex (native Claude) · Sonnet 5.5, effort high — Add safe service-worker caching (30 min)
- [x] **S19c** — Codex (native Claude) · Sonnet 5.5, effort high — Add install guidance and orientation handling (30 min)
- [x] **S19d** — Codex (native Claude) · Sonnet 5.5, effort medium — Verify installability and 375px walkthrough (30 min)

</details>

<details><summary><b>S20</b> — Spend guardrails and GPU failover (6/6)</summary>

- [x] **S20a** — Codex · GPT-6.1 Sol, effort medium — Define spend ledger, upload quota and reserve contract (30 min)
- [x] **S20b** — Codex · GPT-6.1 Sol, effort medium — Implement reconstruction cap and library exemption (30 min)
- [x] **S20c** — Codex · GPT-6.1 Sol, effort medium — Implement disabled-by-default AWS failover switch (30 min)
- [x] **S20d** — Codex · GPT-6.1 Sol, effort high — Run Gate C simulated-cap regression (30 min)
- [x] **S20z** — Codex (native Claude) · Sonnet 5.5, effort medium — Repair stale guardrail test for guest library (admission never consulted) (30 min)
- [x] **R-C** — Codex (native Claude) · Opus 5.5, effort high — Cross-vendor review: Gate C cap accounting and library exemption (15 min)

</details>

<details><summary><b>S21</b> — Benchmark numbers for the pitch (6/6)</summary>

- [x] **S21a** — Codex · GPT-6.1 Sol, effort medium — Freeze benchmark inputs and method (30 min)
- [x] **S21b** — Codex · GPT-6.1 Sol, effort medium — Measure gravity and scene-scale errors (30 min)
- [x] **S21c** — Codex · GPT-6.1 Sol, effort medium — Measure held-out prediction errors (30 min)
- [x] **S21d** — Codex · GPT-6.1 Sol, effort medium — Measure runtime and scene cost (30 min)
- [x] **S21e** — Codex · GPT-6.1 Sol, effort medium — Write BENCHMARK.md and app About data (30 min)
- [x] **S21f** — Codex · GPT-6.1 Sol, effort medium — Cross-check pitch-facing benchmark numbers (30 min)

</details>

<details><summary><b>S22</b> — End-to-end QA on the judging environment; Gate D (2/11)</summary>

- [x] **S22a** — Codex (native Claude) · Opus 5.5, effort medium — Prepare approved judging-candidate QA checklist (30 min)
- [x] **S22b** — Codex (native Claude) · Sonnet 5.5, effort medium — Capture logged-out guest library walkthrough (30 min)
- [ ] **S22c** — Codex (native Claude) · Sonnet 5.5, effort medium — Capture fresh-account full flow run 1 (30 min)
- [ ] **S22d** — Codex (native Claude) · Sonnet 5.5, effort medium — Capture fresh-account full flow run 2 (30 min)
- [ ] **S22e** — Codex (native Claude) · Sonnet 5.5, effort medium — Capture fresh-account full flow run 3 (30 min)
- [ ] **S22f** — Codex (native Claude) · Opus 5.5, effort high — Judge Gate D evidence and prioritize defects (30 min)
- [ ] **S22g** — Codex (native Claude) · Sonnet 5.5, effort medium — Capture 375px and auth-boundary QA (30 min)
- [ ] **S22h** — Codex (native Claude) · Sonnet 5.5, effort medium — Capture retry, spend-cap and report QA (30 min)
- [ ] **S22i** — Codex (native Claude) · Sonnet 5.5, effort medium — Recheck approved candidate after owner-lane fixes (30 min)
- [ ] **S22j** — Codex (native Claude) · Opus 5.5, effort high — Record final Gate D decision and freeze recommendation (30 min)
- [ ] **R-D** — Codex · GPT-6.1 Sol, effort high — Cross-vendor review: Gate D protocol and Claude verdict evidence (15 min)

</details>

<details><summary><b>S23</b> — Promote the judging build (0/3)</summary>

- [ ] **S23a** — Authorize frozen judging promotion (10 min)
- [ ] **S23b** — Codex · GPT-6.1 Sol, effort medium — Promote frozen revision to judging (20 min)
- [ ] **S23c** — Codex · GPT-6.1 Sol, effort medium — Verify deployed revision and smoke flow (30 min)

</details>

<details><summary><b>S24</b> — Three-minute demo video (5/13)</summary>

- [x] **S24a** — Codex (native Claude) · Opus 5.5, effort high — Write evidence-backed three-minute script (30 min)
- [x] **S24b** — Codex (native Claude) · Opus 5.5, effort medium — Review script, captions and footage credits (30 min)
- [ ] **S24c** — Codex (native Claude) · Sonnet 5.5, effort medium — Capture room rebuild and interview (30 min)
- [ ] **S24d** — Codex (native Claude) · Sonnet 5.5, effort medium — Capture held-out prediction and reveal (30 min)
- [ ] **S24e** — Codex (native Claude) · Sonnet 5.5, effort medium — Capture Apollo result and Mystery-g (30 min)
- [ ] **S24f** — Codex (native Claude) · Sonnet 5.5, effort medium — Capture benchmark and Meta model evidence (30 min)
- [ ] **S24g** — Record optional voice-over part 1 (30 min)
- [ ] **S24h** — Record optional voice-over part 2 (30 min)
- [ ] **S24i** — Codex (native Claude) · Sonnet 5.5, effort high — Cut video and align captions (30 min)
- [ ] **S24j** — Codex (native Claude) · Sonnet 5.5, effort medium — Check playback and approval-gated public video link (30 min)
- [x] **S24k** — Codex (native Claude) · Sonnet 5.5, effort medium — Update 3-min script with stopwatch-vs-phone before/after (30 min)
- [x] **S24m** — Codex (native Claude) · Sonnet 5.5, effort medium — Script beat 5b: drop the stopwatch half; show the system measuring fall time and drop height itself (Q22) (20 min)
- [x] **S24l** — Codex (native Claude) · Sonnet 5.5, effort medium — Swap final owner-clip numbers (S07h/S07k/S07m) into the 3-min script (30 min)

</details>

<details><summary><b>S25</b> — README, attribution and public repo (4/6)</summary>

- [x] **S25a** — Codex · GPT-6.1 Sol, effort medium — Write setup, architecture and Meta usage README (30 min)
- [x] **S25b** — Codex · GPT-6.1 Sol, effort medium — Write footage attribution and public-package checklist (30 min)
- [x] **S25c** — Codex · GPT-6.1 Sol, effort medium — Scan tracked files and full Git history (30 min)
- [ ] **S25d** — Authorize public repository visibility (10 min)
- [ ] **S25e** — Codex · GPT-6.1 Sol, effort medium — Make approved repo public and verify anonymous links (20 min)
- [x] **S25f** — Codex (native Claude) · Sonnet 5.5, effort medium — Add MIT LICENSE (owner Q18) and update README/ATTRIBUTION/checklist (30 min)

</details>

<details><summary><b>S26</b> — Submit and post (0/3)</summary>

- [ ] **S26a** — Submit approved project on Cerebral Valley (30 min)
- [ ] **S26b** — Verify entry and contributor listing (30 min)
- [ ] **S26c** — Post demo on X and submit the post link (30 min)

</details>
