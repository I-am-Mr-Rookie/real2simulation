# Real2Simulation: independent judge review, round 6

Reviewed 2026-11-04 against main `b60fdc6e` (code from `6f6a5090`) and https://real2simulation.rookiecoders.tech. Rubric: "Event Rules and Participant Guide.md" lines 130 to 150. I assumed an average recorded demo video with voiceover. All browser testing was signed out, in fresh headed Playwright Chromium contexts at 1440 px and 375 px. I did not sign in, upload, call paid APIs or change anything except this file. I read rounds 1 to 5 and REPORT.md first and kept the same strictness. I credit what the evidence shows, not the fact that a suggestion was followed.

## 1. Scores

| Criterion | Weight | Round 5 | Round 6 | Weighted points |
|---|---:|---:|---:|---:|
| Impact | 30% | 6.5 | **6.5** | 19.5 |
| Use of Meta AI tooling | 25% | 8.0 | **8.0** | 20.0 |
| Technical depth and execution | 20% | 7.0 | **7.0** | 14.0 |
| Demo | 25% | 7.5 | **7.5** | 18.75 |
| **Total** | | **72.25** | | **72.25 / 100** |

## 2. Reasoning per criterion

**Impact (6.5).** Round 5 said one clip was too little and the fix was tuned on it. The team answered by running all 12 owner phone drops through the live path, one run each, none dropped (`evidence/N89/own-sweep/summary.json`, 24 ledger rows). I checked the rows: 11 free-fall fits, median 8.62 m/s^2, sd 0.72, range 7.24 to 9.82, and OWN12 failed because SAM 3.1 returned no objects. The home page shows every row on a chart with the 9.81 line, and the text says plainly that 9 of 11 sit more than 2 sigma low, so the error bars miss a systematic error. That honesty is good and I respect it. But it cuts both ways for impact. The product promise is "film it, get g with error bars", and the team's own 12-clip data now shows the result reads about 12 percent low with bars that are too small, cause unknown. A teacher can still use a 10 percent estimate for a lesson, and the lessons and the predict-first framing remain a credible classroom story. Still, it is the same person, the same book, the same phone and the same table 12 times, so it shows repeatability, not robustness across users or setups. There is still no user, student or teacher evidence. More data, a less flattering picture, the same score.

**Use of Meta AI tooling (8.0).** No change in kind. Hosted SAM 3.1 on the Meta Model API did 24 more tracking runs this round, with one clean failure that the pipeline reports instead of hiding. The recorded Muse Spark 1.3 turn still drives list_files, start_experiment_track and fit, but its only real-clip example is still the slow-motion apple at 2.33 m/s^2, not a book drop near g. The agent cannot be triggered signed out. Solid, multi-step use of two Meta models with real operational work behind it, nothing that would surprise Meta. 8.0 stays.

**Technical depth and execution (7.0).** Good: the sweep was run before and after the rule change and both sets are in the repo, failures included. The new segment rule is short and readable. The speed control and the auto-pause at the last tracked frame work live at both widths (confirmed). Local checks: `tests/pipeline/test_live_experiment.py` 13 of 13 and `tests/web-private` 32 of 32 pass. Against that: the new "gap" readout is wrong in a way that matters (defect 1). The ball is placed so the last dot sits 5 cm above the floor, so by t = 0.37 s the ball is already hitting or bouncing off the floor, and the printed gap measures the floor contact, not gravity. The test that guards this (`featured-run.test.mjs` line 43) allows 3 cm at the fitted g and only asks for more than 1.5 cm at 9.81, so it passes while the fitted g is the worse match. The cutoff 0.85 was chosen by lowest summed fit residuals over only three tried values (0.7, 0.8, 0.85). That criterion tends to favour cutting more frames, and the round 4 value 0.9 is not reported. Carried-over issues remain: Clerk development instance on the judging URL, a 401 on every signed-out editor load, `/api/version` returning HTML on the judging domain. Net, no move.

**Demo (7.5).** Round 5's main demo complaints are fixed in part. The camera now frames every dot and the ball start, clear of the toolbar, and a 0.25x speed makes the 0.37 s fall watchable (confirmed live at both widths). The 12-drop chart is clear and honest at 1440 px. But the comparison shot itself still fails, and now it fails in words: follow the on-screen instructions, press Play at 9.81 and it says the ball is 1.6 cm below the last dot. Set gravity to the fitted -9.07, press Reset and Play, and it says 3.0 cm below. A judge reads that as "the measured value fits worse than the textbook value", the opposite of the story. On a phone the status box sits on top of the ball and the last dots at the moment of the pause. The 1.4 cm difference between the two runs is also invisible at this zoom. The maker can avoid this in the video, so I do not drop the score, but it is not a gain either.

## 3. Defects found

Severity: P0 security or data loss, P1 blocks or undermines a core claim, P2 significant usability or correctness, P3 polish.

1. **P1, the OWN07 replay says the fitted g matches worse than Earth g.** URL: `/lab?editor=1&sample=own07`. Repro (1440x900 or 375x812): set Speed to 0.25x, press Play in the timeline. It auto-pauses and reads "The SIMULATED ball is 1.6 cm below the last dot at gravity 9.81" (ball y 0.034 m). Press Reset, set Gravity y to -9.07 (on phones open "Scene and gravity" first), press Play. It reads "3.0 cm below the last dot at gravity 9.07" (ball y 0.020 m). Lower gravity cannot put a free ball lower; the cause is in `Build/web/src/workspace/measure.mjs` `trajectoryScene`: the track is lifted so its lowest dot is at y = 0.05 m while the floor is at 0 and the ball is 0.05 m in size, so the ball meets the floor right at the last dot and the 9.81 ball has already bounced. The guard test in `tests/web-private/featured-run.test.mjs` line 43 has tolerances loose enough to pass this. Confirmed live with screenshots at both widths.

