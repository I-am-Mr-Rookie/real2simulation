# Real2Simulation: independent judge review, round 4

Reviewed 2026-11-04 against main `20ce186c` and https://real2simulation.rookiecoders.tech. Rubric: "Event Rules and Participant Guide.md" lines 130 to 150. I assumed an average recorded demo video with voiceover. All browser testing was signed out, in fresh headed Playwright Chromium contexts at 1440 px and 375 px. I did not sign in, upload, call paid APIs or change anything except this file.

## 1. Scores

| Criterion | Weight | Round 3 | Round 4 | Weighted points |
|---|---:|---:|---:|---:|
| Impact | 30% | 5.5 | **6.0** | 18.0 |
| Use of Meta AI tooling | 25% | 8.0 | **8.0** | 20.0 |
| Technical depth and execution | 20% | 6.5 | **7.0** | 14.0 |
| Demo | 25% | 6.5 | **7.0** | 17.5 |
| **Total** | | **65.75** | | **69.5 / 100** |

## 2. Reasoning per criterion

**Impact (6.0).** A student or teacher can now finish a real task without an account. In the physics lab I picked a prediction, ran two drops, recorded both, and got a verdict with a drag caveat. The home page cites one real study for predict-first teaching and has a short "Use it in a class" section. That answers the earlier complaint that no student task could be completed, so I add half a point. It stops there for three reasons. First, the product promises "film it with your phone and get g with error bars", but no real clip in the repo or on the site comes back close to 9.81 m/s^2. Both public real results (ST03 and the cropped sample) give about 2.33 m/s^2. The site blames probable slow motion or a wrong apple size. That is honest, but it means the core claim has never been shown working on real footage. Second, the mass lesson cannot fail. The engine has no drag, so run A and run B agree to seven digits. That checks the engine, not an idea a student might hold. The height lesson (sqrt 2) is better, but it is still simulation only. Third, there is no user, teacher or classroom evidence. An honest, useful prototype, but the main value claim is still unproven.

