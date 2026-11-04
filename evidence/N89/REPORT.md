# N89: template labs, copy-a-lab, no-video judge path, judge-driven fixes (Nov 4)

Main a1258972 (pushed). Live: https://real2simulation.rookiecoders.tech (web 83de884a, api a419a664 at 5411b730, both SUCCESS).

## Shipped
- Two template labs: Blank (grid floor only) and Physics lab (10 m x 7.5 m, three walls, open front, 38 objects, all 14 apparatus kinds, 10 g to 1 kg mass set). Public preview, no account. Templates never change.
- Make my copy / Make a copy: saves the scene as the user's own project; counts against the 1 GB quota (lab/<owner hash>/). Card menu "Make a copy" on saved labs. Save (Ctrl+S) on saved labs.
- Public "One real run, start to finish" on / and /library: ST03 frames (face cropped out, Pexels credit), hosted SAM 3.1 track (543 frames), fitted 2330 +/- 110 px/s^2, cost $0.1086, gravity what-if, plus one recorded Muse Spark lab turn (request, tool calls, reply). All numbers from verbatim copies of evidence/N07/live-st03.json and evidence/N28/run1-turns.json (equality tested).
- /lab?editor=1&sample=st03: public 3D replay of that track; gravity starts at the fitted value (px read as mm) so the SIMULATED ball follows the dots; change gravity to see it diverge.
- Guest Fit trace: least squares in the browser up to the first impact (no sign-in). Physics lab: ball-drop is the first sensor, load message says Play, Pause, Fit trace.
- /lab leads with Physics lab (3D) and Blank lab (3D); readable library titles; audience line (students, teachers); guide and landing recommend a simple drop first; footer "Hackathon build".

## Judge (gpt-6-astra, strict, read-only)
- Before: 54.5/100 (JUDGE-REVIEW-ASTRA.md). After first fixes: 61.0/100 (JUDGE-REVIEW-ASTRA-2.md). Fixes 1 to 4 of review 2 are now shipped too (guest fit, recorded Muse turn, drop lesson, ST03 replay); not re-scored.
- Round 3: 65.75/100 (JUDGE-REVIEW-ASTRA-3.md: Impact 5.5, Meta 8, Execution 6.5, Demo 6.5).
- Round 4 not yet scored: both the astra judge and a fallback judge hit the sub-agent usage limit at 18:05 Dhaka (reset 21:50). Re-judge after the reset.

## Round 3 fixes (main b07d0b91, 2afcf394, cded1744, 17734e9b)
- Phones: "Scene and gravity" toolbar button under 900 px opens Scene/Gravity with nothing selected (live checked at 320, 375, 768).
- Guest Agent: 401 shows sign-in and sign-up links plus a link to the recorded agent run.
- Calibration copy: scale is the size of the tracked object over its median tracked box (matches Build/pipeline/live_experiment.py), not an A4 sheet; guide says a pendulum gets a track but no fit.
- Bad ?template= / ?sample= / ?project= links show recovery links (live checked).
- Guest Make a copy keeps edits across sign-in for templates and the ST03 sample.
- ST03 replay starts from the fitted intercepts and slopes of both axes, x acceleration in the gravity vector; test checks every timed point within 4 rmse.
- Featured run: "pipeline code kept the 19 frames"; Muse example separated as a SIMULATED drop. README stale cost claim and em dashes fixed. Library: 15 s timeout, Retry, empty state.
- Guided lesson (Build/web/src/lab-editor/lesson.mjs): "Does a heavier ball fall faster?" predict, fit run A, 10x mass, fit run B, verdict within 2 sigma, prediction scored, no-drag caveat, Copy results. Live run at 1440 and 375: both -9.8100163 +/- 0.0000022 m/s^2, "same", prediction matched.
- Incident: commit 2afcf394 shadowed the imported history record() and crashed /lab?editor=1 for about 8 minutes on DEV (18:00 Dhaka); fixed in cded1744 with a guard test (no local const may shadow an import). All 9 public routes then loaded with no page errors.

