# Real2Simulation — QUEUE

Generated 2026-10-27 Asia/Dhaka from handoff v2, final plan.html SHA256 `0EAEBF9F243CA9F5F80A99E01550E06D688FBE0E5118AD4D302A178919490439`.

## Execution lock and scheduling

**Bounded Oct28 swarm exception:** direct owner authorizes inline agents until
18:30UTC Oct28 (Oct29 00:30Dhaka, direct owner extension), plus simulation-only S10/S11 against synthetic
fixtures despite unfinished physical S07/S09. Evidence:
Run-System/Runs/SWARM-20261028-2400/OWNER-SIMULATION-EXCEPTION.md.
Extension/owner-stop receipt: Run-System/Runs/SWARM-20261029-0030/OWNER-EXTENSION.md.
S10a/b and S11a/b/c are accepted local simulation leaves; this changes no physical
step/gate, S10c contacts, real-scene integration or S12 eligibility. Preserve
original dependencies as integration requirements, not silently deleted gates.

**Latest owner override (Oct28): ALL remaining GPT-6.1 Terra work uses existing managed `gpt-6.1-sol`; preserve lane, Owns, effort, dependencies and approval boundaries. No failure prerequisite. Historical completed receipts and Claude/S02c assignments unchanged.**

**Latest owner update (Oct29 evening), see AGENTS.md:** Owner (Oct29 ~17:20 Dhaka); supersedes older frugality notes only where they conflict. - Claude: weekly reset Oct30 18:00 Dhaka (12:00Z), >90% unused. Use it: run every   dependency-ready Claude row in parallel (isolated Owns, PARALLELISM_POLICY), full   30m windows. Remaining Opus medium -> Opus high; Haiku -> Sonnet high; S13a-d ->   Opus high (Codex capacity-paused). Cross-vendor reviews stay Sol. - Fixture-first unlock (QUEUE deps edited, not deleted): S14a, S15a, S17a start now   vs accepted S08/S09g/S10/S11 + visibly synthetic fixtures; S19a after S15b; S13a after   S04g+S06a; S06a after S05b. Real-integration deps moved onto checkpoint leaves   S06h(S05) S13f(S06d) S13h(S04,S06) S14g(S13) S15d(S14a) S15k(S09,S14) S17f(S14)   S19d(S15). Fixture leaves never claim gate/real-scene evidence. - Modal: monthly $30 is use-it-or-lose-it at month-end reset; $100 grant persists to   Oct2027. GPU order before reset: S05b -> S05c (all approved scenes) -> S05d, S07b ->   tracking on remaining approved clips, S06a-f. Once a probe gives measured cost, size   further useful jobs to consume remaining monthly credit by Oct31 (do not assume exact   reset time); no paid overage, no idle burn, ledger every job. Standing GPU auth reused. - AWS: owner reports quota increase APPROVED (requested: us-east-2, 8 vCPU G/VT   on-demand + spot; region/value not agent-verified). Still OFF for agents until Koushik   (1) creates the $50 EC2 budget alert and (2) supplies agent AWS access (no AWS CLI or   AWS key names on this PC). Credits expire 2027-05: AWS is post-reset overflow and   SAM 3D Objects/batch S18/S21, g6e.xlarge us-east-2, spot batch, stop each session.

**Latest owner reroute (Oct29), supersedes model labels only:** Owner (Oct29): Codex/Sol repeatedly looped into PARTIALs; Claude quota now OK. Model-column-only reroute in QUEUE; lanes, Owns, deps, minutes, approvals unchanged. - Opus 5.5 (high = PARTIAL parents/gates): runtime/GPU/reconstruction S05b-f,   S06a-h, S07b; prediction/Gate RS S12a-f; external Muse/SAM/Modal S13e-h;   LLM interview/Gate A S14a-h. - Sonnet 5.5 high: browser/screen QA/capture S04h, S22b-e/g-i, S24c-f/i/j. - Cross-vendor kept: R-R, R-RS, R-A now Sol high; R-C (Opus) and R-D (Sol) unchanged. - Stay Sol: S02f (blocker is no licensed calibrated source; Opus S02c/S02d hit   the same wall), S13a-d, S16, S18, S20, S21, S23, S25 (deterministic code/tests/   docs/deploy where Sol delivered: S04, S08, S07c-e, audits). Supersedes "do not use Claude extensively" and "preserve Claude usage" notes for these rows. No automatic swap back on failure: record it, controller decides. Routing only: nothing dispatched; owner takeover/fresh-instruction rule stands.

**S03 done (Oct 27). Koushik starts each run with `Complete run <ID>` or `Complete the next run` (see START.md and RUN_SYSTEM.md → Manual run protocol); a TODO row alone is not authorization.** Statuses: TODO, IN PROGRESS, PARTIAL, BLOCKED, DONE. RUNS.md is the generated checklist view of this table. Oct 27: S01a and S01c marked DONE from the owner checklist and DECISIONS_LOG.md; S06a, S07a and S13a now depend on S01a and S01c instead of all of S01, so the spikes no longer wait for sign-in testing (S01b).

- Fixed ownership lanes: CODEX-1, CODEX-2, CLAUDE; KOUSHIK is the human approval lane, not an agent. Manual concurrency follows PARALLELISM_POLICY.md: no fixed count, isolated independent same-lane shards allowed. Model reassignment still needs owner authority.
- Baseline source work totals **5220 minutes (87h)**. Current203 leaf timeboxes, including explicit recovery shards and eight cross-vendor reviews, sum **5725m**, leaving **275m** of the6000m envelope. R-M2 adds15m from that buffer. These are planning ceilings, not measured runtime or a finish estimate; historical decomposition receipts remain below.
- Every leaf <=30m. At minute 25 start no new implementation; unfinished work becomes PARTIAL and splits, never silently overruns or weakens checks.
- Step dependency means **all** source tasks and required reviews for that step DONE with acceptance evidence. Rows within a step are serial except S01c, which is independent of S01b.
- Dispatch CODEX-1: S05 then S07 before non-spike work (S08 may fill while approved clips are unavailable). CODEX-2: S02 browser sourcing and S04 shell as readiness permits. CLAUDE: S09 fixture work once S04a/S05a contracts land; final S09 integration still waits for S04/S05. Later choose dependency-ready rows, not numeric order alone.
- Owner-validated GPU baseline: ~20h need, ~15h current Modal allocation, reset on/after Nov1. S06p preparation is ready without S02; prioritize useful eligible GPU work before reset under API_BUDGET.md. Actual reconstruction/measurement jobs retain approved-input/licence and product dependencies; no dummy compute or spend expansion.
- S05a is contract/licence-only after S03; S05b and actual reconstruction wait for completed, owner-approved S02. No Gate R result is claimed from contract work.
- S01/S04 acceptance loop is explicitly split: S04a starts after S01a/S01c, while S01b sign-in verification waits for S04g and S04h waits for S01b. This preserves final step acceptance without a cycle.
- S12 waits for an actual Gate M result including explicit fallback, never an assumed pass. S22 judging access waits for written candidate-deployment approval; S23 is later promotion of a frozen revision, separately authorized.
- Source `Owns` paths below are proposed future paths, not existing product directories. Cross-lane write sets are disjoint. Within a lane, serial tasks may reuse paths. Shared manifest/lockfile changes go through CODEX-2 in a separate serialized integration run.
- Control-file updates and branch integration are serialized by the current control maintainer, never concurrent edits from all lanes. Read-only cross-vendor reviewers own only review evidence; implementation defects return to the source lane.
- After **every** run, update STATE, task status, decision/cost ledgers and a sanitized `Runs/<RID>/REPORT.md`; no report/product directories are created by S03.
- Models below are **plan routing labels, not verified availability or a claim this chat uses them**. Missing model/provider: stop that dispatch and log; no silent provider or credential change. Sol medium; high for gates; xhigh only escalation; never max. Sol high now owns the former Terra browser/screen work. Optional GPT-6 Luna high may assist mechanical metadata/fixtures only under the original lane with a deterministic check; never facts/design or terminal-heavy work. No planned Astra; at most one written-approved run after two same-gate Sol-xhigh failures. No GPT-5.6 Luna.
- Gate code must receive other-vendor review. Reviews are explicit overhead and never transfer source ownership. If 15m is insufficient, split and account against remaining buffer.
- No product live or external action today; a minimal coding-subscription CLI smoke task is allowed solely for S03 verification. Future live work must satisfy API_BUDGET and owner gates first. Fixtures must be visibly synthetic, never represented as gate/E4 proof.

## Retry holds

`runs_view.py` excludes these runs from Ready now before their explicit UTC
deadline, without changing PARTIAL to DONE/BLOCKED. Expiry permits one bounded
retry, not a claim that the source recovered. After another rate-limit/access
failure, record evidence and extend the hold; do not rapidly retry or bypass
restrictions. The orchestrator may clear a hold early only after recording a
genuinely new rights-cleared source or genuine recovery of the blocked execution
prerequisite. Lane/slot/ownership/approval checks still apply.

| Run | Retry not before (UTC) | Reason |
|---|---|---|

## Leaf tasks

