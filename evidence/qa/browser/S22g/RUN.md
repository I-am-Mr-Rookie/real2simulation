# S22g 375 px and auth-boundary QA

Date 2026-10-31 16:26Z-16:40Z. Route as S22e: Playwright (codex runtime playwright-core), HEADED bundled Chromium, throwaway scripts %TEMP%/s22g. DEV https://web-dev-cd80.up.railway.app. Fresh contexts per check; new Clerk test accounts (s22g-*+clerk_test@example.com, code 424242, kept, emails not committed). No Chrome profile, no in-app browser. Viewport 375 renders clientWidth 360 (scrollbar); 1280 -> 1265.

## Verdict: PASS on all checks; 4 P3 observations (no P1/P2).

## 1. Logged-out fresh profile (375 / 1280)
| Check | Result |
|---|---|
| Overflow (scrollWidth == clientWidth) on /, /library, library demo open, /lab run, /lab fit | PASS both widths (360=360, 1265=1265) |
| Console errors / responses >=400 over whole session | PASS: none (both widths) |
| / labels | PASS: "Real2Simulation", "Sign in", "Try the demo library", "Open the lab", "Guess the Gravity", "RECORDED / SIMULATED / what-if", "We abstain when scale is unverified." |
| /library 2 demos incl. viewer | PASS: "SIMULATED · PLAYABLE", "SCALE_UNVERIFIED", "Display only · not a measurement.", "Play simulated replay" -> "Hide replay", viewer (SVG, no canvas) banner "SIMULATED trajectory: simulator output, not a measurement", "reference axes (not scene geometry)"; projectile (201 samples) and pendulum (251 samples) both opened (screens demo1, demo2). Counts "All 18, RECORDED 0, SIMULATED 3, what-if 0, UNAVAILABLE 15" |
| /lab Mystery-g start + fit | PASS: checkbox "Mystery-g mode / Hide the simulated gravity until reveal" on, "Run trial" -> "Trial ready. Fit the ballistic model or run another trial.", "Fit & reveal" -> "Fit complete. This is simulated evidence, not a calibrated measurement.", "REVEAL 4.810 ± 0.0000545 m/s^2 / Gravity · source: simulated", "Uncertainty is one standard uncertainty (1σ), not a 95% interval." Footer "DEVELOPMENT BUILD" present |
D11 (logged-out profile) closed for library/lab/home. Sidebar patch/search not in the logged-out UI (not exercised).

## 2. Auth boundary
| Check | Result |
|---|---|
| Logged-out GET /workspace | PASS (no data): one redirect, final status 404 at /workspace (not a sign-in page, see O2) |
| Logged-out GET /api/workspace/jobs, /jobs/abc, /scenes/abc/bundle/scene.json, /clips | PASS: 401 {"status":"error","error":{"code":"UNAUTHORIZED","message":"Sign in required."}} |
| Logged-out GET /api/workspace/ | 308 -> /api/workspace (then 401 class) |
| Logged-out POST /api/workspace/jobs | PASS: 401 same body |
| Account A owner positive control | 200 on /api/workspace/scenes/<job>/questions and /api/workspace/jobs/<job> (job_progress); /bundle/scene.json 404 "scene bundle file not found" (owner clip has no scene bundle) |
| Account B reads A's job | PASS: GET /api/workspace/jobs/<A job> -> 404 {"detail":{"code":"NOT_FOUND","message":"job not found"}}; /scenes/<A job>/bundle/scene.json -> 404 "job not found"; /scenes/<A job>/questions -> 404 "scene not found"; /scenes/<A job>/spec -> 405 (GET not allowed, no data); B GET A's /workspace/dev-fixture-<A> page -> 404. Owner vs B messages differ, so the 404 is ownership, not a dead route |
| Sign-out clears access | PASS: Clerk signOut -> lands "/"; /workspace -> 404; A's job API URLs -> 401 "Sign in required." |

## 3. 375 px signed-in (account A)
PASS: no horizontal overflow at workspace, after upload, panel open, after answer. Header: logo, library/lab/github/theme icons, "Workspace" + avatar (no email shown). "Private development fixture", "Connected", question card "Agent needs your answer. Question 1 of 1: ..." with "Answer in agent panel", toggle badge "1", "Agent & tools" panel opens full-width: question, "Your answer" textarea, "Finish" (disabled until text), tools Agent/Clips/Runs & history/Report ("Report available" after finish). Answer + Finish worked; "g = 8.62 ± 1.28 m/s² (MEASURED (owner clip OWN05, user-declared scale ..." text present.

## Observations (proposed rows, owner lanes; none fixed here)
- O1 P3: after Finish at 375 the Agent & tools panel stays open (tool list) and covers the result card; user must close it (screen in-375-result). Proposed: auto-close/scroll to result on Finish.
- O2 P3: logged-out /workspace ends on a bare 404 after redirect rather than sign-in; safe but confusing. Proposed: redirect to /sign-in.
- O3 P3: library opens one replay at a time (opening one hides the other's "Hide replay"; 2nd demo opened after 1st collapses). Not a defect if intended.
- O4 P3: /api/workspace/scenes/<id>/spec returns 405 to GET (info only).

## Limits
Headed Chromium (D10), Playwright route only; not the in-app browser or real Chrome. Test uses own owner clip OWN05 for upload (frames hidden by CSS, not committed). Sidebar patch/search not exercised. Script timings not human timings.

## Privacy
Committed screens: in-375-after-upload (grid placeholder, avatar only), in-375-panel, in-375-result, lo-375-lab-fit, lo-375-demo2. Viewed before commit; no emails, no owner frames. Account emails not recorded.