## After round 3 (main d2bd4bb8, e661d2c0, 8299cb0f; live web 672e034e, api a2b31a5c)
- Second lesson: twice the height, does it take twice as long? Lesson picker and Copy results. Live at 1440 and 375: 0.625 +/- 0.008 s vs 0.883 +/- 0.008 s, ratio 1.413 +/- 0.023 vs sqrt(2) 1.414. Mass lesson unchanged.
- Home: Use it in a class (lesson, film, measure, compare); honest labels list all five labels.
- Public sample clip Build/web/public/samples/apple-drop-pexels.mp4 (ST03 crop 360x1116, 2.6 s, no face). Workspace card No clip yet? Measure our sample uploads it through the normal path (one daily upload) and opens Measure pre-filled (apple, 7 cm, assumed size).
- Pipeline fix in Build/pipeline/live_experiment.py track_record: frames SAM omits stay aligned and marked missing instead of failing the run (tracker returned 75 frames, the video has 78). An index past the video or a billed frame count unlike the probe still fails. Test added.
- Real hosted SAM run on the sample (local, ledgered in evidence/N89/ledger.jsonl, about 0.016 USD per call): free_fall 2.37 +/- 0.45 m/s^2, scale assumed (evidence/N89/live-apple-drop-sample.json). Low g expected: slow-motion stock clip and an assumed apple size; the gravity what-if explains it.
- Live QA after deploy: both lessons at 1440 and 375, no page errors; bad links show recovery links; sample clip HTTP 200; /api/version serves 8299cb0f.

## Batch 5 (Nov 4, 19:00 to 19:40 Dhaka; main 7100d0a7 to the simulator-test commit)
- Live outage found and fixed: the Modal Meta proxy (us-east) started getting an empty /v1/models from Meta, so every DEV hosted SAM 3.1 run failed with HTTP 404 on /responses (the first signed-in Measure our sample run failed this way). Probes: us-west, ap-south, ap-southeast saw all 9 models, eu-west 0. Proxy moved to ap-south and retries a 404 or an empty model list up to 4 times (unbilled); 12 of 12 later /models calls through the proxy saw 9 models. Build/gpu/meta_proxy.py.
- Signed-in DEV QA (fixture, in-app browser): Measure our sample card uploaded the clip, Measure opened pre-filled, the run finished: 2.33 +/- 0.36 m/s^2, scale assumed (user size), what-if about 2.05x slow motion or a 4.2x size error. Muse agent answered with correct labels.
- API 500 fixed: one shared sqlite connection across threadpool threads raised sqlite3.InterfaceError on concurrent file reads. Store.db is now one connection per thread (Build/api/storage/files.py); a regression test failed on the old code and passes now.
- Agent: start_experiment_track and fit take the user's known_size (Muse had dropped 7 cm and left the result in pixels); prompt rounds a value to two significant figures of its uncertainty.
- Recorded DEV turn (evidence/N89/muse-measures-sample.json): one sentence, Muse called list_files, start_experiment_track (hosted SAM 3.1, apple diameter 7 cm), fit too early, fit again: 2.33 +/- 0.36 m/s^2. Shown on the home page as a MEASURED card; a test checks the card is a projection of the evidence file. README Meta usage table has rows for it and the featured hosted SAM run.
- Home: why predict first, citing Crouch, Fagen, Callan and Mazur, Am. J. Phys. 72, 835 (2004), doi 10.1119/1.1707018 (abstract checked on compadre.org).
- Simulator tests: the 4 long-standing failures fixed without touching the engine. R14 pendulum controls now check the energy of the model the engine selected (R15 made amplitude <= 0.1 rad the S08 small-angle ODE on purpose); ramp and pendulum replay hashes regenerated with a note. tests/simulator 125/125, tests/lab 123/123 + pytest 20.
- Paid: about 0.06 USD more hosted SAM and Muse (ledger). Modal: tiny CPU probes and two proxy deploys.

