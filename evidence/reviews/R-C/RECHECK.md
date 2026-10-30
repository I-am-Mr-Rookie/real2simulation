# R-C recheck — Gate C spend/failover guardrails after S20-fix2-orch65

Reviewer: R-C-recheck-orch75, anthropic/claude-opus-5-5 high (cross-vendor vs Sol S20-fix/fix2). Read-only on Build/, tests/, infra/, evidence/S20.
Base: main 19c2e56 (contains S20-fix2). Prior review: [REVIEW.md](REVIEW.md).

## Verdict: **CHANGES_REQUIRED** (P1 open). CLEAR would mean review defects closed, not Gate C pass; it is not reached.

The S20-fix2 boundary itself is sound: every original defect it targeted is closed and no new bypass of
reserve_gpu / AWS reservation was found under concurrency, corrupt/missing state, stale locks, worktrees or replay.
Gate C's *global* cap is still not universal: two Meta entry points and the standalone Modal CLIs bypass it.

## Original findings

| ID | Status | Evidence |
|---|---|---|
| H1 guard has no callers | **Partially closed.** gpu_stages.reserve -> reserve_gpu (lock + require_reconstruction + durable journal) and failover AWS path -> _reserve_aws. Still unwired: Build/pipeline/understand.py (Meta, N1), Build/agent/record_muse.py (M3), standalone Modal CLIs (N2). select_provider has no live caller (AWS default OFF; acceptable). | rg callers; code read |
| H2 per-ledger cap via caller-selected ledgers | **Closed** for the GPU pipeline: count/$ cap taken from global journal AND local ledger; fresh dirs cannot reset. | 64/64 guardrails tests (G1); N-CONC, N-REPLAY |
| M1 no reservation lock / race | **Closed.** O_EXCL lock around project + check + journal fsync/replace + ledger append. 8 real processes x $0.40 -> exactly 2 admitted, 2 journal rows, lock released. | N-CONC |
| M2 AWS bucket + unknown keys | **Closed.** Unknown top-level key pauses; _reserve_aws requires AWS bucket and durably reserves AWS (+Meta candidate) under same lock; repeat receipts cannot refill (A15 test). | N-UNKNOWN-KEY; tests |
| L2 rounding | **Closed.** usd() liability ROUND_CEILING; headroom_usd ROUND_FLOOR (1e-9 -> 0). | N-FLOOR; accounting.py:17,43 |
| Parent/child envelope | **Closed.** project_ledger: liability = max(parent reserve, SUM child worst, max bill); scene-log children not re-added (app_ids guard). Code-read + fix2 tests; not separately probed. | reservations.py:58-94,191 |
| L1 shape-only settlement | Unchanged by design (trusted reconciliation obligation). | — |
| **M3** record_muse Meta not globally reserved | **Still OPEN (known deferred). P2.** Fixed ledger evidence/S14/S14b-ledger.jsonl ($1/20 calls), so not per-file resettable, and it IS inventoried (evidence/S14 *ledger.jsonl) so its rows project into the Meta $120 cap; but no lock, no global pre-transport reservation, est_usd-only sum. Not counted as fixed. | record_muse.py:23,35-42 |

## New findings

| ID | P | Finding | Evidence |
|---|---|---|---|
| N1 | **P1** | Build/pipeline/understand.py::reserve (S13e live Meta path) is the original H2 pattern on Meta: $1/6-call cap per CLI-selected LEDGER file, no lock, no global journal, no require_reconstruction. Ledger row written only AFTER httpx.post (crash after POST = unrecorded spend). A caller-selected ledger outside evidence/S05-S14 / Run-System gpu-ledger is not inventoried, so its spend is invisible to the Meta $120 cap. | N-META-UNDERSTAND: 4 fresh ledgers each admit worst $0.0633; understand.py:121-147 |
| N2 | **P1 (Gate C universality; known in fix2 REPORT)** | Standalone Modal entry points (Build/gpu/scene_job.py, runtime.py, Build/measurement/runtime/modal_track.py, Build/reconstruction/spike/modal_*.py) have no reserve/ledger/admission call; protection is procedural (worker-written job-ledger.json projected afterwards). | rg reserve/ledger in those files: no hits |
| N3 | P3 | Journal refill: the S13f contract count/$ cap is computed only from journal rows + caller ledger. Replacing the server-owned journal with an empty valid one re-admits (old ledgers still project into the Modal $30 cap, and missing-ledger protection is also lost). Needs write access to trusted state; documented "never delete a journal". Optional: anchor journal (monotonic count/hash in receipt) or count projected Modal rows too. | N-REFILL: before [adm,adm,paused] -> after reset [adm,adm] |
| N4 | P3 | Global-lifetime cap: reserve_gpu applies MAX_JOBS=2/$1 to ALL Modal journal rows ever, with no settlement/release path. Fail-closed, but after 2 pipeline jobs all reserve_gpu admissions pause permanently, creating pressure for N3-style manual journal edits. Needs a reviewed reconciliation/release procedure. | reservations.py:236-241 |
| N5 | P3 | Independent clone (not worktree) resolves to its own runtime state; separate cap only if someone copies receipt+journal into it. Stale lock = permanent pause until verified manual removal (intended). Lock contention is non-blocking -> nonretryable SPEND_PAUSED for a legitimately concurrent job (availability, not spend). | N-CLONE, N-STALE |

Fail-closed confirmed: corrupt journal, missing receipt, extra journal key, deleted inventoried ledger, replayed key -> pause with no ledger write (N-CORRUPT-*, N-MISSING-LEDGER, N-REPLAY). Linked worktree -> main state (N-WORKTREE).

## Required before CLEAR

1. N1: route understand.py live Meta calls through the shared lock + durable global Meta reservation before transport (same pattern as reserve_gpu), mapping pause -> StageError SPEND_PAUSED; write the reservation row before POST.
2. M3: same for record_muse.py (owner of Build/agent).
3. N2: wire standalone Modal CLIs through reserve_gpu (or a documented equivalent) before any "universal cap" / Gate C claim.
P3 items optional before Gate C; record decision.

## Probes / checks (fresh, temp dirs only, no network/spend)

- python evidence/reviews/R-C/recheck/probes_recheck.py -> 13 probes, all expectations met; 2 rows document findings (N-REFILL, N-META-UNDERSTAND). Output: [recheck/probes-output.jsonl](recheck/probes-output.jsonl).
- python -m unittest discover -s tests/guardrails -> 64 OK ([recheck/guardrails-tests.txt](recheck/guardrails-tests.txt)).
- Not run: tests/pipeline, AWS adapter suite, old probes.py (asserts old bugs, would call live-root reserve), canonical runtime projection. No real journals, Modal, AWS or Meta touched.
