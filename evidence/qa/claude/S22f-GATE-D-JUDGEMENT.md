# S22f Gate D judgement (rehearsal evidence, DEV) and defect priorities

Judge: S22f-orch226, anthropic/claude-opus-5-5/high, 2026-10-31 ~16:11Z-16:30Z. Read-only: no product code, deploy or account.
Scope: S22b guest QA, S22c run 2 / S22d / S22e fresh-account runs, S15ay fixes, GATE_D_PROTOCOL.md (S22a), source in
Build/web/src + Build/api/workspace, screenshots viewed (S22e w375-after-upload, w1280-result; S22c run2-17-report),
plus one fresh read-only guest HTTP probe (below). Final pass/freeze decision is NOT made here (S22j).

## Bottom line

- **Gate D (a) as written: NOT MET.** Timing holds by a wide margin (3/3 scripted runs < 1 min to result), but the
  "full flow" is not exercised: Run/Fit never execute for the uploaded clip (protocol 3.5) and the report body was never
  verified rendered (3.7). All runs are on DEV; protocol: "Dev results are rehearsal evidence, not Gate D evidence."
- **Gate D (b) guest library demo: MET on DEV (rehearsal)**, not yet on a judging URL (none exists).
- **P2-1 decision: Gate D as written requires an executed fit for the uploaded clip.** Upgrade P2-1 -> P1. Smallest
  honest change: execute the existing fitter on the stored RECORDED track points (see D1). Live SAM 3.1 tracking per
  upload is not required for that and is not proposed.

## Gate D definition used

- final plan / QUEUE.md:656: "Gate D (Nov 3): fresh account completes the full flow in under 5 minutes, 3 runs in a row; logged-out judge can run a library demo"
- QUEUE.md:599: "Gate D: a fresh account completes upload to report in under 5 minutes, 3 runs in a row"
- evidence/qa/claude/GATE_D_PROTOCOL.md section 3 steps 3.1-3.8, section 2 steps 2.1-2.6; "Screenshots alone never pass a step (S22f rule): need timing log + network/console capture."

## Per-criterion verdict

### (a) Fresh-account full flow x3 (protocol section 3)

| # | Criterion | Verdict | Exact evidence |
|---|---|---|---|
| 3.1 | Sign up / sign in | MET (test route) | S22c RUN: "Clerk dev test email, subaddress +clerk_test ... fixed test code 424242"; S22e: "Two NEW Clerk test accounts". Google and real-email OTP untested (S22c "Not done"). |
| 3.2 | Land in private workspace, own empty state | MET | S22e: "Post sign-up landing: /workspace/dev-fixture-... (private workspace), NOT /library (both accounts)". S22c/S22d landed on /library first (fixed by S15ay P3-4). |
| 3.3 | Upload approved clip, stage events visible | PARTIAL | Upload works for OWN05 (all runs). But only clips.csv hashes are accepted: Build/api/workspace/jobs.py create(): `"sha256 is not an owner-approved clips.csv clip"` (422). Stage timeline for the owner clip reads "Queued / Processing / Scene ready" while the job says "no scene" (run2-17-report.png; Build/web/src/workspace/status.mjs:28). |
| 3.4 | Agent interview, valid spec, no invented numbers | PARTIAL | One question asked/answered: "Question 1 of 1: Name one object of known size in the fall plane ..." (S22e). No spec shown/validated for owner clips; result card is visible before the answer and the answer only adds scale lines (S22e "answer then chart ordering is not enforced"). |
| 3.5 | Run experiment / fit: fit table + residuals from fitter | **NOT MET** | S22e: stepper Run/Fit "(not run)"; "No pipeline stage ran for this owner clip (no recording; live execution is not enabled)." Source: jobs.py complete() sets `"executor": "none"` for any owner clip and returns `owner_job(job_id)` with the stored `owner_measurement(clip)`; the fitter is never called. Card: "Clip result (owner clip; no scene, run or fit)". |
| 3.6 | Sidebar patch/search (if in build) | NOT TESTED | No run exercised it. |
| 3.7 | Report rendered; numbers == fitter; download/print or honest fallback | PARTIAL | Runs reach "Report available" (S22d, S22e, run2-17-report.png shows only the tool card). S22e: "report body after click not verified to differ from pre-click page text"; S22d: "did not verify the report body renders after click". Download/print not tested. |
| 3.8 | Total < 5:00 | MET (scripted) | Result at 29.3 s (S22c, 62.8 s incl. Report), 57.9 s (S22d, incl. fixed 8 s wait), 24.2 s / 48.2 s (S22e 1280 / 375). Report click 43-55 ms after S15ay; 33.5 s once in S22c (not reproduced). |

