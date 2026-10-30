# S20-fix2-orch65

- Objective: finish offline R-C H1/H2/M1/M2/L2 fixes from rejected ad99589 WIP.
- Assigned CODEX-2 / gpt-6.1-sol high; OpenCodex-managed; not polled.
- Parent project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97` (delegation contract); canonical root `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`.
- Branch `run/S20-fix2-orch65`, started from `run/S20-fix-orch63`, rebased onto main dbdc059.
- Issue 2026-10-30T05:00:36Z; implementation cutoff 05:25:36Z; deadline 05:30:36Z (11:30:36 Dhaka).
- Owns: Build/guardrails/, infra/failover/, tests/guardrails/, evidence/S20/, Build/pipeline/gpu_stages.py, tests/pipeline/test_gpu_stages.py, this run directory. No canonical controls/merge.
- Reach: GPU reserve caller (segment/reconstruct), admission/accounting/projection, AWS selector, pipeline and guardrail fixtures/regressions, runtime documentation. Risk: outstanding reservations intentionally block retry and survive failed dispatch; unknown/corrupt inventory must pause, never become zero.
- Checks: full pipeline + guardrails unittest suites; G1/G3/C1/X1/R1/A15 regressions; real on-disk inventory projection; timing check, diff check, named-file commit.
- Ponytail full: retain existing accounting/admission and stdlib O_EXCL/atomic JSON, no dependencies; trim unneeded layers. No live calls/spend, bootstrap of live balances, agent edits (M3 deferred), installs, deployment, or publication.
