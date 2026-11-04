# Real2Simulation: independent judge review, round 7

Reviewed 2026-11-04 against main `0e4af2b7` and https://real2simulation.rookiecoders.tech (live `/api/version`: web `227ee876`, api `6f6a5090`). Rubric: "Event Rules and Participant Guide.md" lines 130 to 150. I assumed an average recorded demo video with voiceover. All browser testing was signed out, in fresh headed Playwright Chromium contexts at 1440x900 and 375x812. I did not sign in, upload, call paid APIs or change anything except this file. I read rounds 1 to 6 and REPORT.md first and kept the same strictness. I credit what the evidence shows, not the fact that a suggestion was followed.

## 1. Scores

| Criterion | Weight | Round 6 | Round 7 | Weighted points |
|---|---:|---:|---:|---:|
| Impact | 30% | 6.5 | **6.5** | 19.5 |
| Use of Meta AI tooling | 25% | 8.0 | **8.0** | 20.0 |
| Technical depth and execution | 20% | 7.0 | **7.0** | 14.0 |
| Demo | 25% | 7.5 | **8.0** | 20.0 |
| **Total** | | **72.25** | | **73.5 / 100** |

## 2. Reasoning per criterion

**Impact (6.5).** Nothing changed in the evidence that decides impact. The 12-drop sweep still says the method reads about 12 percent low (median 8.62 m/s^2) with error bars that miss the bias on 9 of 11 clips, cause unknown. The home page now says OWN07 "reads higher than their median (8.62), so it is a worked example, not the typical result", which I confirmed live. That is honest and fixes the round 6 framing complaint, but honesty about a calibration gap does not close it. It is still one person, one book, one phone, one table, and there is still no student or teacher evidence. The classroom story (predict first, film, measure, compare) remains credible for a 10 percent level lesson. Same score.

**Use of Meta AI tooling (8.0).** The new recorded Muse Spark 1.3 turn (`evidence/N89/muse-measures-book.json`, status 200, DEV, fixture account) is a real improvement in the story: from one sentence the agent called `list_files`, `start_experiment_track` (hosted SAM 3.1 on the 1080p OWN07 file), then `fit` three times and replied 9.06 +/- 0.63 m/s^2 with the right labels. The ledger row is there. So the agent's real-clip example is now a ruler-scaled drop near g, not only the slow-motion apple. But it is the same two models doing the same kind of work as before, the turn called `fit` once before tracking had finished (wasted step, about 32k input tokens for the whole turn), and I could not trigger the agent signed out. Solid multi-step use of two Meta models with real ops work behind it (proxy region moves with probes), nothing that would surprise Meta. 8.0 stays.

**Technical depth and execution (7.0).** Good: the round 6 P1 is fixed at the root. `trajectoryScene` in `Build/web/src/workspace/measure.mjs` now lifts the track so the lowest dot is 0.5 m above the floor, and the guard test in `tests/web-private/featured-run.test.mjs` is now meaningful: the fitted g must land within 1 cm of the last dot and 9.81 must miss by more than 3 times that and over 3 cm. I ran `tests/web-private` (32 of 32) and `tests/web-workspace-api` (8 of 8): all pass. `/api/version` now returns JSON on the product domain and the signed-out session lookup is 200 with `userKey: null`; I checked both callers in `AgentPanel.jsx` still treat that as a guest. No page errors and no console errors on `/`, `/library`, `/lab`, `/guide` and the OWN07 replay at either width (confirmed). Against that: the judging URL still runs a Clerk development instance (confirmed), the error bars are still too small for the observed bias, which is a technical calibration flaw, not just an impact one, and the replay readout mixes two coordinate frames (defect 4). Fixing a broken feature and two P3s restores the score the work deserved; it does not add depth. No move.

**Demo (8.0).** The shot the whole product is built around now works live and tells the true story. At 1440 px: Speed 0.25x, Play, it auto-pauses at t = 0.37 s and reads "The SIMULATED ball is 5.4 cm below the last dot at gravity 9.81", and the ball is visibly below the last dot. Set Gravity y to -9.07, Reset, Play: "0.4 cm below the last dot at gravity 9.07". Same numbers at 375 px. On phones the status box no longer covers the ball, and the 12-drop chart is readable at 375 px (both confirmed with screenshots). That moves the demo from "avoid this in the video" to "film this". It is not higher because on phones the comparison is text only (the track is a thin line about 100 px tall and the 5.4 cm gap cannot be seen), there is no side-by-side ghost ball, and the home page is still about 13,100 px tall on a phone.

## 3. Defects found

Severity: P0 security or data loss, P1 blocks or undermines a core claim, P2 significant usability or correctness, P3 polish.

No P0 or P1 found. The round 6 P1 (fitted g looked worse than 9.81) is fixed, confirmed live at both widths.

1. **P2, the headline measurement is biased low and the bars are too small.** File: `evidence/N89/own-sweep/summary.json`. 9 of 11 fits more than 2 sigma below 9.81, median 8.62. The home page discloses this and now calls OWN07 a worked example above the median, which is right. The pipeline still prints "Consistent with Earth g: 1.2 sigma away" for OWN07 because that one clip happens to agree. Confirmed from evidence and live text. A calibration gap, not a code bug.

