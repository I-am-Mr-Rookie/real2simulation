# R-D — Cross-vendor review of the Gate D decision

**Verdict: AGREE WITH CHANGES.** Agree that Gate D of record is **NOT MET / PENDING**, that judging approval/deployment and a fresh candidate run remain necessary, and that the existing fitter now really runs. Do **not** carry forward the unqualified **PASS-on-DEV / all 3.1–3.8 MET** wording: the owner-clip interview does not return a validated experiment spec, the strict viewer criterion is not what was demonstrated, and the retained evidence cannot independently establish the entire claimed streak. These are findings, not authorization to amend a gate or implement another lane's code.

Reviewed snapshot: main `6fb80fa659c6ebf5988d629ce730d7231e64475c`, isolated branch `run/R-D-orch241`. Decision under review: `evidence/qa/claude/S22j-GATE-D-DECISION.md`, written against `341bc50c`. Current source includes S15be; the S22i browser build predates it. Line references below use this review snapshot unless explicitly historical. Assigned reviewer CODEX-1 / gpt-6.1-sol high; Claude authored the decision and fixes.

## Ranked findings and proposed owner rows

### F1 — P1: Step 3.4 is marked MET although the tested branch produces no validated spec

- Claim: `evidence/qa/claude/S22j-GATE-D-DECISION.md:35,40` marks “Agent interview; valid spec; no invented numbers” and the full streak MET.
- Requirement: `evidence/qa/claude/GATE_D_PROTOCOL.md:66,72` requires a valid spec, chips plus free text, and all 3.1–3.8 passing. `Build/api/workspace/analysis.py:35-36` defines the owner question with `chips: []`; `:187-190` returns `owner_clip`, measurement, user scale and live fit **before** either `interview.answers_to_spec` or numeric validation (`:193-203`). `Build/web/src/workspace/controller.mjs:145-151` likewise accepts the owner-result branch before checking for `spec` and `validated_setup`. A successful fit is real, but is not a spec-validation result. Q16's numeric-contract amendment does not make this branch validate a spec.
- Impact: no invented fitter number was found, but the complete step and thus a protocol-conforming 3/3 PASS are not established. “Chips not evidenced” understates that the exercised question has none by design.
- **Owner lane / proposed row:** CLAUDE S22j, **R-D-fix-spec-verdict**: change 3.4 and the full-flow rehearsal summary to PARTIAL with the exact constrained owner-clip scope. Controller then either obtains an explicit criteria amendment or returns a smallest spec-validation/chips task to the original CODEX-1 S14 + CLAUDE S15 owners, followed by CODEX-2 S22 retest. Do not silently redefine “valid spec.”

### F2 — P2: The guest verdict silently substitutes a 2D trace for the protocol's 3D scene criterion

- `evidence/qa/claude/GATE_D_PROTOCOL.md:50` says “3D scene renders within 15 s; controls respond.” S22j `:49` calls 2.3 MET while explicitly conceding “trajectory viewer, not a 3D scene.” `evidence/qa/browser/S22g/RUN.md:13` says “SVG, no canvas”; `Build/web/src/viewer/trajectory-replay.mjs:58-67,91-100` implements a side-view SVG with reference axes, not geometry. The viewed `S22g/lo-375-demo2.png` agrees.
- Important nuance: the top-level Gate D definition only requires opening/running a library demo, and the newer `GATE_D_CHECKLIST.md:33,37-40` explicitly accepts playable traces. The protocol says that checklist supersedes the dependency table (`GATE_D_PROTOCOL.md:5`), not expressly criterion 2.3. This is a criteria inconsistency, **not** a demand to build unnecessary 3D geometry or a claim the useful library replay is broken.
- **Owner lane / proposed row:** CLAUDE S22j, **R-D-fix-viewer-criterion**: reconcile 2.3 with the approved trace-only fallback, document which requirement governs, and label 2.3 as a scoped deviation until resolved. Retain the honest SIMULATED side-view wording; recheck guest playback on the frozen build through CODEX-2 S22/S23c.

### F3 — P2: Exact streak timing/provenance is not independently auditable from the committed receipts

