# Runs checklist

Updated Oct 29, 17:54 Dhaka from QUEUE.md by `Run-System/runs_view.py`. Agents regenerate this file; don't edit it by hand.

**How to run one:** open the tool and model shown, then say `Complete run S05a` (or `Complete the next run`).
All lanes run inside Codex; CLAUDE uses the existing native Claude route, not Claude Code (owner correction Oct29). Manual runs: no fixed agent cap; independent isolated shards only, serialized shared controls/heavy builds (PARALLELISM_POLICY.md).

Progress: **100 / 217** runs done · 0 in progress · 0 blocked · 1 waiting for Koushik · 0 open reviews

## Reviews for Koushik

None open. Routine decisions proceed; necessary owner inputs come from STATE.md.

## Ready now

**CODEX-1**
- [ ] **S05c** — Codex (native Claude) · Opus 5.5, effort high — Reconstruct remaining scene clips (30 min)
- [ ] **S06a** — Codex (native Claude) · Opus 5.5, effort high — Define reproducible GPU image and dry-run contract (30 min)
- [ ] **S14c** — Codex (native Claude) · Opus 5.5, effort high — Implement one-to-three-question interview (30 min)

**CODEX-2**
- Nothing ready yet: check dependencies and retry holds below.

**CLAUDE**
- [ ] **S15d** — Codex (native Claude) · Sonnet 5.5, effort high — Build interview chips and free-text panel (30 min)
- [ ] **S17d** — Codex (native Claude) · Sonnet 5.5, effort high — Compile reports for all four templates (30 min)
- [ ] **S19b** — Codex (native Claude) · Sonnet 5.5, effort high — Add safe service-worker caching (30 min)

## Waiting to retry

- [~] **S02f** — Codex · GPT-6.1 Sol, effort high — Find licensed calibrated Earth-fall replacements (30 min) *(retry held until Oct 29, 12:18 UTC / Oct 29, 18:18 Dhaka; Owner Oct29: pause all GPT/Codex-model (Sol) dispatch until quota reset 18:18 Dhaka; S02f-orch13 hit usage limit.)*

## Waiting for Koushik

- [ ] **S01b** — Verify Google, email OTP and guest access when S04 is available (30 min)

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

<details><summary><b>S01</b> — Finish keys and approvals (2/3)</summary>

- [x] **S01a** — Review Meta access evidence and billing balance (30 min)
- [ ] **S01b** — Verify Google, email OTP and guest access when S04 is available (30 min)
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

<details><summary><b>S04</b> — App skeleton on Railway with sign-in and guest access (9/10)</summary>

- [x] **S04a** — Codex · GPT-6.1 Sol, effort medium — Define shell interfaces and fixture mount points (30 min)
- [x] **S04b** — Codex · GPT-6.1 Sol, effort medium — Create Next.js shell and isolated route layout (30 min)
- [x] **S04c** — Codex · GPT-6.1 Sol, effort medium — Wire Clerk shared-Google and OTP configuration (30 min)
- [x] **S04d** — Codex · GPT-6.1 Sol, effort medium — Add guest library route and authorization boundary (30 min)
- [x] **S04e** — Codex · GPT-6.1 Sol, effort medium — Create FastAPI and worker health skeletons (30 min)
- [x] **S04f** — Codex · GPT-6.1 Sol, effort medium — Configure dev Postgres, Redis and bucket integration (30 min)
- [x] **S04g** — Codex · GPT-6.1 Sol, effort medium — Deploy the dev skeleton via Railway (30 min)
- [x] **S04g1** — Codex · GPT-6.1 Sol, effort medium — Harden dev deployment verifier semantic checks (15 min)
- [x] **S04g2** — Codex · GPT-6.1 Sol, effort medium — Preserve staging destination guards under Python optimization (15 min)
- [ ] **S04h** — Codex (native Claude) · Sonnet 5.5, effort high — Verify sign-in, guest route and dev health (30 min)

</details>

