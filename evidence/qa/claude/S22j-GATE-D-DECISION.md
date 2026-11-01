# S22j final Gate D decision and freeze recommendation

Judge: S22j-orch238, anthropic/claude-opus-5-5/high, 2026-11-01 07:22Z-07:52Z, from main 341bc50c. Read-only: no product
code, deploy, account or paid call. Inputs: evidence/qa/claude/S22f-GATE-D-JUDGEMENT.md (criteria, D1-D11),
evidence/qa/claude/GATE_D_PROTOCOL.md, Run-System/Runs/{S15az-orch227,S15ba-orch228,S15bb-orch233,S15bc-orch234,S15bd-orch236}/REPORT.md,
evidence/qa/browser/{S22g,S22h,S22i}/RUN.md, source in Build/api/workspace and Build/web/src. Screenshots viewed:
S22i r1-result.png, r1-report.png, i-d4-blank.png, i-o2-logged-out.png; each cross-checked with RUN text and source
below (no verdict rests on a screenshot alone). I did not drive a browser.

## Decision

- **Gate D (a) private flow: MET on DEV as rehearsal (3/3 fresh streak); NOT MET of record** (no judging URL).
- **Gate D (b) guest library: MET on DEV as rehearsal; NOT MET of record** (no judging URL).
- **Overall: PASS-on-DEV, of-record PENDING S23.** Protocol line 100: "S22j: PASS only with 3 consecutive <5:00 fresh runs
  + guest pass on the judging URL; else library-only fallback with upload limits." Line 53/16-17: dev = rehearsal. A
  judging URL needs Koushik's written approval (protocol line 14; QUEUE S23a). So the strict PASS is not available today.
- **Fallback status:** QUEUE.md:606 "Fallback: If Gate D fails at freeze, the demo video uses the library path and the
  README states the upload limits honestly." Gate D has not failed; it is unproven of record. Recommendation:
  1. Plan for PASS: private flow is the primary demo path, conditional on S23c re-running the fresh 3/3 streak and the
     guest walkthrough on the judging URL (QUEUE S23c: "repeat S22 smoke").
  2. If S23a approval does not arrive, or S23c fails, by freeze: library-only fallback applies verbatim (QUEUE.md:606).
  3. In BOTH branches the README must state the upload limits (D4 below): even the passing flow only accepts clips.csv
     allowlisted clips with RECORDED precomputed tracks.

## (a) Fresh-account full flow x3 (protocol section 3, lines 63-72)

Build: DEV https://web-dev-cd80.up.railway.app, web 45fbd535 / api e32e910f "per controller" (S22i/RUN.md:3; SHA not
read from a version endpoint by S22i).