- `evidence/qa/browser/S22i/RUN.md:3` dates work 07:14–07:30Z, but `Run-System/Runs/S22i-orch237/TIMEBOX.json:3-8` stops/reports at **07:20:52Z**; `Run-System/Runs/S22i-orch237/REPORT.md:2` says work stopped **07:24Z**. Its evidence commit `341bc50c` was authored **07:20:53Z**, committed **07:21:13Z**. Thus both prose end times are later than the receipt and evidence commit. S22j's own heading `:3` uses 07:22–07:52Z although its receipt stopped 07:27:46Z and evidence was authored 07:27:48Z. These are real documentation inconsistencies, not proof that the flows were fabricated.
- S22i `RUN.md:8-13` retains cumulative 21.2/19.5/21.5-second tables and a console summary, but no per-flow UTC starts/ends, account-kind records, retained network/console capture, or protocol `run.json`. Protocol `:72-73,105-120` requires more than screenshots. S22j admits missing raw logs/JSON (`:99-100`), but still certifies the full streak (`:40`).
- Positive evidence: r1/r2/r3 screenshots have different hashes and different visible job IDs, show the same fitter output, and are consistent with several distinct successful jobs on the recorded build. All 14 inspected TIMEBOX files pass the existing arithmetic validator; author times generally follow stop times and integration commit times may be later. PNGs contain no embedded capture timestamps. These facts support plausibility, not independently timed fresh accounts or consecutiveness. No original script/log was imported from outside this worktree to fill the gap.
- **Owner lane / proposed row:** CODEX-2 S22, **R-D-fix-streak-receipts**, plus CLAUDE S22j verdict update: reconcile prose times to actual receipts without inventing per-flow times; preserve historical failures; capture a new frozen-build streak with per-flow UTC/monotonic timings, safe account aliases, version/SHA provenance and redacted network/console records. Do not retroactively manufacture logs. `Run-System/Runs/R-D-orch241/timing-audit.json` records the audit.

### F4 — P2: Browser-route and footage-release limitations need explicit disposition before capture

- Protocol `GATE_D_PROTOCOL.md:21` and checklist `GATE_D_CHECKLIST.md:16` require the ChatGPT in-app browser. S22c `RUN.md:30`, S22d `:3`, S22e `:3`, S22g `:3`, S22h `:28` and S22i `:3` instead identify standalone Playwright-driven bundled Chromium, explicitly not in-app in the earlier runs. S22j's account/timing limit (`:81-84`) says headed Chromium but does not explicitly identify this route deviation or cite an owner exception. The fresh-account authority receipt describes the signed-in in-app accounts (`evidence/owner/S22/S22-FRESH-ACCOUNT-AUTH-2026-10-31.md:5-12`); that is not, by itself, an express amendment of the browser rule. A controller handout choosing Playwright is not the same thing as a direct owner exception.
- Separately, `clips.csv:29` marks OWN05 **PRIVATE_PROCESSING_ONLY**, all rights reserved, public use pending owner approval; S22i `RUN.md:3` hid its frames by CSS for committed screenshots. S22j's video recommendation (`:116-117`) must not be read as footage-publication approval. Its disclosure list omits this limit. The separate public RM04 scene probe also does not grant rights for OWN05.
- **Owner lane / proposed row:** CODEX-2 S22/S24 + CLAUDE S22j, **R-D-fix-route-and-capture-scope**: attach any existing applicable owner route exception (do not ask again for authority already granted), or resolve the actual scope gap/rerun through the approved surface; carry the route caveat in the verdict. For video/public artifacts, keep owner footage excluded unless Koushik separately approves public use. Add this to the CODEX-2 S25 release disclosure/checklist. No new account, browser, or publication action is authorized by this review.

### F5 — P2: Legacy jobs without a budget can pair a new g with an unchanged old-scale uncertainty

- `Build/api/workspace/analysis.py:130-132` returns the recorded total unchanged when `u_budget` is absent, even though `owner_live_fit` recalculates g from a new length (`:90-101`). `jobs.py:197-202` resolves the persisted job measurement rather than refreshing its terms; S15bb's own REPORT `:36` explicitly notes older jobs lack the budget. Thus this is a reachable compatibility branch, not a claimed observation of a live legacy job.
- Fresh direct probe (`Run-System/Runs/R-D-orch241/fallback-probe.json`): with the same OWN05 measurement and only `u_budget` removed, 20.28 cm gives g **8.621873619319475**, u **1.28**; 40.56 cm gives g **17.24374723863895**, still u **1.28**. With the budget present the latter u is **2.574546958037049**. The old-scale fallback is not a compatible uncertainty for that rescaled value; the generic “uncertainty from the recorded S07m budget” label does not state the scale mismatch. Current fresh uploads used in S22i contain the budget and are not shown to suffer this issue.
- **Owner lane / proposed row:** CLAUDE S15/API, **R-D-fix-legacy-budget-scale**: for legacy measurements use a verified matching recorded budget, or refuse/abstain from presenting a current-scale headline uncertainty when no compatible budget is available. Do not invent terms or change the frozen fitter. Add one legacy-job/changed-scale regression test. CLAUDE S22j should disclose this compatibility limit rather than imply the fallback guarantees a correct combined u at every scale.