<details><summary><b>S05</b> — Gate R spike: metric 3D scene from public clips (2/7)</summary>

- [x] **S05a** — Codex · GPT-6.1 Sol, effort medium — Check reconstruction licences and freeze scene artifact contract (30 min)
- [x] **S05b** — Codex (native Claude) · Opus 5.5, effort high — Probe MapAnything on the first licensed scene (30 min)
- [ ] **S05c** — Codex (native Claude) · Opus 5.5, effort high — Reconstruct remaining scene clips (30 min)
- [ ] **S05d** — Codex (native Claude) · Opus 5.5, effort high — Fit floor, metric scale and gravity orientation (30 min)
- [ ] **S05e** — Codex (native Claude) · Opus 5.5, effort high — Run Gate R and inspect reconstruction failures (30 min)
- [ ] **S05f** — Codex (native Claude) · Opus 5.5, effort high — Apply the named fallback and checkpoint Gate R (30 min)
- [ ] **R-R** — Codex · GPT-6.1 Sol, effort high — Cross-vendor review: Gate R implementation and failure thresholds (15 min)

</details>

<details><summary><b>S06</b> — GPU container on Modal (AWS-ready) (1/9)</summary>

- [ ] **S06a** — Codex (native Claude) · Opus 5.5, effort high — Define reproducible GPU image and dry-run contract (30 min)
- [x] **S06p** — Codex · GPT-6.1 Sol, effort medium — Verify existing Modal allocation and pre-reset GPU readiness (20 min)
- [ ] **S06b** — Codex (native Claude) · Opus 5.5, effort high — Package MapAnything runtime (30 min)
- [ ] **S06c** — Codex (native Claude) · Opus 5.5, effort high — Add optional SAM 3D Objects path (30 min)
- [ ] **S06d** — Codex (native Claude) · Opus 5.5, effort high — Add Modal scene job entry point (30 min)
- [ ] **S06e** — Codex (native Claude) · Opus 5.5, effort high — Add cold-start timing and cost instrumentation (30 min)
- [ ] **S06f** — Codex (native Claude) · Opus 5.5, effort high — Exercise one licensed room clip on Modal (30 min)
- [ ] **S06g** — Codex (native Claude) · Opus 5.5, effort high — Verify CPU dry-run and disabled AWS adapter (30 min)
- [ ] **S06h** — Codex (native Claude) · Opus 5.5, effort high — Checkpoint GPU runtime and fallback evidence (30 min)

</details>

<details><summary><b>S07</b> — Gate M spike: measure g from public free-fall clips (12/13)</summary>

- [~] **S02f** — Codex · GPT-6.1 Sol, effort high — Find licensed calibrated Earth-fall replacements (30 min) *(retry held until Oct 29, 12:18 UTC / Oct 29, 18:18 Dhaka; Owner Oct29: pause all GPT/Codex-model (Sol) dispatch until quota reset 18:18 Dhaka; S02f-orch13 hit usage limit.)*
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

<details><summary><b>S09</b> — 3D world viewer with a rendering budget (7/10)</summary>

- [x] **S09a** — Codex (native Claude) · Opus 5.5, effort medium — Define viewer adapter and synthetic fixture scene (30 min)
- [x] **S09b** — Codex (native Claude) · Opus 5.5, effort medium — Render fixture geometry and orbit camera (30 min)
- [x] **S09c** — Codex (native Claude) · Opus 5.5, effort medium — Load real point-cloud or splat artifacts (30 min)
- [x] **S09d** — Codex (native Claude) · Opus 5.5, effort medium — Add colliders, camera path and scene labels (30 min)
- [x] **S09e** — Codex (native Claude) · Opus 5.5, effort medium — Implement pixel-ratio and detail budgets (30 min)
- [x] **S09f** — Codex (native Claude) · Opus 5.5, effort medium — Pause rendering when idle or hidden (30 min)
- [x] **S09g** — Codex (native Claude) · Opus 5.5, effort medium — Add 375px reduced-detail viewer layout (30 min)
- [ ] **S09h** — Codex (native Claude) · Opus 5.5, effort high — Integrate three measured scene artifacts (30 min)
- [ ] **S09i** — Codex (native Claude) · Opus 5.5, effort high — Measure fps and memory on target laptop (30 min)
- [ ] **S09j** — Codex (native Claude) · Opus 5.5, effort high — Checkpoint viewer evidence and visual fixes (30 min)

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

