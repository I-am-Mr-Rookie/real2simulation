# S20a — one spend/reservation and upload-quota contract (v1)

Status: **contract + offline accounting reference only**. This does not enable uploads,
approve media, reserve money, reconcile current billing or pass Gate C. S20b wires
admission/library behaviour; S20c wires disabled-by-default failover; S20d/R-C test/review it.
Authority: root `API_BUDGET.md`, `AGENTS.md`, approved plan S20, and `contracts/jobs/policy.json`.
Current direct owner decisions supersede historical budget prose, not the monetary limits below.

## 1. Existing sources, not a parallel spend database

| Source / existing writer | Projection into the shared accounting view |
|---|---|
| `Build/agent/record_muse.py` → `evidence/S14/S14b-ledger.jsonl` | `provider`, `reserved_usd`, `est_usd`, `billed_usd`; preserve RID, fixture, model, token counts and UTC. Existing `reserve()` computes a local estimate, not a global reservation. |
| `Build/pipeline/gpu_stages.py::reserve` → each run's `gpu-ledger.jsonl` | `stage`, `idempotency_key`, `reserved_usd`, `billed_usd`, UTC. Already appends before dispatch; its $1/2-job cap remains a subordinate run limit. |
| `evidence/S05/…/job-ledger.json`, `evidence/S06/…/job-ledger.json`, `evidence/S07/…/gpu-ledger.jsonl` | Retain outstanding all-in run reservations (`new_all_in_reservation_usd` where present), attempt/app identity and all child jobs. Different receipt layouts are projected, not rewritten or summed blindly. |
| `Build/gpu/cost_log.py::scene_log/reconcile` → scene cost receipts | `cost.upper_bound.total_usd` → conservative `est_usd`; `cost.billed.total_usd` → `billed_usd` only when available. Key by app ID and originating reservation; GPU/CPU/RAM/startup/idle/egress/storage are part of the same all-in liability. |
| `API_BUDGET.md` + sanitized provider reconciliation receipts | Confirmed historical total, coverage/watermark, verified credit evidence, authorization ceilings and price basis. A promotional allocation or rounded dashboard zero is not a balance/reconciliation. |
| `Build/pipeline/uploads.py::UploadService` + `contracts/jobs/policy.json` | Existing upload owner/session/job identifiers, expiry and file limits. Do not create a second upload store or bypass ownership validation. |

The **view is read-only/in-memory**, not another journal. Later integration must select
the complete set of canonical source ledgers explicitly: scanning just the current run,
omitting older paid runs or treating a missing/unreadable ledger as empty is unsafe.
The source inventory and its reconciled coverage must accompany every admission snapshot.
No new ledger with a zero starting balance may replace old costs.

### Identity, coverage and finality

- One logical provider request/attempt has one stable `request_id`, source reference,
  provider, RID, scene/job ID, purpose (`routine` or explicitly approved `demo`), UTC,
  price-source/date, all-in bound, estimate, nullable billed cost and reconciliation evidence.
  `request_id` is NOT merely scene ID: each paid retry has a distinct attempt identity.
- Project old Meta append-only rows as `source-relative-path#L<line>` (record file hash
  with snapshot). New reservations need a stable attempt ID **before** the call.
  GPU rows use the existing idempotency key plus stage/attempt; attach returned app ID.
- Multiple reserve/result/billing rows for one attempt are events, NOT multiple spends.
  Fold to one current row and reject duplicate/conflicting IDs rather than summing them.
  A provider bill matching an app/request replaces only that request's evidence.
  Never add a billing report total on top of the same per-request billed rows.
- History and request rows are disjoint. The historical receipt lists exactly which
  requests/period it covers; requests already included are excluded from the view.
  A wall-clock cutoff alone does not prove coverage when billing lags. Missing or
  ambiguous coverage, unknown historical cost or malformed data => pause, not zero.