| ID | Lane | Model / effort | Step | Min | Task | Depends | Owns (paths) | Acceptance / evidence | Status |
|---|---|---|---|---:|---|---|---|---|---|
| S01a | KOUSHIK | Human only | S01 | 30 | Review Meta access evidence and billing balance | — | evidence/owner/S01/ | Record owner-reported 44-token success separately from independently verified billing; reveal no key. | DONE |
| S01b | KOUSHIK | Human only | S01 | 30 | Verify Google, email OTP and guest access when S04 is available | S01a, S04g | evidence/owner/S01/ | All three flows have timestamped E2 evidence; until S04, this task waits. | DONE |
| S01c | KOUSHIK | Human only | S01 | 30 | Reconcile service readiness and dev-deploy approval | S01a | evidence/owner/S01/ | Record auth-only versus inference evidence and written dev approval; no extra accounts or purchases. | DONE |
| S02a | CODEX-2 | GPT-6.1 Terra / high | S02 | 30 | Source free-fall and Apollo 15 candidates | — | test-data/public/; clips.csv; evidence/clips/ | Record original source, rights and scale/timebase suitability for at least 3 fall candidates and Apollo 15. | DONE |
| S02b | CODEX-2 | GPT-6.1 Terra / high | S02 | 30 | Source projectile, bounce, pendulum and room candidates | S02a | test-data/public/; clips.csv; evidence/clips/ | Cover remaining experiment types and 3 room scenes; reject sports, NC/ND and unknown rights. | DONE |
| S02c | CODEX-2 | Opus 5.5 / high | S02 | 30 | Acquire licensed clips and record attribution | S02b | test-data/public/; clips.csv; evidence/clips/ | At least 10 usable clips; every file has a source, licence and required credit in clips.csv. | DONE |
| S02c1 | CODEX-2 | Opus 5.5 / high | S02 | 30 | Independently assess NASA real trajectory sources | S02b | evidence/clips/shards/NASA/; test-data/public/shards/NASA/ | Actual source/rights and original-frame suitability evidence or concrete no-usable-result/blocker; isolated report/manifest, no parent controls or merge. Follow S02C_PARALLEL.md. | DONE |
| S02c2 | CODEX-2 | Opus 5.5 / high | S02 | 30 | Independently assess non-sports stock Earth physics | S02b | evidence/clips/shards/STOCK/; test-data/public/shards/STOCK/ | Actual Pexels/Pixabay source/rights and original-frame fall/bounce/projectile evidence or concrete no-usable-result/blocker; isolated report/manifest, no parent controls or merge. Follow S02C_PARALLEL.md. | DONE |
| S02d | CODEX-2 | Opus 5.5 / high | S02 | 20 | Inspect metadata and known-size references | S02c | test-data/public/; clips.csv; evidence/clips/ | Every row has file fps, duration and scale reference or scene-only flag; record slow-motion uncertainty. | DONE |
| S02e | KOUSHIK | Human only | S02 | 10 | Approve the clip list | S02d | evidence/owner/S02/ | Koushik's explicit approval or exclusions are recorded; no agent substitutes approval. | DONE |
| S02f | CODEX-2 | GPT-6.1 Sol / high | S07 | 30 | Find licensed calibrated Earth-fall replacements | S02e | evidence/clips/calibration-recovery/S02f/; Run-System/Runs/S02f/ | Primary-source shortlist with scale, capture-clock, rights and independent-trial limits; no approval or Gate M substitution. | PARTIAL |
| S02g | CODEX-2 | GPT-6.1 Sol / high | S07 | 30 | Verify original FF01/FF02 calibration sources | S02e | evidence/clips/calibration-recovery/S02g/; Run-System/Runs/S02g/ | Source-backed scale/timebase and capture-group determination; negative finding may complete forensics, not S07a. | DONE |
| S02h | CODEX-2 | GPT-6.1 Sol / high | S07 | 30 | Resolve RP03 capture mapping and geometric identifiability | S02e | evidence/clips/calibration-recovery/S02h/; Run-System/Runs/S02h/ | Exact frame/source-backed mapping and scale feasibility or specific missing evidence; no g/approval inference. | DONE |
| S02i | CODEX-2 | GPT-6.1 Sol / high | S07 | 30 | Audit RP01 side-view metric trajectory segments | S02e | evidence/clips/calibration-recovery/S02i/; Run-System/Runs/S02i/ | Actual useful segments, independent scale/clock and uncertainty; do not invent full-flight prerequisite. | DONE |
| S07r | CODEX-1 | GPT-6.1 Sol / high | S07 | 20 | Reconcile input readiness and approved small-sample fallback | S02e | evidence/S07/readiness-review/; Run-System/Runs/S07r/ | Source-backed contract-conflict table and scoped next-run recommendation; no changed gate/approval/product code. | DONE |
| S03a | CODEX-1 | GPT-6.1 Sol / medium | S03 | 20 | Initialize fresh local repository and control policy | — | .gitignore; AGENTS.md; JUDGE_RUBRIC.md; QUEUE.md; STATE.md; DECISIONS_LOG.md; API_BUDGET.md | Independent new Git history; no remote or imported code; safety, rubric, recovery and budgets written. | DONE |
| S03b | CODEX-1 | GPT-6.1 Sol / medium | S03 | 20 | Decompose and validate the complete handoff queue | S03a | .gitignore; AGENTS.md; JUDGE_RUBRIC.md; QUEUE.md; STATE.md; DECISIONS_LOG.md; API_BUDGET.md | All 26 steps covered; every task <=30m; dependencies acyclic; cross-lane paths disjoint; only S03 completed. | DONE |
| S03c | CODEX-1 | GPT-6.1 Sol / medium | S03 | 20 | Implement and verify Windows dispatcher on harmless runs | S03b | Run-System/; .env.example | Fresh worktree/process per run; max2; timeout<=1800s; quota halt; RUN_LOG entries; harmless dry-run evidence, no product implementation. | DONE |
| M-ROOT | CODEX-1 | GPT-6.1 Sol / medium | S03 | 30 | Consolidate event-root repository and merge context | S03c | AGENTS.md; .gitignore; DECISIONS_LOG.md; README.md; tasks for the owner.md; START.md; STATE.md | Preserve Git/history and event context; no parent/plan edits; restricted paths ignored; old folder empty before removal | DONE |
| M-PROMPTS | CODEX-1 | GPT-6.1 Sol / medium | S03 | 30 | Short-prompt self-serve dispatcher and event-root verification | M-ROOT | Run-System/ | Fresh one-line prompt; task manifest; .worktrees confinement; stop command; tests and post-commit dry run | DONE |
| S04a | CODEX-2 | GPT-6.1 Sol / medium | S04 | 30 | Define shell interfaces and fixture mount points | S01a, S01c, S03 | Build/web/src/shell/; Build/web/src/auth/; Build/web/src/app/; Build/web/package.json; Build/api/health/; Build/worker/health/; infra/railway/dev/ | Document viewer, job and guest-library integration contracts; no ownership overlap. | DONE |
| S04b | CODEX-2 | GPT-6.1 Sol / medium | S04 | 30 | Create Next.js shell and isolated route layout | S04a | Build/web/src/shell/; Build/web/src/auth/; Build/web/src/app/; Build/web/package.json; Build/api/health/; Build/worker/health/; infra/railway/dev/ | Shell starts with deterministic smoke check; viewer/workspace modules remain separate. | DONE |
| S04c | CODEX-2 | GPT-6.1 Sol / medium | S04 | 30 | Wire Clerk shared-Google and OTP configuration | S04b | Build/web/src/shell/; Build/web/src/auth/; Build/web/src/app/; Build/web/package.json; Build/api/health/; Build/worker/health/; infra/railway/dev/ | No custom Google client or secret in browser bundles; safe missing-config behavior. | DONE |
| S04d | CODEX-2 | GPT-6.1 Sol / medium | S04 | 30 | Add guest library route and authorization boundary | S04c | Build/web/src/shell/; Build/web/src/auth/; Build/web/src/app/; Build/web/src/proxy.js; Build/web/package.json; Build/api/health/; Build/worker/health/; infra/railway/dev/ | Logged-out /library works; private scene access remains denied. | DONE |
| S04e | CODEX-2 | GPT-6.1 Sol / medium | S04 | 30 | Create FastAPI and worker health skeletons | S04d | Build/web/src/shell/; Build/web/src/auth/; Build/web/src/app/; Build/web/package.json; Build/api/health/; Build/worker/health/; infra/railway/dev/ | Both health endpoints respond 200 locally with targeted tests. | DONE |
| S04f | CODEX-2 | GPT-6.1 Sol / medium | S04 | 30 | Configure dev Postgres, Redis and bucket integration | S04e | Build/web/src/shell/; Build/web/src/auth/; Build/web/src/app/; Build/web/package.json; Build/api/health/; Build/worker/health/; infra/railway/dev/ | Dev-only resources identified; health distinguishes unavailable dependencies. | DONE |
| S04g | CODEX-2 | GPT-6.1 Sol / medium | S04 | 30 | Deploy the dev skeleton via Railway | S04f | Build/web/src/shell/; Build/web/src/auth/; Build/web/src/app/; Build/web/package.json; Build/api/health/; Build/worker/health/; infra/railway/dev/ | Dev URL serves shell and health endpoints; production build runs on Railway. | DONE |
| S04g1 | CODEX-2 | GPT-6.1 Sol / medium | S04 | 15 | Harden dev deployment verifier semantic checks | S04g | infra/railway/dev/ | Exact endpoint service/status/revision/dependency checks reject wrong or missing fields; offline regression fails before fix and passes after; read-only live dev checks pass or failure recorded. No deploy or credentials. | DONE |
| S04g2 | CODEX-2 | GPT-6.1 Sol / medium | S04 | 15 | Preserve staging destination guards under Python optimization | S04g1, F-CODEX-2-2 | infra/railway/dev/; evidence/S04g2/ | Normal and optimized execution reject existing destinations and invalid input without writes; isolated staging manifests remain correct. No upload/deploy/credentials. | DONE |
| S04h | CODEX-2 | Sonnet 5.5 / high | S04 | 30 | Verify sign-in, guest route and dev health | S04g1, S01b | Build/web/src/shell/; Build/web/src/auth/; Build/web/src/app/; Build/web/package.json; Build/api/health/; Build/worker/health/; infra/railway/dev/ | E4 evidence for Google, OTP, guest and both health endpoints; log fallback if Clerk blocks. | DONE |
| S04i | CODEX-2 | GPT-6.1 Sol / high | S04 | 30 | Connect private scene repository and mount workspace route | S04h, S15j | Build/web/src/app/; Build/web/src/auth/; Build/web/src/shell/; Build/web/src/proxy.js; Build/web/package.json; tests/web-private/; evidence/S04i/ | Controller-added Oct30 (S15k blocker: (private) layout notFound). Signed-in owner reaches /workspace/[sceneId] for own scenes; other users and guests get 404; repository is dev-only and labelled; no auth-provider/credential changes. | DONE |
| S04j | CLAUDE | Opus 5.5 / high | S04 | 30 | Wire guest library page to manifest and simulated replay | S04i, S18k, S09k | Build/web/src/app/(public)/library/; Build/web/src/app/api/library/; tests/web-library/; evidence/S04j/ | Controller-added Oct30 army period (owner: Claude does all rows). Logged-out /library lists guest manifest entries with labels; playable simulated traces replay via viewer trajectory-replay; UNAVAILABLE entries readable; no GPU/API calls; Mystery-g answer never served. | DONE |
| S04k | CLAUDE | Opus 5.5 / high | S04 | 30 | Serve guest library from build-time snapshot | S04j | Build/web/src/app/api/library/; infra/railway/dev/stage.py; infra/railway/dev/web.Dockerfile; tests/web-library/; evidence/S04k/ | Controller-added Oct30: web image has no Python, so S04j runtime python spawn would 503 on Railway. Snapshot guest manifest+objects at staging/build time with sha verification; no runtime Python; fail closed; no deploy. | DONE |
| S04l | CLAUDE | Opus 5.5 / medium | S04 | 30 | Polish guest library page copy and UI | S04k, S18l | Build/web/src/app/(public)/library/; tests/web-library/; evidence/S04l/ | Controller-added Oct30 army: align Mystery-g card with S18l honest label (Earth-g practice shape; blind play in /lab); Mobbin/myfront polish; 375px; no new data claims. | DONE |
| S05a | CODEX-1 | GPT-6.1 Sol / medium | S05 | 30 | Check reconstruction licences and freeze scene artifact contract | S03 | Build/reconstruction/spike/; contracts/scene/; test-data/synthetic/scene/; evidence/S05/ | Read upstream model/weight licences; record permissive-use decision or blocker; define fixture artifact. | DONE |
| S05b | CODEX-1 | Opus 5.5 / high | S05 | 30 | Probe MapAnything on the first licensed scene | S05a, S02 | Build/reconstruction/spike/; contracts/scene/; test-data/synthetic/scene/; evidence/S05/ | Record output, runtime and actual GPU/VRAM; no AWS launch. | DONE |
| S05c | CODEX-1 | Opus 5.5 / high | S05 | 30 | Reconstruct remaining scene clips | S05b | Build/reconstruction/spike/; contracts/scene/; test-data/synthetic/scene/; evidence/S05/ | Three scene outputs or explicit failure evidence; preserve original clip IDs. | DONE |
| S05d | CODEX-1 | Opus 5.5 / high | S05 | 30 | Fit floor, metric scale and gravity orientation | S05c | Build/reconstruction/spike/; contracts/scene/; test-data/synthetic/scene/; evidence/S05/ | Known-object scale and A4 plane-normal metrics reproducible per clip. | DONE |
| S05e | CODEX-1 | Opus 5.5 / high | S05 | 30 | Run Gate R and inspect reconstruction failures | S05d | Build/reconstruction/spike/; contracts/scene/; test-data/synthetic/scene/; evidence/S05/ | At least 2/3 within 10%, orientation within 5 degrees and <=4 GPU min/scene, or measured failures. | DONE |
| S05f | CODEX-1 | Opus 5.5 / high | S05 | 30 | Apply the named fallback and checkpoint Gate R | S05e, R-R | Build/reconstruction/spike/; contracts/scene/; test-data/synthetic/scene/; evidence/S05/ | Record pass/fallback1/fallback2 with metrics and licence decision; prepare cross-vendor review. | DONE |
| S06a | CODEX-1 | Opus 5.5 / high | S06 | 30 | Define reproducible GPU image and dry-run contract | S05b, S01a, S01c | Build/gpu/; infra/modal/; evidence/S06/ | Pinned reconstruction inputs and CPU/dry-run contract documented. | DONE |
| S06p | CODEX-1 | GPT-6.1 Sol / medium | S06 | 20 | Verify existing Modal allocation and pre-reset GPU readiness | S03, S01a, S01c | evidence/S06/pre-reset/ | Sanitized account/allocation/reset or explicit access limitation; reconcile existing spend limits; concrete eligible-job prerequisites and Oct28–31/post-reset schedule. Read-only readiness, no GPU launch or uploads. | DONE |
| S06b | CODEX-1 | Opus 5.5 / high | S06 | 30 | Package MapAnything runtime | S06a | Build/gpu/; infra/modal/; evidence/S06/ | Image builds with recorded dependency/licence checks. | DONE |
| S06c | CODEX-1 | Opus 5.5 / high | S06 | 30 | Add optional SAM 3D Objects path | S06b | Build/gpu/; infra/modal/; evidence/S06/ | Check licence and available VRAM first; failure leaves primitive-mesh path usable. | DONE |
| S06d | CODEX-1 | Opus 5.5 / high | S06 | 30 | Add Modal scene job entry point | S06c | Build/gpu/; infra/modal/; evidence/S06/ | One scene artifact contract validated; no personal uploads. | DONE |
| S06e | CODEX-1 | Opus 5.5 / high | S06 | 30 | Add cold-start timing and cost instrumentation | S06d | Build/gpu/; infra/modal/; evidence/S06/ | Scene logs include cold start, GPU seconds and estimated versus billed cost. | DONE |
| S06f | CODEX-1 | Opus 5.5 / high | S06 | 30 | Exercise one licensed room clip on Modal | S06e | Build/gpu/; infra/modal/; evidence/S06/ | Actual scene completes or failure evidence captured; target <=5 min including cold start. | DONE |
| S06g | CODEX-1 | Opus 5.5 / medium | S06 | 30 | Verify CPU dry-run and disabled AWS adapter | S06f | Build/gpu/; infra/modal/; evidence/S06/ | Dry-run succeeds without GPU; AWS cannot activate without owner quota and budget gates. | DONE |
| S06h | CODEX-1 | Opus 5.5 / medium | S06 | 30 | Checkpoint GPU runtime and fallback evidence | S06g, S05 | Build/gpu/; infra/modal/; evidence/S06/ | Record measured cost, timings and chosen renderer/reconstruction path. | DONE |
| S07a | CODEX-1 | GPT-6.1 Sol / medium | S07 | 30 | Define scale, timestamps and held-out tracking inputs | S01a, S01c, S02, S03 | Build/measurement/; tests/measurement/; evidence/S07/ | Current scoped-approved Earth-fall candidate list and actual sample size recorded; scale/capture unknowns and blockers explicit; provenance/immutable split/abstention contract tests pass. Missing target-three shortlist and metric eligibility remain holds, not implementation prerequisites. See S07r/controller decision. | DONE |
| S07b | CODEX-1 | Opus 5.5 / high | S07 | 30 | Implement SAM 3.1 tracking adapter | S07a | Build/measurement/tracking.py; Build/measurement/TRACKING.md; Build/measurement/runtime/; tests/measurement/test_tracking.py; evidence/S07/S07b/ | Sanitized track output carries frame/time coordinates and provenance. | DONE |
| S07c | CODEX-1 | GPT-6.1 Sol / medium | S07 | 30 | Implement deterministic free-fall fit | S07a | Build/measurement/free_fall.py; Build/measurement/FITTING.md; tests/measurement/test_free_fall.py; evidence/S07/S07c/ | Synthetic tracks recover known g; units and residuals tested. | DONE |
| S07d | CODEX-1 | GPT-6.1 Sol / medium | S07 | 30 | Detect slow-motion and propagate measurement uncertainty | S07c | Build/measurement/uncertainty.py; Build/measurement/UNCERTAINTY.md; tests/measurement/test_uncertainty.py; evidence/S07/S07d/ | Timebase ambiguity is explicit; uncertainty includes scale and timestamps. | DONE |
| S07e | CODEX-1 | GPT-6.1 Sol / high | S07 | 30 | Run Earth Gate M measurements | S07d | Build/measurement/gate_m.py; Build/measurement/GATE_M.md; tests/measurement/test_gate_m.py; evidence/S07/S07e/ | 2/3 within 5% of 9.81 with uncertainty covering error, or honest failure/sample size. | DONE |
| S07f | CODEX-1 | GPT-6.1 Sol / high | S07 | 30 | Evaluate Apollo stretch and record Gate M decision | S07e, R-M | Build/measurement/; tests/measurement/; evidence/S07/ | Moon target within 15% if available; table-plane fallback logged if Earth gate fails. | DONE |
| S07g | CLAUDE | Opus 5.5 / high | S07 | 30 | Owner clips: register in clips.csv and measure g on 01_demo_hero with the real pipeline | S07e | clips.csv; Build/measurement/; tests/measurement/; evidence/S07/S07g/ | (1) all 12 owner trims in clips.csv as OWNER_RECORDED (sha256, fps/PTS, duration, scale book edge 0.2028 m, private processing approved, public use pending owner go-ahead; videos stay gitignored); (2) real SAM 3.1 track (Modal, standing GPU auth, ledgered, trims only) + scale + deterministic fit on 01_demo_hero -> g +/- u with uncertainty budget (scale px, timing/PTS, fit) vs local 9.79, labelled MEASURED; no tuning to the target; (3) tests + evidence; failures recorded honestly. | PARTIAL |
| S07i | CLAUDE | Opus 5.5 / high | S07 | 30 | OWN01 measured g from the real SAM 3.1 track; prepare one batched track for OWN02-OWN12 | S07g | Build/measurement/; tests/measurement/; evidence/S07/S07i/ | (1) from evidence/S07/S07g/track-own01.json: scale from SAM masks/box of the book (pre-release frames, 0.2028 m edge) + deterministic free_fall.py fit with split fixed first -> g +/- u with budget vs 9.79, labelled MEASURED; held-out residuals; (2) modal_track.py batch mode: several clips with per-clip windows in ONE admitted invocation (all-in bound <= $0.40, the remaining standalone envelope), tested + dry-run, exact command for the controller; per-clip fall windows for OWN02-OWN12 fixed before tracking; (3) no tuning to 9.79. | TODO |
| S07h | CLAUDE | Opus 5.5 / high | S07 | 30 | Owner clips 02-06: held-out and robustness evaluation with the S07g pipeline | S07i | Build/measurement/; tests/measurement/; evidence/S07/S07h/ | (1) same frozen pipeline/params on 02_live_check, 03, 04, 05a-d (held-out) and 06 robustness clips; per-clip g +/- u or explicit abstain reason; (2) repeatability spread of 05a-d and coverage vs 9.79; robustness outcomes (clutter, low-res, front cover, no sheet); (3) table + ledger, no parameter changes after seeing results. | TODO |
| S08a | CODEX-1 | GPT-6.1 Sol / medium | S08 | 30 | Define versioned experiment schema and units | S03 | contracts/experiment/; Build/templates/; tests/spec/ | Schema captures source labels, scene constraints and physical units. | DONE |
| S08b | CODEX-1 | GPT-6.1 Sol / medium | S08 | 30 | Validate numeric ranges and dimensional consistency | S08a | contracts/experiment/; Build/templates/; tests/spec/ | Bad units, NaN and invalid ranges rejected with readable errors. | DONE |
| S08c | CODEX-1 | GPT-6.1 Sol / medium | S08 | 30 | Validate geometry and numerical stability | S08b | contracts/experiment/; Build/templates/; tests/spec/ | Out-of-scene and unstable setups rejected; add negative fixtures. | DONE |
| S08d | CODEX-1 | GPT-6.1 Sol / medium | S08 | 30 | Add free-fall template and analytic answer | S08c | contracts/experiment/; Build/templates/; tests/spec/ | Template validates and exposes deterministic analytic output. | DONE |
| S08e | CODEX-1 | GPT-6.1 Sol / medium | S08 | 30 | Add projectile template and analytic answer | S08d | contracts/experiment/; Build/templates/; tests/spec/ | Template validates and exposes deterministic analytic output. | DONE |
| S08f | CODEX-1 | GPT-6.1 Sol / medium | S08 | 30 | Add ramp template and analytic answer | S08e | contracts/experiment/; Build/templates/; tests/spec/ | Template validates and exposes deterministic analytic output. | DONE |
| S08g | CODEX-1 | GPT-6.1 Sol / medium | S08 | 30 | Add pendulum template and analytic answer | S08f | contracts/experiment/; Build/templates/; tests/spec/ | Template validates and exposes deterministic analytic output. | DONE |
| S08h | CODEX-1 | GPT-6.1 Sol / medium | S08 | 30 | Run schema and ten-bad-spec regression checks | S08g | contracts/experiment/; Build/templates/; tests/spec/ | All schema tests pass; 10 deliberate invalid specs rejected; all 4 analytic oracles available. | DONE |
| S08i | CODEX-1 | GPT-6.1 Sol / medium | S08 | 30 | Reject unrepresentable fall displacement and extreme sample times | S08h, F-CODEX-1-2 | contracts/experiment/; Build/templates/free_fall.py; tests/spec/; evidence/S08/numeric-guards/ | Readable rejection for signed huge times and collapsed stop plane; one-ULP positive controls, normal oracles and full spec regressions pass. Local synthetic evidence only. | DONE |
| S09a | CLAUDE | Opus 5.5 / medium | S09 | 30 | Define viewer adapter and synthetic fixture scene | S04a, S05a | Build/web/src/viewer/; tests/viewer/; evidence/S09/ | Use S04a/S05a contracts; fixture marked synthetic, not Gate R evidence. | DONE |
| S09b | CLAUDE | Opus 5.5 / medium | S09 | 30 | Render fixture geometry and orbit camera | S09a | Build/web/src/viewer/; tests/viewer/; evidence/S09/ | Fixture loads, orbits and unmounts without leaking resources. | DONE |
| S09c | CLAUDE | Opus 5.5 / medium | S09 | 30 | Load real point-cloud or splat artifacts | S09b | Build/web/src/viewer/; tests/viewer/; evidence/S09/ | Artifact loader validates inputs; real artifact integration still waits for S05. | DONE |
| S09d | CLAUDE | Opus 5.5 / medium | S09 | 30 | Add colliders, camera path and scene labels | S09c | Build/web/src/viewer/; tests/viewer/; evidence/S09/ | Fixture interaction shows aligned geometry and labels. | DONE |
| S09e | CLAUDE | Opus 5.5 / medium | S09 | 30 | Implement pixel-ratio and detail budgets | S09d | Build/web/src/viewer/; tests/viewer/; evidence/S09/ | DPR cap and reduced detail are deterministic per device budget. | DONE |
| S09f | CLAUDE | Opus 5.5 / medium | S09 | 30 | Pause rendering when idle or hidden | S09e | Build/web/src/viewer/; tests/viewer/; evidence/S09/ | Idle/hidden viewer stops unnecessary render work; resumes correctly. | DONE |
| S09g | CLAUDE | Opus 5.5 / medium | S09 | 30 | Add 375px reduced-detail viewer layout | S09f | Build/web/src/viewer/; tests/viewer/; evidence/S09/ | No horizontal scroll at 375px; controls remain usable. | DONE |
| S09h | CLAUDE | Opus 5.5 / high | S09 | 30 | Integrate three measured scene artifacts | S09g, S04, S05 | Build/web/src/viewer/; tests/viewer/; evidence/S09/ | Real integration waits for S04 and S05; three artifact loads verified. | DONE |
| S09i | CLAUDE | Opus 5.5 / medium | S09 | 30 | Measure fps and memory on target laptop | S09h | Build/web/src/viewer/; tests/viewer/; evidence/S09/ | Three scenes orbit >=30fps on identified hardware, or evidence-backed proxy fallback. | DONE |
| S09j | CLAUDE | Opus 5.5 / medium | S09 | 30 | Checkpoint viewer evidence and visual fixes | S09i | Build/web/src/viewer/; tests/viewer/; evidence/S09/ | Document 375px and performance results; separate fixture from real-scene evidence. | DONE |
| S09k | CLAUDE | Opus 5.5 / medium | S09 | 30 | Add simulated-trajectory replay to viewer | S09j, S18g | Build/web/src/viewer/; tests/viewer/; evidence/S09/ | Controller-added Oct30 (S18g deferral). Viewer replays a bounded hashed simulated trace (SIMULATED banner, no geometry invented, mystery mode stays refused); cleanup on unmount; 375px. | DONE |
| S10a | CODEX-1 | GPT-6.1 Sol / medium | S10 | 30 | Build validated-spec apparatus placement | S08, S09 | Build/simulator/; tests/simulator/; evidence/S10/ | Only schema-valid apparatus can enter scene geometry. | DONE |
| S10b | CODEX-1 | GPT-6.1 Sol / medium | S10 | 30 | Implement fixed-step RK4 core | S10a | Build/simulator/; tests/simulator/; evidence/S10/ | Integrator has deterministic step size and analytic smoke tests. | DONE |
| S10c | CODEX-1 | GPT-6.1 Sol / medium | S10 | 30 | Integrate Rapier contacts | S10b | Build/simulator/; tests/simulator/; evidence/S10/ | Contact state mapped to common simulator output without hidden numeric defaults. | DONE |
| S10d | CODEX-1 | GPT-6.1 Sol / medium | S10 | 30 | Implement free-fall and projectile runs | S10c | Build/simulator/; tests/simulator/; evidence/S10/ | Both templates output time-series and analytic comparison inputs. | DONE |
| S10e | CODEX-1 | GPT-6.1 Sol / medium | S10 | 30 | Implement ramp and pendulum runs | S10d | Build/simulator/; tests/simulator/; evidence/S10/ | Both templates output time-series and analytic comparison inputs. | DONE |
| S10f | CODEX-1 | GPT-6.1 Sol / medium | S10 | 30 | Implement seeded replay | S10e | Build/simulator/; tests/simulator/; evidence/S10/ | Repeated same-seed trial hashes and numeric traces match. | DONE |
| S10g | CODEX-1 | GPT-6.1 Sol / medium | S10 | 30 | Hide Mystery-g until fit/reveal | S10f | Build/simulator/; tests/simulator/; evidence/S10/ | UI-facing contract never leaks hidden g before fit. | DONE |
| S10h | CODEX-1 | GPT-6.1 Sol / medium | S10 | 30 | Run four-template Gate P regression | S10g | Build/simulator/; tests/simulator/; evidence/S10/ | All templates within 0.5% of analytic answers; preserve measured errors. | DONE |
| S10i | CODEX-1 | GPT-6.1 Sol / high | S10 | 30 | Resolve contact jitter with RK4-only fallback if needed | S10h | Build/simulator/; tests/simulator/; evidence/S10/ | Any affected template disables dragging; no weakened tolerance. | DONE |
| S10j | CODEX-1 | GPT-6.1 Sol / high | S10 | 30 | Checkpoint Gate P and review packet | S10i, R-P | Build/simulator/; tests/simulator/; evidence/S10/ | Record numeric gate decision and deterministic replay evidence. | DONE |
| S10k | CODEX-1 | GPT-6.1 Sol / high | S10 | 30 | Harden lab session cancellation and stale reveal boundaries | S10j | Build/lab/session-service.mjs; tests/lab/session-service.test.mjs; evidence/S10/session-hardening/ | Reproduced abort and stale/evicted-session failures fixed; fresh actual bridge tests and targeted native gate review. Simulation-only. | DONE |
| S10l | CODEX-2 | GPT-6.1 Sol / medium | S10 | 30 | Preserve complete plotted traces and honest mobile lab labels | S10j | Build/web/src/lab/; tests/lab/ui-contract.test.mjs; evidence/S10/ui-hardening/ | Plot all bounded finite observations, correct displacement/unsupported-fit labels, reject malformed reveal envelope; actual IAB375px flow. | DONE |
| S10m | CODEX-1 | GPT-6.1 Sol / high | S10 | 30 | Reject nonrepresentable contact geometry and initial penetration | S10j | Build/simulator/contacts.mjs; tests/simulator/contacts.test.mjs; evidence/S10/contact-hardening/ | Resolve both R10-S10-audit P2s; preserve exact-touch positive case, analytic0.005 threshold and targeted native re-review. | DONE |
| S10n | CODEX-1 | GPT-6.1 Sol / high | S10 | 30 | Run validated normal-mode synthetic trials in the real browser | S10j | Build/web/src/lab/; Build/lab/session-bridge.py; Build/lab/session-service.mjs; tests/lab/; evidence/S10/browser-simulation/; evidence/S10/browser-transport/ | Reuse actual four RK4 engines in browser, bound validated normal-only DTO, preserve zero Mystery setup leakage; actual IAB375px computation and source/limits verified. | DONE |
| S10o | CODEX-1 | GPT-6.1 Sol / high | S10 | 30 | Repair independent valid-domain RK4 and analytic model findings | S10n | Build/simulator/rk4.mjs; Build/simulator/extended-templates.mjs; tests/simulator/; evidence/S10/numerical-recovery/ | S08 model/RK4 finite recovery, unchanged analytic0.005, recovery25 and combined simulator54 PASS; frozen15/17 retained with explicit incompatible-energy decision, native noP0-P2; R16 combined UI/build verified. | DONE |
| S10p | CODEX-1 | GPT-6.1 Sol / high | S10 | 30 | Stabilize replay canonicalization and initial snapshot consistency | S10j | Build/simulator/replay.mjs; tests/simulator/; evidence/S10/replay-recovery/ | Frozen replay31 and recovery checks; parent52 including actual Rapier contact PASS; one detached snapshot/metadata first, ordinary JSON hashes preserved, consistency not authentication; native noP0-P2. | DONE |
| S10q | CODEX-1 | GPT-6.1 Sol / high | S10 | 30 | Correct local bridge byte decoding and output ceiling | S10n | Build/lab/session-service.mjs; tests/lab/; evidence/S10/transport-recovery/ | SplitUTF8/raw1e6-byte ceiling corrected; parent46 PASS, cancellation/capacity held until close; latentP3 fixed-ASCII reachability retained; native noP0-P2. | DONE |
| S10r | CODEX-2 | GPT-6.1 Sol / high | S10 | 30 | Harden exported fit-reveal and finite plotting helpers | S10n, S10l, S11l | Build/web/src/lab/fit-contract.mjs; tests/lab/ui-helper-*.test.mjs; evidence/S10/ui-helper-recovery/; evidence/S10/ui-helper-oracle/ | Four frozen latentP3s fixed without oracle edits; independent exact dyadic oracle plus recovery/existing/current tests69/69 PASS, native noP0-P2, actual375px normal/Mystery and fresh local production build/boundary checks; R17 integration receipt. | DONE |
| S11a | CODEX-1 | GPT-6.1 Sol / medium | S11 | 30 | Define instrument and fitter API contracts | S07, S08 | Build/instruments/; Build/fitter/; contracts/fit/; tests/fitter/ | Numbers carry units, uncertainty, provenance and measured/simulated labels. | DONE |
| S11b | CODEX-1 | GPT-6.1 Sol / medium | S11 | 30 | Model stopwatch reaction error | S11a | Build/instruments/; Build/fitter/; contracts/fit/; tests/fitter/ | Seeded stopwatch noise is testable and documented. | DONE |
| S11c | CODEX-1 | GPT-6.1 Sol / medium | S11 | 30 | Model camera, ruler and light-gate error | S11b | Build/instruments/; Build/fitter/; contracts/fit/; tests/fitter/ | Quantization/resolution behavior verified on deterministic fixtures. | DONE |
| S11d | CODEX-1 | GPT-6.1 Sol / medium | S11 | 30 | Implement least-squares fitter | S11c | Build/instruments/; Build/fitter/; contracts/fit/; tests/fitter/ | Known synthetic parameters recovered; degenerate fits rejected. | DONE |
| S11e | CODEX-1 | GPT-6.1 Sol / medium | S11 | 30 | Add AIC model selection and residuals | S11d | Build/instruments/; Build/fitter/; contracts/fit/; tests/fitter/ | Model-choice and residual output verified against controlled inputs. | DONE |
| S11f | CODEX-1 | GPT-6.1 Sol / medium | S11 | 30 | Add Jacobian uncertainty | S11e | Build/instruments/; Build/fitter/; contracts/fit/; tests/fitter/ | Covariance calculation handles rank deficiency honestly. | DONE |
| S11g | CODEX-1 | GPT-6.1 Sol / medium | S11 | 30 | Run hundred-seed coverage regression | S11f | Build/instruments/; Build/fitter/; contracts/fit/; tests/fitter/ | 95% interval covers true g in >=90/100 runs, or explicitly log miscalibration. | DONE |
| S11h | CODEX-1 | GPT-6.1 Sol / medium | S11 | 30 | Finalize tool-only numeric API and evidence | S11g | Build/instruments/; Build/fitter/; contracts/fit/; tests/fitter/ | Consumers receive fitter numbers only; uncertainty changes documented, not hidden. | DONE |
| S11i | CODEX-1 | GPT-6.1 Sol / high | S11 | 30 | Correct finite-sample coverage and declared uncertainty overconfidence | S11h | Build/fitter/; tests/fitter/; contracts/fit/; evidence/S11/uncertainty-hardening/ | Resolve R10-S11-audit findings with statistically defensible uncertainty/metadata, fresh multi-seed evidence and targeted native re-review; no physical claim. | DONE |
| S11j | CODEX-1 | GPT-6.1 Sol / high | S11 | 30 | Stabilize full covariance and reject lost residual variance | S11i | Build/fitter/core.py; Build/fitter/README.md; tests/fitter/; evidence/S11/invariants/; evidence/S11/covariance-recovery/ | Independent exact-rational regressions for negative/invalid covariance and residual-square underflow; stable QR factor propagation or honest unavailable; preserve known-zero sigma; fresh checks and narrow native re-review. | DONE |
| S11k | CODEX-1 | GPT-6.1 Sol / high | S11 | 30 | Correct virtual-instrument half-step and lattice rounding | S11j | Build/instruments/synthetic.py; tests/instruments/; evidence/S11/instrument-invariants/ | Frozen dyadic regressions and existing decimal tie semantics preserved by split-floor fix; source82791f3, fresh22 instruments/17 lab/45 fitter and actual IAB375; native noP0-P2; R15 fresh integration receipt. | DONE |
| S11l | CODEX-1 | GPT-6.1 Sol / high | S11 | 30 | Preserve residual scale in RMSE and AIC model selection | S11j | Build/fitter/core.py; Build/fitter/api.py; tests/fitter/; evidence/S11/model-selection-recovery/ | Stable residual scale fixes wrong AIC/RMSE; parent65 fitter PASS, exactzero vs underflow honest, sigmafloor unknown retained; native noP0-P2; actual375px normal/Mystery fit verified. | DONE |
| S12a | CODEX-1 | Opus 5.5 / high | S12 | 30 | Define calibration and withheld-frame boundary | S07r, S07a, S07b, S07c, S07d, S07e, S07f, S10, S11 | Build/real2sim/; tests/prediction/; evidence/S12/ | Training prefix and held-out suffix immutable; no evaluation leakage; Gate M result required. | DONE |
| S12b | CODEX-1 | Opus 5.5 / high | S12 | 30 | Transfer measured parameters into simulator | S12a | Build/real2sim/; tests/prediction/; evidence/S12/ | g, speed, friction and restitution retain provenance and uncertainty. | DONE |
| S12c | CODEX-1 | Opus 5.5 / high | S12 | 30 | Predict held-out projectile and bounce motion | S12b | Build/real2sim/; tests/prediction/; evidence/S12/ | Predictions generated without reading held-out observations. | DONE |
| S12d | CODEX-1 | Opus 5.5 / high | S12 | 30 | Predict pendulum continuation and overlay contract | S12c | Build/real2sim/; tests/prediction/; evidence/S12/ | Predictions and actual frames aligned by clip/timebase; renderer consumes immutable traces. | DONE |
| S12e | CODEX-1 | Opus 5.5 / high | S12 | 30 | Run Gate RS on public motion clips | S12d | Build/real2sim/; tests/prediction/; evidence/S12/ | Median normalized held-out error <=5% across projectile, bounce and pendulum, or measured shortfall. | DONE |
| S12f | CODEX-1 | Opus 5.5 / high | S12 | 30 | Label outputs and choose honest prediction fallback | S12e, R-RS | Build/real2sim/; tests/prediction/; evidence/S12/ | 5-10% shown honestly; >10% limits demo prediction to virtual lab; review packet recorded. | DONE |
| S13a | CODEX-1 | Opus 5.5 / high | S13 | 30 | Define resumable upload and job-stage contracts | S04g, S06a, S01a, S01c | Build/pipeline/; contracts/jobs/; tests/pipeline/ | File limits, retry semantics and stage events versioned. | DONE |
| S13b | CODEX-1 | Opus 5.5 / high | S13 | 30 | Implement bucket upload validation | S13a | Build/pipeline/; contracts/jobs/; tests/pipeline/ | Interrupted upload resumes; unauthorized/invalid input rejected. | DONE |
| S13c | CODEX-1 | Opus 5.5 / high | S13 | 30 | Extract ffmpeg keyframes and metadata | S13b | Build/pipeline/; contracts/jobs/; tests/pipeline/ | Keyframes have original timestamps and clip provenance. | DONE |
| S13d | CODEX-1 | Opus 5.5 / medium | S13 | 30 | Add Redis job lifecycle and retry handling | S13c | Build/pipeline/; contracts/jobs/; tests/pipeline/ | Retry does not duplicate artifacts or spend without idempotency. | DONE |
| S13e | CODEX-1 | Opus 5.5 / high | S13 | 30 | Connect Muse Wonder understanding | S13d | Build/pipeline/; contracts/jobs/; tests/pipeline/ | Actual response validated; keyframe-image fallback explicit if video fails. | DONE |
| S13f | CODEX-1 | Opus 5.5 / high | S13 | 30 | Connect SAM masks and Modal reconstruction | S13e, S06d | Build/pipeline/; contracts/jobs/; tests/pipeline/ | Each stage emits validated output; failures readable and retryable. | DONE |
| S13g | CODEX-1 | Opus 5.5 / medium | S13 | 30 | Stream job progress to shell integration interface | S13f | Build/pipeline/; contracts/jobs/; tests/pipeline/ | Frontend can display stage events without editing CLAUDE-owned UI. | DONE |
| S13h | CODEX-1 | Opus 5.5 / high | S13 | 30 | Measure dev upload-to-scene path | S13g, S04, S06 | Build/pipeline/; contracts/jobs/; tests/pipeline/ | Fresh licensed upload becomes viewable <6 min, or measured failure; retry tests pass. | DONE |
| S14a | CODEX-1 | Opus 5.5 / high | S14 | 30 | Define scene, question and tool-output contracts | S08 | Build/agent/; contracts/agent/; tests/agent/; evidence/S14/ | Structured response schema forbids untraced numeric claims. | DONE |
| S14b | CODEX-1 | Opus 5.5 / high | S14 | 30 | Integrate Muse Wonder scene understanding | S14a | Build/agent/; contracts/agent/; tests/agent/; evidence/S14/ | Scene JSON and candidates validate on recorded fixtures. | DONE |
| S14c | CODEX-1 | Opus 5.5 / high | S14 | 30 | Implement one-to-three-question interview | S14b | Build/agent/; contracts/agent/; tests/agent/; evidence/S14/ | Chips and free-text map into validated spec inputs. | DONE |
| S14d | CODEX-1 | Opus 5.5 / high | S14 | 30 | Add bounded validator-retry loop | S14c | Build/agent/; contracts/agent/; tests/agent/; evidence/S14/ | Max 3 retries; unresolved ambiguity asks user rather than fabricating. | DONE |
| S14e | CODEX-1 | Opus 5.5 / high | S14 | 30 | Connect Muse Spark trial check | S14d | Build/agent/; contracts/agent/; tests/agent/; evidence/S14/ | Trial claims reference actual fitter/simulator output. | DONE |
| S14f | CODEX-1 | Opus 5.5 / high | S14 | 30 | Enforce tool-only numbers in replies | S14e | Build/agent/; contracts/agent/; tests/agent/; evidence/S14/ | Untraced number is blocked and replaced by tool-backed response. | DONE |
| S14g | CODEX-1 | Opus 5.5 / high | S14 | 30 | Run Gate A fixture and thirty-turn suite | S14f, S13 | Build/agent/; contracts/agent/; tests/agent/; evidence/S14/ | 9/10 valid specs and zero invented numeric claims across 30 turns. | DONE |
| S14h | CODEX-1 | Opus 5.5 / high | S14 | 30 | Checkpoint Gate A and template-card fallback | S14g, R-A | Build/agent/; contracts/agent/; tests/agent/; evidence/S14/ | Log pass or constrained-template fallback and cross-vendor review packet. | DONE |
| S15a | CLAUDE | Sonnet 5.5 / high | S15 | 30 | Define workspace states and consume module contracts | S09g, S10 | Build/web/src/workspace/; tests/workspace/; evidence/S15/ | Upload/interview/run/fit/report state graph documented. | DONE |
| S15b | CLAUDE | Sonnet 5.5 / high | S15 | 30 | Build workspace layout and viewport mount | S15a | Build/web/src/workspace/; tests/workspace/; evidence/S15/ | Viewer uses its public interface; no edits to viewer ownership. | DONE |
| S15c | CLAUDE | Sonnet 5.5 / high | S15 | 30 | Build upload status and failure surfaces | S15b | Build/web/src/workspace/; tests/workspace/; evidence/S15/ | Job-stage events visible; retry and partial-state messaging checked. | DONE |
| S15d | CLAUDE | Sonnet 5.5 / high | S15 | 30 | Build interview chips and free-text panel | S15c, S14a | Build/web/src/workspace/; tests/workspace/; evidence/S15/ | Question and answer transitions work against validated fixtures. | DONE |
| S15e | CLAUDE | Sonnet 5.5 / high | S15 | 30 | Build experiment template controls | S15d | Build/web/src/workspace/; tests/workspace/; evidence/S15/ | Only validated spec edits accepted; units visible. | DONE |
| S15f | CLAUDE | Sonnet 5.5 / high | S15 | 30 | Build run and replay controls | S15e | Build/web/src/workspace/; tests/workspace/; evidence/S15/ | Run, pause and seeded replay follow simulator contract. | DONE |
| S15g | CLAUDE | Sonnet 5.5 / high | S15 | 30 | Build virtual instrument controls | S15f | Build/web/src/workspace/; tests/workspace/; evidence/S15/ | Trial measurements display provenance and uncertainty. | DONE |
| S15h | CLAUDE | Sonnet 5.5 / medium | S15 | 30 | Build fit table and residual chart | S15g | Build/web/src/workspace/; tests/workspace/; evidence/S15/ | Every displayed number supplied by fitter; labels measured/simulated retained. | DONE |
| S15i | CLAUDE | Sonnet 5.5 / medium | S15 | 30 | Build sidebar and report navigation | S15h | Build/web/src/workspace/; tests/workspace/; evidence/S15/ | Agent and report modules connect via public interfaces. | DONE |
| S15j | CLAUDE | Sonnet 5.5 / medium | S15 | 30 | Stack workspace at 375px | S15i | Build/web/src/workspace/; tests/workspace/; evidence/S15/ | Sidebar below viewport; no horizontal scroll. | DONE |
| S15k | CLAUDE | Sonnet 5.5 / high | S15 | 30 | Walk full workflow on dev | S15j, S09, S14, S04i | Build/web/src/workspace/; tests/workspace/; evidence/S15/ | Upload, interview, run, fit and report complete in browser. | PARTIAL |
| S15l | CLAUDE | Sonnet 5.5 / medium | S15 | 30 | Checkpoint workspace accessibility and evidence | S15k | Build/web/src/workspace/; tests/workspace/; evidence/S15/ | Keyboard/errors/mobile verified; under compression simplify chart styling. | TODO |
| S15m | CLAUDE | Opus 5.5 / high | S15 | 30 | Plan end-to-end workspace wiring (upload to report) | S15k | evidence/S15/S15m/ | Controller-added Oct30: S15k-orch122 found upload/interview/run/fit/report NOT-WIRED on dev. Read-only integration map + QUEUE-ready row proposals (Owns/deps/acceptance/spend gates) for the smallest honest end-to-end path. | DONE |
| S14i | CODEX-1 | Opus 5.5 / high | S14 | 30 | API workspace analysis routers: internal-token auth, interview questions, spec validate, fit, HTML report | S14c, S11d, S17c, S15k | Build/api/workspace/__init__.py; Build/api/workspace/auth.py; Build/api/workspace/analysis.py; tests/api-workspace/test_analysis.py; evidence/S14i/ | (1) TestClient on the APIRouter: missing/bad token 401, owner header required; (2) questions/spec/fit/report call existing interview/validate_setup/fitter.handle/typeset with no new numeric logic; invalid spec -> errors, never default numbers; (3) report response labelled html-print-fallback + simulated. | DONE |
| S14j | CODEX-1 | Opus 5.5 / high | S14 | 30 | Workspace spec route: owner Q16 'scale unverified, not setup-validated' path for recorded scenes | S13k, S04m | Build/api/workspace/analysis.py; tests/api-workspace/; evidence/S14j/ | (1) RM04 recorded job: valid answers -> 200 spec validated by the numeric spec contract only, labelled verbatim 'scale unverified, not setup-validated', never MET/setup-validated, no invented scale; invalid answers still 422; (2) synthetic/authoritative scenes unchanged; api-workspace tests pass; (3) API redeployed to DEV, verify.py PASS. | DONE |
| S15n | CLAUDE | Opus 5.5 / high | S15 | 30 | Workspace controller: reduce() state + fetch adapters + upload control | S15k | Build/web/src/workspace/controller.mjs; Build/web/src/workspace/upload-view.mjs; tests/workspace/controller.test.mjs; evidence/S15n/ | (1) node --test with fake fetch drives upload.idle -> JOB_UPDATE(ready) -> INTERVIEW_SPEC -> RUN_COMPLETE -> FIT_RESULT -> REPORT_OPEN using PLAN §2 paths; (2) errors map to UNAUTHORIZED/INVALID_INPUT/DEPENDENCY_UNAVAILABLE/SPEND_PAUSED, no fixture data injected as real; (3) existing tests/workspace 79 still pass; file input labelled + keyboard reachable. | DONE |
| S04n | CODEX-2 | Opus 5.5 / medium | S04 | 30 | Web BFF proxy /api/workspace/[...path] (Clerk auth, capped body, private-network forward) | S04i | Build/web/src/app/api/workspace/; tests/web-workspace-api/; evidence/S04n/ | (1) signed-out 401, no upstream call; (2) forwards only owner+token headers, no cookies, no-store; cap 8 MiB (policy chunk_bytes) chunk PUT / 1 MB JSON else 413 (reuse lab route readCapped); (3) missing WORKSPACE_API_URL -> 503 DEPENDENCY_UNAVAILABLE; build PASS. | DONE |
| S13i | CODEX-1 | Opus 5.5 / high | S13 | 30 | API upload + job routes with RECORDED-replay executor (approved-clip sha gate) | S14i, S13h, S20b | Build/api/workspace/jobs.py; tests/api-workspace/test_jobs.py; evidence/S13i/ | (1) resumable upload via UploadService; non-clips.csv sha -> 422; other owner -> 404; (2) RM04 sha -> replay of evidence/S13/S13h events via JobRunner+progress, labelled RECORDED S13h-orch46 with original UTC; no recording -> failed DEPENDENCY_UNAVAILABLE; (3) test asserts recorded executor never imports modal / posts Meta; Redis store via redis-py with MemoryStore in tests. | DONE |
| S04m | CODEX-2 | Opus 5.5 / high | S04 | 30 | Mount workspace routers, extend API image (+jsonschema pin), set var names, deploy API to dev | S13i, S13k, S14i, S04n | Build/api/health/app.py; Build/api/health/requirements.txt; infra/railway/dev/api.Dockerfile; infra/railway/dev/stage.py; infra/railway/dev/test_stage.py; infra/railway/dev/verify.py; infra/railway/dev/test_verify.py; infra/railway/dev/deployments.json; evidence/S04m/ | (1) image import smoke: all routers import inside built image; (2) WORKSPACE_INTERNAL_TOKEN/WORKSPACE_API_URL present by name only on API/web; dev deploy SUCCESS, IDs recorded; (3) verify.py stale S15k text fixed and internal routes 401 without token from public URL. Dev only. | DONE |
| S04o | CLAUDE | Opus 5.5 / medium | S04 | 30 | PrivateWorkspace mounts controller; deploy web to dev | S15n, S04n, S04m | Build/web/src/shell/PrivateWorkspace.mjs; Build/web/src/auth/dev-scenes.mjs; tests/shell-workspace/; evidence/S04o/ | (1) PrivateWorkspace supplies onAction/interview/run/instruments/fit/report from controller; fixture banner removed only when API reachable, else honest unavailable notice; (2) logged-out/other-scene 404 unchanged; (3) web build + dev deploy SUCCESS. | DONE |
| S15o | CLAUDE | Sonnet 5.5 / high | S15 | 30 | Re-walk upload-to-report on dev (successor to S15k) | S04o, S04m, S14j, S15p | evidence/S15/s15o/ | (1) in-app browser: approved RM04 upload -> RECORDED progress -> interview -> run -> fit -> HTML report, every stage PASS/FAIL with screenshots; (2) labels RECORDED/SIMULATED visible; 375px no horizontal scroll; (3) no paid call made (ledgers unchanged). | PARTIAL |
| S15p | CLAUDE | Opus 5.5 / medium | S15 | 30 | Wire workspace run (browser simulator), honest instruments and API report shape | S04o | Build/web/src/shell/PrivateWorkspace.mjs; Build/web/src/workspace/controller.mjs; Build/web/src/workspace/navigation.mjs; tests/workspace/; tests/shell-workspace/; evidence/S15p/ | (1) run uses runBrowserSimulation on the API validated_setup, results labelled SIMULATED (plus any scale label from the spec); (2) report view renders the API {status, labels, html} response safely (no fabricated numbers); instruments show an honest unavailable state; (3) node tests + web build pass; web redeployed to DEV. | DONE |
| S15q | CLAUDE | Opus 5.5 / medium | S15 | 30 | Fix live workspace spec 422 + surface errors and RECORDED labels (S15o controller walk defects) | S15o | Build/web/src/shell/PrivateWorkspace.mjs; Build/web/src/workspace/controller.mjs; Build/web/src/workspace/; Build/api/workspace/analysis.py; tests/workspace/; tests/shell-workspace/; tests/api-workspace/; evidence/S15q/ | (1) the web interview answers reach POST spec in the exact answers_to_spec shape; RM04 recorded job + answers (1.5 m, at rest) -> 200 with label 'scale unverified, not setup-validated' (reproduced against the real router with the real web request body); (2) spec/API errors are visible in the stage panel (no silent stall); RECORDED stage labels (S13h-orch46 / S14g-fix3) visible in the job panel; nav/footer no longer claim signed-out / no uploads; (3) tests + web build pass; api/web redeployed to DEV as needed. | DONE |
| S15r | CLAUDE | Opus 5.5 / high | S15 | 30 | Owner Q20=A: labelled what-if Run on Q16 recorded scenes (API artifact + simulator mode + labels) | S15q | Build/api/workspace/analysis.py; Build/web/src/lab/browser-simulator.mjs; Build/web/src/workspace/; Build/web/src/shell/PrivateWorkspace.mjs; tests/workspace/; tests/shell-workspace/; tests/api-workspace/; tests/simulator/; Build/web/src/shell/ShellFrame.jsx; Build/web/src/shell/AccountNav.jsx; infra/railway/dev/stage.py; infra/railway/dev/test_stage.py; evidence/S15r/ | (1) Q16 scene spec -> API returns a what-if artifact that is explicitly non-synthetic (never forged synthetic:true) with the Q16 label; simulator accepts it only in that labelled mode, synthetic-only rule unchanged otherwise; (2) run/fit/report show 'SIMULATED what-if of your described setup; scale unverified; not measured from the clip' everywhere their numbers appear; (3) all affected tests + web build pass; api/web redeployed to DEV. | DONE |
| S15s | CLAUDE | Opus 5.5 / medium | S15 | 30 | Reach Fit and Report from a finished run in the live workspace | S15r | Build/web/src/workspace/; Build/web/src/shell/PrivateWorkspace.mjs; tests/workspace/; tests/shell-workspace/; evidence/S15s/ | (1) run.done shows a Fit control dispatching FIT_START (ctl.fit on the stored run observations); fit.done shows an Open report control (REPORT_OPEN -> ctl.openReport, sandboxed report); what-if label stays on fit/report; (2) tests prove run.done->fit.done->report on the what-if path and normal path; all workspace/shell/web-private/web-workspace-api tests + npm run build pass; (3) web redeployed to DEV (stage.py web + railway up); controller walks it. | DONE |
| S15t | CLAUDE | Opus 5.5 / high | S15 | 30 | Fix live Fit display rejection and report 422 on DEV | S15s | Build/web/src/workspace/; Build/web/src/shell/PrivateWorkspace.mjs; Build/web/src/app/api/workspace/; Build/api/workspace/analysis.py; tests/workspace/; tests/shell-workspace/; tests/web-workspace-api/; tests/api-workspace/; evidence/S15t/ | (1) root cause of 'Fit display rejected: fit output not ok' after /fit 200 and of /report 422 found with the real RM04 what-if run observations and fixed once in shared code; (2) fit table + sandboxed report render on the what-if path with the verbatim Q20 label; report/fit failures show visible error text; contract test uses the real API fit output, not a hand-made fake; all affected tests + npm run build pass; (3) api/web redeployed to DEV; controller walks it. | DONE |
| S15u | CLAUDE | Sonnet 5.5 / medium | S15 | 30 | Fit view polish: 375px overflow, truthful what-if source note, compact residuals | S15t | Build/web/src/workspace/; tests/workspace/; tests/shell-workspace/; evidence/S15u/ | (1) after a fit, 375px has no horizontal scroll (scrollWidth == clientWidth); (2) on the what-if path the gravity row source note no longer says 'synthetic virtual-lab fit' (uses the what-if label/source); residual table shows a short head with an accessible expand control; displayed values use sensible significant figures while exact fitter output stays available (title/hover); (3) workspace/shell tests + npm run build pass; web redeployed to DEV; controller walks it. | DONE |
| S15v | CLAUDE | Opus 5.5 / high | S15 | 30 | Product: accept 30 fps phone clips, ask for a known size, report uncertainty instead of failing | S07g, S15u | Build/api/workspace/; Build/pipeline/; Build/web/src/workspace/; tests/api-workspace/; tests/workspace/; tests/pipeline/; evidence/S15v/ | (1) upload accepts registered owner phone clips (30 fps, portrait 1080x1920); (2) interview asks for an object of known size (e.g. book edge 20.28 cm) and uses it as user-declared scale (labelled); (3) result is g +/- u from the S07g pipeline (or a recorded S07g result replay, labelled) instead of a failure; api/web redeployed to DEV. | TODO |
| S15w | CLAUDE | Opus 5.5 / high | S15 | 30 | One UI pass: myfront 1.2.0 round-3 + make-interfaces-feel-better | S15u, S15x | Build/web/src/; tests/workspace/; tests/shell-workspace/; evidence/S15w/ | (1) apply myfront 1.2.0 round-3 checklist and make-interfaces-feel-better to public + workspace pages; (2) 375px/desktop no regressions, a11y kept, labels unchanged; (3) tests + build pass; web redeployed to DEV; before/after screenshots by controller. | TODO |
| S15x | CLAUDE | Sonnet 5.5 / medium | S15 | 20 | Propose 6 Mobbin references for the owner to pick 3 | - | evidence/ui/mobbin-S15x/ | (1) 6 Mobbin screens (upload/progress, measurement result with uncertainty, report) relevant to Real2Sim, each with link, what to borrow and why; (2) one-line owner question in REPORT for Koushik to pick 3; no copying of assets. | DONE |
| S13j | CODEX-1 | Opus 5.5 / high | S13 | 30 | OPTIONAL/CUT-FIRST: re-capture RM04 geometry bytes into private dev bucket via existing e2e.py under guardrails | S13i | evidence/S13j/; Build/pipeline/recorded/ (new manifest only) | (1) admission.require_reconstruction + gpu_stages.reserve ledger before dispatch, cap $30/floor $5, standing GPU auth; (2) bytes sha-recorded, private bucket, no public URL; (3) container stopped, billed vs reserved logged. | TODO |
| S13k | CODEX-1 | Opus 5.5 / medium | S13 | 30 | RM04 replay: stitch recorded S14g-fix3 live understand spec + owner-scoped scene resolver | S13i | Build/api/workspace/jobs.py; tests/api-workspace/test_jobs.py; evidence/S13k/ | (1) RM04 replay emits understand from evidence/S14/S14g-fix3-live.json (valid RM04 spec) labelled RECORDED S14g-fix3 with its own recorded UTC (or explicit "time not recorded"), never as live or S13h; job reaches ready; (2) a ready owner job exposes an owner-scoped scene resolver (base_spec/template from the recorded spec) injectable into analysis.create_router, so questions/spec stop 404ing; other owner 404; (3) api-workspace tests all pass; no Meta/GPU call, no invented stage output. | DONE |
| S16a | CODEX-2 | GPT-6.1 Sol / medium | S16 | 30 | Define sidebar tool-call and search contracts | S12, S14 | Build/sidebar-tools/; tests/sidebar-tools/; evidence/S16/ | Spec patch, rebuild and library search typed and testable. | DONE |
| S16b | CODEX-2 | GPT-6.1 Sol / medium | S16 | 30 | Implement validator-first spec patch tool | S16a | Build/sidebar-tools/; tests/sidebar-tools/; evidence/S16/ | Invalid patch rejected before any rebuild. | DONE |
| S16c | CODEX-2 | GPT-6.1 Sol / medium | S16 | 30 | Implement rebuild and tool-output plumbing | S16b | Build/sidebar-tools/; tests/sidebar-tools/; evidence/S16/ | Tool results retain numeric provenance and retry behavior. | DONE |
| S16d | CODEX-2 | GPT-6.1 Sol / medium | S16 | 30 | Connect Baseten Spark Open library search | S16c | Build/sidebar-tools/; tests/sidebar-tools/; evidence/S16/ | Use exact model ID meta-models/muse-spark-open-1026; sanitized model ID logged per call. | DONE |
| S16e | CODEX-2 | GPT-6.1 Sol / medium | S16 | 30 | Verify real dev search inference | S16d | Build/sidebar-tools/; tests/sidebar-tools/; evidence/S16/ | Actual dev request returns usable library result; record cost without secrets. | DONE |
| S16f | CODEX-2 | GPT-6.1 Sol / medium | S16 | 30 | Add Fireworks fallback | S16e | Build/sidebar-tools/; tests/sidebar-tools/; evidence/S16/ | Provider failure switches only via explicit configuration; no silent false bonus claim. | DONE |
| S16g | CODEX-2 | GPT-6.1 Sol / medium | S16 | 30 | Test patch safety and search failures | S16f | Build/sidebar-tools/; tests/sidebar-tools/; evidence/S16/ | Bad patches and unavailable search yield readable behavior. | DONE |
| S16h | CODEX-2 | GPT-6.1 Sol / medium | S16 | 30 | Checkpoint open-weight evidence and fallback claims | S16g | Build/sidebar-tools/; tests/sidebar-tools/; evidence/S16/ | If both open providers fail use Meta Spark and drop bonus claim. | DONE |
| S17a | CLAUDE | Sonnet 5.5 / high | S17 | 30 | Define report data contract and numeric assertions | S11 | Build/reports/; tests/reports/; evidence/S17/ | All numbers trace to fitter output; report accepts no model-authored numerics. | DONE |
| S17b | CLAUDE | Sonnet 5.5 / high | S17 | 30 | Build deterministic report tables and charts | S17a | Build/reports/; tests/reports/; evidence/S17/ | Units, uncertainty and source labels preserved. | DONE |
| S17c | CLAUDE | Sonnet 5.5 / high | S17 | 30 | Build TeX/HTML report rendering | S17b | Build/reports/; tests/reports/; evidence/S17/ | Escaped user text and template-specific content render safely. | DONE |
| S17d | CLAUDE | Sonnet 5.5 / high | S17 | 30 | Compile reports for all four templates | S17c | Build/reports/; tests/reports/; evidence/S17/ | PDF compiles for all 4 or explicit HTML print fallback. | DONE |
| S17e | CLAUDE | Sonnet 5.5 / high | S17 | 30 | Automate numeric report-to-fitter diff | S17d | Build/reports/; tests/reports/; evidence/S17/ | Every reported number equals fitter output across all templates. | DONE |
| S17f | CLAUDE | Sonnet 5.5 / medium | S17 | 30 | Checkpoint report accessibility and fallback evidence | S17e, S14 | Build/reports/; tests/reports/; evidence/S17/ | Download/print path verified; no fabricated PDF success. | DONE |
| S18a | CODEX-2 | GPT-6.1 Sol / medium | S18 | 30 | Define library manifest and immutable artifact format | S06, S12, S13 | Build/library/; test-data/library-artifacts/; tests/library/; evidence/S18/ | Every demo carries source, licence, attribution and numeric provenance. | DONE |
| S18b | CODEX-2 | GPT-6.1 Sol / medium | S18 | 30 | Precompute free-fall demos | S18a | Build/library/; test-data/library-artifacts/; tests/library/; evidence/S18/ | Licensed inputs only; artifact provenance links actual runs. | DONE |
| S18c | CODEX-2 | GPT-6.1 Sol / medium | S18 | 30 | Precompute projectile and bounce demos | S18b | Build/library/; test-data/library-artifacts/; tests/library/; evidence/S18/ | Held-out comparisons and uncertainty stored with original clip IDs. | PARTIAL |
| S18d | CODEX-2 | GPT-6.1 Sol / medium | S18 | 30 | Precompute pendulum and scene demos | S18c | Build/library/; test-data/library-artifacts/; tests/library/; evidence/S18/ | Precomputed artifacts validate and expose safe defaults. | DONE |
| S18e | CODEX-2 | GPT-6.1 Sol / medium | S18 | 30 | Prepare Apollo and Mystery-g entries | S18d | Build/library/; test-data/library-artifacts/; tests/library/; evidence/S18/ | Moon result only claimed if measured; Mystery-g marked simulated. | DONE |
| S18f | CODEX-2 | GPT-6.1 Sol / medium | S18 | 30 | Implement guest manifest and artifact endpoint | S18e | Build/library/; test-data/library-artifacts/; tests/library/; evidence/S18/ | Anonymous demos require no new GPU/API calls. | DONE |
| S18g | CODEX-2 | GPT-6.1 Sol / medium | S18 | 30 | Implement library loading integration | S18f | Build/library/; test-data/library-artifacts/; tests/library/; evidence/S18/ | Library loading consumes viewer interface without editing CLAUDE-owned modules. | DONE |
| S18k | CODEX-2 | GPT-6.1 Sol / medium | S18 | 30 | Publish playable demo assets for guest library | S18g | Build/library/; test-data/library-artifacts/; tests/library/; evidence/S18/ | Controller-added Oct30 (S18g deferral). Bounded hashed simulator traces for projectile/free-fall/pendulum from accepted simulator code; RM02/RM04 PLY bundles only if accepted bytes match declared SHA; else UNAVAILABLE. No new GPU/API, no invented geometry, Mystery-g answer never public. | DONE |
| S18l | CLAUDE | Opus 5.5 / medium | S18 | 30 | Fix R-L P2: Mystery-g answer recoverable from public trace/repo | R-L | Build/library/; test-data/library-artifacts/; tests/library/; evidence/S18/ | Controller decision on R-L P2: Mystery-g must not be presented as blind while its g is recoverable; route the challenge to a server-owned hidden g if /lab provides one, else relabel honestly (practice challenge, Earth-g baseline). | DONE |
| R-L | CLAUDE | Opus 5.5 / medium | S18 | 15 | Cross-vendor review: guest library exposure and Mystery-g answer withholding | S18k | evidence/reviews/R-L/ | Read-only review of Sol-authored S18e-S18k guest/loader/playable code; findings with P-levels; never edit another lane. | DONE |
| S18h | CODEX-2 | GPT-6.1 Sol / medium | S18 | 30 | Verify licences and approved clip list | S18g | Build/library/; test-data/library-artifacts/; tests/library/; evidence/S18/ | Drop unknown-rights clips; record every demo credit. | DONE |
| S18i | CODEX-2 | GPT-6.1 Sol / medium | S18 | 30 | Measure library load times | S18h | Build/library/; test-data/library-artifacts/; tests/library/; evidence/S18/ | At least 6 demos open <3 sec; identify test conditions. | DONE |
| S18j | CODEX-2 | GPT-6.1 Sol / medium | S18 | 30 | Checkpoint minimum-library fallback | S18i | Build/library/; test-data/library-artifacts/; tests/library/; evidence/S18/ | If needed minimum 4 public clips plus Mystery-g; document cut honestly. | DONE |
| S19a | CLAUDE | Sonnet 5.5 / high | S19 | 30 | Add PWA manifest and icons from owned assets | S15b | Build/web/src/pwa/; Build/web/public/pwa/; tests/pwa/ | Manifest valid; no unlicensed icon assets. | DONE |
| S19b | CLAUDE | Sonnet 5.5 / high | S19 | 30 | Add safe service-worker caching | S19a | Build/web/src/pwa/; Build/web/public/pwa/; tests/pwa/ | Private uploads and authenticated responses never cached publicly. | DONE |
| S19c | CLAUDE | Sonnet 5.5 / high | S19 | 30 | Add install guidance and orientation handling | S19b | Build/web/src/pwa/; Build/web/public/pwa/; tests/pwa/ | Android/iOS guidance truthful; no unsupported orientation-lock claim. | DONE |
| S19d | CLAUDE | Sonnet 5.5 / medium | S19 | 30 | Verify installability and 375px walkthrough | S19c, S15 | Build/web/src/pwa/; Build/web/public/pwa/; tests/pwa/ | Browser installability evidence and library/viewer walkthrough pass; APK deferred. | DONE |
| S20a | CODEX-2 | GPT-6.1 Sol / medium | S20 | 30 | Define spend ledger, upload quota and reserve contract | S13 | Build/guardrails/; infra/failover/; tests/guardrails/; evidence/S20/ | Meta cap includes confirmed historical usage, pending requests and conservative estimates. | DONE |
| S20b | CODEX-2 | GPT-6.1 Sol / medium | S20 | 30 | Implement reconstruction cap and library exemption | S20a | Build/guardrails/; infra/failover/; tests/guardrails/; evidence/S20/ | Cap breach pauses uploads but guest precomputed library still works. | DONE |
| S20c | CODEX-2 | GPT-6.1 Sol / medium | S20 | 30 | Implement disabled-by-default AWS failover switch | S20b | Build/guardrails/; infra/failover/; tests/guardrails/; evidence/S20/ | Owner quota approval and $50 budget required before enabling. | DONE |
| S20d | CODEX-2 | GPT-6.1 Sol / high | S20 | 30 | Run Gate C simulated-cap regression | S20c, R-C | Build/guardrails/; infra/failover/; tests/guardrails/; evidence/S20/ | Per-scene cost logged; cap enforcement and AWS-off tests pass; no live overspend. | DONE |
| S21a | CODEX-2 | GPT-6.1 Sol / medium | S21 | 30 | Freeze benchmark inputs and method | S12, S18 | BENCHMARK.md; Build/benchmark/; Build/web/src/about/; evidence/S21/ | Record clip IDs, sample counts and units; no held-out leakage. | DONE |
| S21b | CODEX-2 | GPT-6.1 Sol / medium | S21 | 30 | Measure gravity and scene-scale errors | S21a | BENCHMARK.md; Build/benchmark/; Build/web/src/about/; evidence/S21/ | Report each measured error with uncertainty and sample size. | DONE |
| S21c | CODEX-2 | GPT-6.1 Sol / medium | S21 | 30 | Measure held-out prediction errors | S21b | BENCHMARK.md; Build/benchmark/; Build/web/src/about/; evidence/S21/ | Normalize by range/bounce height/period as Gate RS defines. | DONE |
| S21d | CODEX-2 | GPT-6.1 Sol / medium | S21 | 30 | Measure runtime and scene cost | S21c | BENCHMARK.md; Build/benchmark/; Build/web/src/about/; evidence/S21/ | Separate estimates from billed cost and cold start from GPU time. | DONE |
| S21e | CODEX-2 | GPT-6.1 Sol / medium | S21 | 30 | Write BENCHMARK.md and app About data | S21d | BENCHMARK.md; Build/benchmark/; Build/web/src/about/; evidence/S21/ | All claims trace to recorded measurements; no extrapolation. | DONE |
| S21f | CODEX-2 | GPT-6.1 Sol / medium | S21 | 30 | Cross-check pitch-facing benchmark numbers | S21e | BENCHMARK.md; Build/benchmark/; Build/web/src/about/; evidence/S21/ | App/video inputs match BENCHMARK.md; missing data explicitly unavailable. | DONE |
| S22a | CLAUDE | Opus 5.5 / medium | S22 | 30 | Prepare approved judging-candidate QA checklist | S15, S16, S17, S19, S20 | evidence/qa/claude/ | Opus records Gate D protocol; written candidate-deploy approval required before judging traffic. | DONE |
| S22b | CODEX-2 | Sonnet 5.5 / medium | S22 | 30 | Capture logged-out guest library walkthrough | S22a | evidence/qa/browser/ | Sol drives browser only; guest can open and run a demo. | DONE |
| S22c | CODEX-2 | Sonnet 5.5 / medium | S22 | 30 | Capture fresh-account full flow run 1 | S22b | evidence/qa/browser/ | Sol records duration and errors without creating accounts or accepting terms without approval. | TODO |
| S22d | CODEX-2 | Sonnet 5.5 / medium | S22 | 30 | Capture fresh-account full flow run 2 | S22c | evidence/qa/browser/ | Second independent flow duration and outcome recorded. | TODO |
| S22e | CODEX-2 | Sonnet 5.5 / medium | S22 | 30 | Capture fresh-account full flow run 3 | S22d | evidence/qa/browser/ | Third independent flow duration and outcome recorded. | TODO |
| S22f | CLAUDE | Opus 5.5 / high | S22 | 30 | Judge Gate D evidence and prioritize defects | S22e | evidence/qa/claude/ | Opus evaluates 3 consecutive <5min runs plus guest success; no claiming from screenshots alone. | TODO |
| S22g | CODEX-2 | Sonnet 5.5 / medium | S22 | 30 | Capture 375px and auth-boundary QA | S22f | evidence/qa/browser/ | Sol captures browser evidence; source changes go to original owners. | TODO |
| S22h | CODEX-2 | Sonnet 5.5 / medium | S22 | 30 | Capture retry, spend-cap and report QA | S22g | evidence/qa/browser/ | Sol checks observable outcomes; no terminal/product coding. | TODO |
| S22i | CODEX-2 | Sonnet 5.5 / medium | S22 | 30 | Recheck approved candidate after owner-lane fixes | S22h | evidence/qa/browser/ | Sol re-runs broken flows; fixes are separate scoped owner-lane tasks. | TODO |
| S22j | CLAUDE | Opus 5.5 / high | S22 | 30 | Record final Gate D decision and freeze recommendation | S22i | evidence/qa/claude/ | Opus records pass or library-only fallback with upload limits; cross-vendor review required. | TODO |
| S23a | KOUSHIK | Human only | S23 | 10 | Authorize frozen judging promotion | S22 | evidence/owner/S23/ | Koushik approves judging deployment in writing; candidate approval does not imply public-release permission. | TODO |
| S23b | CODEX-2 | GPT-6.1 Sol / medium | S23 | 20 | Promote frozen revision to judging | S23a | infra/railway/judging/; evidence/S23/ | Sol deploys approved immutable SHA; records returned revision. | TODO |
| S23c | CODEX-2 | GPT-6.1 Sol / medium | S23 | 30 | Verify deployed revision and smoke flow | S23b | infra/railway/judging/; evidence/S23/ | Version endpoint equals frozen SHA; repeat S22 smoke; rollback only to known passing revision. | TODO |
| S24a | CLAUDE | Opus 5.5 / high | S24 | 30 | Write evidence-backed three-minute script | S21, S23 | media/script/ | Opus leads with measurement/Real2Sim; every claim links benchmark or actual run. | DONE |
| S24b | CLAUDE | Opus 5.5 / medium | S24 | 30 | Review script, captions and footage credits | S24a | media/script/ | Opus names Meta models and event-only work; includes uncertainty and honest misses. | DONE |
| S24c | CODEX-2 | Sonnet 5.5 / medium | S24 | 30 | Capture room rebuild and interview | S24b | media/capture/; media/edit/ | Sol screen capture only; no staged results or personal files. | TODO |
| S24d | CODEX-2 | Sonnet 5.5 / medium | S24 | 30 | Capture held-out prediction and reveal | S24c | media/capture/; media/edit/ | Sol records real prediction compared with unseen frames. | TODO |
| S24e | CODEX-2 | Sonnet 5.5 / medium | S24 | 30 | Capture Apollo result and Mystery-g | S24d | media/capture/; media/edit/ | Only claim measured Moon g if real; simulated Mystery-g labelled. | TODO |
| S24f | CODEX-2 | Sonnet 5.5 / medium | S24 | 30 | Capture benchmark and Meta model evidence | S24e | media/capture/; media/edit/ | Visible values match BENCHMARK.md or recorded run. | TODO |
| S24g | KOUSHIK | Human only | S24 | 30 | Record optional voice-over part 1 | S24f | media/narration/ | Koushik reads script; captions-only fallback if unavailable. | TODO |
| S24h | KOUSHIK | Human only | S24 | 30 | Record optional voice-over part 2 | S24g | media/narration/ | Koushik completes optional narration; no agent impersonation. | TODO |
| S24i | CODEX-2 | Sonnet 5.5 / high | S24 | 30 | Cut video and align captions | S24h | media/capture/; media/edit/ | Sol edits via UI; final duration <=3:00; credits and labels retained. | TODO |
| S24j | CODEX-2 | Sonnet 5.5 / medium | S24 | 30 | Check playback and approval-gated public video link | S24i | media/capture/; media/edit/ | Public upload requires written go-ahead; verify playback and all on-screen numbers. | TODO |
| S24k | CLAUDE | Sonnet 5.5 / medium | S24 | 30 | Update 3-min script with stopwatch-vs-phone before/after | S07h | media/script/ | (1) DEMO_SCRIPT_DRAFT.md adds the stopwatch-vs-phone before/after beat using only S07g/S07h measured numbers (with u) and labels; (2) owner clips public use marked pending go-ahead; (3) still fits 3:00. | TODO |
| S25a | CODEX-2 | GPT-6.1 Sol / medium | S25 | 30 | Write setup, architecture and Meta usage README | S21, S23 | README.md; ATTRIBUTION.md; evidence/release/ | README distinguishes measured results from estimates; no credentials or personal files. | DONE |
| S25b | CODEX-2 | GPT-6.1 Sol / medium | S25 | 30 | Write footage attribution and public-package checklist | S25a | README.md; ATTRIBUTION.md; evidence/release/ | Every asset has rights; README links actual live URL and video or marks pending. | DONE |
| S25c | CODEX-2 | GPT-6.1 Sol / medium | S25 | 30 | Scan tracked files and full Git history | S25b | README.md; ATTRIBUTION.md; evidence/release/ | Secret scan clean; if anything leaks stop publication and request rotation/remediation approval. | DONE |
| S25d | KOUSHIK | Human only | S25 | 10 | Authorize public repository visibility | S25c, S23, S24f | evidence/owner/S25/ | Koushik gives written go-ahead after clean scan; no implicit publication. | TODO |
| S25e | CODEX-2 | GPT-6.1 Sol / medium | S25 | 20 | Make approved repo public and verify anonymous links | S25d | README.md; ATTRIBUTION.md; evidence/release/ | Sol changes visibility only after approval; logged-out repo/live/video checks recorded. | TODO |
| S25f | CODEX-2 | Sonnet 5.5 / medium | S25 | 30 | Add MIT LICENSE (owner Q18) and update README/ATTRIBUTION/checklist | S25c | LICENSE; README.md; ATTRIBUTION.md; evidence/release/PUBLIC_PACKAGE_CHECKLIST.md | (1) LICENSE = standard MIT text, copyright 2026 Koushik Sadhak Jeet; (2) README/ATTRIBUTION state MIT covers project code/docs only, third-party clips/models keep their own licences; (3) checklist LICENSE item closed, nothing published. | DONE |
| S26a | KOUSHIK | Human only | S26 | 30 | Submit approved project on Cerebral Valley | S24, S25 | evidence/submission/ | Koushik submits working repo/video/live links and judge note before Nov4 18:00 Dhaka. | TODO |
| S26b | KOUSHIK | Human only | S26 | 30 | Verify entry and contributor listing | S26a | evidence/submission/ | Submission confirmation visible; solo Koushik listed; preserve timestamp evidence. | TODO |
| S26c | KOUSHIK | Human only | S26 | 30 | Post demo on X and submit the post link | S26b | evidence/submission/ | Koushik posts and registers URL for prize; verify links and shutdown GPU/warm-container checklist. | TODO |
| R-R | CLAUDE | GPT-6.1 Sol / high | S05 | 15 | Cross-vendor review: Gate R implementation and failure thresholds | S05e | evidence/reviews/R-R/ | Read-only source review; record findings and evidence. Unresolved gate defects block parent completion and return to original owner, never silently edit another lane. | DONE |
| R-M | CLAUDE | Opus 5.5 / medium | S07 | 15 | Cross-vendor review: Gate M fitting, timebase and uncertainty | S07e | evidence/reviews/R-M/ | Read-only source review; record findings and evidence. Unresolved gate defects block parent completion and return to original owner, never silently edit another lane. | DONE |
| R-M2 | CLAUDE | Opus 5.5 / medium | S07 | 15 | Review S07f summary-boundary fixes and honest fallback | R-M | evidence/reviews/R-M2/ | Read pinned run/S07f233e5e2 source/diff; independently check F1/F2 and independence/coverage contracts. No source edits or inferred physical pass. | DONE |
| R-P | CLAUDE | Opus 5.5 / medium | S10 | 15 | Cross-vendor review: Gate P analytic comparison and replay | S10i | evidence/reviews/R-P/ | Read-only source review; record findings and evidence. Unresolved gate defects block parent completion and return to original owner, never silently edit another lane. | DONE |
| R-RS | CLAUDE | GPT-6.1 Sol / high | S12 | 15 | Cross-vendor review: Gate RS held-out boundary and error normalization | S12e | evidence/reviews/R-RS/ | Read-only source review; record findings and evidence. Unresolved gate defects block parent completion and return to original owner, never silently edit another lane. | DONE |
| R-A | CLAUDE | GPT-6.1 Sol / high | S14 | 15 | Cross-vendor review: Gate A tool-number enforcement | S14g | evidence/reviews/R-A/ | Read-only source review; record findings and evidence. Unresolved gate defects block parent completion and return to original owner, never silently edit another lane. | DONE |
| R-W | CLAUDE | Opus 5.5 / high | S04 | 15 | Cross-vendor review: private workspace auth boundary and proxy | S04i | evidence/reviews/R-W/ | Read-only review of Sol-authored S04i (owner repository, clerkMiddleware matcher, 404 fail-closed, no existence leak); findings with P-levels; never edit another lane. | DONE |
| R-C | CLAUDE | Opus 5.5 / high | S20 | 15 | Cross-vendor review: Gate C cap accounting and library exemption | S20c | evidence/reviews/R-C/ | Read-only source review; record findings and evidence. Unresolved gate defects block parent completion and return to original owner, never silently edit another lane. | DONE |
| R-D | CODEX-1 | GPT-6.1 Sol / high | S22 | 15 | Cross-vendor review: Gate D protocol and Claude verdict evidence | S22j | evidence/reviews/R-D/ | Read-only source review; record findings and evidence. Unresolved gate defects block parent completion and return to original owner, never silently edit another lane. | TODO |
| F-CODEX-1-1 | CODEX-1 | GPT-6.1 Sol / medium | FILLER | 15 | Document owned-module edge cases | S03 | evidence/fillers/CODEX-1/1/ | Read only finished modules owned by this lane; produce concrete missing-case checklist. No implementation or other-lane edits. | DONE |
| F-CODEX-1-2 | CODEX-1 | GPT-6.1 Sol / medium | FILLER | 15 | Review owned-module test coverage gaps | S03 | evidence/fillers/CODEX-1/2/ | Read only finished modules owned by this lane; produce concrete missing-case checklist. No implementation or other-lane edits. | DONE |
| F-CODEX-2-1 | CODEX-2 | GPT-6.1 Sol / medium | FILLER | 15 | Document owned-module edge cases | S03 | evidence/fillers/CODEX-2/1/ | Read only finished modules owned by this lane; produce concrete missing-case checklist. No implementation or other-lane edits. | DONE |
| F-CODEX-2-2 | CODEX-2 | GPT-6.1 Sol / medium | FILLER | 15 | Review owned-module test coverage gaps | S03 | evidence/fillers/CODEX-2/2/ | Read only finished modules owned by this lane; produce concrete missing-case checklist. No implementation or other-lane edits. | DONE |
| F-CLAUDE-1 | CLAUDE | Opus 5.5 / medium | FILLER | 15 | Document owned-module edge cases | S03 | evidence/fillers/CLAUDE/1/ | Read only finished modules owned by this lane; produce concrete missing-case checklist. No implementation or other-lane edits. | DONE |
| F-CLAUDE-2 | CLAUDE | Opus 5.5 / medium | FILLER | 15 | Review owned-module test coverage gaps | S03 | evidence/fillers/CLAUDE/2/ | Read only finished modules owned by this lane; produce concrete missing-case checklist. No implementation or other-lane edits. | DONE |

