# S24d shots: held-out prediction and reveal (real DEV product)

Capture script: [capture.mjs](capture.mjs) (Playwright Chromium, headed, fresh Clerk test account per context, DEV https://web-dev-cd80.up.railway.app, 2026-11-01 about 08:00 to 08:12 UTC). Env: OWN05, RM04 (local clip paths), OUT, ONLY (a, d, e). Videos (.webm, gitignored under media/capture/S24d/): abc-flow.webm 1920x1080 (55 s), d-viewer.webm 1920x1080 (36 s), e-backup-1280.webm 1280x720 (54 s). One PNG still per shot is committed. Every number below is read from the live page after the real fit (fitter on the server); nothing is typed by hand.

Privacy: OWN05 (owner clip, not OWN07) is uploaded for beats a to c. A CSS rule (video and [poster] visibility hidden) is injected with addInitScript before any navigation; the workspace page showed no video, poster or thumbnail of it in any still (all PNGs inspected: upload step, chart, report; none shows a frame). The job id and avatar are visible; no email is rendered (the test address is never shown on screen). RM04 is a public Pexels clip.

## Stills and numbers
| Beat | File (still) | Video + key timestamps (s) | URL | Numbers shown and source | Gap |
|---|---|---|---|---|---|
| a1 workspace | a1-workspace.png | abc-flow 12.3 workspace_ready | /workspace/<id> | none | none |
| a2 upload | a2-upload.png | abc-flow 15.0 upload_started | same | "Uploading 05_repeat_a__035711.mp4: 0%" (file name of owner clip shown; no frame) | The file name contains the owner clip name; crop in edit if undesired. |
| a3 agent question | a3-agent-question.png | abc-flow 23.2 agent_question | same | "Agent needs your answer. Question 1 of 1: Name one object of known size in the fall plane ..." (agent text from API) | none |
| a4 known size | a4-known-size.png | abc-flow 28.9 known_size_typed, 29.6 answer_sent | same | typed "book cover horizontal edge 20.28 cm" (scripted input) | none |
| b1 fit curve and band | b1-chart-fit-band.png | abc-flow 33.4 fit_shown | same | Chart axes 346 px, 443 px, 681 px, 0 s, 0.1 s, 0.2 s; "HELD-OUT CHECK PASS: CHI2/DOF = 2.32/3, P = 0.51"; legend with RECORDED track points, SIMULATED fit (solid), SIMULATED prediction (dashed), 1-sigma band sigma 2 px; all from workspace live fit + recorded S07m track points | none |
| b2 reveal | b2-heldout-reveal.png | abc-flow 37.7 heldout_reveal (dashed prediction vs hollow held-out points inside the band, after the "held out" divider) | same | same chart; held-out residuals 4.6, 9.6, 19.9 px (in panel) | b2 is pixel-identical to b1 and c1: the chart is static, there is no animated reveal in the product. For the edit, cut between the divider and the hollow points inside one clip. |
| b3 data table | b3-data-table.png | abc-flow 40.9 data_table | same | "Show data table" opened: per-point values | not transcribed here; read from the PNG if needed |
| c1 g headline | c1-g-headline.png | abc-flow 44.8 g_headline | same | g = 8.62 ± 1.29 m/s² (fitter core.py fit_least_squares degree 2 + jacobian_covariance); Uncertainty fit 0.15, detection 1.27, clock 0.07, centroid vs box 0.12, scale 0.07 | identical frame to b1 (headline is beside the chart). |
| c2 caveats | c2-caveats.png | abc-flow 48.5 caveats | same | "Scale unverified; not a validated measurement"; Recorded reference g = 8.62 ± 1.28 m/s² (precomputed S07m); "Held-out check PASS: chi2/dof = 2.32/3 = 0.77, p = 0.51 ... forking-paths caveat ... not accuracy: it can still sit far from the local 9.79 m/s^2"; "Your known size: book cover horizontal edge 20.28 cm = 0.2028 m (user-declared, not verified)" | none |
| c3 report | c3-report.png | abc-flow 52.3 report_body | same | Report click scrolls to the result body (Fit residuals 0.1, -0.2, 0.2, -0.1 px; rmse 0.12; dof 1; 4 points fitted) | The Report control scrolls the same page; there is no separate document view. |
| c4 report scrolled | c4-report-scrolled.png | abc-flow 55.4 report_scrolled | same | caveat block, scale lines | none |
| d RM04 viewer | d1-viewer.png, d2-viewer-orbit.png | d-viewer 31.9 viewer_loaded, 36.2 orbited (drag orbit from about 32 to 36 s) | same (RM04 job) | Label "Scene geometry: Display only, scale unverified, not a measurement."; question "How far does the ball fall before it lands, in metres?" 1 of 3; "Scene loaded." | Point cloud only, no numbers; interview not answered. |
| e backup 1280x720 | e-a1..e-a4, e-b1, e-b2, e-b3, e-c1..e-c4 (.png) | e-backup-1280 23.6 agent_question, 28.9 typed, 33.1 fit_shown, 37.1 heldout_reveal, 40.2 data_table, 43.9 g_headline, 47.5 caveats, 51.1 report_body, 54.2 report_scrolled | same | same values as b and c (body text identical, g = 8.62 ± 1.29) | At 720 px the chart and panel stack, so e-b1 shows the legend half; e-b2 is the chart. |

## Notes for the editor (S24i)
- Each webm is one continuous take of 36 to 55 s with a 12 to 15 s lead-in (sign-up and workspace load): trim from the timestamps above. Usable segments: upload to answer 15 to 30 s; fit and reveal 33 to 45 s (chart readable from 33.4, 12 s hold); caveats 45 to 55 s.
- Marks.json holds the abc-flow marks of the last run only; d-viewer marks are from the first run and e marks from the second run, copied here.
- Wait times are scripted (2 to 4 s holds, typed answer at 70 ms per key); no frantic clicks.