- A run-level reserve that covers child jobs is **one envelope**: while unresolved,
  account `max(parent reservation, sum(child liabilities))`; do not add parent to children.
  Keep unrelated standalone job reservations separate. The reference helper consumes
  already-folded, nonoverlapping rows; it does not infer envelopes from heterogeneous files.
- `settled=true` requires explicit reconciliation evidence: exact final bill (including
  a verified zero), matched identity, resource stop and no remaining accrual/queued work.
  A stopped process, `release_suggested_usd`, billed amount alone, or cost-log `status=billed`
  is NOT enough. `cost_log.reconcile` itself warns that recent bills can still accrue.

## 2. Money and protected reserve

USD only; accept finite nonnegative numbers/decimal strings, never booleans, NaN,
infinity, negative values or unknown-as-zero. `accounting.py` uses standard-library
Decimal and rounds **up** to 8 decimal places, matching GPU receipt precision.
Do not sum token counts as USD. No provider credits or coding subscriptions are fungible.

For each unresolved request:

`liability = max(conservative all-in reservation, latest estimate, provisional billed cost)`

The reservation is mandatory; a lower measured estimate or partial bill cannot release it.
For a finally reconciled request: `liability = final billed USD` (including cost overruns).
Every present monetary field is validated even if another field would dominate it.

### Meta envelope — acceptance oracle

```
committed = confirmed_disjoint_historical_USD + sum(current_request_liabilities)
projected = committed + worst_case_new_request_USD
routine cap permits only projected < 120 USD
allocation = 150 USD; protected demo reserve = 30 USD
```

Thus **at** $120, not merely above it, routine admission stops. History, pending
calls, timed-out/failed calls, retries, conservative unbilled estimates and provisional
bills all count. The candidate is not yet in the view; if already reserved, pass zero
and reuse the same attempt rather than counting/reserving twice.
All Meta usage counts toward the cumulative routine threshold, including any earlier
demo usage; relabelling purpose cannot unlock routine spending.
Routine work cannot borrow the $30 reserve or treat the $150 allocation as its cap.
Demo spending requires separate explicit purpose/owner authority, a known available
balance and total commitment within $150; the reference helper does NOT authorize it.

`meta_snapshot(history, requests, candidate)` returns Decimal accounting and
`routine_cap_allows`, a **necessary arithmetic condition only**. Requests must be
unique Meta-only rows with `request_id`, `provider="Meta Model API"` and the existing
cost fields. Unknown history raises ValueError even for an empty request list.
No caller may turn that exception into permission.

Live admission additionally requires fresh verified applicable credits, reconciled
coverage and affordable pending liabilities + candidate, valid price/resource bounds,
unchanged owner/media authority and the atomic reservation below. Unknown/insufficient
credit => pause. Never use a billing alert as a cap or infer live readiness from this helper.

### Other providers — independent envelopes

- **Modal:** $30 monthly authorized ceiling, no paid overage. A $100 persistent grant
  or $130 displayed credit does not raise this ceiling. Reserve against verified
  applicable credit/headroom and the stricter monthly/run/job limits. Do not assume
  the reset instant or automatically discard unresolved reservations on Nov1; reconcile
  their billing period against provider evidence first. Below $5 remaining while AWS
  is unavailable, pause new reconstructions; library stays accessible. No idle burn.
- **AWS:** $50/month EC2 gross budget, us-east-2, spot batch only, session shutdown.
  A budget alert is not a spending cap. Include CPU/GPU, boot, storage, transfer and
  interruption/retry bounds. Region/quota/credit/price evidence and local bounded-job
  headroom are still needed. Documented owner quota and budget receipts can be reused;
  do not invent a per-job consent gate. Failover stays OFF until S20c integration
  explicitly validates all gates (see `infra/failover/CONTRACT.md`).
- Baseten/Fireworks and other paid routes have no new spend authority from S20a.
  Unknown provider budgets fail closed. Never automatically swap provider on a cap breach.

## 3. Reservation lifecycle — integration obligation, not implemented here