## Step acceptance contracts (unchanged JSON)

Parent steps are summaries, not runnable >30m tasks. Required evidence levels are copied from the plan; none of the product evidence exists yet.

### S01 — Finish keys and approvals

- Source owner: Koushik
- Source timebox: 90m; priority: critical; source dependencies: none.
- Leaf tasks: S01a, S01b, S01c.
- Required evidence: E2.
- Acceptance: One test call to muse-spark-1.3 succeeds with the new Meta key
- Acceptance: Clerk sign-in works with Google (shared credentials) and email OTP; guests reach /library
- Acceptance: Keys live only in .env or Railway variables and are never printed
- Acceptance: Written go-ahead for Railway dev deploys recorded in DECISIONS_LOG.md
- Fallback: If Meta access or credit is unavailable, use Muse Spark Open on Baseten and open-weight SAM 3 on Modal where available; Meta-only steps wait and nothing is faked.
- Status: NOT STARTED — acceptance not claimed.

### S02 — Build the licensed public clip set

- Source owner: CODEX-2 · GPT-6.1 Sol (high, browsing and computer use only) + Koushik (10-minute approval)
- Source timebox: 120m; priority: critical; source dependencies: none.
- Leaf tasks: S02a, S02b, S02c, S02c1 (NASA support), S02c2 (room support), S02d, S02e. S02c workers explicitly apply Ponytail; see S02C_PARALLEL.md. Shard research completion is not parent clip acceptance.
- Required evidence: E1.
- Acceptance: At least 10 clips plus clips.csv in test-data/public, every row with source, licence and attribution
- Acceptance: Every clip has a frame rate from the file metadata and a known-size reference object, or is marked scene-only
- Acceptance: Koushik's approval of the list recorded in DECISIONS_LOG.md
- Fallback: If fewer than 3 usable free-fall clips are found, add Wikimedia Commons strobe and slow-motion clips and treat slow-motion timebase detection (S07) as required; if still short, Gate M runs on what exists and reports the sample size.
- Status: S02a/S02b DONE. S02c unmerged54460a5: eleven unapproved local candidates, two narrowly checked for local visual tracking/scene-motion feasibility only; require-ten fails2/10. Owner changed S02c to Opus5.5/high, retaining CODEX-2 ownership. Q2 permits provisional licensed local acquisition; Pexels public-repository redistribution and third-party rights remain unresolved. S02d/S02e not started; no calibrated trial or final-use owner approval; parent acceptance not claimed.