## Round 4 (Nov 4, 20:29 to 21:40 Dhaka; judge on 20ce186c, fixes in 6ae7faae)
- Judge round 4 (Claude Opus high, fresh context, signed out): 69.5 (Impact 6.0, Meta 8.0, Execution 7.0, Demo 7.0), up from 65.75. evidence/N89/JUDGE-REVIEW-4.md. Top fix: no real clip measured g near 9.81.
- Pipeline bug found by running the owner phone clip OWN07 (book drop, Realme C53, 30 fps) through the live path: the automatic free-fall segment kept 2 landing frames, so the fit gave 6.73 +/- 0.86 m/s^2 with 28.7 px residuals (evidence/N89/live-own07-fullres-before-impact-fix.json). moving_segment now cuts up to 3 trailing steps slower than 90% of the fastest step (the landing). Rerun through the live path: 9.07 +/- 0.62 m/s^2, 3.2 px residuals, 1.2 sigma from Earth g (evidence/N89/live-own07-book-drop.json); a 540p copy gives 9.11 +/- 0.46 (live-own07-book-drop-540p.json). Test added. The ST03 recorded segment is unchanged.
- Home: "A phone drop at home comes out near Earth g" MEASURED card (verbatim copy of the evidence, test-checked) with chart; ST03 card kept as the slow-motion counterexample. The owner clip itself is not published: the OWN07 receipt covers only demo-video snippets, so only the derived track is public (a test asserts no OWN07 video under public/).
- New public replay /lab?editor=1&sample=own07: MEASURED dots in metres, SIMULATED ball at Earth g runs slightly ahead; set gravity to the fitted value to match (test: lands within 3 cm of the last dot at fitted g, more than 1.5 cm ahead at 9.81).
- Lab right panel overflow at 1440 px fixed (panel grid minmax(0, 1fr); lesson select width 100%).
- README: try-it step for the phone replay; About is a component, not a route.
- Verified: node suites pass (workspace 172, simulator 125, lab 123, lab-editor 63, pwa 51, viewer 49, shell-workspace 39, web-private 32, others); pytest agent 214, api-storage 44, api-workspace 32, pipeline 69, fitter 89, lab 20; next build pass; secret scan clean. Deployed api e5183c1f and web 552c6974 from 6ae7faae, both SUCCESS, /api/version 6ae7faae. Live headed Playwright signed out at 320/375/768/1440: no overflow, no page errors, no em dashes, new replay and card render.
- Paid: 3 hosted SAM runs on OWN07, about 0.05 USD (ledger).
- Not fixed from round 4: Clerk development instance on the judging URL (a production instance needs DNS and OAuth changes; risk of breaking sign-in before the deadline), ST03 replay still a thin column, mass lesson 7-digit SIMULATED precision.

## Round 5 (Nov 4, 21:46 to 22:10 Dhaka; judge on 7324493e, fixes in 6f6a5090)
- Judge round 5 (Claude Opus high, fresh context, signed out): 72.25 (Impact 6.5, Meta 8.0, Execution 7.0, Demo 7.5), up from 69.5. evidence/N89/JUDGE-REVIEW-5.md. Main criticisms: one clip only and the fix was tuned on it; replay too fast to see the comparison.
- All 12 owner phone drops run once each through the live path (same prompt "yellow book", same ruler size), none dropped. Under the round 4 rule only 6 of 12 were clean free falls: the book slides on the table after landing and the sideways motion kept the segment going (evidence/N89/own-sweep-before-slowdown-rule). One rule now replaces the round 4 one: the segment ends before the first moving step after the fastest that is over 15% slower than the step before it (free fall only speeds up). The 0.85 cutoff gave the lowest summed fit residuals over the 12 tracks (67 px vs 80 at 0.8, 95 at 0.7), checked offline on the stored tracks without new calls; it was not chosen by closeness to 9.81. The stock apple segment now ends at frame 76 (frame 77 moved 32 px after 66 px: the landing); test updated.
- Live rerun of all 12 with the new rule (evidence/N89/own-sweep/summary.json): 11 free-fall fits, median 8.62 m/s^2, sd 0.72, range 7.24 to 9.82; OWN12 failed this time (SAM 3.1 returned no objects). 9 of 11 sit more than 2 sigma below 9.81: repeatable but biased low, cause not separated (box size from the still frames before release barely changes it: mean 8.43 to 8.52). Home shows all 12 rows with bars and the 9.81 line, and says the bars miss a systematic error; OWN07 stays as the worked example.
- Replay: camera frames every dot and the ball start; Speed control (1, 0.5, 0.25, 0.1x; physics time unchanged); a measured-track replay pauses at the last tracked frame and prints the ball-to-dot gap (OWN07: 1.6 cm below at 9.81).
- Library lede matches the cards; the Scene and gravity button has its own icon (it was a second down arrow on phones); chart caption says the 1 sigma band is thinner than the line.
- Verified: pytest pipeline 69, agent 214, api-workspace 32; node web-private + lab-editor 95; next build; secret scan clean. Deployed api 3ed5ac8e and web 7b9ce46e from 6f6a5090, SUCCESS, /api/version 6f6a5090. Live Playwright signed out, 24 page checks at 320/375/768/1440: no overflow, no page errors, no em dashes; live replay auto-pause at 1440 and 375.
- Paid: 24 hosted SAM runs (two sweeps), about 0.40 USD (ledger).

