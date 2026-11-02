# N77 accounting verification

Command: `python -m pytest tests/gpu tests/reconstruction tests/guardrails/test_daily_cap.py -q`.
Result: **174 passed, 6 subtests passed**, Python 3.14.5; one pre-existing anyio plugin pytest deprecation warning.
No provider calls, GPU instances, credentials, deploys or pushes.

## Cap invariant
- Before spawn: compute reservation and this batch's independent worst-GPU idle reservation both exist.
- On a normal four-call serial run: four compute settlements and exactly one idle settlement.
- Compute is bounded by STARTUP_S + TIMEOUT_S; reservation slack funds short inter-call gaps at A10G, not the next result's possibly cheaper GPU.
- A longer gap closes the previous tail and reserves a fresh one. A result transfer longer than the compute bound also breaks sharing: the old tail may have accrued before the client received the result.
- A failed or ambiguously cancelled call keeps its full compute estimate; the independent idle reservation remains funded. This equals the old combined upper bound for a failed single call.
- A process crash leaves outstanding rows counted at their reservations. Idle rows are deliberately not released by a call lease reaper.
- No class/global state shares tails between different batches or processes.
- The worst-GPU idle row is labelled `SF3D serial batch idle tail`; per-mesh receipt `cost_basis` explains its exclusion.
- Standalone calls still reserve and settle their own tail.

## Regression coverage
Four-call batch, failure in the middle followed by another success, exceptional context exit, abort before spawn, concurrent batches, tail admission denied, long gap, clipped transfer, GPU change during a gap, mismatched ledger/closed batch, and lease reaper with a late result.
The real background room caller is exercised with four fake meshes; all end ready, all rows settle, exactly one tail exists, and every actual amount is <= its reservation.

## Evidence
`accounting.json` contains fresh SQLite ledger rows from seven named unit-test methods in `tests/gpu/test_sf3d.py`, including integer 1e-8 USD reservations and settlements. It is **SYNTHETIC**, not billing or live generation evidence.
No Modal termination completion timestamp was established, so P3-5's optional elapsed-time refund was not applied. A cancellation acknowledgement alone is not used to release headroom.