### S03 — Retarget the Run System to Real2Simulation

- Source owner: CODEX-1 · GPT-6.1 Sol (medium; high for gates)
- Source timebox: 60m; priority: critical; source dependencies: none.
- Leaf tasks: S03a, S03b, S03c; owner-authorized rework M-ROOT/M-PROMPTS adds60m from buffer, not a silent rewrite of source60m.
- Required evidence: E1.
- Acceptance: The event folder is the git repository root with the control files; archive/, .env and private data are gitignored; git log shows only new commits
- Acceptance: QUEUE.md tasks are 30 minutes or less, with disjoint Owns paths for parallel tasks
- Acceptance: Run-System dispatcher script starts each run as a fresh session with a short prompt (for example "Complete run R12"), runs one task per lane, at most 2 at once, kills a run at 30 minutes, and logs each run to RUN_LOG.md; one dry run proves it
- Acceptance: API_BUDGET.md tracks the Meta credit with the $120 stop
- Fallback: If the dispatcher script is not ready, Koushik starts each lane by hand from its own CLI or T3 Code on the PC with the same QUEUE.md and STATE.md files.
- Status: DONE — local documentation/repository verification only.

### S04 — App skeleton on Railway with sign-in and guest access

- Source owner: CODEX-2 · GPT-6.1 Sol (medium)
- Source timebox: 240m; priority: critical; source dependencies: S01, S03.
- Leaf tasks: S04a, S04b, S04c, S04d, S04e, S04f, S04g, S04h.
- Required evidence: E4.
- Acceptance: Dev URL serves the app; Clerk sign-in works with Google (shared credentials) and email OTP; guests reach /library
- Acceptance: A logged-out visitor reaches /library
- Acceptance: API and worker health endpoints return 200 on Railway
- Fallback: If Clerk blocks progress for more than 2 hours, ship guest mode plus a single demo account and finish Clerk in S22.
- Status: NOT STARTED — acceptance not claimed.

