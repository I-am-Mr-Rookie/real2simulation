# S24f shots: demo beats 8 and 9

Capture: [capture.mjs](capture.mjs) (Playwright Chromium, not Chrome, 1920x1080 recordVideo, owner video elements CSS-hidden before navigation). Card source: [card.html](card.html). Videos are gitignored (`*.webm`); local files: `beat8-card.webm`, `beat9-close.webm`. Run 2026-11-01 08:3x UTC. No sign-in, no owner clips, no emails, no audio opened.

| Beat | File | Duration | URL | Numbers shown and source | Gap |
|---|---|---|---|---|---|
| 8 | 8a-checklist-card.png, beat8-card.webm | 10.7 s (trim to 6-10 s; rows 1-8 fade in at 0.3 s steps of 0.6 s) | local card.html (project-authored) | Modal billed $0.599594: BENCHMARK `modal_month_to_date_billed_usd` (read 2026-10-29T15:49:15Z). Modal billed $1.052013: sum of rows in [billing-oct-daily.json](../../../evidence/S13l/billing-oct-daily.json) (10-28 0.006384, 10-29 0.746927, 10-30 0.298702). Gate M NOT_MET_INPUT_READINESS, Gate RS NOT_MET (7 of 466 sealed frames), Gate A MET_AMENDED_Q16: BENCHMARK Gates and Summary. Metric scale unverified (RM02/RM04/RM05 abstained): BENCHMARK unavailable table. Meta Model API S16e 1176 tokens, 2.52345 s, cost UNAVAILABLE: BENCHMARK `meta_s16e_*`. SAM 3.1 on A10G, ST03 tracking $0.0233059, 47.93 GPU-s: BENCHMARK `st03_tracking_*`. | BENCHMARK has no "Muse calls" row (Muse is not in this build); only the S16e Meta Model API call is shown. The later $1.052013 is not in BENCHMARK (see VO mismatches). |
| 9 | 9a-repo-top.png | beat9-close.webm 31 s total; repo 7.4-16 s | https://github.com/I-am-Mr-Rookie/real2simulation | Public repo, anonymous view. 950 commits, MIT licence shown by GitHub. | GitHub header shows owner avatar (small face photo, two places) and About text "Private Real2Simulation project backup": crop the avatar and the About box, or use only the file list; the About text is stale for a public repo (owner action, not changed). Judging URL pending, none shown. |
| 9 | 9b-benchmark-md.png | | https://github.com/I-am-Mr-Rookie/real2simulation/blob/main/BENCHMARK.md | Rendered BENCHMARK.md (top as captured, scrolled view). | none |
| 9 | 9c-benchmark-gates.png | | same | "Gates (honest status)" section verbatim from GitHub. | Repo copy shows "Gate M: NOT_MET" (BENCHMARK text) while card says NOT_MET_INPUT_READINESS (BENCHMARK Summary): both are BENCHMARK wording. |
| 9 | 9d-dev-home.png | | https://web-dev-cd80.up.railway.app/ | DEV homepage hero "Film Physics Simulate it in 3D", chips RECORDED / SIMULATED / what-if. No numbers. | DEV site, not labelled as judging site. |

## Key moments for the editor (seconds from video start; see marks.json)

beat8-card.webm: first row 2.8, all eight rows visible 7.6, hold to 10.7. For the 11 s window use 2.8-10.7 or trim the lead.
beat9-close.webm: repo top 7.4 (still 9a), README scroll done 11.9, BENCHMARK.md top 16.3 (9b), gates section 20.7 (9c), DEV hero 28.8 (9d), end 31.1. The first ~5 s of each page is load and wait: cut.

## VO mismatches (nothing changed)

1. b08-01 "Modal bill so far: under a dollar." and the caption "Modal billed to date $0.599594": BENCHMARK's pinned figure is $0.599594 as read 2026-10-29T15:49:15Z. The S13l daily billing report (2026-10-28 to 10-30) sums to $1.052013, so "under a dollar" is no longer supported as current month-to-date. Either re-record the line or say "about a dollar" after the owner decides; the card shows both numbers with their sources. Not independently re-read from Modal today (no billing call made).
2. b09-02 "Try it." with no judging URL: the judging URL is pending, so the close shows only the repo. The repo About text still says "Private ... backup".
3. b09-01 "Every number you saw is a pointer into the repo's benchmark": the $1.052013 on the card is from S13l, not a BENCHMARK pointer.
