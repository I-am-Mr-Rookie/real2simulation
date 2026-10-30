# S15o controller walk (exception) — DEV, ChatGPT in-app browser

Run by the controller chat on 2026-10-30 ~20:58-21:06Z. Worker S15o-orch161 could not reach the in-app browser: the IAB is bound to the controller chat session (cua inventory metadata codexSessionId = controller), so it is unavailable inside worker chats. Recorded controller exception; no code changed.
Web DEV e6bf5fe2, API DEV a2777e67. Profile was already signed in as the owner; auth was not changed. No paid call.

| # | Stage | Result | Evidence |
|---|---|---|---|
| 1 | Signed-in /workspace -> own dev workspace, LIVE notice ("Connected to the private workspace API…") | PASS | 01-live-notice.png |
| 2 | Upload approved RM04 (test-data/public/RM04.mp4, sha256 8231fbca…87ec per S15o-orch161) — 4 chunks + complete, all 200 | PASS | 02-after-upload.png; API log |
| 3 | Job job_95c6a189… queued -> processing -> scene ready | PASS | 02-after-upload.png |
| 3b | RECORDED provenance labels (S13h-orch46 / S14g-fix3) visible | FAIL (P2): only the generic "RECORDED or SIMULATED by the server" notice; stage labels not rendered | page text |
| 3c | Scene viewport | FAIL (P2): "The scene could not be shown" + "LOAD_FAILED: Scene could not be loaded" (no RM04 geometry bytes on dev; cf. optional S13j) | 02-after-upload.png |
| 4 | Interview: GET questions 200; 2 questions shown; answered 1.5 m, "Starts at rest" | PASS | 03-after-interview.png |
| 5 | Spec: POST scenes/{job}/spec -> **422** (API log). UI shows only "All questions answered." with no error and no next step | FAIL (P1): expected 200 + label 'scale unverified, not setup-validated' (S14j). Likely request-body/answer-shape mismatch between web interview answers and interview.answers_to_spec ({id: {chip}|{text}}); UI swallows the error (P2) | 04-stuck-after-spec-422.png; API log |
| 6-8 | Run / Fit / Report | NOT REACHED (blocked by 5; Run additionally pending owner Q20) | — |
| 9 | 375px viewport: scrollWidth 360 == clientWidth 360, no horizontal scroll | PASS | 05-375px.png |
| 10 | Console: only the Clerk development-keys warning; no secret/token visible in page text | PASS | tab console |

Other defects (P3): nav shows "Sign in" link while signed in; footer says "No uploads are enabled" while uploads work.

