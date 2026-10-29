# S05f-fix-orch32 REPORT — DONE

Lane/model: S05 owner repair, anthropic/claude-opus-5-5 medium; coding quota OpenCodex-managed; not polled. UTC start 2026-10-29T15:51:06Z, end 2026-10-29T15:56:05+00:00. Base main `a63fe31`; branch `run/S05f-fix-orch32`. CPU only, $0; tokens unobservable.

## Changes (Build/reconstruction/spike/)
- **D1** `gate_r.py`: `load_json` = `json.loads(..., object_pairs_hook=_unique_pairs)`; any duplicate member (any nesting level, all three CLI inputs) raises `ValueError` before the fixed-cohort check. CLI uses it instead of the plain lambda.
- **D2** `evaluate`: each job's `scenes` must be a nonempty list, unique, subset of the cohort, and disjoint from scenes already covered by earlier jobs (conflicting coverage → `ValueError`, no overwrite) — validated before amortizing lifetime/cost.
- Thresholds/constants untouched: 10%, 5°, 240 s, 2/3, EPS, COHORT.
- `test_gate_r.py` +3 tests: `test_d2_job_scene_ids_validated_before_amortizing` (failing control 600 s → gpu FAIL; duplicate ×3, unknown IDs, empty, non-list, cross-job conflict all rejected; legit 2-scene amortization 262/2=131 s kept); `test_d1_duplicate_json_members_rejected` (hook raises; nested unique OK); `test_d1_cli_rejects_conflicting_duplicate_scene` (real CLI subprocess, real NPZ hashes: unique-bad control exits 0 with FAIL; duplicate-key file exits nonzero "duplicate JSON members").

## Fresh checks (evidence/S05/S05f/fix-orch32/)
- `gate-r-tests.txt`: 14/14 OK.
- `spike-tests.txt`: 86 ran, 1 error = pre-existing `test_modal_scenes` ImportError (no `modal` package locally; same as S05f's 83-test record). No new failures.
- `reproduce-after-fix.txt`: `reproduce_remaining.py` (unedited) now exits 1 at its D1 assertion — CLI exit 1 with `ValueError: duplicate JSON members: ['RM02']`. The PASS dict printed in that assertion is the stale pre-existing `duplicate-cli-result.json` from the R-R worktree (CLI no longer writes). Its D2 section is unreachable after D1 fails, so `d2-after-fix.txt` runs the same D2 inputs directly: control FAIL; duplicate job IDs REJECTED; unknown IDs REJECTED. Reproduction side-file writes in evidence/reviews were reverted (`git checkout -- evidence/reviews`); no evidence/reviews diff committed.
- `gate-rerun.txt` + `GATE_R-rerun.json`: real CLI on evidence/S05/S05f/RESULT.json → `FAIL {scale 0, orientation 0, qualifying 0, gpu 3, clips 3}`; rerun JSON == committed GATE_R.json (True). Real gpu_jobs coverage passes the new D2 validation (RM02 orch14 job; RM04+RM05 S05c job).

## Ponytail (full)
Reuse: stdlib `object_pairs_hook`, existing `ValueError` fail-closed pattern, existing `clip`/`ev`/`JOBS` fixtures and the reviewer's own synthetic counterexamples. Smallest complete change: one 6-line hook + 4-line validation block; no new module/option/dependency. Skipped: cost_usd numeric validation (not requested), reproduce script edits (forbidden), GATE_R.md/JSON regeneration (identical output).

## Limits / next
No gate claim beyond what ran: Gate R remains FAIL (0/3). Not re-reviewed cross-vendor; R-R should recheck D1/D2 against this branch. Not merged (controller integrates). Communication: silent; one completion line to controller.
