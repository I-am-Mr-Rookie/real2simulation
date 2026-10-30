# S15q-orch162 REPORT — DONE

Lane CLAUDE; model anthropic/claude-opus-5-5 / medium; OpenCodex-managed, not polled. UTC 2026-10-30T21:07:40Z -> 21:17Z. Branch run/S15q-orch162, code commit 7fed014b (from main 30a11c2f). Tokens/cost: unknown (unobservable); no Meta/GPU/paid call.

## Result
- P1 422 root cause PROVEN + fixed (web side; API validation untouched): web posted `answers` as the interviewAnswers() ARRAY; API requires the `{question_id: {chip}|{text}}` OBJECT. New `specAnswers()` in controller.mjs converts (chip wins over text: exactly one key). Detail: [evidence/S15q/ROOT-CAUSE.md](../../../evidence/S15q/ROOT-CAUSE.md).
- P2 silent stall fixed: view.mjs used `view.error ?? jobStatus.error` so viewer LOAD_FAILED masked the spec error. Stage panel now shows `CODE: message: <API errors>` + Retry (SPEC_RETRY -> resubmit completed answers); job panel lists BOTH viewer and job errors. errorOf appends API `errors[]` to the message (240-char cap kept).
- P2 provenance: job panel renders server provenance verbatim (label, "(not a live run)", per-stage stage_labels e.g. RECORDED S13h-orch46 / understand: RECORDED S14g-fix3 @ recorded_utc, note). Per-stage S13h UTC remain in the existing event log (recorded timestamps).
- P3 NOT in Owns -> for controller: nav "Sign in" = Build/web/src/shell/ShellFrame.jsx:9 (authAvailable false branch) / Build/web/src/shell/AccountNav.jsx:9 (signed-out fallback); footer "No uploads are enabled" = Build/web/src/shell/ShellFrame.jsx:12.
- Run failure stays honest (unchanged RUN_FAIL path); viewer LOAD_FAILED out of scope.

## Files
Build/web/src/workspace/{controller,view,react}.mjs; Build/web/src/shell/PrivateWorkspace.mjs; tests/workspace/spec-body.test.mjs (+ fixtures rm04-questions.json = Build.agent.interview.questions() for RM04 free_fall, rm04-spec-body.json); tests/api-workspace/test_jobs.py (+1 test). analysis.py unchanged -> API not redeployed.

## Checks (fresh)
- `node --test tests/workspace/*.test.mjs tests/shell-workspace/*.test.mjs tests/web-private/*.test.mjs tests/web-workspace-api/*.test.mjs` (node_modules junction, removed after) -> 110/110 pass.
- `python -m unittest discover -s tests/api-workspace` (PYTHONPATH root;tests/api-workspace) -> 21 OK (incl. new RM04 web-body 200 / old-array 422).
- `npm run build` (Build/web) -> success.
- Deploy: `stage.py web %TEMP%\s15q-web-ctx-orch162` (111 files, rev 7fed014b) + `railway up --detach` -> web deployment 4ad6b82c-7b39-4ef4-96ab-8a674989f883 SUCCESS 21:14:23Z (previous e6bf5fe2 REMOVED). `python infra/railway/dev/verify.py` -> pass. Browser walk = controller.

## deployments.json lines for controller (services.web)
```json
"deploymentId": "4ad6b82c-7b39-4ef4-96ab-8a674989f883",
"previousDeploymentId": "e6bf5fe2-6013-42a6-9337-33888fcc9a1e",
"redeployNote": "S15q-orch162: stage.py web + railway up (spec body answers_to_spec shape; visible spec errors + retry; RECORDED provenance in job panel)",
"sourceRevision": "7fed014b4e1fbb7660c012baac2c287610594823",
"verifiedUtc": "2026-10-30T21:14:23Z",
"providerStatus": "SUCCESS"
```

## Ponytail
Reused: existing reducers/interviewAnswers (README contract kept), errorOf, ws-failure/ws-retry markup, renderWorkspace positional args, stage.py/railway up, test_jobs finish()+scene_resolver harness. Smallest: one 1-line mapper at the boundary instead of changing reducer output/API; error masking fixed by listing both errors. No new deps/abstractions. Skipped: P3 (outside Owns), viewer LOAD_FAILED, Run (Q20), live signed-in walk (controller's IAB). Risk: chips_and_free_text with both chip+text sends chip only (typed text dropped); live end-to-end 200 on DEV unverified until controller walk.

Communication: silent; one completion message to controller.

