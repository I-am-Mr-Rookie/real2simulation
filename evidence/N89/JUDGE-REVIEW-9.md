# Real2Simulation: independent judge review, round 9

Reviewed 2026-11-04 against main `c9a2d787` and https://real2simulation.rookiecoders.tech. Live `/api/version`: web `0970c9a2` (round 8 home and README changes), api `ea258fba` (round 7). Rubric: "Event Rules and Participant Guide.md" lines 130 to 150. I assumed an average recorded demo video with voiceover. All browser testing was signed out, in fresh headed Playwright Chromium contexts at 1440x900 and 375x812. I did not sign in, upload, call paid APIs or change anything except this file. I read rounds 1 to 8 and REPORT.md first and kept the same strictness.

## 1. Scores

| Criterion | Weight | Round 8 | Round 9 | Weighted points |
|---|---:|---:|---:|---:|
| Impact | 30% | 6.5 | **6.5** | 19.5 |
| Use of Meta AI tooling | 25% | 8.0 | **8.0** | 20.0 |
| Technical depth and execution | 20% | 7.0 | **7.0** | 14.0 |
| Demo | 25% | 8.0 | **8.0** | 20.0 |
| **Total** | | **73.5** | | **73.5 / 100** |

## 2. Reasoning per criterion

**Impact (6.5).** Round 8 changed one sentence of framing, not the measurement. The home page now adds the clip-to-clip spread (0.56) in quadrature to the OWN07 fitter bar and reports "9.07 +/- 0.84 m/s², 0.9 sigma from 9.81" (confirmed live at both widths). That makes a single phone result honestly wider, which is good, but it does not touch the real problem: the 11 drops are biased low as a group. Their median is 9.03 with sd 0.56, so the mean of 11 sits roughly 4 to 5 standard errors below 9.81. A spread term describes scatter, not bias, and "0.9 sigma" for one clip reads more reassuring than the ensemble justifies. The evidence base is still one person, one book, one phone, one table, with no student or teacher using it. The classroom story is plausible and honestly labelled, unchanged from round 8. Same score.

**Use of Meta AI tooling (8.0).** The only Meta-related change is in the agent tool layer: `fit` in `Build/api/agent/handlers.py` now polls the experiment for up to 90 s instead of returning "not finished" to Muse Spark, with a test (`tests/agent/test_handlers.py`, 5 of 5 pass locally). That removes a wasted model step, which is sensible, but it is a small reliability fix, and `/api/version` still reports api `ea258fba`, which does not contain it (defect 1). Hosted SAM 3.1 tracking plus a tool-calling Muse agent remains solid, multi-step use of two Meta models; nothing here would surprise Meta. I could not trigger the agent signed out. Same score.

