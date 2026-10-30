# S20c failover selector — OFF by default, offline plans only

The single accounting authority is `Build/guardrails/CONTRACT.md`; do not create
an AWS-specific parallel ledger or treat a provider swap as fresh headroom.

`Build/guardrails/failover.py::select_provider` implements the switch. Default
provider remains Modal; AWS selection requires `R2S_ENABLE_AWS` exactly `"1"`.
It reuses unchanged `Build/gpu/aws_adapter.py::activate`, not a competing launcher.
There is no automatic selection on quota/cap/auth/runtime failure. A requested
AWS plan failing any gate raises nonretryable `SPEND_PAUSED`, not Modal fallback.

Current root AGENTS/API_BUDGET receipts record us-east-2 G/VT spot 8-vCPU approval
and a $50 EC2 budget; on-demand remains zero/pending. These are authority/config
receipts, not evidence that this run launched an instance or reverified live credits.
Do not ask for the same approval again; validate actual applicable quota, region,
spot-only selection, budget receipt, available credit, bounded all-in cost and stop
before an authorized future session. No account/policy/terms/billing changes here.

AWS must refuse wrong region, on-demand, missing/stale/malformed gate evidence,
unknown headroom and an unbounded session. Stop every session, including failures.
The $50 gross budget alert is not a hard spend cap or authorization to exceed credits.
Failover cannot replace or refill the independent Meta $120 routine/$30 reserve envelope.

## Caller contract

```python
from Build.guardrails.failover import select_provider

# Server-owned paths, verified all-in estimates and reconciled snapshot only.
# With no environment flag, this returns an admitted Modal plan, not a launch.
plan = select_provider(state_path, candidate_modal_usd="1", candidate_meta_usd="0")

# Only with R2S_ENABLE_AWS=1, BOTH explicit receipt paths, fresh headroom and
# passing S20b admission does this return an AWS spot plan. No env writes here.
plan = select_provider(
    state_path, candidate_modal_usd="1", candidate_meta_usd="0",
    quota_receipt_path=quota_path, budget_receipt_path=budget_path,
    candidate_aws_usd="2", max_session_seconds=600,
)
```

Amounts above are **synthetic illustrations, not live prices, balances or approval**.
Result fields: `provider` (Modal/AWS), unchanged S20b `admission`, `launched=False`,
and `aws` (None, or region/instance/market/all_in_usd/max_session_seconds/stop_on_exit).
No enable flag is persisted and no cloud call is made. AWS selection now has a
deliberate local side effect: it durably reserves its bound before returning the
plan, with `aws.reservation_id`. Repeating selection is a NEW liability, not a
read-only quote or permission to reuse stale headroom. Modal-only selection stays
a read-only preflight (the pipeline reserves at its own paid boundary).

AWS requires an `AWS` bucket in the shared admission snapshot with `historical_usd`,
`requests` and verified net `credit_headroom_usd`. Under the SAME canonical
`evidence/S20/runtime/admission.lock` as pipeline GPU reservations, the selector
projects existing sources and the pre-existing `reservations.json`, rechecks S20b,
checks $50 gross/AWS credits/budget receipt headroom net of outstanding journal
liabilities, and atomically reserves AWS (and any Meta candidate). Missing state
pauses; no automatic empty-journal creation. See `Build/guardrails/ADMISSION.md`.
Conservative receipt debits may over-reserve until explicit reconciliation, never
release money based on a lagging AWS Budgets alert. Unknown top-level keys pause.

S20b is called first for **both** providers. Meta history/pending/candidate and
Modal cap/credit/$5 floor remain unchanged. This deliberately conservative selector
does NOT unlock AWS when Modal's floor/cap has already paused reconstruction.
Provider-aware relief would require a separately reviewed S20b accounting change;
this switch is not permission to bypass it. Existing approvals are not requested again.

## Explicit receipt schemas

Two readable local JSON paths are mandatory only when AWS is selected. Receipts
are server-owned evidence, not upload/browser inputs. Reject duplicate JSON keys,
missing/wrong schema, unapproved receipts, wrong region, naive/future/stale timestamps
(same five-minute freshness limit as S20b), invalid values and insufficient headroom.
Refresh observed facts without inventing a new owner consent gate. `owner_approved`
records the existing owner decision; `as_of` records fresh verification, not approval time.

Quota receipt (`aws-quota-receipt/1`):
- `as_of`: timezone-aware ISO timestamp; `owner_approved`: true.
- `region`: `us-east-2`; `market`: `spot` (on-demand always refused).
- `quota_code`: `L-3819A6DF`; `spot_quota_vcpu`: integer >=4 for g6e.xlarge.

Budget receipt (`aws-budget-receipt/1`):
- `as_of`, `owner_approved`, `region`: same checks as quota receipt.
- `budget`: `name="Real2Sim EC2 50 USD"`, `amount_usd=50`, `currency="USD"`,
  `period="MONTHLY"`, `gross=true`; `services`/`alerts` lists must include all
  existing AWS adapter EC2-Compute/EC2-Other filters and actual50/80/100 + forecast100.
- `coverage_verified=true`, `credit_verified=true`: caller has freshly reconciled
  the **shared** source inventory, all outstanding AWS liabilities and applicable credits.
- `remaining_gross_usd`: $50 minus shared-ledger reconciled gross commitments,
  within [0,50]; `credit_headroom_usd`: applicable credit net of outstanding liabilities.
  Both must be known finite nonnegative amounts with at most eight decimal places;
  neither is rounded up into spending permission. This receipt is a projection,
  **not a second AWS ledger**; its flags do not prove its contents true.

`candidate_aws_usd` is a positive conservative all-in bound (rounded UP by existing
S20a `usd`), <= both headrooms. Include compute/boot/storage/transfer/interruption
and any retries; flags and budget alerts alone do not bound charges. Session limit
is an integer in [1,3600] seconds (local conservative maximum); the returned plan
requires `stop_on_exit=True`. These are preflight constraints, not an implemented watchdog.

## Integration boundary / unchanged behavior

The pipeline now globally reserves Modal work (ADMISSION.md); no pipeline/upload
AWS dispatch call site or termination watchdog is added here. Before real dispatch
the controller must validate receipt provenance and enforce all-in limits plus
guaranteed shutdown on success/failure. An AWS plan reserves locally but does not
establish cloud health, implement termination or authorize a launch by itself.
Fresh live credit/price/quota/headroom
and bounded-job/shutdown evidence remain mandatory at that boundary.

No AWS configuration, environment variable, cloud resource or existing adapter
changed. No SDK/API calls, installs or live resources in this run. The existing
shared runtime journal records the new local reservation.