<details><summary><b>S12</b> — Real2Sim bridge and prediction; Gate RS (0/7)</summary>

- [ ] **S12a** — Codex (native Claude) · Opus 5.5, effort high — Define calibration and withheld-frame boundary (30 min)
- [ ] **S12b** — Codex (native Claude) · Opus 5.5, effort high — Transfer measured parameters into simulator (30 min)
- [ ] **S12c** — Codex (native Claude) · Opus 5.5, effort high — Predict held-out projectile and bounce motion (30 min)
- [ ] **S12d** — Codex (native Claude) · Opus 5.5, effort high — Predict pendulum continuation and overlay contract (30 min)
- [ ] **S12e** — Codex (native Claude) · Opus 5.5, effort high — Run Gate RS on public motion clips (30 min)
- [ ] **S12f** — Codex (native Claude) · Opus 5.5, effort high — Label outputs and choose honest prediction fallback (30 min)
- [ ] **R-RS** — Codex · GPT-6.1 Sol, effort high — Cross-vendor review: Gate RS held-out boundary and error normalization (15 min)

</details>

<details><summary><b>S13</b> — Upload and reconstruction job pipeline (0/8)</summary>

- [ ] **S13a** — Codex (native Claude) · Opus 5.5, effort high — Define resumable upload and job-stage contracts (30 min)
- [ ] **S13b** — Codex (native Claude) · Opus 5.5, effort high — Implement bucket upload validation (30 min)
- [ ] **S13c** — Codex (native Claude) · Opus 5.5, effort high — Extract ffmpeg keyframes and metadata (30 min)
- [ ] **S13d** — Codex (native Claude) · Opus 5.5, effort high — Add Redis job lifecycle and retry handling (30 min)
- [ ] **S13e** — Codex (native Claude) · Opus 5.5, effort high — Connect Muse Wonder understanding (30 min)
- [ ] **S13f** — Codex (native Claude) · Opus 5.5, effort high — Connect SAM masks and Modal reconstruction (30 min)
- [ ] **S13g** — Codex (native Claude) · Opus 5.5, effort high — Stream job progress to shell integration interface (30 min)
- [ ] **S13h** — Codex (native Claude) · Opus 5.5, effort high — Measure dev upload-to-scene path (30 min)

</details>

<details><summary><b>S14</b> — Scene-understanding and interview agent (2/9)</summary>

- [x] **S14a** — Codex (native Claude) · Opus 5.5, effort high — Define scene, question and tool-output contracts (30 min)
- [x] **S14b** — Codex (native Claude) · Opus 5.5, effort high — Integrate Muse Wonder scene understanding (30 min)
- [ ] **S14c** — Codex (native Claude) · Opus 5.5, effort high — Implement one-to-three-question interview (30 min)
- [ ] **S14d** — Codex (native Claude) · Opus 5.5, effort high — Add bounded validator-retry loop (30 min)
- [ ] **S14e** — Codex (native Claude) · Opus 5.5, effort high — Connect Muse Spark trial check (30 min)
- [ ] **S14f** — Codex (native Claude) · Opus 5.5, effort high — Enforce tool-only numbers in replies (30 min)
- [ ] **S14g** — Codex (native Claude) · Opus 5.5, effort high — Run Gate A fixture and thirty-turn suite (30 min)
- [ ] **S14h** — Codex (native Claude) · Opus 5.5, effort high — Checkpoint Gate A and template-card fallback (30 min)
- [ ] **R-A** — Codex · GPT-6.1 Sol, effort high — Cross-vendor review: Gate A tool-number enforcement (15 min)