**Technical depth and execution (7.0).** The fit wait is small and tested both ways (finishes while waiting, and still says "not finished" when the wait is zero). It is a blocking `time.sleep` loop inside a sync handler, which ties up a threadpool worker for up to 90 s per call; fine at hackathon load, not something I would ship to many users. The systematic term is one line of code, but it double counts a little (the 0.56 spread already contains each fit's own scatter) and the replay card still shows the old "1.2 sigma away" alone, so the product now quotes two different sigma figures for the same clip. The round 8 P3 "scale assumed (user size)" was not fixed and now also appears on the home page in the contradictory form "measured with a ruler by the maker (scale assumed (user size))" (confirmed live). No page errors, no console errors, no horizontal overflow and no em dashes on `/`, `/library`, `/lab`, `/guide` and the OWN07 replay at either width. Clerk is still a development instance. No move.

**Demo (8.0).** Nothing in the demo path changed this round. The OWN07 replay loads cleanly at both widths with the dots, the SIMULATED ball, the Speed control and the MEASURED readout (confirmed live, screenshot at 375 px). I did not replay the auto-pause and gap this round because no replay code changed since round 8 confirmed it. The "Guess the Gravity: Watch a drop. Guess g. Then see the reveal." card still opens the generic `/lab` template picker at both widths (confirmed live), and the phone home page is now 13,334 px tall (round 8: 13,240). With an average video, 8.0 is still the honest ceiling.

## 3. Defects found

Severity: P0 security or data loss, P1 blocks or undermines a core claim, P2 significant usability or correctness, P3 polish.

No P0 or P1 found.

1. **P2, the headline measurement is still biased low as a group, and the new systematic term hides that for one clip.** File: `Build/web/src/app/(public)/home/FeaturedRun.jsx` line 24 (`sysU = Math.hypot(pq.uncertainty, sd)`); data in `evidence/N89/own-sweep-refit/summary.json`. Repro: open `/`, read "One of them in detail (OWN07)": "1.2 sigma away" then "9.07 +/- 0.84 m/s², 0.9 sigma from 9.81", while the sweep above shows median 9.03 and 6 of 11 more than 2 sigma low. Confirmed live and from source. Calibration and framing issue, not a crash.

2. **P2, carried over: the judging URL uses a Clerk development instance.** Repro: open `/sign-in`, search the page HTML for `pk_test_` and `accounts.dev`; 2 hits each. Confirmed live.

3. **P3, the round 8 agent fix is not shown as deployed.** URL: `https://real2simulation.rookiecoders.tech/api/version`. Repro: `curl -s .../api/version` returns `"api_revision":"ea258fba..."`; the fit wait is in `5edfba11`. REPORT.md says the third API upload "went through". Either the API was not redeployed or the revision field is not tied to the uploaded code; a judge cannot tell which. Confirmed live (version) and from source (diff). Signed-out visitors are not affected.

4. **P3, carried over and now on the home page too: "scale assumed (user size)" contradicts "measured with a ruler".** URLs: `/` (OWN07 card: "measured with a ruler by the maker (scale assumed (user size))") and `/lab?editor=1&sample=own07` (description and fit card). Confirmed live at 1440 and 375.

5. **P3, two different sigma figures for the same clip.** `/` shows 1.2 and 0.9 sigma side by side; the replay fit card shows only "1.2 sigma away" with +/- 0.62. Confirmed live.

6. **P3, carried over: "Guess the Gravity" card does not lead to a guessing game about a drop.** URL: `/`. Repro: click the card; it opens `/lab` (template picker). Confirmed live at both widths.

7. **P3, carried over: home page length on phones.** `/` at 375 px is 13,334 px tall; `/library` 8,337 px. Confirmed live.

8. **P3, two Play buttons on the phone replay.** URL: `/lab?editor=1&sample=own07` at 375 px: one in the top bar and one above the timeline. Confirmed live (screenshot); I did not test whether they behave differently.

9. **P3, blocking wait in the agent fit tool.** `Build/api/agent/handlers.py` `fit`: `time.sleep(2)` loop up to 90 s in a threadpool worker. Source only. Harmless at demo scale.

10. **P3, carried over: README promises a seeded SAMPLE workspace project** (`README.md` line 23). Not verified, needs sign-in. The README video line now says PENDING (fixed from round 8, source).

## 4. Top 5 fixes by expected score gain per hour

| Rank | Fix | Time | Expected gain (points /100) | Gain/hour |
|---|---|---:|---:|---:|
| 1 | Record the demo video around the working replay: 9.81 at 0.25x with the zoomed 5.4 cm gap, then 9.07 with 0.4 cm, then the 12-drop chart with the honest median, then the Muse book turn. It is a primary artifact for a 25 percent criterion. | 2h | +1.5 | 0.75 |
| 2 | Replace "(scale assumed (user size))" with "scale from a ruler-measured book width" whenever the size was declared with an uncertainty, and show one sigma figure per clip (pick the systematic one and use it on the replay card too). | 20m | +0.2 | 0.6 |
| 3 | Redeploy the API from current main and confirm `/api/version` shows it, or tie `api_revision` to the uploaded commit so it cannot lie. | 15m | +0.1 | 0.4 |
| 4 | Point the "Guess the Gravity" card at the OWN07 replay with gravity hidden (guess, then reveal the fitted g and the gap). Turns the best shot into a game and fixes a mismatched card. | 1h | +0.4 | 0.4 |
| 5 | Say plainly on the home page that the 11-drop mean is about 8 percent low and several standard errors below 9.81, and name the leading suspect (rolling-shutter, box-centre drift or perspective) with one cheap offline test on the stored tracks. Honesty about bias is worth more than a wider bar. | 1h | +0.3 | 0.3 |

Estimates overlap and are not additive.

## 5. What I did not check

- Anything signed in: upload, live SAM 3.1 tracking, the Muse agent (including the new 90 s fit wait), room reconstruction, Make my copy, Save, quotas, the seeded SAMPLE project. Judged from source and repo evidence only, so unverified.
- The replay auto-pause, zoom and gap numbers this round (no replay code changed since round 8, which confirmed them).
- Whether the deployed API code really is `ea258fba`; I trusted the `/api/version` field.
- The owner videos (private); I did not rerun SAM or the refit.
- Test suites other than `tests/agent/test_handlers.py`.
- Lessons, the guide in depth, accessibility, widths other than 1440 and 375, other browsers, real phones.
- The demo video, which I assumed to be average, as instructed.
