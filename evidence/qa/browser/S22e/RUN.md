# S22e Gate D fresh-account run 3 (fixed build)

Date 2026-10-31 16:06:46Z-16:10:04Z (TIMEBOX; corrected by controller per S22f D9). Route as S22c/S22d: Playwright (codex runtime playwright-core), HEADED bundled Chromium, script %TEMP%/s22e/r.mjs (throwaway). DEV https://web-dev-cd80.up.railway.app (deploy 243368cd / web b7a61913). Two NEW Clerk test accounts (s22e-<w>-<id>+clerk_test@example.com, code 424242), kept. No Google, no Chrome profile, no in-app browser.

## Verdict: PASS vs <5 min (scripted). 1280 px: result visible 24 s after page load (incl. sign-up), Report opened. 375 px: PASS on the Agent-panel check.
| Step (cumulative s) | 1280 | 375 |
|---|---|---|
| home | 8.4 | 7.8 |
| sign-up form filled | 10.4 | 9.2 |
| code prompt | 11.4 | 10.1 |
| signed in | 14.1 | 12.3 |
| private workspace | 18.6 | 16.9 |
| upload -> interview question shown | 23.9 | (30 s fixed wait ends) 47.1 |
| answer + finish | 24.2 | 48.2 |
Report click: 48 ms (1280), 55 ms (375). Script timings; no human time. The 375 "report" mark (79.8 s) is a script wait-timeout artifact, not app latency.

## Checks
- Post sign-up landing: /workspace/dev-fixture-... (private workspace), NOT /library (both accounts).
- Console/network: zero console errors, zero >=400 responses, zero requests to s04o-probe on workspace load (both accounts).
- 375 px: after upload the Agent panel does NOT open (agent form 0x0); question card "Agent needs your answer. Question 1 of 1" plus toggle badge "1 question waiting" shown above the result; clicking "Agent & tools" opens the panel, question answerable (textarea found, answer + Finish worked). Screens: w375-after-upload, w375-result.
- 1280 px: panel open beside the result; chart and result card visible (w1280-result).

## Verbatim labels (same as S22d)
"Agent needs your answer. Question 1 of 1: Name one object of known size in the fall plane and its length with units, e.g. book cover edge in cm." / "Answer in agent panel"; "Clip result (owner clip; no scene, run or fit)"; "OWN05 · OWNER_RECORDED / RECORDED · RECORDED replay of a MEASURED result"; "g = 8.62 ± 1.28 m/s² (MEASURED (owner clip OWN05, user-declared scale 0.2028 m, phone clock not externally verified))"; "HELD-OUT CHECK PASS: CHI2/DOF = 2.32/3, P = 0.51"; legend "RECORDED track points (filled: fit prefix; hollow: held out)", "SIMULATED fit to the prefix (solid)", "SIMULATED prediction over the held-out points (dashed)"; after answer: "Scale: book cover horizontal edge in fall plane = 0.2028 m (user-declared, not verified)", "Your known size: book cover horizontal edge 20.28 cm = 0.2028 m (user-declared, not verified)"; "No pipeline stage ran for this owner clip (no recording; live execution is not enabled). Nothing failed; no scene is shown."; stepper Run/Fit "(not run)".

## S22c defects
| ID | Status |
|---|---|
| P2-1 Run/Fit never execute | STILL PRESENT (stepper "(not run)", recorded replay; "live execution is not enabled") |
| P3-1 404 s04o-probe | FIXED (no request, no 404) |
| P3-2 375 px panel covers result | FIXED (no auto-open; badge + on-demand open) |
| P3-3 Report click slow | Not reproduced (48/55 ms). Caveat: report body after click not verified to differ from pre-click page text (page text identical in script capture) |
| P3-4 redirect to /library | FIXED (lands on workspace) |
New defects: none observed. Observation: the recorded result card (g = 8.62...) is already visible before the question is answered; answering only adds the scale lines, so "answer then chart" ordering is not enforced (P3, matches S22d, not new).

## Privacy
Committed: w1280-result.png (chart/labels, video hidden by CSS), w375-after-upload.png (3D grid placeholder), w375-result.png. No email, no owner frames. Viewed before commit.

