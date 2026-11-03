# N82 verification

## Scope and behavior
- Owner-scoped `DELETE /internal/workspace/rooms/{id}` removes only that inactive room's directory. Other owners receive the same 404 as a missing room. Uploaded videos, project records, other rooms and daily upload/start counters remain.
- Building, manual shell/object/rescale mutations and queued/running SF3D work block deletion with 409. File removal uses validated exact paths, rejects linked/escaping artifacts, keeps status until other artifacts are removed, and reports I/O failure as retryable 503.
- Controller clarification supersedes the original sample-copy deletion request: SAMPLE rooms have no delete action and return 409. `Build/api/storage/sample.py` is unchanged; its shared pack stays intact.
- Each own room has a menu action and an inline accessible confirmation with the exact requested warning. Cancel/Escape restores menu focus without deleting; successful deletion refreshes rooms and storage, failures remain visibly explained.

## Reproducible automated checks
```powershell
python -m pytest tests/reconstruction/test_room_delete.py tests/reconstruction/test_live_room.py tests/reconstruction/test_object_lift.py tests/reconstruction/test_shape_upgrade.py tests/api-storage -q -rs
node --test tests/workspace/*.test.mjs tests/api-storage/*.test.mjs
npm run build --prefix Build/web
node evidence/N82/build-qa.cjs
node --check evidence/N82/dev-cleanup.cjs
git diff --check
```
Fresh resumed-run results: Python 116 passed, 1 skipped, 6 subtests passed; Node 171 passed; production build and actual-component QA bundle passed; cleanup-script syntax and Git whitespace checks passed. The skip is Windows symlink creation; the mocked escape guard passed. One installed anyio pytest deprecation warning remains.
The API tests cover owner isolation, retained uploads/other rooms, exact storage decrease, busy admission, prepared SF3D batches, terminal jobs, linked paths, I/O retry and concurrent fake shell/object failures. The UI test covers all grouped rooms, SAMPLE exclusion, exact warning, Cancel and targeted confirmation. No model calls are needed.

## Existing in-app browser evidence (completed before resumption)
- Local `http://localhost:8088` used the actual `createLive` component and workspace CSS, real FastAPI storage/room endpoints and synthetic owned files. The minimal loopback harness is `qa-entry.mjs`, `build-qa.cjs`, `serve_qa.py`; GPU/experiment status is stubbed. This is not a Clerk-backed authenticated workspace end-to-end test.
- At 1366px and 375px: exact confirmation rendered, Cancel did not delete, selected rooms disappeared, busy deletion displayed 409, SAMPLE showed only Open, no horizontal overflow or browser logs. Mobile buttons measured 44px high. See `browser-check.json`.
- `local-audit.json` and `local-deletes.jsonl` record successful owner-room deletes, retained rooms and original upload. Displayed storage fell 2.8 MB to 2.3 MB to 1.7 MB; upload allowance stayed 19. Two local fixture runs explain repeated receipts.
- JPEG captures remain local, excluded from the commit under the worker's no-media-binaries rule: `confirm-1366.jpg`, `confirm-375.jpg`, `deleted-1366.jpg`, `busy-375.jpg`, `sample-menu-375.jpg`, `dev-before.jpg`, `dev-after.jpg`.

## Completed DEV fixture cleanup, not rerun on resumption
- Only the authorized fixture account was used; no private owner projects or media were opened. In-app native project-confirm automation stalled, so the controller explicitly approved the headed Playwright Chromium fallback. This exception applies to cleanup, not the local in-app UI evidence above.
- Deleted exactly `17f7acaaed9945aab6b782b3c93c91cc`, `89f46b23753945718843074eaf9004e4`, `3a0b6e11051c4ea59fe08034deab553b`. Prefix `c46d33ba` was already absent. N64/N76 empty projects were correlated with their authorized run timestamps.
- `dev-cleanup-first-pass.json` is a partial earlier pass; `dev-cleanup.json` is the final DONE pass. `dev-cleanup-summary.json` combines them: eight projects became five, SAMPLE and all four other remaining projects retained identical IDs/titles/created timestamps. Existing project Delete keeps Files; displayed storage stayed 52 MB. DEV upload bytes were not independently audited.
- The cleanup script is retained for audit only. Do not rerun it without fresh authorization. Tabs/helpers were closed after the original checks; no new DEV deletions or browser sessions were started on resumption.

## Limits and cost
- Mutation admission is process-local, consistent with existing room queues; shared leases are required before multiple API worker processes.
- The real symlink test may skip where Windows denies symlink creation. A separate non-skipped mocked resolved-path escape test covers refusal before removal.
- Paid calls: 0; cost: $0. No deploy, push, purchases or account-setting changes.