## Round 6 (Nov 4, 22:12 to 22:50 Dhaka; judge on b60fdc6e, fixes in 02a939b9, 0290c5ca, 227ee876)
- Judge round 6 (Claude Opus high, fresh context): 72.25, no change. evidence/N89/JUDGE-REVIEW-6.md. P1: the replay said the fitted g matched the dots worse than 9.81, because the floor sat right under the last dot so both balls were stopped when compared.
- Replay: the lowest dot now sits 0.5 m above the floor and the auto-pause lands on the nearest physics step. Local check at 1440 and 375: 5.4 cm gap at 9.81, 0.4 cm at the fitted 9.07. Test asserts fitted g within 1 cm and 9.81 off by more than 3 times that and over 3 cm.
- Phone framing leaves room below the track; status panel capped on phones; OWN07 is described as one of 12 with the sweep median; sweep chart text larger.
- Meta proxy (Build/gpu/meta_proxy.py) moved from ap-south to us-west: ap-south dropped request bodies over about 300 KB with HTTP 408, which broke DEV phone uploads. After deploy: 9 models listed, 385 KB and 6.4 MB uploads return 200.
- Recorded Muse turn on DEV (fixture account) on the 1080p OWN07 file: list_files, start_experiment_track, fit x3, result 9.06 +/- 0.63 (evidence/N89/muse-measures-book.json). The home agent card uses it.
- /api/version on the product domain now returns the web and API revisions (it returned the HTML shell). Signed-out session lookup returns 200 with userKey null, so the public editor no longer logs a 401.
- Verified: node web-workspace-api + lab-editor + workspace 243 pass; next build; secret scan clean. infra stage test: 1 pre-existing failure (API fixture lacks the RM04 sample asset), web staging unaffected.

## Round 7 (Nov 4, 22:50 to 23:05 Dhaka; judge on 0e4af2b7, fixes in ea258fba)
- Judge round 7 (Claude Opus high, fresh context): 73.5 (Impact 6.5, Meta 8.0, Execution 7.0, Demo 8.0), up from 72.25. evidence/N89/JUDGE-REVIEW-7.md. Main points: phone results read low with bars too small; on phones the replay gap can only be read, not seen; the MEASURED readout used a different frame from the dots.
- Low bias, partly explained: in 7 of 11 owner drops the last kept frame was already the landing (contact inside the final frame interval slows that step by under 15%, so the slowdown rule kept it). New check in Build/pipeline/live_experiment.py (drop_contact): drop the last frame when the parabola through the others misses it by over 3 residual sigmas (1 px floor), one frame only. Refit of the round 5 live SAM tracks from the local store, no new calls (evidence/N89/own-sweep-refit/summary.json): median 8.62 to 9.03, sd 0.72 to 0.56, range 7.56 to 9.22, 6 of 11 still more than 2 sigma low. OWN01 moved down (9.82 to 9.07) and OWN07 is unchanged, so the check does not pull toward 9.81. Home and README show the refit and say the first pass read 8.62.
- Replay: at the auto-pause the camera zooms to the last dot and the ball (Reset restores the full view), so the 5.4 cm gap is visible on a 375 px phone; the MEASURED readout under the timeline uses the dots' lifted frame, so it agrees with the ball's y.
- Verified: pytest pipeline 70, agent 214, api-workspace 32; node lab-editor + web-private + workspace 267; next build; local headed Playwright at 1440 and 375: 5.4 cm at 9.81, 0.4 cm at 9.07, no page errors. Secret scan clean.
- Deployed web c11c685e and api 310018ea from ea258fba, both SUCCESS. Live Playwright signed out, 24 page checks at 320/375/768/1440: no overflow, no page errors, no em dashes.

## Round 8 (Nov 4, 23:05 to 23:20 Dhaka; judge on 262b24cc, fixes in 5edfba11, 0970c9a2)
- Judge round 8 (Claude Opus high, fresh context): 73.5, no change. evidence/N89/JUDGE-REVIEW-8.md. Its P2 "live API still round 5" was a timing race: the API deploy from ea258fba finished at about 23:06, after the judge read /api/version.
- Agent fit tool now waits up to 90 s for a running track instead of answering "not finished" (the recorded Muse turn wasted one fit call on that); test added (tests/agent 215).
- Home: the clip-to-clip spread (0.56) is added as a systematic term to the OWN07 result: 9.07 +/- 0.84, 0.9 sigma from 9.81. README video line says PENDING until the link exists.
- Railway "Failed to create code snapshot" failed two API uploads of 5edfba11 (no build ran; the previous API kept serving); a third upload went through.
- API 3f027c1e from 0970c9a2 (includes 5edfba11) SUCCESS at about 23:21; /api/version on the API host reads 0970c9a2. Web 19dbdd69 from 0970c9a2 SUCCESS.

