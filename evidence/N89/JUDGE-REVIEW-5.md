# Real2Simulation: independent judge review, round 5

Reviewed 2026-11-04 against main `7324493e` and https://real2simulation.rookiecoders.tech. Rubric: "Event Rules and Participant Guide.md" lines 130 to 150. I assumed an average recorded demo video with voiceover. All browser testing was signed out, in fresh headed Playwright Chromium contexts at 1440 px and 375 px. I did not sign in, upload, call paid APIs or change anything except this file. I read rounds 1 to 4 first and kept their strictness. I credit what the evidence shows, not the fact that a suggestion was followed.

## 1. Scores

| Criterion | Weight | Round 4 | Round 5 | Weighted points |
|---|---:|---:|---:|---:|
| Impact | 30% | 6.0 | **6.5** | 19.5 |
| Use of Meta AI tooling | 25% | 8.0 | **8.0** | 20.0 |
| Technical depth and execution | 20% | 7.0 | **7.0** | 14.0 |
| Demo | 25% | 7.0 | **7.5** | 18.75 |
| **Total** | | **69.5** | | **72.25 / 100** |

## 2. Reasoning per criterion

**Impact (6.5).** The main gap from round 4 was that no real clip measured g near 9.81. There is now one. `evidence/N89/live-own07-book-drop.json` is a real hosted SAM 3.1 run on the maker's own 30 fps phone clip of a falling book. It gives 9.07 +/- 0.62 m/s^2 from a ruler-measured book width, 1.2 sigma from Earth g. A 540p copy gives 9.11 +/- 0.46, and the ledger shows the runs. The team also kept the failed run from before the fix (6.73 +/- 0.86) in the repo, which is honest. This is the first proof that the core promise ("film it, get g with error bars") can work on real footage, so I add half a point. It is not more for four reasons. It is one clip, filmed by the maker, with 12 frames (0.37 s) of free fall. The landing-frame cut in `moving_segment` was written after seeing this same clip fail. The rule makes physical sense and has a unit test, but it has been checked on exactly one real clip. A 7 percent uncertainty is fine for a class demo, but the value sits 7.5 percent low, and that is not explained. And there is still no user, student or teacher evidence. The two lessons and the Crouch and Mazur citation are a credible teaching story, not demand.

**Use of Meta AI tooling (8.0).** No change in kind. Hosted SAM 3.1 on the Meta Model API does the tracking for both real runs (83 frames for the book, 543 for the apple). The recorded Muse Spark 1.3 turn drives list_files, start_experiment_track and fit. The proxy work around the regional model-list outage is real operational effort. The new OWN07 result raises the value of the SAM output, but it does not show a new Meta capability. The agent still cannot be triggered signed out. Its only real-clip run is the 2.33 m/s^2 slow-motion apple, not the book that comes out near g. Solid tool use beyond a wrapper, nothing that would surprise Meta. 8.0 stays.

**Technical depth and execution (7.0).** Confirmed live: the right-panel overflow at 1440 px is fixed. Lesson buttons stack inside the panel, and the gravity inputs are fully visible. Confirmed live: the height lesson runs end to end at 375 px (0.625 vs 0.883 s, ratio 1.413 +/- 0.023 vs sqrt 2), with zero page errors and no sideways scroll. Locally, 32 of 32 web-private tests and 13 of 13 `test_live_experiment.py` tests pass, including the new impact-cut test. The segment fix is small, readable and comes with a test. Unchanged problems keep this from rising: the judging URL still runs a Clerk development instance (`pk_test_`, `trusty-muskrat-5470.clerk.accounts.dev`). Every signed-out editor load still logs a 401. `/api/version` on the judging domain returns the HTML app shell instead of a version. The Library intro contradicts its own first card (details below). The round's work was mostly one heuristic and one CSS fix, so I see no reason to move the score.

**Demo (7.5).** The story a video can now tell is complete and true. A phone clip goes to hosted SAM 3.1, then the fitter returns 9.07 +/- 0.62 m/s^2, then a 3D replay where you change gravity. The home and library cards render cleanly with a fitted-curve chart. `/lab?editor=1&sample=own07` loads at both widths with no page errors. I set gravity y to -9.07 and played it, and the ball followed the dots. That is worth half a point over round 4. The replay itself is still weak to watch. The fall lasts 0.37 s in real time with no slow motion, so it is over in a blink. The default camera cuts the top of the track off under the toolbar. The 9.81 vs 9.07 difference is about 3 cm at landing and invisible at this zoom. After landing, the ball bounces and rolls off to the side for three more seconds. The real footage is private, so a judge on the site only sees dots. The maker can show the clip in their own video, which is fine. The ST03 replay is still a thin column of dots.

## 3. Defects found

Severity: P0 security or data loss, P1 blocks or undermines a core claim, P2 significant usability or correctness, P3 polish.

1. **P2, the phone-drop replay cannot show its own comparison.** URL: `/lab?editor=1&sample=own07` at 1440x900 and 375x812. Repro: open the page, press Play, watch. The fall takes 0.37 s in real time, the top dots and the ball's starting point sit under the floating toolbar, and the card says "runs slightly ahead of the dots", but no viewer can see a 3 cm lead at this zoom. Then set Gravity y to -9.07 (only possible while paused) and play again. It looks the same. After landing, the ball bounces off the track and rolls for about 3 s. There is no slow-motion control (no speed or playbackRate code in `Build/web/src/lab-editor/`). Confirmed live with screenshots.

