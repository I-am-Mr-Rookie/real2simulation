# S20 fix4 — N4 settlement and fix3 verification

## Controller-visible predecessor note

S20-fix3-orch78 is timing-FAILED, PARTIAL and not accepted. Its two WIP commits
7809496 / 075e8b7 were explicitly cherry-picked onto fresh main e72338c as
83e9431 / ee2c941 for this successor's independent verification. The predecessor
REPORT/TIMEBOX remain untouched history, not this run's acceptance evidence.
This note supersedes FIX3-ADMISSION.md's N4 decision; no canonical controls edited.

## Operational observation (read-only, not a reset)

Canonical `evidence/S20/runtime/` contains only `.gitignore`; `reservations.json`
and `receipt.json` are absent. Thus the current journal count is **unavailable,
not a verified zero**. See `fix4-canonical-journal.json` for fresh timestamp/count
observation. This run neither initializes nor repairs live state.

Before this fix, every Modal journal row ever counted against two jobs / $1,
including the new standalone callers. Once provisioned, two admitted jobs (or
an outstanding $1) would permanently pause further tracking/reconstruction,
irrespective of completion/billing. Deleting the journal is NOT a remedy.

## Reviewed settlement

`python -m Build.guardrails.settlement REQUEST_ID REVIEWED_RECEIPT.json`

This local operator command uses the same canonical-root resolver, exclusive
admission lock and fsynced atomic JSON replacement as reservation. It performs
no provider calls. **Not executed on real state by this run.**

It accepts exactly one existing unsettled Modal reservation, with a unique app
binding already present in its existing ledger/projection. For a standalone job,
retain the returned request ID and record its observed app ID as an append-only
result event in the same inventoried ledger before settlement. Never guess an
app ID or modify/delete a reservation. A result event uses existing fields:
`{"request_id":"...", "provider":"Modal", "app_id":"ap-..."}`.
Multiple reservations bound to one app or multi-app parent envelopes fail closed.

A reviewed receipt is a JSON object with these required fields:

```json
{
  "schema": "modal-settlement/1",
  "request_id": "EXACT existing journal request_id",
  "app_id": "ap-EXACT-observed-app",
  "status": "completed",
  "containers": [],
  "completed_at": "ACTUAL aware ISO timestamp after reservation",
  "billing_read_at": "ACTUAL aware ISO timestamp after completion",
  "billing_final_verified": true,
  "reviewed_by": "ACTUAL reviewer identity / review receipt",
  "scene_log": "repository-relative reconciled cost_log receipt path",
  "scene_log_sha256": "SHA256 of unchanged cost_log bytes",
  "billing_report": "repository-relative saved Modal billing JSON array path",
  "billing_report_sha256": "SHA256 of unchanged billing report bytes"
}
```

`containers: []` must reflect actual stopped-container evidence; final billing
verification is a trusted reviewer decision, not something this code can infer
from an hourly report. `cost_log.reconcile` alone explicitly allows lagging or
still-accruing totals and is NOT sufficient. Keep the review/stop evidence with
the receipt. Do not set final verification merely to regain a slot.

The command verifies chronology, matching request/app, stopped/completed state,
explicit final verification and reviewer, stable source hashes, at least one
matching provider billing row, no duplicate environment/interval/resource rows, finite
nonnegative costs, and exact conservatively-rounded agreement with cost_log's
`cost.billed.status == billed` / `total_usd`. It rejects a bill lower than one
already observed. Missing or ambiguous billing, changed files and write failures
release nothing. A zero bill requires explicit matching zero-cost provider rows;
missing rows never mean zero.

Settlement preserves all request IDs, reservations, old ledger events and replay
protection. Only the two-job/$1 **outstanding** contract excludes settled rows.
Projection rechecks the immutable receipt and source hashes on every admission;
final billed USD (including overruns) remains counted against the gross monthly
$30 Modal cap and credit-floor calculation. Stale receipts remain a pause; no
automatic month/reset migration or new allocation is introduced.

## Additional critical verification fix

Fix3's parent pipeline and child standalone launcher both reserved the same job;
the child also required an amount environment variable the parent never passed.
Now the parent forwards its durable request ID. The child atomically consumes it
once under the same lock, revalidating current projected budgets/receipt before
dispatch. Invalid, missing, wrong-stage, stale, already-claimed or settled IDs
pause; no second slot/reservation, no unsigned bypass boolean. Segment propagates
the ID through a scoped ContextVar, reset even on call failure. Standalone callers
still require their explicit all-in bound and create/claim one reservation.
The five local mains also insert their repository root before importing Build's
guardrails package; file-based launchers no longer rely on an inherited PYTHONPATH.

N1/M3 remain pre-POST shared durable Meta reservation; all five requested Modal
entrypoint tails remain guarded. Source-level and real temporary-file/process
regressions are offline; no universal external/deployed-account cap is claimed.

## Remaining trust boundaries

No manual journal reset, clone copying or stale-lock auto-break. Trusted-state
editors can still tamper with the journal (R-C N3); no tamper anchor added.
Independent clones are not shared authorities (N5). Existing completed historical
JSON envelopes continue to count conservatively; they are not active journal
slots. Final review and immutable evidence must be preserved for released slots.
No live Meta, Modal, AWS, billing reconciliation, container stop or physical gate
was exercised. Further controller review, not this local receipt, accepts Gate C.
