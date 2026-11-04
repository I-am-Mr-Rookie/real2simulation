# Real2Simulation: independent judge review, round 8

Reviewed 2026-11-04 against main `262b24cc` and https://real2simulation.rookiecoders.tech. Live `/api/version`: web `ea258fba` (round 7 fixes), api `6f6a5090` (round 5). Rubric: "Event Rules and Participant Guide.md" lines 130 to 150. I assumed an average recorded demo video with voiceover. All browser testing was signed out, in fresh headed Playwright Chromium contexts at 1440x900 and 375x812. I did not sign in, upload, call paid APIs or change anything except this file. I read rounds 1 to 7 and REPORT.md first and kept the same strictness. I credit what the evidence shows, not the fact that a suggestion was followed.

## 1. Scores

| Criterion | Weight | Round 7 | Round 8 | Weighted points |
|---|---:|---:|---:|---:|
| Impact | 30% | 6.5 | **6.5** | 19.5 |
| Use of Meta AI tooling | 25% | 8.0 | **8.0** | 20.0 |
| Technical depth and execution | 20% | 7.0 | **7.0** | 14.0 |
| Demo | 25% | 8.0 | **8.0** | 20.0 |
| **Total** | | **73.5** | | **73.5 / 100** |

## 2. Reasoning per criterion

**Impact (6.5).** The round 7 change narrows the calibration gap but does not close it. The new landing-frame check (`drop_contact` in `Build/pipeline/live_experiment.py`) is physically motivated, is applied the same way to every clip, and moved one clip (OWN01, 9.82 to 9.07) away from 9.81, which argues against it being tuned to hit g. I checked `evidence/N89/own-sweep-refit/summary.json` against the round 5 file: the median moves from 8.62 to 9.03 and the spread from 0.72 to 0.56, and the home page shows exactly those numbers (confirmed live). But the method still reads about 8 percent low, 6 of 11 drops are still more than 2 sigma below 9.81, and the evidence is still one person, one book, one phone, one table, with no student or teacher in the loop. For a classroom "film it, measure it, compare with a simulation" tool, an 8 percent bias with honest disclosure is usable, but it is the same impact story as last round. Same score.

**Use of Meta AI tooling (8.0).** No change in this round. Hosted SAM 3.1 does the tracking and the Muse Spark agent drives list, track and fit tools (recorded turn in `evidence/N89/muse-measures-book.json`). The refit used stored SAM tracks, no new model calls. Solid multi-step use of two Meta models with real ops work behind it; nothing that would surprise Meta. I could not trigger the agent signed out. Same score.

**Technical depth and execution (7.0).** Good: `drop_contact` is small, has a 1 px floor so clean tracks are left alone, only ever drops one frame, and comes with a test that checks both the drop and the no-op case. I ran `tests/pipeline/test_live_experiment.py` (14 of 14 pass) and `tests/web-private` (32 of 32 pass). The round 7 P3 on mixed frames is fixed: before Play the strip reads "Tracked object reading (m): 0.500 at t = 0.37 s. MEASURED" and after the auto-pause "ball-1 y position (m): 0.446", which is the 5.4 cm gap the status text reports (confirmed live). No page errors and no console errors on `/`, `/library`, `/lab`, `/guide` and the OWN07 replay at either width. Against that, the deployed API was not updated: `/api/version` reports api revision `6f6a5090`, which is the round 5 commit, and the API runs `live_experiment.analyse` in process (`Build/api/experiment/__init__.py` line 119). So the home page sentence "The pipeline now drops that frame" is true of the repo and the refit, not of what a judge's upload would run today (defect 1). The judging URL still uses a Clerk development instance, and the error bars are still too small for the observed spread, which is a calibration flaw in the fitter's uncertainty model. A useful fix offset by a deploy gap. No move.

**Demo (8.0).** The replay is now the best moment in the product and it holds up live. At 1440 px and 375 px, at Speed 0.25x, Play auto-pauses at t = 0.37 s, the camera zooms onto the last dot and the ball, and the 5.4 cm gap at gravity 9.81 is visible as well as readable; at 1440 px, Gravity y set to -9.07, then Play gives "0.4 cm below the last dot at gravity 9.07"; Reset restores the full track view (all confirmed with screenshots). That removes the round 7 phone complaint. I did not raise the score because the desktop gap was already visible last round, so the gain is mostly for phone visitors, and the remaining weaknesses are unchanged: no side-by-side ghost ball at the fitted g, the home page is 13,240 px tall on a phone, and the "Guess the Gravity: Watch a drop. Guess g." card still drops you on the generic `/lab` template picker rather than a drop to watch. With an average video, 8.0 is the honest ceiling for what I saw.

## 3. Defects found

Severity: P0 security or data loss, P1 blocks or undermines a core claim, P2 significant usability or correctness, P3 polish.

No P0 or P1 found.

