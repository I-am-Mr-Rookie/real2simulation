# S20b-orch51 — reconstruction cap / library exemption

- Parent project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97` (controller contract; no new chat created).
- CODEX-2; assigned gpt-6.1-sol/medium; OpenCodex-managed; not polled.
- Issued 2026-10-29T22:04:09+00:00; cutoff 22:29:09Z; deadline 22:34:09Z (04:34:09 Dhaka).
- Base main c19fbf793284450931f39d929719be1ff74af615; branch run/S20b-orch51.
- Owns: Build/guardrails/; infra/failover/; tests/guardrails/; evidence/S20/; this run directory. No canonical control edits or merge.

## Smallest complete scoped objective

Implement an offline fail-closed admission guard using S20a Decimal accounting,
existing reservation/cost receipt fields and SPEND_PAUSED semantics. Test strict
Meta routine cap, Modal ceiling/credit floor, missing/corrupt/stale state and a
guest-library read independent of admission. Save evidence and exact caller handoff.

## Reach / risks before writing

New guard + tests + contract documentation only. Existing gpu_stages.reserve callers
are reconstruct and segment; integrate at their shared reservation boundary later,
and preflight uploads before accepting bytes. Existing library/page.jsx is a static
guest page with no published scenes; leave it unchanged and never invoke admission
from it. No current live-cap or actual precomputed-playback claim is possible.
Snapshot reconciliation, atomic check/reserve, upload quota persistence and paid
boundary wiring are outside the explicitly narrowed controller contract.

Use no new dependency, ledger, provider route, API or configuration; reuse accounting.
Checks: guardrails unit suite; unchanged GPU cost-log and pipeline suites; scoped
diff/whitespace; worker_timebox validator. Offline only; no spend.