**3 consecutive < 5 min:** holds for timing only. Caveats: (1) all timings are Playwright-scripted (headed bundled
Chromium), exclude human reading/typing and real-email delivery; the ~5x margin makes a human < 5:00 likely but that is
an estimate, not measured; (2) Clerk test accounts (+clerk_test, 424242), not Google/real inbox; (3) S22c run 1 was
BLOCKED by environment (no flow executed), so I do not count it as a streak reset; (4) the three runs span three builds
(S22c pre-fix, S22d web c74afc74, S22e web b7a61913); protocol 6: "a fixed flow still needs a fresh 3-in-a-row streak"
on the approved candidate; (5) DEV only. Because 3.5 fails in every run, **no run passes 3.1-3.8, so the streak is 0/3
as written** even though the timing streak is 3/3.

### (b) Logged-out judge runs a library demo (protocol section 2)

| # | Criterion | Verdict | Exact evidence |
|---|---|---|---|
| 2.1 | Root 200, no login wall | MET (DEV) | Fresh probe 2026-10-31T16:13Z (node fetch, no cookies): "/ 200 425ms". |
| 2.2 | /library lists licensed demos | MET (DEV) | Probe: "/library 200 173ms"; "/api/library/manifest 200 89ms ... demos=18". S22b L1/L3: labels + artifact sha256 match. |
| 2.3 | Demo scene renders | MET with caveat | S22b L4: "Projectile (201 samples) and pendulum (251 samples) open, play, scrub ... at 1280 and 375". Caveat (S22b): IAB session "was SIGNED IN as owner ... guest-equivalent". |
| 2.4 | Demo runs, numbers labelled | MET (DEV) | S22b L4 "SIMULATED trajectory — simulator output, not a measurement"; probe: "lab start 200 436ms status=ok", "lab fit 200 119ms fit.status=ok". |
| 2.5 | Private route blocked for guest | MET (DEV) | S22c run 1 probe: "/workspace 404 (anonymous, unauthenticated GET)". |
| 2.6 | Console/network clean | MET (signed-in runs) | S22e: "zero console errors, zero >=400 responses". No fresh logged-out browser console capture. |
| env | On judging URL | NOT MET | No candidate/judging environment exists (protocol 0: written candidate-deploy approval required). |

## Prioritised defects

Priority key (maps protocol P0/P1/P2): **P1** = blocks Gate D as written or of record; **P2** = honesty/clarity a judge sees; **P3** = polish/evidence hygiene.