</details>

<details><summary><b>S15</b> — Workspace UI (3/12)</summary>

- [x] **S15a** — Codex (native Claude) · Sonnet 5.5, effort high — Define workspace states and consume module contracts (30 min)
- [x] **S15b** — Codex (native Claude) · Sonnet 5.5, effort high — Build workspace layout and viewport mount (30 min)
- [x] **S15c** — Codex (native Claude) · Sonnet 5.5, effort high — Build upload status and failure surfaces (30 min)
- [ ] **S15d** — Codex (native Claude) · Sonnet 5.5, effort high — Build interview chips and free-text panel (30 min)
- [ ] **S15e** — Codex (native Claude) · Sonnet 5.5, effort high — Build experiment template controls (30 min)
- [ ] **S15f** — Codex (native Claude) · Sonnet 5.5, effort high — Build run and replay controls (30 min)
- [ ] **S15g** — Codex (native Claude) · Sonnet 5.5, effort high — Build virtual instrument controls (30 min)
- [ ] **S15h** — Codex (native Claude) · Sonnet 5.5, effort high — Build fit table and residual chart (30 min)
- [ ] **S15i** — Codex (native Claude) · Sonnet 5.5, effort high — Build sidebar and report navigation (30 min)
- [ ] **S15j** — Codex (native Claude) · Sonnet 5.5, effort high — Stack workspace at 375px (30 min)
- [ ] **S15k** — Codex (native Claude) · Sonnet 5.5, effort high — Walk full workflow on dev (30 min)
- [ ] **S15l** — Codex (native Claude) · Sonnet 5.5, effort high — Checkpoint workspace accessibility and evidence (30 min)

</details>

<details><summary><b>S16</b> — Sidebar agent tools and the open-weight component (0/8)</summary>

- [ ] **S16a** — Codex · GPT-6.1 Sol, effort medium — Define sidebar tool-call and search contracts (30 min)
- [ ] **S16b** — Codex · GPT-6.1 Sol, effort medium — Implement validator-first spec patch tool (30 min)
- [ ] **S16c** — Codex · GPT-6.1 Sol, effort medium — Implement rebuild and tool-output plumbing (30 min)
- [ ] **S16d** — Codex · GPT-6.1 Sol, effort medium — Connect Baseten Spark Open library search (30 min)
- [ ] **S16e** — Codex · GPT-6.1 Sol, effort medium — Verify real dev search inference (30 min)
- [ ] **S16f** — Codex · GPT-6.1 Sol, effort medium — Add Fireworks fallback (30 min)
- [ ] **S16g** — Codex · GPT-6.1 Sol, effort medium — Test patch safety and search failures (30 min)
- [ ] **S16h** — Codex · GPT-6.1 Sol, effort medium — Checkpoint open-weight evidence and fallback claims (30 min)

</details>

<details><summary><b>S17</b> — Lab report and charts (3/6)</summary>

- [x] **S17a** — Codex (native Claude) · Sonnet 5.5, effort high — Define report data contract and numeric assertions (30 min)
- [x] **S17b** — Codex (native Claude) · Sonnet 5.5, effort high — Build deterministic report tables and charts (30 min)
- [x] **S17c** — Codex (native Claude) · Sonnet 5.5, effort high — Build TeX/HTML report rendering (30 min)
- [ ] **S17d** — Codex (native Claude) · Sonnet 5.5, effort high — Compile reports for all four templates (30 min)
- [ ] **S17e** — Codex (native Claude) · Sonnet 5.5, effort high — Automate numeric report-to-fitter diff (30 min)
- [ ] **S17f** — Codex (native Claude) · Sonnet 5.5, effort high — Checkpoint report accessibility and fallback evidence (30 min)

</details>

<details><summary><b>S18</b> — Demo library with licensed footage (0/10)</summary>