### S05 — Gate R spike: metric 3D scene from public clips

- Source owner: CODEX-1 · GPT-6.1 Sol (medium; high for gates)
- Source timebox: 180m; priority: critical; source dependencies: S02, S03.
- Leaf tasks: S05a, S05b, S05c, S05d, S05e, S05f.
- Required evidence: E2.
- Acceptance: Known-object size within 10% on at least 2 of 3 scene clips (standard sizes, not tape measurements, so the threshold is looser)
- Acceptance: Floor plane found and gravity direction agrees with the A4 plane normal within 5 degrees
- Acceptance: GPU time 4 minutes or less per scene; licence recorded in DECISIONS_LOG.md
- Fallback: Fallback 1: one keyframe plus SAM 3D Objects layout plus one question (desk height). Fallback 2: planes and boxes textured with video frames. Log the fallback as a decision; the experiment flow does not change.
- Status: NOT STARTED — acceptance not claimed.

### S06 — GPU container on Modal (AWS-ready)

- Source owner: CODEX-1 · GPT-6.1 Sol (medium; high for gates)
- Source timebox: 240m; priority: critical; source dependencies: S05, S01.
- Leaf tasks: S06p (additive20m pre-reset readiness; independent of footage approval), S06a, S06b, S06c, S06d, S06e, S06f, S06g, S06h.
- Required evidence: E2.
- Acceptance: One room clip becomes a scene artifact on Modal in under 5 minutes including cold start
- Acceptance: Cost per scene logged
- Acceptance: The image starts locally or on CPU in a dry-run mode, so the AWS path is ready
- Fallback: If SAM 3D Objects fails (memory, install or licence), ship MapAnything output with primitive meshes and drop SAM 3D from the pitch.
- Status: NOT STARTED — acceptance not claimed.