### F6 — P3: S15be did not resolve the reported fixture announcement

- S22j `:108-112` explicitly leaves the fixture role=alert wording to S15be. `Run-System/Runs/S15be-orch239/REPORT.md:7,14` says the title was already fixed and the alert is “most likely” the Next.js route announcer, **not browser verified**; it made no fix for that alert.
- `Build/web/src/auth/dev-scenes.mjs:19` still returns “Private development fixture”; `Build/web/src/shell/PrivateWorkspace.mjs:82-83,97,170` initially has `api = checking`, `live = false` and uses `scene.title` until the probe completes. The role=alert text was recorded even after the result in S22i `RUN.md:35`. The installed Next app-router announcer creates an assertive alert and derives text from document title or h1, which is consistent with a possible stale announcement, but this does not prove the observed node's origin or screen-reader behavior.
- Positive: the other S15be subtitle changes really are present: `Build/web/src/shell/workspace-shell.mjs:50-59` uses owner interview / live-fit labels for both tools; `Build/web/src/workspace/layout.mjs:18-21` separates “fit not run” from the live-fit heading. Those are source-verified, not newly browser-verified.
- **Owner lane / proposed row:** CLAUDE S15, **R-D-fix-announcer-recheck**: inspect the actual alert node and initial-load/route transition on the next approved browser run; fix its source minimally if it announces fixture wording during a live workspace. Keep this item OPEN rather than claiming S15be fixed all three items. Preserve genuine fixture disclosure where appropriate.

### F7 — P3: One fix report's alternate-scale uncertainty is not current code output

- `Run-System/Runs/S15bb-orch233/REPORT.md:21` reports 10 cm `u = 0.6348`; a fresh direct `owner_live_fit` returns **0.6350844502877578**, displayed **0.64**, because its absolute ruler term is recomputed at the new length. The 20.28 cm value agrees with the report and browser evidence. S22j itself quotes only the alternate `g = 4.25`, which is correct; no wrong current headline was found.
- **Owner lane / proposed row:** CLAUDE S15 / report owner, **R-D-fix-numeric-receipt**: append a sourced correction to the numerical receipt from the saved direct probe; do not hand-edit fitter outputs or round the implementation to match the old report. This is receipt hygiene, not a reason to change the fitter.

## Independent numeric and uncertainty checks

Fresh verification artifacts are under `Run-System/Runs/R-D-orch241/`:

- Required `python -m unittest tests/api-workspace/test_live_fit.py`: **7 passed**. Expanded fresh `python -B -m unittest tests/api-workspace/test_live_fit.py tests/api-workspace/test_analysis.py tests/api-workspace/test_jobs.py`: **28 passed**, `python-tests.txt`.
- `numeric-probe.json`: direct `owner_measurement('OWN05')` → `user_scale` → `owner_live_fit`, compared against an independent `fit_least_squares` + `gravity_quantity` + `jacobian_covariance` call on the non-held-out points. Four fitted points, three held out, dof 1. Perturbing held-out y values by 500 px leaves g and u unchanged. Residuals match a direct prediction of the held-out points.

| Answer | Code g (m/s²) | Code u (m/s²) | Display (2 decimals) |
|---|---:|---:|---|
| 20.28 cm | 8.621873619319475 | 1.2874051062222112 | 8.62 ± 1.29 |
| 10 cm | 4.2514169720510075 | 0.6350844502877578 | 4.25 ± 0.64 |

