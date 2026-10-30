# R-C recheck2 — Gate C spend/failover guardrails after S20-fix3 + S20-fix4-orch87

Reviewer: R-C-recheck2-orch106, anthropic/claude-opus-5-5 high (cross-vendor vs Sol fix3/fix4). Read-only on Build/, tests/, infra/, evidence/S20.
Base: main e144027 (contains 3ee7652 fix3 cherry-pick, 2ab1a3a fix4). Prior: [RECHECK.md](RECHECK.md), [REVIEW.md](REVIEW.md).

## Verdict: **CLEAR** — no P0/P1/P2 open. Only P3 residual trust/availability boundaries remain (recorded below).
CLEAR = review defects closed. It is NOT Gate C pass; S20d runs the regression. No live Meta/Modal/AWS/billing was exercised.

## Prior findings

| ID | Status | Evidence |
|---|---|---|
| N1 P1 understand.py Meta per-ledger cap | **Closed.** live_post -> reserve_meta: shared admission.lock, global journal, require_reconstruction(candidate_meta_usd), row persisted before httpx.post; pause -> StageError SPEND_PAUSED. | N-META-GLOBAL (4 fresh ledgers -> 3 admitted, 4th paused), N-META-PREPOST (real live_post closure, POST mocked to crash -> 1 journal row); understand.py:143-168 |
| M3 P2 record_muse | **Closed.** main() reserve_meta before httpx.post, fixed ledger, SystemExit SPEND_PAUSED on pause. | record_muse.py:51-68 (code read; fix3 agent tests 52 OK per fix4 report, not rerun here) |
| N2 P1 standalone Modal mains | **Closed for the five named GPU mains** (scene_job, runtime, modal_track, modal_rm02, modal_scenes): admit_standalone runs in the local entrypoint before .remote()/guarded_probe; no amount -> pause; shares the 2-job/$1 envelope. | rg; N-STANDALONE |
| Parent/child double reservation (fix4) | **Closed.** gpu_stages forwards S20_MODAL_REQUEST_ID; claim_gpu consumes once under lock, rechecks budgets; unknown/empty/wrong-stage/claimed/settled pause; no second slot. | N-CLAIM-CONCURRENT (8 threads -> 1 win, reclaim paused), N-CLAIM-FORGED, N-STANDALONE (empty id paused) |
| N4 P3 lifetime cap | **Closed.** settle_gpu: hash-bound proof + scene log + billing rows, chronology, completed/containers [], reviewed_by, single app binding. Settled rows leave the active 2-job/$1 count but liability = final billed in monthly $30. No reset/refill path. | test_settlement (in 91 OK); N-SETTLE-REPLAY, N-SETTLE-EVIDENCE-REUSE, N-SETTLE-CONCURRENT (1 win, 1 settled row, lock released), N-SETTLED-FLAG-TAMPER (settled without evidence -> pause) |
| N3 P3 journal refill by trusted-state editor | Unchanged (documented trust boundary in FIX4-SETTLEMENT.md). | — |
| N5 P3 clone/stale lock/contention | Unchanged; linked worktree -> main state verified. | N-WORKTREE, N-STALE-LOCK |

Fail closed verified for every entry point (reserve_gpu, claim_gpu, settle_gpu, reserve_meta): corrupt journal, missing receipt, stale lock (N-CORRUPT-JOURNAL, N-MISSING-RECEIPT, N-STALE-LOCK).

## New observations (all P3, none blocks CLEAR)

| ID | P | Finding | Evidence |
|---|---|---|---|
| R2-1 | P3 | Settlement authenticity = local operator trust. A repo writer can author a self-consistent zero bill (scene log + billing rows + proof); it releases the slot AND drops that row's monthly liability from reserved $0.50 to $0. Same privilege class as N3; no provider-signed anchor. Mitigation: keep proof/billing exports committed + reviewed (procedure in FIX4-SETTLEMENT.md); optionally require billed >= cost_log upper bound or a second reviewer. | N-SETTLE-FORGED-ZERO |
| R2-2 | P3 | Request IDs are bearer tokens: any same-stage launcher can claim another pending reservation (S20_MODAL_REQUEST_ID). No extra slot/$, but the reserved bound belongs to the parent job, not the child that consumed it. Optionally bind operation into the reservation at reserve time. | N-CLAIM-BEARER |
| R2-3 | P3 | Guard lives in local entrypoints only. modal run FILE::function (direct remote function), modal deploy/shell, and two unguarded CPU-only Modal launchers (Build/reconstruction/spike/cpu_import_probe.py, Build/gpu/modal_image.py) spend Modal credit outside the journal. Procedural; fix4 explicitly claims no universal account cap. Recommend wiring admit_standalone (or a documented CPU exemption) and a runbook line forbidding ::function invocation. | code read; Modal CLI ::function semantics inferred, NOT live-verified |
| R2-4 | P3 | Availability: inventoried ledgers/settlement evidence under .worktrees/ are inside root; removing a worktree that holds them permanently pauses admission until reviewed recovery (fail-closed, not spend). | code read (project/final_amount read_bytes) |

## Checks (fresh, temp dirs only, no network/spend)
- python -B evidence/reviews/R-C/recheck2/probes_recheck2.py -> 15/15 expectations met ([probes-output.jsonl](recheck2/probes-output.jsonl)). Reuses tests/guardrails/test_settlement.py fixture.
- python -B -m unittest discover -s tests/guardrails -t tests/guardrails -> 91 OK ([log](recheck2/guardrails-tests.txt)).
- python -B -m unittest discover -s tests/pipeline -t tests/pipeline -> 53 OK ([log](recheck2/pipeline-tests.txt)).
- Not run: tests/agent, tests/measurement, AWS adapter, real-process (vs thread) concurrency for claim/settle (recheck M1 already proved the lock with 8 processes), canonical runtime journal (absent per fix4; not touched).
