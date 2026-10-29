# S20b — offline reconstruction admission guard

`admission.require_reconstruction(path, candidate_modal_usd=..., candidate_meta_usd=0)`
returns Decimal accounting or raises `ReconstructionPaused` (`code=SPEND_PAUSED`,
`retryable=False`). No exception may be converted to permission. This is a guard
ready for caller integration, **not deployed/live enforcement**.

## Decisions

- Meta: S20a confirmed disjoint history + request liabilities + candidate must be
  strictly below $120, including when this reconstruction adds no Meta calls.
- Modal: same conservative liabilities, independent $30 authorized ceiling.
  Projected authorized AND credit headroom must remain at least $5. This is the
  conservative default while S20c AWS failover remains OFF; no automatic provider swap.
- Verified available credit must cover the candidate. Displayed allocations and
  billing alerts are not verified headroom. Missing/corrupt/unreadable/unsupported,
  paused, unverified, future or older-than-five-minute snapshots pause new work.
  Five minutes is a reversible local freshness default, not a provider guarantee.
- A new paid attempt needs a strictly positive all-in Modal bound; zero/unknown
  cannot bypass admission. Existing already-reserved attempts are recovered by
  their existing identity, not submitted as new zero-cost admissions.
- Final reconciliation can release only that request's reservation; caller must
  attach a nonempty `reconciliation_ref` and actually validate that final evidence.

## Snapshot boundary

Server-owned JSON, schema `reconstruction-admission/1`. Never accept this snapshot,
its amounts, flags or source references from the upload request/browser.

```json
{
  "schema": "reconstruction-admission/1",
  "as_of": "2026-10-29T22:10:00+00:00",
  "paused": false,
  "coverage_verified": true,
  "credit_verified": true,
  "sources": ["SYNTHETIC history receipt", "SYNTHETIC pending ledger"],
  "Meta Model API": {
    "historical_usd": "110", "requests": [], "credit_headroom_usd": "40"
  },
  "Modal": {
    "historical_usd": "1", "requests": [], "credit_headroom_usd": "29"
  }
}
```

**Synthetic illustration, not current balances.** `requests` uses S20a existing
`request_id`, `provider`, `reserved_usd`, `est_usd`, nullable `billed_usd`, `settled`
fields. Providers must match exactly; duplicate request IDs within a provider pause.
Project existing gpu-ledger `idempotency_key` + stage/attempt to `request_id`;
project scene-log `cost.upper_bound.total_usd` to `est_usd`. Keep the reservation
despite lower/provisional billing. Fold run envelopes/events before calling this
guard; do not add a parent envelope to its own child reservations.

`historical_usd` must be known and disjoint from request rows. `credit_headroom_usd`
is fresh verified applicable credit **net of all outstanding liabilities**; it is
not a gross credit display or a second spend total. The caller verifies inventory
completeness, source hashes/coverage, period, receipt finality and actual headroom
before setting the flags/as_of. The guard validates their shape, not their truth.
No reconciler or second authoritative ledger is introduced by this run.

## One owning paid-boundary integration finding

**`Build/pipeline/gpu_stages.py::reserve` (currently line 39)** is shared by both
segment and reconstruct. Under a single global cross-process serialization
boundary: load/reconcile canonical state, call this guard with this attempt's
all-in bound, enforce existing run/job limits, durably reserve BEFORE dispatch,
then publish updated snapshot coverage. On `ReconstructionPaused`, map to existing
`StageError(exc.code, str(exc), exc.retryable)`. Storage/lock failure must pause.
Never just import the helper and leave check/read/append racing. Recheck state
at each new paid attempt; aggregate any upload envelope without double charging.

The upload owner must invoke the same preflight before accepting a new session/
bytes and map failure to existing `UploadError("SPEND_PAUSED", ...)`. No HTTP upload
route exists in this checkout; durable user/day quota remains separate future work.
Existing CLI/other paid entry points are NOT protected merely by this helper.

No pipeline/web edits were authorized. Controller integrates those boundaries;
until then this run must not be described as a live global cap or quota gate.

## Library exemption and verification scope

Guest GET/library/viewer/precomputed asset reads **never call admission**, never
read its snapshot and never consume a reservation. Keep the public route separate
from all reconstruction guards; do not add a global middleware kill switch.
Existing `Build/web/src/app/(public)/library/page.jsx` is an import-free static
guest page saying no demos are published. No scene playback is connected there.

Offline tests show cap breach pauses before existing upload-store/reservation
side effects in a harness; missing/corrupt state also pauses. The existing public-library DTO and SYNTHETIC precomputed
manifest can still be read with the guard patched to fail if called. They also
check the real library page has no guard/dependency import. This is exemption
evidence, **not live HTTP, published demo or physical-scene success**.
`evidence/S20/S20b/render-library.mjs` additionally renders the real static empty
guest component using already-installed Next SWC/React. This is component rendering,
not connected precomputed playback.

Run: `python -m unittest discover -s tests/guardrails -v`.