- Backend: `Build/api/workspace/analysis.py:80-81,96-106` excludes held-out points from fitting, calls the real fitter, and returns numbers, not model prose. `:179-190` executes this on POST spec for owner clips; `jobs.py:263-267` itself remains a recorded-result/no-scene path. It is **live CPU fitting on RECORDED tracking**, not live SAM, reconstruction or a physics gate pass.
- Rendering: `Build/web/src/workspace/controller.mjs:147-149` forwards `live_fit`; `view.mjs:92-107` prints its values with rounding only. Recorded reference is visibly separated (`view.mjs:118-124`). The curve comes from stored `measurement.series` (`result-chart.mjs:1,9-35`), not a new live-fit curve. S22j discloses this correctly.
- Uncertainty provenance: S07h `measure_heldout.py:2,11` imports S07i's rule; `evidence/S07/S07i/measure_own01.py:83-99` combines detection, timing, scale, centroid-vs-box; `:15-20,64-68` declares 0.5 mm ruler, 2 px detection, PTS/clock and independence assumptions. `Build/measurement/uncertainty.py:124-133` performs the conditional propagation. `evidence/S15bb/add_u_budget.py:18-33` copies/rederives those budget terms and asserts their recorded total; live `_u_total` (`analysis.py:117-134`) rescales terms, recomputes the length-dependent scale term, and adds current OLS scatter in quadrature.
- At the recorded 20.28 cm scale, original unrounded total is **1.2788792449092994** (recorded display 1.28); live total **1.2874051062222112** is larger. The new rule is **the recorded budget plus an extra fit-scatter term**, not exactly the original S07m total or a newly calibrated uncertainty. At 10 cm an absolute 1.28 floor would compare different scales; the correctly rescaled/recomputed budget is used instead. No smaller fit-only headline was found on fresh OWN05. The existing missing-budget test covers the original scale, but not the changed-scale legacy defect independently found in F5. Held-out errors are deliberately not an uncertainty term; do not call the uncertainty validated.
- Optional Node check: 5 owner-clip tests passed; 3 shell/retry test-file imports failed because isolated worktree `Build/web/node_modules` has no React. No dependencies installed or linked and no product conclusion inferred from the import failure. Full log: `node-tests.txt`.
- Optional anonymous GET at 08:00:24Z: `/` and `/library` both **200 HTML**, no redirect (`http-probe.json`). This is availability only, not fresh playback/auth/SHA verification.

## Claim-by-claim disposition of S22j

| S22j claim | Independent disposition / owning evidence |
|---|---|
| 3.1 test sign-up MET | Supported by QA testimony and Clerk development-mode screenshot; not Google, real inbox OTP, or human timing. No new sign-up was performed here. |
| 3.2 private empty workspace MET | Supported by S22i `RUN.md:13,20`; cross-owner 404 positive/negative controls are in S22g `:24-26`; current auth source checks identity/ownership. Not re-exercised after S15be. |
| 3.3 approved upload/stages MET | Supported, **allowlist only**. `jobs.py:243-248` rejects unknown SHA with 422; `status.mjs` and S22i `:18,24-27` support corrected status/retry/error copy. Spend-cap outcome is not runtime-tested. |
| 3.4 valid spec MET | **Not established / PARTIAL**, F1. Real free-text scale extraction and real fit are not spec validation/chips. |
| 3.5 fitter/residuals MET | **Agree on the narrow recorded owner-clip fit**, independently executed; labels and numbers match source/screenshot. Not live tracking/3D. |
| 3.6 sidebar N/A | Agree for this signed-in surface: tools at `workspace-shell.mjs:54-59` are Agent/Clips/Runs/Report. Does not verify backend sidebar tools or imply they are absent project-wide. |
| 3.7 report body MET | Body and fitter numbers supported by r1-report screenshot and renderer. Browser print fallback only; S22h `:12` did not generate a PDF, and S22i did not recheck print. No download/PDF success inferred. |
| 3.8 timing MET | QA reports scripted sub-300-second timings, not human timings. Exact independent timing audit is limited as F3. |
| 3/3 full-flow MET / PASS-on-DEV | **Change to scoped, evidence-limited rehearsal, not all-criteria PASS**, F1/F3; three result screenshots are not sufficient to fill missing step/trace evidence. |
| 2.1 root 200 | Prior logged-out browser evidence + fresh anonymous GET agree. |
| 2.2 licensed demo list MET | S22g `:13` / screenshot show SIMULATED project-authored demos, credit, 18 entries with only 3 simulated playable items and 15 unavailable, not 18 working recorded scenes. Underlying artifact hashing was S22b evidence cited by S22f, not freshly rerun here. |
| 2.3 scene/viewer MET | Trace replay supported; strict 3D wording unresolved, F2. Do not convert RM04's separate signed-in scene check into a guest library 3D pass. |
| 2.4 demo runs/labels MET | Supported by S22g `:13-14` and simulated replay source. Mystery-g numbers are simulated; no physical-g claim follows. Not freshly browser-run here. |
| 2.5 guest blocked MET | Supported by S22g `:21-26`, S22i `:23` screenshot, `server-access.js:26-31` (verified logged-out redirect; other failures 404), and job ownership guard `jobs.py:238-240`. |
| 2.6 console/network clean MET | Prior S22g summary only; no committed raw capture to independently replay. Scoped to that old guest session, not the current freeze. |
| Judging environment NOT MET (a,b) | **Agree**. No judging authorization/deploy verified. `dev-scenes.mjs:6-9` / `server-access.js:10` really gate private access on Railway env name `dev`; a successful DEV flow does not establish another environment. |

