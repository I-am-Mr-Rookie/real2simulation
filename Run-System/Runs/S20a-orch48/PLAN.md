# S20a-orch48 — spend, reservation and upload-quota contract

- Objective: define one contract over existing ledgers; prove Meta accounting includes historical usage, pending requests and conservative unbilled estimates. This is S20a, not live Gate C enforcement.
- Parent: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; source controller `01a1882d-3481-7ce3-8f88-45c942e341cd`.
- CODEX-2; assigned gpt-6.1-sol/medium; OpenCodex-managed; not polled. Exact runtime identity/tokens/task dollars unobservable.
- Base main `7fbf29f`; branch `run/S20a-orch48`; isolated `.worktrees/S20a-orch48`. Canonical controls are controller-owned; no merge/push by worker.
- Issued 2026-10-29T21:52:08+00:00; implementation cutoff 22:17:08+00:00; deadline 22:22:08+00:00 (Oct30 04:22:08 Dhaka).
- Owns: `Build/guardrails/`, `infra/failover/`, `tests/guardrails/`, `evidence/S20/`, `Run-System/Runs/S20a-orch48/` only.

## Smallest complete change / impact map

Read/apply Ponytail full. Reuse `Build/agent/record_muse.py` ledger fields/reservation estimates, `Build/pipeline/gpu_stages.py` pre-dispatch JSONL reservations, `Build/gpu/cost_log.py` estimated/upper-bound/billed receipts, existing upload DTO/policy and API_BUDGET limits. No new persistence or dependency. Pure standard-library accounting reference plus contract documentation and offline boundary tests. Existing callers stay unchanged; integration, storage locking and library exemption enforcement belong to S20b. AWS switch implementation belongs to S20c.

Changes reach only new contract, its tests, failover handoff and evidence. No source ledger is rewritten; no history, private input or secret is copied. A pure snapshot is not a live spend lock. Unknown history must fail closed, provisional bills must not release reservations, and source coverage must avoid double counting.

## Acceptance / checks

1. Contract names authoritative ledgers, identity/coverage/reconciliation rules, atomic reserve lifecycle, $120 routine stop + protected $30 demo reserve, independent Modal/AWS limits, per-user UTC-day quota and library exemption.
2. Offline tests prove historical + pending + conservative estimates, strict threshold, invalid/unknown money, no double counting and final-vs-provisional billing behaviour.
3. Fresh adjacent cost-log/pipeline regression where available; saved evidence; scoped diff; TIMEBOX validator; commit with forced staging of ignored Owns.

Budget: no network, inference, GPU, uploads, deployment, installs or other spend. Historical balances are not reverified. Full window used if incomplete; fully verified DONE may finish early.
