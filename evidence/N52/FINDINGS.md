# N52 semantic room shell

## Cause and fix

- N49 did not sample a decoded SAM mask. `sam_text` discarded masks, and `lift` approximated the object with a bounding rectangle and a broad depth band. White desks, wall, floor and metal chair frames contaminated the mean. The cached RM02 grid is HWC RGB, normalized 0 to 1, so this was not an RGB/BGR swap or a frame-size mismatch.
- Decode SAM's actual inclusive-box-local raster and paste it at the box origin in the submitted view's pixel grid. Use it for lifting, cut-outs and furniture colour. Preserve the old box-sequence/JSON-cache interface. Invalid masks retain validated boxes with an explicit fallback reason; invalid image dimensions/boxes still fail validation.
- Added wall/floor noun masks for source-colour sampling. Empty surface samples retain the documented geometric/grey fallback. Colours are source-image means, not colour-calibrated material measurements.
- Assign window/door detections to the nearest shown wall, including EXTENT walls; clip their rectangles to that wall and render existing frames/panels. Placements are explicitly MODEL-ESTIMATED.
- Keep same-view instance masks separate; do not merge chairs into tables. Partition oversized instances into occupied size-prior cells, and cap cross-view footprint growth. Priors and partition identities are estimates, not measured object counts. Sparse cells do not become invented furniture.
- Chair fronts face the nearest table, or room centre without tables. Sofas choose the inward side while preserving their measured long axis. Bound whole oriented furniture footprints when placing scan-edge walls, so chairs do not protrude through them.
- The strict codec is vendored from [Meta's parser](https://github.com/meta-models/meta-sam/tree/9348a8a791d3e5b6417232227e32e10464cdf49f/python), with its SAM licence. Only local type/error adaptation changed. No dependency, renderer or physics change.

## Public RM02 evidence

Uses N49's existing public Pexels MapAnything data, not another GPU reconstruction. `comparison.json` contains code-derived before/after colours and dimensions. The rebuilt shell has five desk/table proxies, four green chair proxies and three window-frame groups on EXTENT walls. Largest local chair width is 0.8379 model metres, versus 1.4835 before. The previous 2.2454 by 3.3315 desk-row extent is gone; the largest new desk footprint axes are 1.1794 by 0.719. Scale remains unverified, and one partial desk still has a thin observed footprint.

`rm02/rm02-side-by-side.jpg` is an actual 1280 px headed-Chromium comparison: unmodified sampled video frame versus the local lab's real canvas, using its Fit view button. Recognisable: green chairs, individual desks, floor, enclosing walls and window frames. Not photorealistic: metal tubing, rounded desk tops, blinds, wall lighting and unseen geometry are simplified. The three inferred window groups do not establish the true physical window count.

`verify.mjs` validates the actual generated scene, green colours, size bounds, facing and furniture containment. All five actual table-top drop checks pass after three simulated seconds (`rm02/ball-rest.json`). This is SIMULATED physics, not a physical room measurement.

Paid: 177 hosted `sam-3.1` image calls, estimated $0.4425 total (176 room noun calls and one diagnostic), no new GPU jobs. Per-call UTC/model/units/cost: `ledger.json`; controller can merge `data/spend.sqlite3` from this worktree. Surface prompts add 32 calls, estimated $0.08 per 16-view room. Provider invoices were not checked.

## Private owner-room limitation

**NOT RUN under the controller's approved five-minute fallback.** The available headed Chromium context is signed out on DEV and the private result route returns 401. The controller then approved the persistent in-app owner session. Bounded retries could not access it: `cua.createBrowserTab('iab', ...)` returned `Browser is not available: iab`, the browser inventory was empty, `open_in_codex` queued the tab on the hidden worker, and native Codex UI retries produced input-geometry errors. This is a worker access limitation, not evidence that the owner's persistent session is signed out.

No owner room data was fetched, no Build lab shell click was performed, and no new-code local rebuild of that exact room was possible. Walls, door, window, table, sofa and chair recognisability are **not assessed**, not substituted with older N06. Session-check receipts and a login-only screenshot stay under `test-data/private/N52/`, excluded from Git. No deploy was performed.

## Checks and reproduction

Use the production pins in `Build/api/health/requirements.txt` for Python checks: unpinned latest FastAPI changes its route-introspection API and fails an existing GPU test. The pinned full suite and new semantic-shell regressions pass. Node lab-editor tests and the Next build pass; the headed browser records zero page errors. One existing optional Node fitter subcheck logs `KeyError: objects` and skips its fitter assertion internally; direct Rapier checks of all five room tables pass independently. See the run report for final counts.

From this worktree: `uv run` with the production pins, then `python evidence/N52/rebuild.py <N49-RM02-job-dir> evidence/N52/rm02 data/spend.sqlite3` (no `--paid` for cache-only replay); `node evidence/N52/verify.mjs`; start the built web app at port 3052; `node evidence/N52/shoot.mjs`.

Remaining structural cost: the strict pure-Python mask codec's canonical round-trip dominates cached replay (about a minute without profiling here). `profile.json` is diagnostic, not production latency; timings under profiling are higher. It has 213 mask records but 212 unique payloads, so a decode cache would save almost nothing. Validation was not weakened to speed it up. Raw public SAM replies are cached locally; no private media or source video is committed.
