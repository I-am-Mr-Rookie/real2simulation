# S22c Gate D fresh-account run 1: BLOCKED (no in-app browser)

Verdict: FAIL/NOT RUN. The full flow was not executed, so there is no timing against the <5 min target.

- Account letter used: none. Sign-up method: none. No account was created.
- Blocker (P1, environment): cua_repl cannot reach the in-app browser from this chat.
  - createBrowserTab("iab", url, {visible:false}) threw "Browser is not available: iab" at 13:57Z and again at 14:19Z.
  - cua.listBrowsers() returned []. cua.getState() listed only native apps.
  - Chrome was not used (owner rule: in-app browser only). No other browser was substituted.
- Controller messaging tool was not available in this chat, so no nonterminal blocker could be sent.
- Only HTTP probes were run (no login, GET only), 2026-10-31T13:58Z:

| Path | Status | ms |
|---|---|---|
| / | 200 | 867 |
| /library | 200 | 432 |
| /lab | 200 | 417 |
| /sign-up | 200 | 224 |
| /api/library/manifest | 200 | 359 |
| /workspace | 404 (anonymous, unauthenticated GET) | 249 |

Probes show the DEV site is up. They are not evidence of sign-up, upload, interview, fit or report behavior.
No screenshots, console logs or labels were captured. No defects against the app were observed.
Next action: run S22c where iab is exposed (a chat created by the app for this project), reusing evidence/owner/S22/S22-FRESH-ACCOUNT-AUTH-2026-10-31.md.



## Run 2 (S22c-orch220): headless-route retry, fresh DEV accounts. Verdict: PASS vs <5 min (scripted), with defects below

Date 2026-10-31 14:36Z to 14:50Z. Route: Playwright (codex runtime playwright-core), bundled Chromium, 1280x800 plus one 375 px pass. Not Chrome, not the in-app browser. Site: https://web-dev-cd80.up.railway.app (DEV).

### Sign-up method
- Clerk dev test email, subaddress +clerk_test (r2s-gated-run1, 1b, 1c, 1d, 1e @example.com), email code step with fixed test code 424242. No real inbox, no Google. No Clerk setting changed. Test emails accepted (test mode on).
- Bot check: HEADLESS Chromium stalled on "Verifying your request / Please wait while we verify your request." (Cloudflare Turnstile, cf-turnstile-response hidden input) for more than 25 s, never reached the code prompt. HEADED bundled Chromium (headless:false, hidden-driven via CDP) passed in about 1 s with no interaction. Nothing was bypassed or altered. Implication: automated/headless QA of sign-up needs a headed browser; real users on a normal browser are not affected (unverified for real devices).
- Browser console on first load: Clerk development-keys warning (expected).

### Timings (account r2s-gated-run1c, one scripted pass, 1280x800, real timestamps START 14:45:01Z, END 14:46:03Z)
| Step | Duration | Cumulative |
|---|---|---|
| 1 home load (hero visible) | 1.8 s | 1.8 s |
| 2 home -> sign-up form | 2.5 s | 4.3 s |
| 3 submit email -> code prompt | 1.3 s | 5.6 s |
| 4 enter 424242 -> signed in (lands on /library) | 2.2 s | 7.8 s |
| 5 -> private workspace (/workspace/dev-fixture-...) | 1.1 s | 8.9 s |
| 6 upload OWN05 mp4 -> interview question | 19.1 s | 28.0 s |
| 7 type answer + Finish -> result (chart, g, labels) | 1.3 s | 29.3 s |
| 8 open Report | 33.5 s (see P3-3) | 62.8 s |
Time to result: 29.3 s. Including Report: 63 s. Target <5 min: PASS. Caveat: scripted, no human reading/typing time; account run1b gave the same shape (result at 25.3 s). An earlier exploratory pass (account run1, step by step) was not timed as a flow.

### Flow reached
home -> sign-up -> /library -> Private workspace -> upload accepted (checksum-approved owner clip) -> one agent question "Name one object of known size in the fall plane and its length with units, e.g. book cover edge in cm." -> answered "book cover horizontal edge 20.28 cm" -> "Clip result (owner clip; no scene, run or fit)" with chart -> Report available.