- [ ] **S18a** — Codex · GPT-6.1 Sol, effort medium — Define library manifest and immutable artifact format (30 min)
- [ ] **S18b** — Codex · GPT-6.1 Sol, effort medium — Precompute free-fall demos (30 min)
- [ ] **S18c** — Codex · GPT-6.1 Sol, effort medium — Precompute projectile and bounce demos (30 min)
- [ ] **S18d** — Codex · GPT-6.1 Sol, effort medium — Precompute pendulum and scene demos (30 min)
- [ ] **S18e** — Codex · GPT-6.1 Sol, effort medium — Prepare Apollo and Mystery-g entries (30 min)
- [ ] **S18f** — Codex · GPT-6.1 Sol, effort medium — Implement guest manifest and artifact endpoint (30 min)
- [ ] **S18g** — Codex · GPT-6.1 Sol, effort medium — Implement library loading integration (30 min)
- [ ] **S18h** — Codex · GPT-6.1 Sol, effort medium — Verify licences and approved clip list (30 min)
- [ ] **S18i** — Codex · GPT-6.1 Sol, effort medium — Measure library load times (30 min)
- [ ] **S18j** — Codex · GPT-6.1 Sol, effort medium — Checkpoint minimum-library fallback (30 min)

</details>

<details><summary><b>S19</b> — Installable PWA and phone layout (1/4)</summary>

- [x] **S19a** — Codex (native Claude) · Sonnet 5.5, effort high — Add PWA manifest and icons from owned assets (30 min)
- [ ] **S19b** — Codex (native Claude) · Sonnet 5.5, effort high — Add safe service-worker caching (30 min)
- [ ] **S19c** — Codex (native Claude) · Sonnet 5.5, effort high — Add install guidance and orientation handling (30 min)
- [ ] **S19d** — Codex (native Claude) · Sonnet 5.5, effort high — Verify installability and 375px walkthrough (30 min)

</details>

<details><summary><b>S20</b> — Spend guardrails and GPU failover (0/5)</summary>

- [ ] **S20a** — Codex · GPT-6.1 Sol, effort medium — Define spend ledger, upload quota and reserve contract (30 min)
- [ ] **S20b** — Codex · GPT-6.1 Sol, effort medium — Implement reconstruction cap and library exemption (30 min)
- [ ] **S20c** — Codex · GPT-6.1 Sol, effort medium — Implement disabled-by-default AWS failover switch (30 min)
- [ ] **S20d** — Codex · GPT-6.1 Sol, effort high — Run Gate C simulated-cap regression (30 min)
- [ ] **R-C** — Codex (native Claude) · Opus 5.5, effort high — Cross-vendor review: Gate C cap accounting and library exemption (15 min)

</details>

<details><summary><b>S21</b> — Benchmark numbers for the pitch (0/6)</summary>

- [ ] **S21a** — Codex · GPT-6.1 Sol, effort medium — Freeze benchmark inputs and method (30 min)
- [ ] **S21b** — Codex · GPT-6.1 Sol, effort medium — Measure gravity and scene-scale errors (30 min)
- [ ] **S21c** — Codex · GPT-6.1 Sol, effort medium — Measure held-out prediction errors (30 min)
- [ ] **S21d** — Codex · GPT-6.1 Sol, effort medium — Measure runtime and scene cost (30 min)
- [ ] **S21e** — Codex · GPT-6.1 Sol, effort medium — Write BENCHMARK.md and app About data (30 min)
- [ ] **S21f** — Codex · GPT-6.1 Sol, effort medium — Cross-check pitch-facing benchmark numbers (30 min)

</details>

<details><summary><b>S22</b> — End-to-end QA on the judging environment; Gate D (0/11)</summary>

