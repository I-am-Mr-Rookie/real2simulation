# R-C N1 / M3 / N2: offline integration receipt

Meta live transports now reserve under the same canonical `admission.lock` as GPU/AWS.
`reserve_meta` projects all inventoried liabilities plus the durable journal, validates the
fresh server-owned receipt, applies the existing strict routine `< $120` stop (protecting
the $30 demo reserve), credit headroom, and global per-stage contract count/dollar caps.
It fsyncs the global row and local row BEFORE POST. The result uses the same request ID;
lower estimates do not release reserves, transport/append failures retain debt.
Fresh caller ledger paths cannot reset global accounting. Pure `understand.reserve` is
still a local cost calculator/precheck, NOT transport authorization; `live_post` is the boundary.

## Standalone Modal invocation

All five requested mains call `Build.guardrails.standalone.admit_standalone` before
`remote` or `guarded_probe` dispatch. It reuses `reserve_gpu`, the SAME two-job/$1
pipeline envelope, $30 gross Modal cap and $5 credit floor; no separate allocation.
An operator must set `S20_MODAL_RESERVATION_USD` to the **reviewed conservative all-in
bound for the complete invocation** (startup, CPU/GPU, retries, shutdown and transfer).
Missing, malformed, nonpositive, over-cap or unsupported state pauses. This is not a
price estimator and does not expand existing input, runtime, budget or stop approvals.
Use repository root on PYTHONPATH for file-based Modal/watchdog launchers.
The shared ledger is canonical `evidence/S20/runtime/standalone-gpu-ledger.jsonl`.
No live state was initialized by this fix. Missing state remains a hard pause.

Modal CLI can create its app context before invoking a local entrypoint: this integration
guards paid function dispatch, not arbitrary CLI framework initialization or separately
deployed/external remote-function callers. No universal cloud-account billing cap claimed.

## P3 decisions / reconciliation (N3–N5)

- N3: do not reset, delete, truncate, replace or copy an empty journal to regain capacity.
  Server-owned state remains a trusted-write boundary; no tamper-evident anchor added.
- N4: no automatic release added. Two lifetime pipeline/standalone jobs/$1 remains a
  deliberate fail-closed availability limit. Before any future release mechanism:
  reconcile final bills/app IDs and stopped containers for EVERY request; preserve
  immutable old rows and source hashes; have the controller review an explicit new
  contract/envelope and tested migration. A lower estimate or `settled` flag alone is
  NOT permission to clear the journal/count or re-admit. No release performed here.
- N5: linked worktrees share canonical state. Independent clones are not authorized
  alternate spend authorities. Lock contention/crashed locks pause without retries or
  automatic break. Controller must verify owner/process/cloud stop before any manual
  lock removal; never infer that a PID-only lock is safe to break.

Tests use temporary runtime receipts/journals and synthetic credentials; transports mocked.
The original R-C probe intentionally demonstrates the pure local `reserve` calculator
and journal tampering; it is retained unchanged as review evidence, not a live-POST proof.
New `tests/guardrails/test_live_admission.py` exercises the actual transport boundaries,
cross-process exclusion, persistence ordering and five entrypoint admission tails offline.
