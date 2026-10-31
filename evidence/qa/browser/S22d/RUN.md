# S22d Gate D fresh-account run 2 + RM04 viewer check

Date 2026-10-31 15:42Z-15:52Z. Route (same as S22c run 2): Playwright (codex runtime playwright-core), HEADED bundled Chromium, 1280x800 plus 375 px. DEV https://web-dev-cd80.up.railway.app (web c74afc74, api a0a27f13). Clerk test email (+clerk_test@example.com, unique per run), code 424242. No Google, no Chrome profile, no in-app browser. Accounts not deleted. Real email not shown in committed shots.

## Verdict: PASS vs <5 min (scripted): result in ~58 s from page load (incl. 8 s fixed wait in script), Report opened.
| Step | Cumulative |
|---|---|
| home loaded (networkidle, headed) | 10.4 s |
| sign-up form filled | 17.5 s |
| code prompt | 18.6 s |
| signed in (lands /library) | 21.5 s |
| private workspace (/workspace/dev-fixture-...) | 24.0 s |
| OWN05 upload -> interview question | 49.1 s (upload step 25.1 s) |
| answer "book cover horizontal edge 20.28 cm" + Finish -> result chart | 57.9 s (includes fixed 8 s wait; result was present by then) |
| open Report | click took 43 ms |
Scripted; no human reading/typing time. Turnstile passed headed (no stall).

## OWN05 labels (verbatim, same as S22c)
- "Agent needs your answer. Question 1 of 1" (panel text: "Name one object of known size in the fall plane and its length with units, e.g. book cover edge in cm.")
- "Clip result (owner clip; no scene, run or fit)"; "OWN05 · OWNER_RECORDED / RECORDED · RECORDED replay of a MEASURED result"
- "g = 8.62 ± 1.28 m/s² (MEASURED (owner clip OWN05, user-declared scale 0.2028 m, phone clock not externally verified))"
- "HELD-OUT CHECK PASS: CHI2/DOF = 2.32/3, P = 0.51"; "A PASS is conditional on these assumptions and is not accuracy: it can still sit far from the local 9.79 m/s^2."
- Legend: "RECORDED track points (filled: fit prefix; hollow: held out)", "SIMULATED fit to the prefix (solid)", "SIMULATED prediction over the held-out points (dashed)", 1-sigma band; axis note "Scale unverified. RECORDED replay of MEASURED SAM 3.1 track points; curve SIMULATED (quadratic fit to the prefix)".
- "No pipeline stage ran for this owner clip (no recording; live execution is not enabled). Nothing failed; no scene is shown." Stepper Run/Fit "(not run)". Report card: "Report available".

## RM04 check (same account, DEV geometry from S13m): PASS
- Upload RM04 (Pexels) -> after ~25 s: scene loaded, no 503, no console error besides the 404 below. canvas count 1; point cloud visible (screens rm04-1280, rm04-375-closed).
- Visible labels verbatim: "Scene geometry: Display only, scale unverified, not a measurement." (chip above stepper; the exact requested wording is present). Viewer banner: "RECONSTRUCTION: METRIC SCALE UNVERIFIED (NOMINAL MODEL OUTPUT, NOT CALIBRATED); NOT PHYSICS OR GATE R EVIDENCE". Controls "+", "−", "▶". "Scene loaded." Status "RECORDED S13h-orch46 (not a live run)"; stages validate/keyframes/understand/segment/reconstruct/package all RECORDED (understand: S14g-fix3 @ 2026-10-30T05:06:04Z); "replay of recorded S13h events with their original UTC timestamps; not a live run".
- Interview asks 3 questions (first: "How far does the ball fall before it lands, in metres?"); I did not answer them (Report shows "No report yet (needs a finished fit or clip result)"). Not tested: Run/Fit for RM04 (not run), 3D orbit/play interaction.
- 375 px: the Agent & tools panel again opens full-screen after upload and hides the scene; after closing it the point cloud renders at 375 px (rm04-375-closed). Chips wrap cleanly.

## S22c defects: reproduction
| ID | Status |
|---|---|
| P2-1 Run/Fit never execute (precomputed replay, no scene for OWN05) | Reproduced (stepper "(not run)", "live execution is not enabled"); RM04 shows scene but also a recorded replay, not live |
| P3-1 404 GET /api/workspace/jobs/s04o-probe on every workspace load | Reproduced (every load) |
| P3-2 375 px panel auto-opens full screen after upload | Reproduced (RM04 375 shot) |
| P3-3 Report click 33.5 s | NOT reproduced: 43 ms. Caveat: Report is a card/stepper chip; I confirmed the card text "Report available" but did not verify the report body renders after click |
| P3-4 post sign-up redirect to /library | Reproduced |
New: none. Headless not retried (headed only).

## Console/network
Only 404 s04o-probe plus generic "Failed to load resource" 404. No 503, no page errors.

## Privacy
Committed shots: own05-result-1280 (chart/labels only, scrolled past video, video hidden by CSS), rm04-1280, rm04-375-closed (Pexels frames). No email, no owner frames.


