# S07-pts-audit-orch58 — DONE

## Result

- Audited **all 1,664 committed evidence files at dispatch snapshot ea0dcc9** for
  tracking PTS outputs: **23 audited files, 18 OK / 5 WRONG**, 2,641 timestamp
  occurrences. New errata maps for all five wrong files; accepted evidence unchanged.
- Additional affected historical files beyond orch40's two named receipts:
  `S07b/orch13/result-run10.json`, `result-run11.json`, and
  `S07b/orch14/result-run1.json`: ST03 f76 **2.569233 -> 2.535867 s**.
  Accepted orch14 result has the same error; RM04 orch40 f11 **0.48 -> 0.44 s**.
- Full-stream local ffprobe on freshly SHA256-verified ST03/RM04; both sources
  match acquisition pins and clips.csv paths/URLs. **clips.csv has no SHA column**;
  hashes come from `evidence/clips/S02c-acquisition.json`, not an invented column.
- Added `L4: 0.000222` USD/GPU-second to existing `Build/gpu/cost_log.py:RATES`,
  with source URL/date comment. Official [Modal pricing](https://modal.com/pricing),
  fetched 2026-10-30 via TinyFish search + fetch_content. Published list rate,
  not a newly observed bill. No change to existing rates or billing semantics.

## Evidence / consumers

- `evidence/S07/S07b-errata/audit-orch58/README.md`: every audited file labelled
  OK/WRONG, exact wrong frames, source hashes, exclusions, and consumer analysis.
- `audit.json`: per-file SHA256, JSON pointers, all differences, source/probe
  metadata, exclusions and malformed inventory-text exception.
- `ST03-full-presentation.json`, `RM04-full-presentation.json`: fresh whole-stream
  probe results (543 / 231 frames), no decode-packet truncation.
- Five new `*-frame_map.json` maps bind to originals with `errata_for` and
  `original_sha256`. Previously accepted errata are unchanged and independently OK.
- `checks.json`: all five correction maps checked; old method reproduced and
  existing fixed `_pts` compared with full decode at every distinct map endpoint
  (RM04 f11; ST03 f70/f76/f83/f542). Fixed helper agrees at all five endpoints.
- Existing `predict.st03_record` applies ST03 errata and re-seals; current S12
  prediction/overlay/Gate-RS receipts cite it. S13f replay explicitly applies RM04
  errata; S13f/S13h live segmentation maps are already correct. No consumer edits.
- Historical S12 `boundary-ST03.json` / `params-ST03.json` retain older quarantined
  boundary/abstentions; current corrected prediction supersedes that seal. They
  were not rewritten. S06 camera `time_s=float(i)` is an index clock, not old
  `_frames` PTS; no affected S06 tracking map was found.

## Fresh verification

Commands executed in this isolated worktree, with `PYTHONPATH` set to it:

| Check | Result |
|---|---|
| `python evidence/S07/S07b-errata/audit-orch58/audit.py --self-check` | PASS (bad timestamps/indexes rejected; duplicate map/record extraction checked) |
| `python .../audit.py <canonical root>` | PASS: 1,664 scanned; 18 OK / 5 WRONG |
| `python .../check.py` | PASS: 23 files / 2,641 occurrences / 5 corrections / 5 old+fixed comparisons |
| `python -m unittest discover -s tests/gpu -v` | 2/2 PASS (L4 estimate, CPU/memory, zero duration, receipt bounds, billing isolation/back-solve) |
| `python -m unittest discover -s Build/gpu -p test_cost_log.py -v` | 5/5 PASS |
| `python -m unittest discover -s tests/prediction -v` | 33/35 PASS locally; 2 simulator integration cases lacked worktree Rapier dependency |
| Same 2 simulator cases with only `params.ROOT` pointing to canonical preinstalled simulator | 2/2 PASS; no install, symlink, code change or canonical write |
| `python -m unittest discover -s tests/pipeline -p test_gpu_stages.py -v` | 6/6 PASS (offline mocked calls) |
| `python -m unittest discover -s tests/measurement -p test_modal_track.py -v` | 8/8 PASS, including real local ST03 ffprobe regression |
| `git diff --check` | PASS |

Logs: `checks.log`, `missing-simulator-dependency.log`,
`canonical-simulator-check.log` in this run directory. The local prediction suite
is **not** represented as 35/35 passing in the isolated worktree: missing
`@dimforge/rapier3d-compat` was confirmed by direct Node import; canonical installed
dependency reuse verified the two cases without changing the no-install scope.

## Contract / Ponytail full

- S07 lane; assigned `gpt-6.1-sol` / medium. Exact managed model runtime identity
  not independently introspectable. **OpenCodex-managed; not polled**. Token usage
  unobservable; no paid GPU/Meta calls, no new infrastructure cost.
- Issued 2026-10-30T00:55:41+00:00; deadline 2026-10-30T01:25:41+00:00
  (07:25:41 Dhaka); implementation cutoff 01:20:41Z. Actual stop/report timestamps
  are in `TIMEBOX.json`; all acceptance criteria completed early, no incomplete
  early-stop exception requested.
- Parent project `91e441f8-e40c-4ec4-bea2-de7fa1582d97` / controller
  `01a1882d-3481-7ce3-8f88-45c942e341cd`, as supplied in launch handout; launcher
  project association not independently verified. Branch `run/S07-pts-audit-orch58`
  in requested `.worktrees/S07-pts-audit-orch58`, base ea0dcc9. Controller integrates;
  no main/control edits, merge, deploy, publication or worktree removal here.
- Read/applied installed Ponytail full 5.3.3. Reused existing `cost`, `scene_log`,
  `reconcile`, `_pts`, unittest, ffprobe and accepted evidence schemas. Product
  change is one missing rate plus provenance comment; no new API/config/dependency.
  Batch audit is standard-library-only; no second runtime timestamp implementation.
  Reused already-installed canonical simulator only to resolve optional check
  dependency availability, without altering source/dependencies or broadening Owns.
- Communication: one mandatory initial skill/work update (higher-priority
  instruction), no optional progress chatter; one authorized final controller
  callback. No owner question or canonical-control write needed.

## Skips / risks / next

Skipped GPU/Meta jobs, billing refresh, installs, untracked evidence, consumer rewrites
and historical re-sealing; this is a committed-snapshot audit, not concurrent-output
coverage. Correction validates file PTS only, not masks/centroids/capture clock/scale
or physical gates. Historical boundary/params and cost receipts remain historical.
Controller should integrate the scoped commit; future consumers must use errata-
corrected maps/current prediction path, not stale original PTS or old S12 seals.