### S07 — Gate M spike: measure g from public free-fall clips

- Source owner: CODEX-1 · GPT-6.1 Sol (medium; high for gates)
- Source timebox: 180m; priority: critical; source dependencies: S01, S02, S03.
- Leaf tasks: S07a, S07b, S07c, S07d, S07e, S07f.
- Required evidence: E2.
- Acceptance: g within 5% of 9.81 m/s^2 on at least 2 of 3 Earth free-fall clips, with a stated uncertainty that covers the error
- Acceptance: Stretch: the Apollo 15 clip gives the Moon's g within 15%
- Acceptance: Fitter unit tests pass on synthetic data
- Fallback: If Gate M fails, Measure mode is limited to table-plane experiments (homography only) and the pitch leads with the virtual lab and Mystery-g. Log it as a decision.
- Status: PARTIAL — evaluator and reviewed S07f decision complete; Gate M NOT_MET_INPUT_READINESS/physics NOT_RUN (0 eligible/0 measured, null g/error/coverage). R-M/R-M2 reviews DONE; S07b live tracking PARTIAL. Simulated lab/Mystery-g lead, calibrated table-plane Measure unavailable; no physical acceptance or S12 unlock.

### S08 — Experiment spec, validator and 4 templates

- Source owner: CODEX-1 · GPT-6.1 Sol (medium; high for gates)
- Source timebox: 240m; priority: critical; source dependencies: S03.
- Leaf tasks: S08a, S08b, S08c, S08d, S08e, S08f, S08g, S08h.
- Required evidence: E3.
- Acceptance: Schema tests pass
- Acceptance: Validator rejects 10 deliberately bad specs, each with a readable reason
- Acceptance: Each template exposes an analytic answer for Gate P
- Fallback: Cut to 3 templates (drop the ramp) if the step overruns by 2 hours.
- Status: DONE — S08a–S08h complete. 91 experiment tests PASS, including ten named invalid specs rejected with readable reasons at both setup/oracle boundaries and all four validated deterministic analytic references. Ramp requires positive downhill acceleration; pendulum is linearized with amplitude <=0.1 rad; contact-mounted setups unsupported. Synthetic contract/reference acceptance only: no integrator accuracy or Gate P acceptance.