| # | Criterion | Verdict | Exact evidence |
|---|---|---|---|
| 3.1 | Sign up / sign in | MET (test route) | S22i/RUN.md:3 "new Clerk test accounts (s22i-*+clerk_test@example.com, code 424242 ...)"; :13 "Each run: signed up". Google and real-email OTP not exercised (S22f:30). Sign-in card shows Clerk "Development mode" (i-o2-logged-out.png, viewed). |
| 3.2 | Land in private workspace, own empty state | MET | S22i/RUN.md:13 "landed on the private workspace"; :20 D8 FIXED "Header/title \"Private workspace\""; r1-result.png header "Private workspace". Isolation: S22g/RUN.md:25 account B reads A's job -> 404. |
| 3.3 | Upload approved clip; stage events; cap message honest | MET (allowlist only) | S22i/RUN.md:13 "upload accepted"; :18 D5 FIXED "Queued / Processing / Clip result ready (no scene)" (source Build/web/src/workspace/status.mjs:38). Allowlist: Build/api/workspace/jobs.py:247 "sha256 is not an owner-approved clips.csv clip"; UI copy S22i/RUN.md:26 and Build/web/src/workspace/view.mjs:67 (seen in i-d4-blank.png). Cap: S22h/RUN.md:16 "Build/api never emits 402 or SPEND_PAUSED"; re-checked: rg "SPEND_PAUSED" Build/api -> 0 hits; web copy only at status.mjs:43. Not live-observable. |
| 3.4 | Agent interview; valid spec; no invented numbers | MET (free text; chips not evidenced) | S22i/RUN.md:7 answer "book cover horizontal edge 20.28 cm"; :21 D6 FIXED "Clip result: shown after you answer the known-size question." S22h/RUN.md:11 a 10 cm answer gives g = 4.25, "exactly the 10/20.28 ratio" (answer drives scale; g not stored). Numbers come from the fitter (3.5). Chips not shown in any S22g-i evidence. |
| 3.5 | Run experiment / fit: fit table + residuals from fitter | MET (fit live on RECORDED track) | S22i/RUN.md:13 "\"Track: RECORDED ... Fit: done (run now on the server)\", g = 8.62 ± 1.29 m/s² (fitter core.py fit_least_squares degree 2 + jacobian_covariance)", residuals "0.1,-0.2,0.2,-0.1 px, rmse 0.12, dof = 1, held-out residuals 4.6, 9.6, 19.9 px". Source: Build/api/workspace/analysis.py:39-40 labels; view.mjs:97 "Fit: done (run now on the server)"; S15az REPORT:7 owner_live_fit runs fit_least_squares on held_out == false points; S15az REPORT:19 test "displayed g/held-out residuals equal a direct fitter call". u = 1.29: S15bb REPORT:16,21 "g = 8.6219 +- 1.2874". r1-result.png shows the same strings. Closes S22f D1. |
| 3.6 | Sidebar patch/search (if in build) | N/A (not in signed-in UI) | r1-result.png tools list: Agent, Clips, Runs & history, Report only; rg -i "patch" Build/web/src/shell/PrivateWorkspace.mjs finds no patch/search control. Not exercised (S22i/RUN.md:36). |
| 3.7 | Report rendered; numbers == fitter; download/print or honest fallback | MET (print fallback only) | S22i/RUN.md:13 "Report click: body text contains the fitter g, scale, held-out and \"not a validated measurement\" caveats"; r1-report.png shows g = 8.62 ± 1.29, residuals, scale line, divider + "Recorded reference (not affected by your scale)" (view.mjs:118; S22i/RUN.md:28). Report is the page body, not a separate document (S22h/RUN.md:9). Download/print: no control; browser Ctrl+P print-media body identical length 3147 = 3147, PDF not generated (S22h/RUN.md:12, on web 5d26756d). Closes S22f D3. |
| 3.8 | Total < 5:00 | MET (scripted) | S22i/RUN.md:10-12 home->report 21.2 s, 19.5 s, 21.5 s; :13 "Console errors: 0 in all three." |
| streak | 3 consecutive passing 3.1-3.8 | MET on DEV | S22i/RUN.md:5 "Gate D streak 3/3 PASS"; all three on one build (:3), per protocol line 99 "a fixed flow still needs a fresh 3-in-a-row streak". |
| env | On judging URL | NOT MET | Protocol lines 14-17; no S23 record; QUEUE S23a-c TODO. |

## (b) Logged-out judge runs a library demo (protocol section 2, lines 46-53)