## Round 9 and stop (Nov 4, 23:20 to 23:35 Dhaka; judge on c9a2d787)
- Judge round 9 (Claude Opus high, fresh context): 73.5, no change. evidence/N89/JUDGE-REVIEW-9.md. Rounds 8 and 9 each gained under 1 point: plateau rule met, loop stopped.
- Its P2: the round 8 spread term ("0.9 sigma") read as reassurance while the 11 drops are biased low as a group. Replaced: the home now states the mean of the 11 fits (8.75, 11% under 9.81, 6.2 standard errors below), names the suspects (box centre drift as the book tilts, perspective, rolling shutter), and says one agreeing clip does not remove the group bias. All numbers computed from the rows.
- Left open (judge P2/P3, not fixed tonight): Clerk development instance on the judging URL (switching needs an end-to-end sign-up test); "scale assumed (user size)" label next to "ruler-measured"; Guess the Gravity card opens /lab; two Play buttons on the phone replay; home page about 13,300 px tall on phones; the demo video (owner records the voiceover).
- After round 9 (913f4a1d, web 56b0160f SUCCESS 23:32): the home explains that a typed size, even ruler-measured, is labelled scale assumed and its tolerance is in the bar; the Guess the Gravity card now describes Mystery-g mode (what /lab offers). Live HTML checked: group-bias text, scale text and card text present, no em dash. So of the left-open list, the scale wording and the Guess card are addressed by wording only.

## Verified
- Node suites lab-editor 59, workspace 172, web-private 30, web-guide 3, web-library 10, shell-workspace 39, viewer 49 pass; api-storage pytest 43 pass; next build pass. tests/lab + simulator: 4 failures pre-existing on c9c00135 (R14 pendulum controls, ramp/pendulum hash oracle), untouched.
- Live headed Playwright on the custom domain: featured run renders, sample replay loads gravity -2.33, guest fit gives -9.8100 m/s^2 from 76 of 317 samples (first impact cut), no page errors. Screenshots in evidence/N89/shots/.
- Signed-in DEV (in-app browser, fixture): Make my copy on the blank template created a saved lab with preview on a5411b730 api.
- Secret scan of the diff: no credential; one hit is MODEL_API_MODEL (public model id, known false positive).

## Not done / not verified
- No separate judging Railway environment: only "dev" exists and a fresh one would lack the database, volumes, Clerk and Modal wiring. The judging URL is the existing custom domain on the final revision (Koushik's go-ahead: deploy after tests + DEV QA pass).
- QA leftovers in the DEV fixture account: "Blank lab" (91883d5a...). Not deleted: UI deletion needs action-time confirmation.
- Not checked: fresh judge sign-up end to end, paid inference, phone layout of the new sections, the agent panel for signed-out visitors.
- Voiceover script and demo video: not started, by instruction.

## N90 (Nov 5, Koushik follow-ups)
- Home: scroll-craft engine (unchanged copy) mounted; hero pins and scrubs the real ST03 clip (MEASURED dots, fitted curve, all values from featured-st03.json); room flow reveal; ST03 steps pan rail; class steps light up; reduced motion and phones get flow layout. Less body text: stat strip from stored rows, long method text and the Muse reply behind details. Mobbin references: Spade, Linear, Height, Frontify.
- Guide: templates and Make my copy, guest Fit trace, sample replays (Speed, auto-pause, gravity), Guess the Gravity with Mystery-g.
- Footer: Meta AI credit first (Muse Spark/Wonder/Open, SAM 3.1, MapAnything), sponsors (Meta Model API, Baseten, Modal) and hosts (Meta, Cerebral Valley); Stability attribution kept.
- Verified: node 280 + new N90 test pass; next build; secret scan clean. Web deployed from e16df838, SUCCESS, /api/version e16df838. Live Playwright signed out, 16 checks at 320/375/768/1440: no overflow, no page errors, no em dashes. API not redeployed (unchanged).