### S09 — 3D world viewer with a rendering budget

- Source owner: CLAUDE · Opus 5.5 (medium)
- Source timebox: 300m; priority: critical; source dependencies: S04, S05.
- Leaf tasks: S09a, S09b, S09c, S09d, S09e, S09f, S09g, S09h, S09i, S09j.
- Required evidence: E2.
- Acceptance: 3 scenes load and orbit at 30 fps or more on a mid-range laptop
- Acceptance: At 375 px wide the viewer loads the reduced detail level without horizontal scroll
- Fallback: If splats are too heavy, render a decimated point cloud plus textured proxy boxes.
- Status: NOT STARTED — acceptance not claimed.

### S10 — Builder and in-browser simulator; Gate P

- Source owner: CODEX-1 · GPT-6.1 Sol (medium; high for gates)
- Source timebox: 300m; priority: critical; source dependencies: S08, S09.
- Leaf tasks: S10a, S10b, S10c, S10d, S10e, S10f, S10g, S10h, S10i, S10j.
- Required evidence: E3.
- Acceptance: Gate P: every template matches its analytic answer within 0.5%
- Acceptance: The same seed replays identically
- Acceptance: Mystery-g hides g in the UI and reveals it only after a fit
- Fallback: If Rapier contact jitter breaks a template, run that template on RK4 only and disable free dragging for it.
- Status: NOT STARTED — acceptance not claimed.