| # | Criterion | Verdict | Exact evidence |
|---|---|---|---|
| 2.1 | Root 200, no login wall | MET (DEV) | S22g/RUN.md:12 "/ labels PASS ... \"Try the demo library\"" in a fresh logged-out profile; S22f:51 "/ 200 425ms". |
| 2.2 | /library lists licensed demos | MET (DEV) | S22g/RUN.md:13 counts "All 18, RECORDED 0, SIMULATED 3, what-if 0, UNAVAILABLE 15"; S22f:52 manifest demos=18, sha256 match (S22b). |
| 2.3 | Demo scene renders, controls respond | MET (trajectory viewer, not a 3D scene) | S22g/RUN.md:13 projectile (201 samples) and pendulum (251 samples) open; "viewer (SVG, no canvas)"; "reference axes (not scene geometry)". |
| 2.4 | Demo runs; numbers labelled | MET (DEV) | S22g/RUN.md:13 "SIMULATED trajectory: simulator output, not a measurement"; :14 Mystery-g "REVEAL 4.810 ± 0.0000545 m/s^2 / Gravity · source: simulated". |
| 2.5 | Private route blocked for guest with clear sign-in prompt | MET (DEV) | S22g/RUN.md:21,23 API 401 "Sign in required."; S22i/RUN.md:23 O2 FIXED "/workspace -> /sign-in"; i-o2-logged-out.png shows the sign-in card; source S15bc REPORT:6. |
| 2.6 | Console/network clean | MET (DEV) | S22g/RUN.md:11 "Console errors / responses >=400 over whole session: PASS: none (both widths)". |
| env | On judging URL | NOT MET | Protocol line 53: "(b) passes only when 2.1-2.5 pass on the approved candidate/judging URL". |

Caveat: (b) was last browser-run by S22g (2026-10-31 16:26Z-16:40Z; web SHA not recorded in its RUN.md), before
S15ba/bb/bc/bd. Those runs changed workspace/shell/auth files; the library route is not in their reported changes, but
(b) has not been re-run on web 45fbd535. S23c must re-run it on the judging URL.

## S22f defects: final state

| ID | State | Evidence |
|---|---|---|
| D1 fit not executed (P1) | FIXED | 3.5 above. |
| D2 no judging env (P1) | OPEN, owner-gated | See limit 1; Build/web/src/auth/dev-scenes.mjs:6-9 private workspace only when Railway env name is "dev"; server-access.js:10 returns null otherwise. |
| D3 report body (P1) | FIXED (print = browser fallback) | 3.7 above. |
| D4 allowlist (P2) | GUARD KEPT, copy FIXED; README disclosure pending S25 | jobs.py:247; view.mjs:67; S22i/RUN.md:26. |
| D5 timeline | FIXED | S22i/RUN.md:18. |
| D6 scale label before answer | FIXED | S22i/RUN.md:21. |
| D7 scene label/viewport for no-scene | FIXED | S22i/RUN.md:19; S15bb REPORT:17. |
| D8 header | FIXED (header); role=alert leftover in S15be | S22i/RUN.md:20,35. |
| D9 S22e timestamp | Not rechecked here (docs, controller). | S22f:73. |
| D10 headless Turnstile | OPEN as QA-route limit | S22g/RUN.md:38 headed Chromium only. |
| D11 logged-out profile | CLOSED for home/library/lab | S22g/RUN.md:15. |

## Honest limits that must be disclosed (README / video / submission text)

1. **DEV only; no judging environment.** All evidence is DEV rehearsal (protocol lines 16-17). D2 needs Koushik's written
   candidate/judging approval (S23a) and S23b/c. Structural: a non-"dev" Railway environment gives fresh accounts no
   workspace (dev-scenes.mjs:6-9, server-access.js:10; source-read only, S22f:66). S23 must either promote the DEV
   service shape or add an explicit env flag before the freeze SHA, then re-run the streak.