1. Authenticate/authorize user and validate input/licence. Determine stable scene/job,
   attempt and idempotency IDs, provider, purpose and conservative all-in bound.
   Include bounded allowed retries (existing job policy), cold start/setup, queue/wall
   deadline, shutdown/idle tails and transfer/storage. Unknown unbounded components refuse.
2. Under **one cross-process/global serialization boundary** over the canonical
   source set: read validated coverage + latest costs + pending reservations, check
   provider/global/run caps + credit and quota, then durably append reservation **before**
   any paid dispatch. Compare/check/write must be atomic; atomic file replacement alone
   is not a global lock. One writer is acceptable until a transactional shared store exists.
3. Only after reservation succeeds dispatch exactly that bounded attempt. An idempotent
   retry of admission returns the existing attempt without another charge/quota slot;
   another paid attempt requires its own reserve. `SPEND_PAUSED` is nonretryable per
   existing `contracts/jobs/policy.json`. Never dispatch on lock/storage/write failure.
4. Attach provider request/app ID and measured estimate/bill to the original reservation.
   Crash, timeout, cancellation, HTTP failure, missing usage or ambiguous stop keeps
   the full reserve outstanding. Recover from source evidence, not a zeroed new ledger.
5. Release only the excess after explicit final reconciliation. A verified never-dispatched
   attempt may reconcile to zero. Overruns are counted even above cap and pause new
   work; do not clamp bills to the original reserve. Preserve audit evidence, no deletion.

**Known owning-source gaps:** Meta recorder writes its ledger after the response and
its local guard sums estimates; GPU reservation read/check/append is not cross-process
atomic; old GPU bills may be provisional. These are not fixed by importing the pure
reference. S20b must wire a serialized guard at every paid boundary (including CLI
entry points or explicitly disable unsupported live paths); no runtime-cap claim until
that is verified. Caller edits outside this run's Owns require controller integration.

## 4. Per-user upload quota and library exemption

Contract decision (routine reversible default, **not an owner-provided capacity fact**):
**1 newly accepted reconstruction upload per authenticated user per UTC calendar day**.
S20b may expose a validated positive-integer operator setting; invalid/missing state
must pause admissions, not imply unlimited quota. No client-controlled cap or user key.

- Key = server-verified existing owner ID + `YYYY-MM-DD` UTC, not email/IP or local
  Dhaka/browser date. Reset at 00:00 UTC. Use server time. Do not log credentials or media.
- Count the session accepted by `UploadService.create`, once, before storing bytes;
  reject unauthorized/invalid/paused requests before consuming a slot. Keep existing
  100 MiB file, 60 s duration, 8 MiB chunks, MIME and 24 h session expiry policy;
  daily quota does not replace size, ownership or licence checks.
- Session resume/chunk retry, same idempotency key, processing-stage retries and
  midnight continuation do not consume a second slot. Charge the creation UTC day.
  New accepted session consumes another slot even if previous work later fails/expires;
  do not refund automatically and permit a paid retry loop. Reservation release is separate.
- Quota check+consume is durable and serialized with admission. Counter missing,
  corrupted, unavailable or inconsistent with upload metadata => fail closed. No
  persistence design is added in S20a; reuse upload/session store during S20b integration.
- Any exhausted quota, global/provider cap, unknown cost/credit or kill switch pauses
  **new reconstruction uploads**, not guest GET/library/viewer/precomputed simulation.
  Existing library access neither consumes quota nor triggers paid recomputation.
  Already-reserved bounded attempts may complete safely; do not leave idle GPU resources.
- S20b must keep the paid reconstruction boundary distinct from public library routes;
  S20d must test cap breach + exhausted quota + unknown ledger while guest library works.

## 5. Handoff checks

Offline reference: `python -m unittest discover -s tests/guardrails -v`.
Test values are synthetic accounting cases, not current balances or physical evidence.
S20b: serialized provider reservations + upload quota/library route integration and crash/
concurrency/idempotency tests. S20c: default-off switch + actual gate evidence. R-C/S20d:
independent cap/library regression. No network calls or dependency installs are needed here.