- [ ] **S22a** — Codex (native Claude) · Opus 5.5, effort high — Prepare approved judging-candidate QA checklist (30 min)
- [ ] **S22b** — Codex (native Claude) · Sonnet 5.5, effort high — Capture logged-out guest library walkthrough (30 min)
- [ ] **S22c** — Codex (native Claude) · Sonnet 5.5, effort high — Capture fresh-account full flow run 1 (30 min)
- [ ] **S22d** — Codex (native Claude) · Sonnet 5.5, effort high — Capture fresh-account full flow run 2 (30 min)
- [ ] **S22e** — Codex (native Claude) · Sonnet 5.5, effort high — Capture fresh-account full flow run 3 (30 min)
- [ ] **S22f** — Codex (native Claude) · Opus 5.5, effort high — Judge Gate D evidence and prioritize defects (30 min)
- [ ] **S22g** — Codex (native Claude) · Sonnet 5.5, effort high — Capture 375px and auth-boundary QA (30 min)
- [ ] **S22h** — Codex (native Claude) · Sonnet 5.5, effort high — Capture retry, spend-cap and report QA (30 min)
- [ ] **S22i** — Codex (native Claude) · Sonnet 5.5, effort high — Recheck approved candidate after owner-lane fixes (30 min)
- [ ] **S22j** — Codex (native Claude) · Opus 5.5, effort high — Record final Gate D decision and freeze recommendation (30 min)
- [ ] **R-D** — Codex · GPT-6.1 Sol, effort high — Cross-vendor review: Gate D protocol and Claude verdict evidence (15 min)

</details>

<details><summary><b>S23</b> — Promote the judging build (0/3)</summary>

- [ ] **S23a** — Authorize frozen judging promotion (10 min)
- [ ] **S23b** — Codex · GPT-6.1 Sol, effort medium — Promote frozen revision to judging (20 min)
- [ ] **S23c** — Codex · GPT-6.1 Sol, effort medium — Verify deployed revision and smoke flow (30 min)

</details>

<details><summary><b>S24</b> — Three-minute demo video (0/10)</summary>

- [ ] **S24a** — Codex (native Claude) · Opus 5.5, effort high — Write evidence-backed three-minute script (30 min)
- [ ] **S24b** — Codex (native Claude) · Opus 5.5, effort high — Review script, captions and footage credits (30 min)
- [ ] **S24c** — Codex (native Claude) · Sonnet 5.5, effort high — Capture room rebuild and interview (30 min)
- [ ] **S24d** — Codex (native Claude) · Sonnet 5.5, effort high — Capture held-out prediction and reveal (30 min)
- [ ] **S24e** — Codex (native Claude) · Sonnet 5.5, effort high — Capture Apollo result and Mystery-g (30 min)
- [ ] **S24f** — Codex (native Claude) · Sonnet 5.5, effort high — Capture benchmark and Meta model evidence (30 min)
- [ ] **S24g** — Record optional voice-over part 1 (30 min)
- [ ] **S24h** — Record optional voice-over part 2 (30 min)
- [ ] **S24i** — Codex (native Claude) · Sonnet 5.5, effort high — Cut video and align captions (30 min)
- [ ] **S24j** — Codex (native Claude) · Sonnet 5.5, effort high — Check playback and approval-gated public video link (30 min)

</details>

<details><summary><b>S25</b> — README, attribution and public repo (0/5)</summary>

- [ ] **S25a** — Codex · GPT-6.1 Sol, effort medium — Write setup, architecture and Meta usage README (30 min)
- [ ] **S25b** — Codex · GPT-6.1 Sol, effort medium — Write footage attribution and public-package checklist (30 min)
- [ ] **S25c** — Codex · GPT-6.1 Sol, effort medium — Scan tracked files and full Git history (30 min)
- [ ] **S25d** — Authorize public repository visibility (10 min)
- [ ] **S25e** — Codex · GPT-6.1 Sol, effort medium — Make approved repo public and verify anonymous links (20 min)

</details>

<details><summary><b>S26</b> — Submit and post (0/3)</summary>

- [ ] **S26a** — Submit approved project on Cerebral Valley (30 min)
- [ ] **S26b** — Verify entry and contributor listing (30 min)
- [ ] **S26c** — Post demo on X and submit the post link (30 min)

</details>
