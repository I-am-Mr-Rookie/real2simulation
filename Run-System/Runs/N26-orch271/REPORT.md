# N26-orch271 REPORT
Status: DONE. Branch run/N26-orch271 (base main 5aaa04a4). No deploy. Web side of the N13/N25 fixes, all in Build/web/src.
- F8: API errors show detail.message; the ISO reset_at inside it is shown in browser local time (apiErrorText in workspace/live.mjs). Seen: "resets at Nov 2, 12:00 AM GMT+6".
- F1: Result card shows "No value reported. No fit: <reason>" on abstain; chartGeom draws the server result.curve + band_1sigma (browser refit only for results without one, e.g. the recorded sample); abstain draws dots only.
- F4: tag "scale assumed (user size)" (scaleTag); the label "scale assumed (user size): <typed text>" is shown once; shareable() unchanged.
- F2: Projects/Processing rows and the opened card use sample.title plus a SAMPLE tag.
- F6: LabEditor shows room.scale.reference_rejected.reason in the Room panel and in the A4 click status text.
- F3: agent mode is stored per user (key r2s.agent.mode.<server-verified scene id>), undecided until the user is known; the old global key is ignored, so a new account always sees "Choose how the agent runs" once. Browser: card on first load after sign-up even with the legacy key set; not shown again after Continue.
- F10: green with an empty queue reads "GPU on, idle". The API sends no idle time (state, queue_length, your_position, source only), so no minutes are shown.
Checks: node --test globs workspace, shell-workspace, web-private, lab-editor: 212/212 (new tests: mode decision, apiErrorText, gpuDot idle, server curve + abstain chart, scaleTag, labelsOf, sample name). npm run build exit 0.
Browser: headed Playwright Chromium, next dev :3026 + local uvicorn :8126, temp R2S_DATA_DIR, fresh clerk_test account, desktop + 375 px. evidence/N26/e2e.mjs, e2e.json, e2e.log, 15 PNGs: fresh contributor card, no-size / typed-size / abstain cards, SAMPLE row in Projects and Processing, upload limit text, GPU idle dot. Fixtures: evidence/N26/seed.py runs the real fitter on the RECORDED apple track (no SAM call).
Paid calls: none.
Skipped: F6 not shown in a browser (no sample room bundle in the worktree; build only). The 429 body and the green/empty GPU status are mocked responses (listed in e2e.json). No DEV deploy.
Risks: existing users see the contributor card once more (old global key cannot be attributed to a user). Mode stays per browser. GPU label cannot show idle minutes until the API provides them. Railway CLI was linked temporarily in Build/web to pull Clerk dev keys into a gitignored .env.local (deleted, unlinked).
