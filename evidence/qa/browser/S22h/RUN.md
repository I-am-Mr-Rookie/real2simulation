# S22h retry, spend-cap and Report QA

Date 2026-11-01 06:35Z-06:56Z. Route as S22g: Playwright (codex runtime playwright-core), HEADED bundled Chromium, fresh contexts, new Clerk test accounts (s22h-*+clerk_test@example.com, code 424242, kept, emails not committed). DEV https://web-dev-cd80.up.railway.app (web 5d26756d, api 885a1368 per controller). OWN05 uploaded with video hidden by CSS. Throwaway scripts in %TEMP%/s22h. No code, env or paid call touched.

## Verdict: D3 PASS, D4 PASS-with-P2 copy, retry PASS-with-P2, spend cap code-read only (not live-observable). No P1.

| # | Check | Result |
|---|---|---|
| 1a | Report renders (D3): account A, OWN05 + "book cover horizontal edge 20.28 cm", click Report | PASS. Report is the main page body (the Report tool button scrolls to it; button text stays "Report available"). Body text: "g = 8.62 ± 0.15 m/s² (fitter, Build/fitter/core.py fit_least_squares(degree 2) + jacobian_covariance (OLS, RSS/dof))"; "Scale: user-declared scale 0.2028 m over a RECORDED 287.6 px reference; scale unverified"; "Held-out points (3) were excluded from this fit and only score it. Few fitted points (dof = 1); ... not a validated measurement."; "Your known size: book cover horizontal edge 20.28 cm = 0.2028 m (user-declared, not verified)"; plus recorded reference "g = 8.62 ± 1.28 m/s² (MEASURED ...)", held-out PASS chi2/dof 2.32/3, p 0.51 with forking-paths caveat. Screen d3-report-1280.png |
| 1b | Live-fit card values exact | "SIMULATED fit (fitter, run now) to RECORDED MEASURED SAM 3.1 track points"; g = 8.62 ± 0.15 m/s²; "Fit residuals (px): 0.1, -0.2, 0.2, -0.1; rmse = 0.12 px; dof = 1; points fitted = 4"; "Held-out residuals (px, 3 points not fitted): 4.6, 9.6, 19.9"; banner "HELD-OUT CHECK PASS: CHI2/DOF = 2.32/3, P = 0.51" |
| 1c | Second account, "book cover horizontal edge 10 cm" | PASS: g = 4.25 ± 0.07 m/s² (scale 0.1 m), differs from 8.62; same residuals/dof. 8.62 -> 4.25 is exactly the 10/20.28 ratio |
| 1d | Download / print | No download/print/export control exists (visible buttons enumerated). Honest fallback: browser Ctrl+P only; print-media body text identical length (3147 = 3147), so nothing hidden for print; PDF output not generated (headed). Not a defect, a gap: propose row |
| 2a | Reload mid-interview (upload done, question pending) | State is dropped: page returns to "No file uploaded yet / Waiting for an upload / No job yet", no error, no spinner. Honest but the pending question and job are not resumed (screen retry-reload.png). P3 |
| 2b | Upload same clip twice | After the answer the file input is removed (0 inputs): second upload impossible in the same session, result unchanged. No stuck state |
| 2c | Offline then online | Offline pick: "DEPENDENCY_UNAVAILABLE: Workspace API unreachable." in a red box, no spinner, no stuck state. After online: red box stays; picking the SAME file again made no request and no change (P2, F run; screen retry-offline-online.png). Picking a DIFFERENT file then OWN05 again: requests POST,PUT,POST, interview textarea appears, error cleared (G run). No Retry button exists in this state |
| 3 | Spend cap | Code-read only. Web maps HTTP 402 -> SPEND_PAUSED (controller.mjs), copy "Processing is paused by a spend limit. Retrying will not help until it is lifted." (status.mjs), Retry withheld (workspace README). Build/api never emits 402 or SPEND_PAUSED (rg), and the owner-clip path runs no GPU/model. Read-only DEV: unauthenticated /api/workspace/jobs -> 401 "Sign in required."; /api/health -> 404 on web. Live outcome NOT observable without triggering paid work (forbidden) |
| 4 | D4 non-allowlisted file | PASS: 1 s blank mp4 (ffmpeg) -> POST /api/workspace/uploads 422; UI red box exactly "INVALID_INPUT: sha256 is not an owner-approved clips.csv clip"; page returns to "No file uploaded yet", no spinner. Static hint above already says "Only approved licensed clips listed in clips.csv are accepted; other files are rejected by checksum." (screen d4-nonallowlisted.png) |

## Proposed fix rows (none applied)
- P2 Upload input: reset input.value after each attempt (or key the input) so re-picking the same file after an error retries; add a visible Retry/"Choose file again" in the DEPENDENCY_UNAVAILABLE box.
- P2 D4 copy: replace raw "INVALID_INPUT: sha256 ..." with plain text, e.g. "This clip is not on the approved list. Use a demo clip from the library; your own videos can't be processed in this build."
- P3 Persist or resume the interview after reload, or say "Session reset, upload again".
- P3 Add Download/Print report (or document Ctrl+P) before judging.
- P3 Report: recorded-reference lines still show "scale ... 0.2028 m" below a user scale of 0.1 m (labelled recorded, but can confuse); consider a divider.
- P3 SPEND_PAUSED is unreachable from the API today (no 402); confirm the guard's surface before claiming it in the demo.

## Limits
Headed Chromium, Playwright route only; not in-app browser/real Chrome. 1280 px only. No live spend-cap observation. Tracks are recorded OWN05; no live SAM/GPU. Retry F/G differences inferred from request logs, root cause (same-file change event) not code-verified.

## Privacy
Committed screens: d3-report-1280, d4-nonallowlisted, retry-reload, retry-offline-online. Viewed before commit; no emails, no owner frames (video hidden).