**Use of Meta AI tooling (8.0).** This round adds a recorded Muse Spark 1.3 turn that drives the real pipeline from one sentence: list_files, then start_experiment_track (hosted SAM 3.1 on a real clip with the user's 7 cm), then fit twice. It returns 2.33 +/- 0.36 m/s^2 with the right labels (`evidence/N89/muse-measures-sample.json`, home page card). This fixes round 3's main complaint that the agent example was a separate synthetic drop. The team also diagnosed and worked around a regional Meta model-list outage in the proxy (`Build/gpu/meta_proxy.py`), which shows real operational work with the API. I did not raise the score. The agent run is one recorded DEV turn in a fixture account, so a judge cannot reproduce it signed out. The agent called fit too early and had to retry. The measured number itself is wrong by a factor of about 4 from known g. Real judges will see solid tool-calling over SAM, but nothing that would surprise Meta. 8.0 already credited this level of integration.

**Technical depth and execution (7.0).** I confirmed live that the round 3 P1 and P2 defects are fixed. The "Scene and gravity" button works at 375 px, and I changed ST03 gravity to -9.81 and ran it there. Bad `sample`, `template` and `project` links now explain the problem and point to recovery options. Reset now keeps the RECORDED/MEASURED provenance. The guide's calibration copy now says to measure the tracked object's own size, which matches `live_experiment.py`. The guest fit is real browser least squares, cut at the first impact (76 of N samples). The server fixes are credible in source: one sqlite connection per thread, and SAM-omitted frames kept aligned. 93 of 93 lab-editor and web-private tests pass locally. I saw no page errors on 28 page loads. New problems lower confidence a little: the right panel overflows at 1440 px, the judging URL runs a Clerk development instance, and the editor never reaches network idle. A crash shipped to DEV for 8 minutes this afternoon (fixed, with a guard test).

**Demo (7.0).** The signed-out path now holds up. I ran Home, then the physics lab: Play, Pause, Fit trace (-9.8100163 +/- 0.0000022 m/s^2), then the full lesson. Next the ST03 replay with changed gravity. Everything worked at both widths with zero page errors. That is a working demo, worth half a point more. It is not yet an impressive one. The ST03 replay is a thin column of blue dots on an empty grid. When gravity changes, the ball simply runs out of the dots. You cannot see measured and simulated side by side in time. The strongest Meta moment (Muse measuring a clip) is a static card, not something a visitor can trigger. An average video of this path is clear but not exciting.

## 3. Defects found

Severity: P0 security or data loss, P1 blocks or undermines a core claim, P2 significant usability or correctness, P3 polish.

1. **P1, product proof: no real clip measures g near 9.81.** URL: `/` (cards "One real run" and "Muse measures"), `evidence/N89/live-apple-drop-sample.json`, `clips.csv` row ST03 ("probable slow motion"). Repro: open the home page and read the MEASURED card. It shows 2.33 +/- 0.36 m/s^2, and the copy says "Far below 9.81 m/s^2". No other real-footage result is public. Confirmed live and in evidence.

2. **P2, right panel overflows at desktop width.** URL: `/lab?editor=1&template=physics-lab` at 1440x900. Repro: load the page with nothing selected. In the right column, "Both fall the same" is clipped and step 2's text is cut at "then I". The Gravity z input is cut off and a horizontal scrollbar appears under the panel. At 375 px the lesson sheet also scrolls sideways, and the first row of choices is cut at the top. Confirmed live (screenshots), cause not traced in CSS.

3. **P2, the judging URL uses a Clerk development instance.** URL: `/sign-in` (also `/workspace`, which redirects there). Repro: open the page signed out. The widget reads "Secured by Development mode", and the page source loads `trusty-muskrat-5470.clerk.accounts.dev` with a `pk_test_` key. Judges who sign up see a dev-instance auth flow, which also has user limits. Confirmed live.

4. **P2, the ST03 replay is hard to read as a comparison.** URL: `/lab?editor=1&sample=st03`. Repro: open Scene, set gravity to 0, -9.81, 0, press Play. The default camera shows a vertical line of dots on an empty grid. The simulated ball drops past the dots with no timing overlay and no ghost at the fitted g, so the gap between the "what-if" and the measurement is not visible as a number or picture. Confirmed live at 1440 and 375.

5. **P3, the mass lesson can only confirm the engine.** File: `Build/web/src/lab-editor/lesson.mjs` (mass lesson). Repro: run the lesson. Both runs show -9.8100163 +/- 0.0000022 m/s^2. The caveat admits the engine has no drag. Showing 7-digit precision on a simulated value also makes the outcome look like a measurement. Confirmed live.

6. **P3, signed-out editor makes a failing session call and keeps polling.** File: `Build/web/src/lab-editor/AgentPanel.jsx:79`. Repro: open any `/lab?editor=1...` URL signed out. The console logs "401" on load, and the page never reached network idle within 45 s in my runs. Functionally harmless, but noisy for anyone who opens dev tools. Confirmed live; I did not identify the polling source.

7. **P3, README entry problems.** File: `README.md`. Line 10 says the demo video is PENDING. Lines 19 to 20 promise a seeded SAMPLE workspace project, which I could not verify signed out. Line 57 mentions an About page, but `/about` returns 404 live. Confirmed live (404) and in source.

8. **P3, guest edit carry-over covers only templates and ST03.** File: `Build/web/src/lab-editor/LabEditor.jsx:602` and `:623`. Repro path: import a scene JSON signed out, edit it, press Make a copy, then go through sign-in. Only `template` and `sample:st03` edits are restored, so imported scenes are lost. Source only, not executed.

9. **P3, home page length on phones.** URL: `/` at 375 px. The full page is about 10,900 px tall, so the class-use section sits far below the fold behind two long run cards. Confirmed live (full-page screenshot).

No P0 was found. Anonymous `/workspace` redirects to sign-in, and `?project=garbage` says "Sign in to open your saved lab" without leaking anything.

## 4. Top 5 fixes by expected score gain per hour

| Rank | Fix | Time | Expected gain (points /100) | Gain/hour |
|---|---|---:|---:|---:|
| 1 | Film one new drop with a ruler-measured ball at normal speed (60 fps if possible). Run it through the existing pipeline. Publish the frames and result (for example 9.6 +/- 0.4 m/s^2) as the featured MEASURED card next to 9.81. This proves the core claim on real footage. Cost is about $0.02 of SAM. | 75m | +3.0 | 2.4 |
| 2 | Fix the right-panel overflow (let the lesson buttons wrap, add min-width 0 on the panel and inputs), and check 1440, 768 and 375 px. | 20m | +0.75 | 2.2 |
| 3 | Make the ST03 replay show the comparison: frame the camera on the dots, add a ghost ball at the fitted g next to the user's g, and show both landing times. | 45m | +1.0 | 1.3 |
| 4 | Link the Muse MEASURED card to a public replay of that same run in metres (7 cm scale), so a signed-out judge can open the agent's result in 3D. | 30m | +0.5 | 1.0 |
| 5 | Move the judging domain to a Clerk production instance, or at least confirm sign-up works there without a dev banner. | 45m | +0.5 | 0.7 |

Estimates overlap and are not additive. Fix 1 matters most. Without it, Impact and Demo stay capped, however polished everything else gets.

## 5. What I did not check

- Anything signed in: upload, live SAM 3.1 tracking, the Muse agent, room reconstruction, Make my copy, Save, quotas, GPU status. I judged these from source and repo evidence only, so they are unverified.
- The height lesson live. I ran only the mass lesson end to end, at both widths.
- The Guess the Gravity game, library card interactions, the guide's screenshots, and 768 px or other browsers and devices.
- Performance on low-end phones, and accessibility beyond what the screenshots show.
- The demo video (assumed average, per instructions), and the backend test suites other than lab-editor and web-private.