1. **P2, the live API does not run the round 7 landing-frame check that the home page describes.** URL: `https://real2simulation.rookiecoders.tech/api/version`. Repro: `curl -s https://real2simulation.rookiecoders.tech/api/version` returns `"api_revision":"6f6a5090..."`; `git log --oneline -1 6f6a5090` is the round 5 commit and `git log 6f6a5090..ea258fba -- Build/pipeline` lists the round 7 commit, which added `drop_contact`. The home page says "The pipeline now drops that frame". Confirmed live (version) and from source (the API imports `live_experiment` in process). If `api_revision` is not tied to the deployed code, the team should make it so; either way a judge cannot tell from the outside.

2. **P2, the headline measurement is still biased low and the bars are too small.** File: `evidence/N89/own-sweep-refit/summary.json`. Median 9.03, 6 of 11 fits more than 2 sigma below 9.81. The home page discloses this (confirmed live). The OWN07 card still says "Consistent with Earth g: 1.2 sigma away", true for that clip only. Calibration gap, not a code bug.

3. **P2, carried over: the judging URL uses a Clerk development instance.** Repro: fetch `/sign-in` and search for `pk_test_` and `accounts.dev`; 2 hits each. Confirmed live.

4. **P3, README claims a video that does not exist yet.** File: `README.md` line 10: "Demo video: linked on the submission page (recorded on this build)". REPORT.md says the video is not started. Fine if it is true by submission; misleading if a judge reads the repo first and no link is present. Source only.

5. **P3, the fit card contradicts the home page on the scale.** URL: `/lab?editor=1&sample=own07`, either width. The card under the timeline reads "MEASURED: hosted SAM 3.1 box centres in image pixels. scale assumed (user size)", while the home page and README say the book width was ruler-measured (20.3 cm +/- 0.2 cm). "Assumed" undersells the evidence and reads like a guess. Confirmed live.

6. **P3, carried over: "Guess the Gravity" card does not lead to a guessing game about a drop.** URL: `/`. Repro: click the "Guess the Gravity / Watch a drop. Guess g." card; it opens `/lab`, a template picker with a "Mystery-g mode" checkbox on a synthetic trial. Confirmed live.

7. **P3, carried over: home page length on phones.** `/` at 375 px is 13,240 px tall (round 7: 13,114). `/library` 8,242 px. Confirmed live.

8. **P3, carried over: the recorded Muse turn calls `fit` before tracking finishes.** File: `evidence/N89/muse-measures-book.json`. Evidence only.

9. **P3, carried over: README promises a seeded SAMPLE workspace project.** `README.md` step 4. Not verified, needs sign-in.

No horizontal overflow, no em dashes in visible text, no page errors and no console errors on the pages above at 1440 and 375 (confirmed live). The physics engine was ready in under 1 s in both fresh contexts this round, so I could not reproduce the round 7 slow-load report.

## 4. Top 5 fixes by expected score gain per hour

| Rank | Fix | Time | Expected gain (points /100) | Gain/hour |
|---|---|---:|---:|---:|
| 1 | Redeploy the API on the round 7 commit (or remove "The pipeline now drops that frame" from the home page) and confirm `/api/version` shows it. Cheap, and it keeps a stated claim true. | 15m | +0.3 | 1.2 |
| 2 | Record the demo video around the working replay: 9.81 at 0.25x with the zoomed gap, then 9.07 with 0.4 cm, then the 12-drop chart with the honest median, then the Muse book turn. The video is a primary artifact for a 25 percent criterion. | 2h | +1.5 | 0.75 |
| 3 | Fix the README video line so it is a real link (or says pending), and reword "scale assumed (user size)" to "scale from a ruler-measured book width" when the size was declared with an uncertainty. | 15m | +0.15 | 0.6 |
| 4 | Point the "Guess the Gravity" card at the OWN07 replay with gravity hidden (guess, then reveal the fitted g and the gap). That turns the best shot into a game and fixes a mismatched card. | 1h | +0.4 | 0.4 |
| 5 | Add a systematic term to the reported bars, estimated from the 11-drop spread (sd 0.56), and say so on the card. Then the stated uncertainty covers the observed scatter. | 1h | +0.3 | 0.3 |

Estimates overlap and are not additive. Moving Clerk to production is still only worth it if sign-up can be tested end to end before the deadline.

## 5. What I did not check

- Anything signed in: upload, live SAM 3.1 tracking, the Muse agent, room reconstruction, Make my copy, Save, quotas, the seeded SAMPLE project. Judged from source and repo evidence only, so unverified.
- Whether the deployed API code really is `6f6a5090`; I trusted the `/api/version` field.
- The 12 owner videos themselves (private). I did not rerun SAM or the refit; I compared the two summary files and read the `drop_contact` code and test.
- The Gravity y edit at 375 px (the input is in a hidden panel on phones; I tested 9.07 at 1440 only).
- Lessons, the guide in depth, accessibility beyond screenshots, other widths, other browsers, real phones.
- Test suites other than `tests/pipeline/test_live_experiment.py` and `tests/web-private`.
- The demo video, which I assumed to be average, as instructed.