2. **P2, only one real clip supports the headline claim, and the fix was tuned on it.** Files: `Build/pipeline/live_experiment.py` (`moving_segment`, the "up to 3 trailing steps" rule), `evidence/N89/live-own07-book-drop.json`, `evidence/N89/live-own07-fullres-before-impact-fix.json`. Repro: compare the two evidence files (6.73 +/- 0.86 before, 9.07 +/- 0.62 after, same clip). No second independent real clip has been run through the new rule. The ST03 apple is said to be unchanged, but it is slow motion, so it cannot validate the result. Confirmed from evidence and source. I did not rerun SAM.

3. **P2, the judging URL still uses a Clerk development instance.** URL: `/sign-in`. Repro: `curl -s https://real2simulation.rookiecoders.tech/sign-in` and search for `pk_test_` and `clerk.accounts.dev`. Both are present. A judge who signs up goes through a dev-instance flow with a dev banner and user limits. Confirmed live.

4. **P3, Library intro contradicts its first card.** URL: `/library` at 1440. The intro says "One real tracked run, then simulated trajectories ... Nothing here is a calibrated measurement." The next heading says "Two clips went through the live pipeline", and the first card is a MEASURED result with a ruler-measured scale. Confirmed live.

5. **P3, signed-out editor logs a 401 on every load.** URLs: `/lab?editor=1&sample=own07`, `&sample=st03`, `&template=physics-lab`. Repro: open any of them signed out with devtools open. The console shows "Failed to load resource: 401". It still happens on this commit. Confirmed live.

6. **P3, `/api/version` on the judging domain returns HTML.** Repro: `curl https://real2simulation.rookiecoders.tech/api/version`. It returns the Next.js page shell, not a version string. REPORT.md says `/api/version` serves the commit, which may be true only on the API host. Harmless to users, but the team's own deploy check does not work on the domain judges see. Confirmed live.

7. **P3, the phone toolbar shows two identical down-arrow icons.** URL: `/lab?editor=1&sample=own07` at 375 px. Repro: look at the second toolbar row. Export and the "Scene and gravity" button both use a down-arrow glyph, so the gravity control is hard to find. Confirmed live (screenshot). I did not check the aria labels.

8. **P3, the chart legend promises a 1 sigma band that is not visible.** URL: `/` and `/library`, OWN07 card. The legend reads "BAND: 1 SIGMA", but no band is visible at either width, probably because it is thinner than the line. Confirmed live (screenshot). Cause not traced.

9. **P3, carried over: README says the demo video is PENDING and promises a seeded SAMPLE workspace project.** File: `README.md` lines 10 and 22 to 23. Neither can be checked signed out. Source only.

10. **P3, carried over: home page length on phones.** URL: `/` at 375 px. The page is now about 12,000 px tall (round 4: about 10,900). The class-use section is even further below the fold. Confirmed live.

No P0 was found. `/workspace` redirects to sign-in when signed out, and `/about` returns 404, which matches the README fix.

## 4. Top 5 fixes by expected score gain per hour

| Rank | Fix | Time | Expected gain (points /100) | Gain/hour |
|---|---|---:|---:|---:|
| 1 | In the OWN07 replay, frame the camera on the whole track, add a 0.25x speed toggle, show a second ghost ball at the fitted g next to the 9.81 ball, and stop the run at first contact so the ball does not roll away. Print both landing times. This is the single shot the demo video needs. | 60m | +1.25 | 1.25 |
| 2 | Run a second independent real drop (a ball this time, a different height) through the same live path. Add it as a second MEASURED row under the book result. Two clips near g, not tuned on, is much stronger than one. About $0.02 of SAM. | 45m | +0.75 | 1.0 |
| 3 | Fix the Library intro text so it matches the MEASURED card, and replace the duplicate down-arrow icon on phones with a gravity or sliders icon. | 10m | +0.15 | 0.9 |
| 4 | Record a Muse turn on the book clip (or the second drop), so the agent's real-clip example lands near g instead of at 2.33. Show it as the Muse card. | 30m | +0.4 | 0.8 |
| 5 | Move the judging domain to a Clerk production instance, or at least test sign-up once on the judging URL and say in the README that it uses a development instance. | 45m | +0.4 | 0.5 |

Estimates overlap and are not additive. The deadline is tonight, so fixes 1 and 3 are the safe ones. Fix 5 risks breaking sign-in, so only do it if it can be tested end to end before submission.

## 5. What I did not check

- Anything signed in: upload, live SAM 3.1 tracking, the Muse agent, room reconstruction, Make my copy, Save, quotas, the GPU status dot. I judged these from source and repo evidence only, so they are unverified.
- The OWN07 video itself (private) and whether its 30 fps capture clock is real. I trusted the evidence file and the 540p rerun.
- The mass lesson this round (round 4 ran it). I ran the height lesson only, at 375 px.
- The ST03 replay interactions, the Guess the Gravity game beyond loading `/lab`, the guide content, 768 px, other browsers and real phones.
- Accessibility beyond what screenshots show, and performance on low-end devices.
- Backend test suites other than `tests/web-private` and `tests/pipeline/test_live_experiment.py`.
- The demo video, which I assumed to be average, as instructed.