Defects D1/D3 have materially improved; D4's guard stays; D5/D6/D7/D8 visible-header fixes are supported by source and screenshots. D9's S22e prose was corrected to 16:06:46–16:10:04Z (`S22e/RUN.md:3`), inside its receipt, evidence authored 16:10:12Z/committed 16:10:29Z. D10 remains a headed/scripted QA limitation. D11 is closed only for the recorded logged-out home/library/lab session, not every current build. New F1–F5 prevent treating unresolved gate defects as closed merely because all three screenshots display the correct g.

## Disclosure checklist to carry into README/video/judge note

Retain all nine S22j limits, with these explicit completions:

1. DEV rehearsal only; env-name gating, no judging approval/pass. Record the frozen deployed SHA rather than assuming current main equals the tested deployment; S15be changed Build files after the streak and needs retest.
2. Fresh **Clerk development test** accounts, scripted headed Chromium, same OWN05/20.28 cm answer; not Google/real-email delivery/human timing or broader clip robustness. Explicitly disclose the not-in-app route and resolve its authority, F4.
3. Checksum-allowlisted uploads only; no arbitrary user-video processing; RECORDED precomputed SAM tracking, CPU fit run now, no live SAM/GPU on upload. OWN05 has no reconstructed scene.
4. Owner known-size branch has one free-text question, **no validated experiment spec/chips**, F1. Do not present it as the tested Gate A validated-setup path.
5. Scale user/owner-declared, not independently verified; phone clock not externally verified; uncertainty includes **declared assumptions**, not calibrated coverage. Legacy jobs lacking budget terms do not recompute the fallback u for a new length (F5). Only four fit points/dof 1; held-out errors are large. The displayed held-out PASS and prediction band belong to the stored third/post-hoc S07m analysis, not a fresh validated measurement.
6. Recorded chart/reference and live-fit number are separate; a new scale does not redraw the stored chart. Show the measured/recorded/simulated labels verbatim.
7. Guest playback is a **SIMULATED SVG side-view trajectory**, not a reconstructed 3D scene. Most library entries are UNAVAILABLE. F2 must be resolved before claiming the full literal protocol passed.
8. No API SPEND_PAUSED/402 outcome was observed, no real spend-cap demo, no claim of live failover; no need to spend to test it. No PDF/download/accessible-export claim; print-media body visibility is not a saved or usability-tested PDF.
9. Retained evidence has the timing/raw-capture limitations in F3. Role=alert fixture text remains unverified/unfixed in S15be, F6. S15be's other copy fixes are source-only until rechecked.
10. **Owner footage remains private-processing-only**, F4. CSS-hidden frames in QA screenshots are not permission to publish the actual video/frames; keep footage excluded or obtain separate approval. Preserve public-clip licence/credit boundaries independently.

Verbatim label sources checked: `analysis.py:39-40,111` (live-fit/track/scale caveat); `view.mjs:98,119` (fit done, separate recorded reference); `trajectory-replay.mjs:7`; `PrivateWorkspace.mjs:23` (scene geometry display-only). Current live-fit g/u and residuals are code output. The scene label applies only to an actual scene (`PrivateWorkspace.mjs:181`), not OWN05.

## Review scope / next action

Read both Claude judgements, protocol and linked checklist, all six requested browser RUN files, all six fix REPORTs, relevant API/workspace/shell/auth source, S07 uncertainty provenance, 14 timing receipts and Git author/commit metadata. Inventoried/hashes checked for all 45 PNGs; individually viewed 14 representative screenshots: S22c run2-17-report; S22d own05-result-1280; S22e w1280-result; S22g lo-375-demo2; S22h d3-report-1280; S22i r1-result, r1-report, r2-result, r3-result, i-d4-blank, i-offline, i-reload, i-o1-after, i-o2-logged-out. Screenshots corroborate visible states, not timing or freshness by themselves.

Controller: route the proposed rows to their original owners, preserve the **of-record NOT MET** decision and library-only fallback rule, and do not accept an unqualified parent Gate D completion until the criteria/evidence defects are disposed and the approved frozen candidate is retested. No product code, canonical controls, deploy, account, paid/GPU job or public artifact was changed by R-D.

Skipped: new browser/E2E/accounts, all 45 images at full resolution, complete dependency install/build and paid paths. Risk: this completed review is not a fresh candidate acceptance test, calibrated physics result, or permission to publish private footage.