### Labels seen verbatim (result)
- "OWN05 · OWNER_RECORDED / RECORDED · RECORDED replay of a MEASURED result"
- "g = 8.62 ± 1.28 m/s² (MEASURED (owner clip OWN05, user-declared scale 0.2028 m, phone clock not externally verified))"
- "HELD-OUT CHECK PASS: CHI2/DOF = 2.32/3, P = 0.51"; source note: "S07m v3 predictive chi-square; a THIRD, post-hoc analysis chosen after v1/v2 failed, forking-paths caveat ... A PASS is conditional on these assumptions and is not accuracy: it can still sit far from the local 9.79 m/s^2."
- Chart legend: "RECORDED track points (filled: fit prefix; hollow: held out)", "SIMULATED fit to the prefix (solid)", "SIMULATED prediction over the held-out points (dashed)", "1-sigma predictive band: sigma_px * sqrt(1 + leverage) (S07m v3 held-out variance), sigma 2 px"; axis note "Scale unverified. RECORDED replay of MEASURED SAM 3.1 track points; curve SIMULATED (quadratic fit to the prefix)". Chart has 1-sigma band, held-out divider, "Show data table".
- "Scale: book cover horizontal edge in fall plane = 0.2028 m (user-declared, not verified)"; "Your known size: book cover horizontal edge 20.28 cm = 0.2028 m (user-declared, not verified)".
- Stage text: "no scene: owner clip, scene reconstruction not run (not a live run)"; "No pipeline stage ran for this owner clip (no recording; live execution is not enabled). Nothing failed; no scene is shown." Stepper: Upload done, Interview done, Run "(not run)", Fit "(not run)", Report.
- Header chips: "Connected", "Instruments off". Footer banner: "DEVELOPMENT BUILD ... Synthetic lab results are not calibrated measurements."

### 375 px (account run1e)
Result screen renders with the chart, divider, band and Upload/Interview/Report chips; document scrollWidth 360 <= 375 viewport width in 1280 pass after resize, no horizontal page overflow seen. The Agent & tools panel auto-opens full screen after upload (see P3-2). Screens: run2-b24-375-result-top.png. (run2-b25 chart-scroll shot failed in script; run2-b24 already shows the chart.)

### Console / network errors
- HTTP 404 GET /api/workspace/jobs/s04o-probe on every workspace load, plus the generic console "Failed to load resource ... 404" (P3-1).
- A Cloudflare Turnstile CSP console error ("Fetch API cannot load data:,") appeared only in the headless bot-check stall. No page errors otherwise.

### Defects
| ID | Sev | Finding |
|---|---|---|
| P2-1 | P2 | The end-to-end journey never executes Run or Fit: result is a precomputed OWN05 replay (stepper "Run (not run)", "Fit (not run)", "no scene", "live execution is not enabled"). A new user gets a chart and g with honest labels but no 3D scene or live fit. Matches the labels; Gate D "run/fit" step is not exercised. |
| P3-1 | P3 | Every workspace load requests /api/workspace/jobs/s04o-probe and gets 404 (console error). Looks like a leftover probe id. |
| P3-2 | P3 | At 375 px the Agent & tools panel opens over the whole screen after upload; user must find the X to see the scene/result area. |
| P3-3 | P3 | Opening Report took 33.5 s in the script (Playwright click wait); cause not diagnosed (could be hidden/overlapping control or script artifact). Unverified; recheck by hand. |
| P3-4 | P3 | Post sign-up redirect lands on /library, not the workspace; user must click "Private workspace". |
| ENV | info | Headless Chromium blocked by Turnstile bot check at sign-up (see above); headed passes. |

### Screens (evidence/qa/browser/S22c/)
run2-10-home, run2-11-signup, run2-12-after-signup, run2-13-workspace, run2-14-interview-q, run2-15-agent-panel, run2-16-result, run2-17-report (1280); run2-b20..b24 (375). run2-01..03 are from the first exploratory pass (03 shows the email code prompt). Video preview hidden in all post-upload shots; no owner clip frames.

### Not done
No human-eye usability pass; Google sign-up; real-email OTP delivery (test code only, so email delivery is untested); Gate D runs 2 and 3.


