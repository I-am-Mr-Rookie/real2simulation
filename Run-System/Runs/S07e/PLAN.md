# S07e plan

Start: 2026-10-28 08:21 UTC (approximate first instruction read; first exact
retained clock 08:25:14 UTC). Implementation cutoff 08:46; stop 08:51 UTC.
CODEX-1 requested gpt-6.1-sol/high; backend identity unobservable.
Base 971b9f48576d923785cc6ded438662b32dd0a0ab; new run/S07e, unmerged.

Objective: reproducible actual-source Gate M evaluation, including honest
insufficient-input acceptance; unchanged 2/3 within 5%, with honest uncertainty.

Owns ONLY Build/measurement/gate_m.py, Build/measurement/GATE_M.md,
tests/measurement/test_gate_m.py, evidence/S07/S07e/, Run-System/Runs/S07e/.
No canonical/control/input/approval/schema writes. No fanout, external calls,
runtime/media processing, secrets, GPU, fallback enactment or S12 unlock.

1. Inspect current accepted sources, approvals and frozen measurement modules.
2. RED synthetic evaluator regressions; smallest stdlib evaluator reusing fitter,
   validator and uncertainty. Reject approval-string self-authorization.
3. GREEN full measurement suite; actual-source artifact with SHA256 receipts,
   actual counts, abstentions and null absent measurements. Reproduce bytewise.
4. Record limitations, required R-M/S07f handoff, scope audit; scoped commit.

Ponytail full: reuse frozen functions and synthetic test helpers, no dependencies
or new schema/platform. Systematic debugging: trace failures before corrections.