### S11 — Virtual instruments and the fitter service

- Source owner: CODEX-1 · GPT-6.1 Sol (medium; high for gates)
- Source timebox: 240m; priority: critical; source dependencies: S07, S08.
- Leaf tasks: S11a, S11b, S11c, S11d, S11e, S11f, S11g, S11h.
- Required evidence: E3.
- Acceptance: Coverage test: across 100 seeds, the 95% interval contains the true g in at least 90 runs
- Acceptance: Fitter output is the only source of numbers in later steps (API contract)
- Fallback: If the coverage test fails, widen the noise model's documented uncertainty and record the miscalibration; never hide it.
- Status: NOT STARTED — acceptance not claimed.

### S12 — Real2Sim bridge and prediction; Gate RS

- Source owner: CODEX-1 · GPT-6.1 Sol (medium; high for gates)
- Source timebox: 180m; priority: critical; source dependencies: S07, S10, S11.
- Leaf tasks: S12a, S12b, S12c, S12d, S12e, S12f.
- Required evidence: E3.
- Acceptance: Gate RS: across the projectile, bounce and pendulum clips, the median held-out error is 5% or less of the motion's size (range, bounce height, or period)
- Acceptance: Every value in the UI is labelled measured or simulated
- Fallback: If the error is 5-10%, show it honestly with its uncertainty. Above 10%, demo prediction in the virtual lab only and keep Measure mode for g.
- Status: NOT STARTED — acceptance not claimed.

### S13 — Upload and reconstruction job pipeline

- Source owner: CODEX-1 · GPT-6.1 Sol (medium; high for gates)
- Source timebox: 240m; priority: critical; source dependencies: S04, S06, S01.
- Leaf tasks: S13a, S13b, S13c, S13d, S13e, S13f, S13g, S13h.
- Required evidence: E4.
- Acceptance: A fresh upload on the dev URL becomes a viewable scene in under 6 minutes
- Acceptance: Failures at any stage show a readable message and leave the job retryable
- Fallback: If Wonder video input is unreliable, send keyframes as images instead of the full video.
- Status: NOT STARTED — acceptance not claimed.

### S14 — Scene-understanding and interview agent

- Source owner: CODEX-1 · GPT-6.1 Sol (medium; high for gates)
- Source timebox: 240m; priority: critical; source dependencies: S08, S13.
- Leaf tasks: S14a, S14b, S14c, S14d, S14e, S14f, S14g, S14h.
- Required evidence: E3.
- Acceptance: Gate A: 9 of 10 recorded scene fixtures produce a valid spec
- Acceptance: Gate A: an automated check finds no number in agent replies that is absent from tool outputs, across 30 test turns
- Fallback: If structured output fails, the agent picks from template cards only and free-text custom experiments are cut.
- Status: NOT STARTED — acceptance not claimed.

### S15 — Workspace UI

- Source owner: CLAUDE · Sonnet 5.5 (high)
- Source timebox: 360m; priority: critical; source dependencies: S09, S10, S14.
- Leaf tasks: S15a, S15b, S15c, S15d, S15e, S15f, S15g, S15h, S15i, S15j, S15k, S15l.
- Required evidence: E4.
- Acceptance: A browser walk-through completes upload, interview, run, fit and report on the dev URL
- Acceptance: No horizontal scroll at 375 px; the sidebar stacks under the viewport
- Fallback: Under compression, drop the custom chart styling and keep a single data table plus one fit chart.
- Status: NOT STARTED — acceptance not claimed.

### S16 — Sidebar agent tools and the open-weight component

- Source owner: CODEX-2 · GPT-6.1 Sol (medium)
- Source timebox: 240m; priority: high; source dependencies: S12, S14.
- Leaf tasks: S16a, S16b, S16c, S16d, S16e, S16f, S16g, S16h.
- Required evidence: E3.
- Acceptance: Spec patches go through the validator before any rebuild
- Acceptance: Spark Open on Baseten serves library search in the dev environment, with the model ID logged per call
- Fallback: If Baseten fails, use Muse Spark Open on Fireworks; if both fail, use Muse Spark on the Meta API and drop the open-weight bonus claim.
- Status: NOT STARTED — acceptance not claimed.

### S17 — Lab report and charts

- Source owner: CLAUDE · Haiku 5.5 (high)
- Source timebox: 180m; priority: high; source dependencies: S11, S14.
- Leaf tasks: S17a, S17b, S17c, S17d, S17e, S17f.
- Required evidence: E3.
- Acceptance: PDF compiles for all 4 templates
- Acceptance: Every number in the PDF equals the fitter output (automated diff)
- Fallback: Fall back to an HTML report with print-to-PDF if Tectonic fails on Railway.
- Status: NOT STARTED — acceptance not claimed.

### S18 — Demo library with licensed footage

- Source owner: CODEX-2 · GPT-6.1 Sol (medium)
- Source timebox: 300m; priority: high; source dependencies: S06, S12, S13.
- Leaf tasks: S18a, S18b, S18c, S18d, S18e, S18f, S18g, S18h, S18i, S18j.
- Required evidence: E3.
- Acceptance: At least 6 demos open from precomputed artifacts in under 3 seconds
- Acceptance: Every demo has a filled source and licence field; no YouTube downloads
- Fallback: Minimum viable library: 4 public clips plus Mystery-g. Drop any clip whose licence is not verified.
- Status: NOT STARTED — acceptance not claimed.

### S19 — Installable PWA and phone layout

- Source owner: CLAUDE · Haiku 5.5 (high)
- Source timebox: 120m; priority: medium; source dependencies: S15.
- Leaf tasks: S19a, S19b, S19c, S19d.
- Required evidence: E2.
- Acceptance: The browser reports the app as installable
- Acceptance: The phone layout passes a 375 px walk-through of the library and viewer
- Fallback: Cut the APK; keep the PWA.
- Status: NOT STARTED — acceptance not claimed.

### S20 — Spend guardrails and GPU failover

- Source owner: CODEX-2 · GPT-6.1 Sol (medium)
- Source timebox: 120m; priority: high; source dependencies: S13.
- Leaf tasks: S20a, S20b, S20c, S20d.
- Required evidence: E3.
- Acceptance: Gate C: per-scene cost appears in logs, and a simulated cap breach pauses uploads while the library still works
- Acceptance: The AWS switch stays off by default
- Fallback: If time is short, a manual kill switch in Railway variables replaces the automatic cap.
- Status: NOT STARTED — acceptance not claimed.

### S21 — Benchmark numbers for the pitch

- Source owner: CODEX-2 · GPT-6.1 Sol (medium)
- Source timebox: 180m; priority: high; source dependencies: S12, S18.
- Leaf tasks: S21a, S21b, S21c, S21d, S21e, S21f.
- Required evidence: E3.
- Acceptance: BENCHMARK.md reports each metric with sample size and method
- Acceptance: Numbers in the app and video match BENCHMARK.md
- Fallback: Report whatever was measured, with its sample size; never extrapolate missing runs.
- Status: NOT STARTED — acceptance not claimed.

### S22 — End-to-end QA on the judging environment; Gate D

- Source owner: CLAUDE · Opus 5.5 (medium) + CODEX-2 · GPT-6.1 Sol (high, browsing and computer use only) (Playwright runs)
- Source timebox: 300m; priority: critical; source dependencies: S15, S16, S17, S19, S20.
- Leaf tasks: S22a, S22b, S22c, S22d, S22e, S22f, S22g, S22h, S22i, S22j.
- Required evidence: E4.
- Acceptance: Gate D: a fresh account completes upload to report in under 5 minutes, 3 runs in a row
- Acceptance: A logged-out judge can open and run a library demo
- Fallback: If Gate D fails at freeze, the demo video uses the library path and the README states the upload limits honestly.
- Status: NOT STARTED — acceptance not claimed.

### S23 — Promote the judging build

- Source owner: Koushik + CODEX-2 · GPT-6.1 Sol (medium)
- Source timebox: 60m; priority: critical; source dependencies: S22.
- Leaf tasks: S23a, S23b, S23c.
- Required evidence: E4.
- Acceptance: The deployed revision equals the frozen commit SHA
- Acceptance: Judging URL passes the S22 smoke flow once more
- Fallback: Roll back to the last revision that passed Gate D.
- Status: NOT STARTED — acceptance not claimed.

### S24 — Three-minute demo video

- Source owner: CODEX-2 · GPT-6.1 Sol (high, browsing and computer use only) (capture, edit) + CLAUDE · Opus 5.5 (medium) (script) + Koushik (voice-over)
- Source timebox: 300m; priority: critical; source dependencies: S21, S23.
- Leaf tasks: S24a, S24b, S24c, S24d, S24e, S24f, S24g, S24h, S24i, S24j.
- Required evidence: E4.
- Acceptance: Video is 3:00 or shorter and plays from its public link
- Acceptance: Every on-screen number matches BENCHMARK.md or a live run
- Fallback: If a prediction misses, show the miss with its uncertainty; do not stage or edit results.
- Status: NOT STARTED — acceptance not claimed.

### S25 — README, attribution and public repo

- Source owner: CODEX-2 · GPT-6.1 Sol (medium)
- Source timebox: 120m; priority: high; source dependencies: S21, S23.
- Leaf tasks: S25a, S25b, S25c, S25d, S25e.
- Required evidence: E3.
- Acceptance: The repo is public after Koushik's go-ahead and contains no secrets (secret scan clean)
- Acceptance: README links the live URL and the video
- Fallback: If the secret scan finds anything, rotate the key, rewrite history before publishing, and record it.
- Status: NOT STARTED — acceptance not claimed.

### S26 — Submit and post

- Source owner: Koushik
- Source timebox: 90m; priority: critical; source dependencies: S24, S25.
- Leaf tasks: S26a, S26b, S26c.
- Required evidence: E4.
- Acceptance: The submission page shows the entry with working links
- Acceptance: Submitted before stop-work (Nov 4, 18:00 Dhaka)
- Fallback: If the form errors, retry, then contact organisers on Discord with a timestamped screenshot well before the hard deadline.
- Status: NOT STARTED — acceptance not claimed.

## Gate schedule and deadline modes

- Gate R (Oct 28, 22:00 Dhaka): metric scene from public clips, known-object size within 10% on 2 of 3 clips
- Gate M (Oct 28, 22:00 Dhaka): g within 5% of 9.81 m/s^2 on 2 of 3 public free-fall clips, with honest uncertainty
- Gate P (Oct 30): simulator matches the analytic answer within 0.5% for every template
- Gate RS (Oct 31): held-out prediction error 5% or less (median) on the public projectile, bounce and pendulum clips
- Gate A (Oct 31): valid spec on 9 of 10 fixtures and no invented numbers across 30 turns
- Gate C (Nov 1): per-scene cost logged and the spend cap pauses uploads, never the library
- Gate D (Nov 3): fresh account completes the full flow in under 5 minutes, 3 runs in a row; logged-out judge can run a library demo
- Gate S (Nov 4): repo public and secret-free, video 3:00 or less, all links load, submitted before 18:00 Dhaka
- Final: run scripts/validate_plan.py on this file after any edit to the handoff

Normal now; compression if any gate >12h late or S15 not started by Nov 1 12:00 Dhaka. Compression keeps S01–S15, minimum S18, S20–S26 and only Spark Open search from S16; cut voice, Muse Image, primitives, APK, conical pendulum and chart polish. Freeze Nov 3 18:00; submission mode Nov 4 10:00; **owner stop-work Nov 4 18:00 Dhaka**; organizer deadline Nov 5 08:00 Dhaka (= Nov 4 21:00 EST). S17/S19 are optional but S22 JSON lists them: skip only with an explicit logged scope-cut decision and honest QA coverage, not implicit dependency deletion. Planned validation command names do not exist yet; do not run or claim them now. The plan itself was not edited by this executor; owner-side revisions were detected and reconciled (D18 and latest consolidation decision).
