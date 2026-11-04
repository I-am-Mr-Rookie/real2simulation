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