2. **Accounts and timing.** Clerk test accounts (+clerk_test, code 424242) on a Clerk development instance ("Development
   mode" on the sign-in card); Google and real-email OTP untested. Timings are Playwright-scripted in headed Chromium and
   exclude human reading/typing and email delivery (S22f:39-41; S22i/RUN.md:3). A human < 5:00 is likely (~14x margin)
   but not measured.
3. **Uploads limited to the clips.csv allowlist (D4).** jobs.py:247 rejects any other checksum with 422; UI says
   "This clip is not on the approved list. Try a demo clip from the library; your own videos cannot be processed in this
   build." (view.mjs:67). A judge's own video cannot complete the flow.
4. **Track points are RECORDED precomputed SAM 3.1; only the fit runs live.** analysis.py:40 "Track: RECORDED
   (precomputed SAM 3.1, not run live)"; no live SAM/GPU per upload (S22h/RUN.md:28). The result chart curve is the
   stored S15aw series/curve, not redrawn from the live fit (S15az REPORT:26).
5. **Scale is user-declared, unverified.** S22h/RUN.md:9 "Scale: user-declared scale 0.2028 m over a RECORDED 287.6 px
   reference; scale unverified"; a different answer changes g proportionally (S22h/RUN.md:11). Not a calibrated measurement.
6. **Held-out residuals are shown, and large.** 4.6, 9.6, 19.9 px vs fit rmse 0.12 px, dof = 1 (S22i/RUN.md:13); the held-out
   PASS (chi2/dof 2.32/3, p 0.51) is a post-hoc third analysis with a forking-paths caveat (r1-report.png; S22h/RUN.md:9).
   u = 1.29 combines fit scatter with recorded S07m budget terms (S15bb REPORT:16); it is not a validated uncertainty.
7. **SPEND_PAUSED is not observable from the API today** (S22h/RUN.md:16, :25; rg Build/api -> 0 hits). Do not claim a
   live spend-cap demo; the owner-clip path runs no GPU/model.
8. **No download/print control**; browser print is the fallback (S22h/RUN.md:12). Report = page body.
9. **Evidence format:** S22g-i recorded RUN.md tables + screenshots; raw scripts/logs stayed in %TEMP% (S22i/RUN.md:3), not
   protocol section 7 run.json files. Deployed SHAs are "per controller", not from a version endpoint.

## Freeze recommendation

Freeze candidate: the main SHA that contains S15be and is deployed to the judging URL by S23b; S23c records it via the
version endpoint (QUEUE S23c "Version endpoint equals frozen SHA").

**May still change before judging (each later change to Build/ requires a fresh 3/3 streak + guest pass, protocol line 99):**
- Row S15be P3 copy only (row present in the canonical working QUEUE.md, not yet in committed main 341bc50c):
  (1) Agent/Runs subtitle "Scene ready; interview in progress (not a measurement)" for no-scene owner clips
  (Build/web/src/workspace/layout.mjs:14; S22i/RUN.md:34); (2) report.owner copy "Clip result (owner clip; no scene,
  run or fit)" although the fit now runs (layout.mjs:18; visible as the Agent subtitle in r1-result.png);
  (3) role=alert "Private development fixture" on signed-in pages (dev-scenes.mjs:19 title; S22i/RUN.md:35).
- S23 judging deploy: S23a written approval, S23b promote, S23c verify; plus the env-flag change in limit 1 only if the
  judging env is not named "dev".
- README "Upload limits" and the disclosures above (S25 / S22f D4 row). Docs only.
- Video capture S24d-f (media/capture, media/edit only): show the labels verbatim, use the private flow only after S23c
  passes, otherwise the library path (QUEUE.md:606).

**Must not change after freeze:**
- Fitter and live-fit numeric path: Build/fitter/core.py, Build/api/workspace/analysis.py owner_live_fit, owner_clips.json
  values (scale_reference_px, u_budget, series). No hand-reconciled or model-authored numbers.
- The allowlist guard jobs.py:247 (rights boundary) and the auth boundaries (401 "Sign in required.", cross-account 404,
  /workspace -> /sign-in).
- Labels, verbatim: "SIMULATED fit (fitter, run now) to RECORDED MEASURED SAM 3.1 track points" and
  "Track: RECORDED (precomputed SAM 3.1, not run live)" (analysis.py:39-40); "Fit: done (run now on the server)"
  (view.mjs:97); "Recorded reference (not affected by your scale)" (view.mjs:118); "Scale unverified; not a validated
  measurement." (analysis.py:111); "SIMULATED trajectory: simulator output, not a measurement"
  (Build/web/src/viewer/trajectory-replay.mjs:7); "Scene geometry: Display only, scale unverified, not a measurement."
  (Build/web/src/shell/PrivateWorkspace.mjs:23).
- Library manifest/demos and licences; no new features, models, providers or paid paths.

## Next

R-D (Sol, cross-vendor) reviews this decision. Then S15be, S25 README limits, S23a (Koushik), S23b/c, S24d-f.

