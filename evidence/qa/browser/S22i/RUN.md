# S22i recheck candidate after fixes: fresh Gate D streak

Date 2026-11-01 07:14Z-07:30Z. Route as S22h: Playwright (codex runtime playwright-core), HEADED bundled Chromium, fresh contexts, new Clerk test accounts (s22i-*+clerk_test@example.com, code 424242, kept, emails not committed). DEV https://web-dev-cd80.up.railway.app (web 45fbd535, api e32e910f per controller). OWN05 uploaded with video hidden by CSS; committed shots contain no owner-footage frames. Scripts in %TEMP%/s22i. No code, env or paid call touched.

## Verdict: Gate D streak 3/3 PASS. All listed defects fixed. No P1/P2; two P3 leftovers.

## 1. Streak (1280 px, fresh account each, OWN05, answer "book cover horizontal edge 20.28 cm")
| Run | home->workspace | upload->interview ready | answer->fit shown | Report body | total (home to report) | 3.5 fit executed | 3.7 report body |
|---|---|---|---|---|---|---|---|
| 1 | 12.6 s | 16.2 s | 18.5 s | 21.2 s | 21.2 s | PASS | PASS |
| 2 | 10.9 s | 14.6 s | 16.8 s | 19.5 s | 19.5 s | PASS | PASS |
| 3 | 13.2 s | 16.6 s | 18.9 s | 21.5 s | 21.5 s | PASS | PASS |
All < 5 min (limit 300 s). Each run: signed up, landed on the private workspace, upload accepted, result card: "Track: RECORDED ... Fit: done (run now on the server)", g = 8.62 ± 1.29 m/s² (fitter core.py fit_least_squares degree 2 + jacobian_covariance), "Uncertainty: fit 0.15, detection 1.27, clock 0.07, centroid vs box 0.12, scale 0.07 (quadrature)", fit residuals 0.1,-0.2,0.2,-0.1 px, rmse 0.12, dof = 1, held-out residuals 4.6, 9.6, 19.9 px, held-out PASS chi2/dof 2.32/3 p 0.51, scale and unverified labels. Report click: body text contains the fitter g, scale, held-out and "not a validated measurement" caveats, "Your known size ... (user-declared, not verified)". Console errors: 0 in all three. Stepper reads Fit "(not run)" before the answer and "Fit: done" after (Fit pill text not re-read after; line in card is). Screens: run1-result.png, run1-report.png, run2-result.png, run3-result.png.

## 2. Defect recheck
| Defect | Result | Evidence |
|---|---|---|
| D5 timeline | FIXED | Owner clip timeline "Queued / Processing / Clip result ready (no scene)" |
| D7 no scene label/viewport for no-scene clips | FIXED | OWN05 body has no "Display only" line and no viewport; only placeholder text "No scene yet. The viewport appears when an upload produces a scene." |
| D8 header | FIXED | Header/title "Private workspace" in nav and page |
| D6 scale label before answer | FIXED | "Clip result: shown after you answer the known-size question."; recorded scale labelled "owner-declared scale (recorded)" |
| O1 375 px panel closes after Finish | FIXED | 375 px: panel opened, Finish, textarea gone, g visible (o1-after.png) |
| O2 logged-out /workspace | FIXED | /workspace -> /sign-in, sign-in form present |
| Same-file re-pick after offline error | FIXED | Offline: "DEPENDENCY_UNAVAILABLE: Workspace API unreachable." + Try again button. Online same-file re-pick: POST,PUT,POST, interview textarea appears |
| "Try again" | FIXED | Offline error, online, click Try again: POST,PUT,POST, interview textarea appears |
| Non-approved clip | FIXED | blank 1 s mp4: "This clip is not on the approved list. Try a demo clip from the library; your own videos cannot be processed in this build." with small code INVALID_INPUT |
| Reload mid-interview | FIXED | "Your earlier session was reset by the page reload. Upload the clip again to start over." (reload.png) |
| Divider before "Recorded reference" | FIXED | DOM check (4th fresh account): an hr is the previous sibling of the "Recorded reference (not affected by your scale)" heading |

## 3. RM04 scene job: PASS
Upload RM04 (public Pexels clip): scene loaded in ~40 s wait, canvas count 1, point cloud visible, label "Scene geometry: Display only, scale unverified, not a measurement." shown above the stepper (rm04-1280.png). 3 interview questions waiting; not answered.

## Observations (P3, none applied)
- P3 Runs & history / Agent tool subtitle still reads "Scene ready; interview in progress (not a measurement)" for the OWN05 no-scene job before the answer, contradicting "no scene" (r1-pre.txt). Proposed: reuse the owner label there (S15 shell/status row).
- P3 A role=alert element with text "Private development fixture" exists in the DOM of signed-in workspace pages (DOM check, fresh account, also after the result); document.title is "Real2Simulation", so it is not the title. Whether it is visible/announced to screen readers was not checked. Proposed: relabel as "Private workspace" like D8 (S15 owner lane).
- Not tested: print/download (unchanged from S22h: no control), spend cap live, non-dev judging env (D2), sidebar patch/search, logged-out library render (D11).

