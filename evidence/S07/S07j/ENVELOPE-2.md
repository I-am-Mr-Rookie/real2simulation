# S07j standalone Modal envelope 2 (reviewed contract; code only, nothing run)

Per evidence/S20/FIX3-ADMISSION.md N4: no release, no clearing, no settled flag. Old rows stay immutable
and stay counted. Contract constant: `Build/guardrails/standalone.py` `LEDGER, MAX_JOBS, CAP_USD`.

## Envelope 1 (exhausted, untouched)
Ledger `evidence/S20/runtime/standalone-gpu-ledger.jsonl`, 2 jobs / $1.00, rows read-only (not modified by S07j):

| # | request (journal `evidence/S20/runtime/reservations.json`) | app | reserved | outcome |
|---|---|---|---|---|
| 1 | `...:segment:modal-track:OWN01:24e8a049...` | ap-9SEBfxKkipzckSWGcQRGvt | $0.60 | OWN01 tracked |
| 2 | `...:segment:modal-track:batch:OWN02,...,OWN11:...` | ap-7qnUtLNN8xQy534jpuXcQs | $0.40 | OWN02-06 tracked; OWN07-11 CUDA OOM (stopped) |

Controller dashboard reads (Modal Usage & billing, in-app browser; cycle Oct 1-31): $0.78 before both jobs,
$0.80 after job 1, $0.89 at 23:44Z after job 2 (may lag); spend $0.00; $30 monthly credits.
Observed both jobs ~= $0.11 total vs $1.00 reserved. Both journal rows remain unsettled (full $1.00 liability).

## Envelope 2 (new)
- Ledger `evidence/S20/runtime/standalone-gpu-ledger-2.jsonl` (new path; created only by a future admission).
- `MAX_JOBS=3`, `CAP_USD=1.50`. `reserve_gpu` applies both to (a) EVERY unsettled Modal journal row
  (global, includes the two old rows) and (b) the new ledger. So the bound is cumulative:
  old 2 jobs/$1.00 + **at most 1 new job of at most $0.50**. A 4th job or >$0.50 fails closed (`ReconstructionPaused`).
- Unchanged: `S20_MODAL_RESERVATION_USD` all-in bound required; global receipt freshness/pause/headroom/floor
  (`require_reconstruction` via `reserve_gpu` + `claim_gpu`); one durable claim per reservation.
- Why: the OOM fix (load SAM once per container) needs one more bounded job to re-track OWN07-OWN11;
  observed spend ($0.11) is far below envelope 1's $1.00, $29+ monthly credit headroom remains.
  Any further job needs a new reviewed envelope (new constant + tests), not an edit of this one.

## Re-track job bound (OWN07-OWN11)
`track_batch` timeout 780 s + 300 s startup: (300+780) s x (A10 $0.000306 + 2 cores x $0.0000131 + 16 GiB x
$0.00000222)/s = 1080 x $0.0003677 = **$0.397 all-in worst case**, independent of clip count (5 clips, 12-22
frames each, below OWN01's 21-frame/16 GiB peak). Reserve $0.40 <= $0.50 remaining.

## Tests (offline, fake runtime)
`tests/guardrails/test_live_admission.py`: `test_envelope2_keeps_old_rows_and_admits_only_its_bound`
(old ledger bytes + journal rows identical; $0.51 refused; $0.40 admitted to ledger-2; 4th job refused),
`test_envelope2_still_requires_global_modal_headroom`, updated `test_standalone_and_pipeline_share_same_job_cap`.
`tests/guardrails/test_simulated_cap_regression.py` pins envelope 1 for the historical Gate C replay.