2. **P2, the judging URL still uses a Clerk development instance.** Repro: `curl -s https://real2simulation.rookiecoders.tech/sign-in | grep -o "pk_test_\|clerk.accounts.dev"`. Both present (2 hits each). Confirmed live. A judge who signs up sees a development banner and dev-instance limits.

3. **P3, on phones the replay comparison cannot be seen, only read.** URL: `/lab?editor=1&sample=own07` at 375x812. Repro: Speed 0.25x, Play, wait for the auto-pause. The track is a thin vertical line about 100 px tall above a lot of empty floor; the ball and the last dot overlap, so 5.4 cm vs 0.4 cm is only in the status text. Confirmed live (screenshot).

4. **P3, the replay readout mixes two coordinate frames.** URL: `/lab?editor=1&sample=own07` at 375x812. Repro: load the page and read the strip under the timeline before pressing Play: "Tracked object reading (m): -0.760 at t = 0.37 s. MEASURED". After Play the same strip reads "ball-1 y position (m): 0.446 at t = 0.37 s. SIMULATED". The dots on screen are lifted by `lift` in `trajectoryScene` but the MEASURED readout shows raw tracked metres, so a viewer comparing the two numbers sees a 1.2 m mismatch that does not exist. Confirmed live (screenshots); cause from source.

5. **P3, on a cold first visit the physics engine can stay "Loading" for more than 10 s and a Play press is silently ignored.** URL: `/lab?editor=1&sample=own07` at 375x812, fresh browser. In my first run, 6 s after load plus a Play click plus 4 s, the status still read "Loading the physics engine..." and Play looked disabled. A second fresh context was ready in 3.5 s (1440 px: 2.1 s). Seen once live, not reproduced; could be a cold CDN. Worth a visible spinner on the Play button.

6. **P3, the recorded Muse turn calls `fit` before tracking finishes.** File: `evidence/N89/muse-measures-book.json`, `tool_calls`. The first `fit` returns "tracking has not finished, so there is nothing to fit yet"; the agent then fits twice more. Harmless here but costs tokens and looks clumsy if shown in the video. Source and evidence only.

7. **P3, carried over: README says the demo video is PENDING and promises a seeded SAMPLE workspace project.** File: `README.md` lines 10 and 22. Source only; I did not verify the SAMPLE project because it needs sign-in.

8. **P3, carried over: home page length on phones.** `/` at 375 px is 13,114 px tall (round 6: about 12,900). `/library` is 8,117 px. Confirmed live.

9. **P3, carried over and not rechecked: "Guess the Gravity" on the home page.** Round 6 found it opens `/lab` with a template picker rather than an obvious guessing game. I confirmed the card text is still on `/` but did not follow it this round.

No horizontal overflow, no em dashes in visible text, no page errors and no console errors on `/`, `/library`, `/lab`, `/guide` and the OWN07 replay at 1440 and 375 (confirmed live).

## 4. Top 5 fixes by expected score gain per hour

| Rank | Fix | Time | Expected gain (points /100) | Gain/hour |
|---|---|---:|---:|---:|
| 1 | Record the demo video around the working replay: 9.81 vs fitted g at 0.25x on desktop, then the 12-drop chart with the honest median, then the Muse book turn. The live product now supports this; the video is a 25 percent criterion and the primary artifact. | 2h | +1.5 | 0.75 |
| 2 | Show the MEASURED readout in the same lifted frame as the dots (or show both as "height above the last dot"), so the two numbers under the timeline agree. | 15m | +0.15 | 0.6 |
| 3 | On phones, zoom the camera to the last 10 cm at the auto-pause (or add a ghost ball at the fitted g next to the 9.81 ball), so the gap is visible without reading. | 45m | +0.4 | 0.55 |
| 4 | Fix the README: link the video once it exists, remove or correct the seeded SAMPLE promise. Judges read the README first. | 10m | +0.1 | 0.6 |
| 5 | Add one paragraph and one test on where the low bias could come from (rolling shutter, frame timestamps vs 30 fps nominal, book tilt changing box width) and widen the reported bars with a systematic term estimated from the 12-clip spread. Turns a weakness into visible rigour. | 1h | +0.4 | 0.4 |

Estimates overlap and are not additive. Moving Clerk to production is still only worth it if sign-up can be tested end to end before the deadline; a broken sign-in on the judging URL would cost far more than the dev banner.

## 5. What I did not check

- Anything signed in: upload, live SAM 3.1 tracking, the Muse agent, room reconstruction, Make my copy, Save, quotas, the GPU status dot, the seeded SAMPLE project. Judged from source and repo evidence only, so unverified.
- The Meta proxy move to us-west (`Build/gpu/meta_proxy.py`) and the claimed 385 KB and 6.4 MB uploads returning 200; these are DEV and Modal side and need sign-in or paid calls.
- The 12 owner videos themselves (private) and the cause of the low bias. I trusted the evidence files and did not rerun SAM.
- Both lessons, the guide content in depth, and the Guess the Gravity flow.
- The signed-out Agent panel guest message after the 401 to 200 change (checked from source only).
- Widths other than 1440 and 375, other browsers, real phones, accessibility beyond screenshots, performance on low-end devices.
- Test suites other than `tests/web-private` and `tests/web-workspace-api`.
- The demo video, which I assumed to be average, as instructed.
