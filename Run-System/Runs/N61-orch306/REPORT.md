# N61-orch306

Status: DONE. Four N60 findings fixed; local verification only.
- F01: legacy room rows use update timestamps when created is absent; ready room opens from card/Open, experiment remains in Project actions.
- F02: snapshot-only Saved lab opens `/lab?editor=1&project=<id>`, not the agent drawer.
- F03: graph value/unit/label wrap on desktop and stack compactly on phones; removed phone hiding and site-caption spacing.
- F04: include exact room/experiment file_id references even with null file.project_id; missing source never falls back to an unrelated video/overlay.
- Tests: six new regression tests; confirmed failures before fixes, then `node --test tests/workspace/*.test.mjs tests/lab-editor/*.test.mjs`: 198 passed, 0 failed/skipped.
- Build: `npm run build` passed (exit 0); `git diff --check` passed.
- Evidence: `evidence/N61/node-tests.txt`, `evidence/N61/build.txt`.
- In-app browser attempted once: `Browser is not available: iab`. Used test-based reasoning as dispatched; no browser fallback or live UI claim.
- Scope: workspace, lab-editor.css only in lab-editor, focused tests, evidence and this contract receipt. N59 code untouched.
- Paid calls: none. Deploy/push: none. No dependency added, secrets read, account actions or owner projects opened.
- Skipped: rendered/DEV verification. Risk: phone layout and menu behavior still need an available in-app-browser recheck after integration.