| ID | Pri | Defect (verified how) | Owner lane | Proposed fix row |
|---|---|---|---|---|
| D1 (was P2-1) | P1 | Upload never runs Fit; result is a sha256-keyed replay of a precomputed MEASURED result (RUN.md x3 + jobs.py complete()). Fails protocol 3.5. | CLAUDE S15 (Opus high) | **S15az** Owner-clip live fit, server-side: after the interview answer, run the EXISTING pure fitter Build/fitter/core.py fit_least_squares / select_model (as Build/real2sim/boundary.py fit_prefix already does) on the stored RECORDED prefix points of owner_clips.json (held-out excluded) inside Build/api/workspace; Fit stage "done"; show fitter coefficients, residuals, rmse/dof and held-out residuals labelled "SIMULATED fit (fitter, run now) to RECORDED MEASURED SAM 3.1 track points"; keep the recorded S07m value as a separate labelled MEASURED reference; Run stage labelled "Track: RECORDED (precomputed SAM 3.1, not run live)" instead of "(not run)". Do NOT route through POST /api/workspace/fit: Build.fitter.api.handle rejects non-simulated inputs (probe: `source.label must be "simulated" for S11 synthetic values`), and relaxing that trust boundary is a larger change. Scale: user's answer x a RECORDED reference pixel length; owner_clips.json has none (keys: height, measurement, r_frame_rate, scale_reference, scale_value_m, series, sha256, width), so take it from the S07 source file or keep the fit in px and label scale unverified; never invent. Accept: test that the displayed values equal the fitter output on the same points; no model-authored numbers; build green. |
| D2 | P1 | No judging/candidate environment; all Gate D runs on DEV = rehearsal (protocol 0). Also source: private workspace exists only when Railway env name is "dev" (Build/web/src/auth/dev-scenes.mjs developmentScenesEnabled; server-access.js:10 returns null otherwise), so a non-dev judging env would give fresh accounts no workspace. Source-verified only, not runtime-tested. | Koushik (written candidate approval) + CODEX-2 S23 (Sol) | **S23-pre**: decide judging env shape (promote DEV service vs new env); if new env, replace the dev-name check with an explicit env flag and persistent scene store; then S22i re-runs the 3-run streak + guest on that URL. |
| D3 | P1 | Report body never verified rendered after click; download/print untested (S22d, S22e caveats; run2-17-report.png shows only "Report available"). Protocol 3.7/5.4. | CODEX-2 S22 (Sonnet) + CLAUDE S17 if broken | **S22i** includes: click Report, assert report body text contains the fitter g and labels, test download/print or honest fallback; capture network/console. |
| D4 | P2 | Uploads accepted only for approved clips.csv hashes (jobs.py 422 "sha256 is not an owner-approved clips.csv clip"). A judge's own video cannot complete the flow. Deliberate rights guard; must be disclosed. Error copy shown in UI not verified. | CLAUDE S25 README + S22j | **S22j/S25**: README "Upload limits" states the allowlist; S22i checks the UI message for a non-allowlisted file. |
| D5 | P2 | Owner-clip job timeline shows "Queued / Processing / Scene ready" directly below "no scene: owner clip, scene reconstruction not run" (run2-17-report.png; status.mjs:28 STEPS). Contradictory. | CLAUDE S15 (Sonnet medium) | **S15ba** For executor "none" jobs: timeline ends "Clip result ready (no scene)"; same row as D6/D7. |
| D6 | P2 | Result card label "user-declared scale 0.2028 m" is visible before the fresh user declares anything (S22d/S22e: "answering only adds the scale lines"); the declaration is the owner's, recorded earlier. Only the matching 20.28 cm answer was ever tested, so whether a different answer changes g is unverified (source: g comes from stored owner_measurement, so it cannot). | CLAUDE S15 (with S15az) | Folded into S15az: show result only after the answer; scale from the user's answer, or relabel "owner-declared scale (recorded)". |
| D7 | P3 | "Scene geometry: Display only, scale unverified, not a measurement." shown for OWN05 with no scene, above an empty 3D grid placeholder (w375-after-upload.png; PrivateWorkspace.mjs:163 renders it whenever `live`). Controller candidate confirmed. | CLAUDE S15 (Sonnet medium) | S15ba: render SCENE_LABEL and the viewer only when a scene is loaded. |
| D8 | P3 | Workspace header "Private development fixture" on every signed-in view (w375-after-upload.png, w1280-result.png; dev-scenes.mjs:19 title). Reads as fake to a judge. Controller candidate confirmed. | CLAUDE S15 (Sonnet medium) | S15ba: title "Private workspace" when live; keep fixture wording only in fixture mode. |
| D9 | P3 | Evidence timestamp: S22e RUN.md "Date 2026-10-31 ~16:08Z-16:20Z" but S22e REPORT/TIMEBOX end 16:10:04Z and its commit is 16:10:29Z. End time is wrong (STATE line "16:20Z" likewise approximate). | Controller (docs) | Correct the S22e RUN.md date line to the TIMEBOX times. |
| D10 | P3 | Headless Chromium stalls on Cloudflare Turnstile at sign-up (S22c ENV); headed passes. QA-route limit, real browsers unverified. | CODEX-2 S22 | Keep headed route for S22i; note in protocol. |
| D11 | P3 | 3.6 sidebar patch/search and guest 2.3/2.6 in a truly logged-out browser not exercised. | CODEX-2 S22 | S22i: logged-out Playwright profile for library render + console; sidebar check if in build. |

Resolved from S22c: P3-1 (s04o-probe 404), P3-2 (375 px auto-open), P3-4 (redirect) FIXED per S22e RUN.md and S15ay
REPORT; P3-3 (Report 33.5 s) not reproduced (43/48/55 ms), cause undiagnosed, treated as script artifact.

## What would make Gate D (a) pass as written (for S22j, not decided here)

D1 + D3 fixed (and D2 environment), then a fresh 3-in-a-row streak (protocol 6). Otherwise the QUEUE S22 fallback applies:
"the demo video uses the library path and the README states the upload limits honestly." D1's change keeps tracking
recorded, so the README must still say uploads are limited to approved clips with precomputed tracks.

## Limits of this judgement

- Did not drive a browser; flow verdicts rest on RUN.md text + source + viewed screenshots; guest probe is HTTP only.
- D1 feasibility probe only (not a product number): Build/fitter/core.py fit_least_squares ran on the 4 OWN05 prefix points (7 total) with degree 2 and returned a FitResult (dof 1, very weak). A live g needs the missing reference pixel length; it may differ from the recorded 8.62 m/s^2 (S07m used a different analysis). Show fitter output as is; do not reconcile by hand.
- D2's non-dev behaviour is source-read only.