2. **P2, on phones the status message covers the ball and the landing at the comparison moment.** URL: `/lab?editor=1&sample=own07` at 375x812. Repro: press Play; the status box (about y 300 to 380 px) sits over the lower track; at the auto-pause the ball is hidden behind the "Paused at t = 0.37 s" text. Confirmed live (screenshot).

3. **P2, the headline measurement is biased low and the bars are too small, shown by the team's own data.** File: `evidence/N89/own-sweep/summary.json`. 9 of 11 fits are more than 2 sigma below 9.81, median 8.62. The site says so, which is right, but the pipeline still prints "Consistent with Earth g: 1.2 sigma away" for OWN07 as the worked example, the best-looking clip of the set. Confirmed from evidence and live text. Not a code bug, a calibration gap.

4. **P2, the judging URL still uses a Clerk development instance.** Repro: `curl -s https://real2simulation.rookiecoders.tech/sign-in` and search for `pk_test_` and `clerk.accounts.dev`. Both present. Confirmed live.

5. **P3, segment cutoff chosen on a narrow, biased criterion.** File: `Build/pipeline/live_experiment.py` `moving_segment` docstring and REPORT.md round 5. Only 0.7, 0.8 and 0.85 are reported, scored by summed residuals, which rewards shorter segments. Source and report only.

6. **P3, the signed-out editor logs a 401 on every load.** URLs: `/lab?editor=1&sample=own07` and `&sample=st03`. Repro: open signed out; `GET /api/workspace/session` returns 401 and the console shows "Failed to load resource: 401". Confirmed live.

7. **P3, `/api/version` on the judging domain returns the HTML app shell.** Repro: `curl https://real2simulation.rookiecoders.tech/api/version`. Confirmed live.

8. **P3, the 12-drop chart is unreadable on phones.** URL: `/` at 375 px, "Twelve phone drops" card. The clip labels and axis numbers render at roughly 5 px. Confirmed live (screenshot).

9. **P3, "Guess the Gravity" does not lead to a guessing game.** URL: `/` at 375 px. Repro: tap "Guess the Gravity Watch a drop. Guess g." It opens `/lab`, headed "Test a motion model" with a template picker; the guess flow is not obvious. `/guess` returns 404. Confirmed live; I did not play the flow through.

10. **P3, carried over: README says the demo video is PENDING and promises a seeded SAMPLE workspace project.** File: `README.md` lines 10 and 22. Source only.

11. **P3, carried over: home page length on phones.** `/` at 375 px is about 12,900 px tall (round 5: about 12,000). Confirmed live.

No P0 found. `/workspace` redirects to sign-in signed out. No page errors, no sideways scroll and no em dashes on `/`, `/library`, `/lab`, `/guide` at either width.

## 4. Top 5 fixes by expected score gain per hour

| Rank | Fix | Time | Expected gain (points /100) | Gain/hour |
|---|---|---:|---:|---:|
| 1 | Fix the replay comparison: put the floor below the landing (or disable floor contact for track replays), report the gap at the last tracked time before any contact, and tighten the test so the fitted g must beat 9.81. Then the on-screen numbers tell the true story. | 30m | +0.75 | 1.5 |
| 2 | On phones, move the status box below the canvas or shrink it during playback so the ball and last dots stay visible at the pause. | 15m | +0.25 | 1.0 |
| 3 | Show a ghost ball at the fitted g next to the 9.81 ball in one run, and zoom the camera to the last 10 cm at the pause, so the difference is visible without reading text. This is the shot the video needs. | 45m | +0.6 | 0.8 |
| 4 | Make OWN07 the honest example, not the best one: show the median clip, or print the sweep median next to OWN07, and drop "Consistent with Earth g" from the worked example while the bias is unexplained. Bump chart text size on phones. | 20m | +0.2 | 0.6 |
| 5 | Record one Muse turn on a book clip so the agent's real-clip example is a ruler-scaled drop, not the slow-motion apple. | 30m | +0.3 | 0.6 |

Estimates overlap and are not additive. The deadline is close, so fixes 1 and 2 are the safe ones. Moving Clerk to production is still worth it only if sign-up can be tested end to end before submission.

## 5. What I did not check

- Anything signed in: upload, live SAM 3.1 tracking, the Muse agent, room reconstruction, Make my copy, Save, quotas, the GPU status dot. Judged from source and repo evidence only, so unverified.
- The 12 owner videos themselves (private), their frame timing, and whether the low bias comes from scale, blur, perspective or the phone clock. I trusted the evidence files and did not rerun SAM.
- Both lessons this round (rounds 4 and 5 ran them), the Guess the Gravity flow past its first screen, the guide content.
- Widths other than 1440 and 375, other browsers, real phones, accessibility beyond screenshots, performance on low-end devices.
- Test suites other than `tests/pipeline/test_live_experiment.py` and `tests/web-private`.
- The demo video, which I assumed to be average, as instructed.
