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
