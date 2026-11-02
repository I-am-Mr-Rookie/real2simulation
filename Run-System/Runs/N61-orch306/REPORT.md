# N61-orch306

Status: DONE. F01 to F04 fixed and confirmed in the in-app browser on DEV, desktop and 375 px.
- Controller-reported DEV: web 5ad1fa2f, main f7cf60ae. Rebased this branch onto main before the UI-only follow-up.
- F01: sample card/Open opens classroom room e704985d4073435fb816941a6ab12e82; Open experiment exposes the apple result and its working replay.
- F02: existing N60 Saved lab card and Open menu route to /lab?editor=1&project=17f7acaaed9945aab6b782b3c93c91cc, not the agent drawer.
- F03: recorded index 4 shows -49.500 px at 0.17 s, MEASURED, fully wrapping at both widths; uncertainty/scale caveats remain visible.
- F04: ST03 preview displays source file 42fcf3760e5742efa729285887bbbe13 with its matching pixel path, despite file.project_id null.
- Final verification used only the existing N46/N60 test fixture and existing data, at 1366 x 900 and 375 x 850. Quota stayed 0 of 20 uploads remaining.
- No new reproducible finding in these four paths. Initial snapshot fallback recovered; subsequent snapshot responses were 200 with decoded images.
- Full UI evidence: evidence/N61/UI-RECHECK.md. Screenshots are local, uncommitted JPEGs beside it.
- Prior implementation checks: 198 Node tests passed; npm run build passed; no code changed or test/build rerun in this UI-only follow-up.
- Placeholder login failed once, then controller supplied the existing fixture; under five minutes lost, no new account created.
- Before reissue, created a clearly named supplemental QA snapshot-only project c46d33ba096a4dd6b0a786d69b6eda3e in the initial session; retained, not deleted.
- Paid calls, uploads, purchases, settings changes and worker deploy/push: none. No existing private owner project, prohibited room or N06 opened.
- Timing receipt: evidence/N61/UI-TIMEBOX-RECEIPT.json. Controller's reissued Run-System TIMEBOX.json preserved unstaged per evidence/report-only commit scope.
- Skipped: paid inference/new uploads and physical calibration. Browser remains signed in to the QA fixture; no metric-accuracy claim.
