# S20-fix4-orch87

CODEX-2 / S20; assigned gpt-6.1-sol/high; OpenCodex-managed; not polled.
Parent project: 91e441f8-e40c-4ec4-bea2-de7fa1582d97.
Issued 2026-10-30T06:17:59+00:00; cutoff 06:42:59Z; deadline 06:47:59Z (12:47:59 Dhaka).
Base main e72338c; worktree .worktrees/S20-fix4-orch87, branch run/S20-fix4-orch87.

Objective: critically verify timing-rejected fix3, close N4 with reviewed final-billing
settlement, and rerun all six requested offline checks. Fix3 cherry-picked as 83e9431,
ee2c941; its PARTIAL/timing FAIL report remains historical, not accepted evidence.

Owns: Build/guardrails/; Build/pipeline/{understand.py,gpu_stages.py};
Build/agent/record_muse.py; Build/gpu/{scene_job.py,runtime.py,cost_log.py};
Build/measurement/runtime/modal_track.py; Build/reconstruction/spike/;
tests/{guardrails/,pipeline/,agent/test_muse.py,measurement/test_modal_track.py};
evidence/S20/; Run-System/Runs/S20-fix4-orch87/.

Reach: shared journal projection/reservation, settlement evidence validation, five
standalone launch tails, pipeline callers, offline temporary-state regressions.
Reuse existing lock/durable replacement, cost accounting and journal; no new dependencies.
Preserve request IDs/replay protection and monthly spend; fail closed on unknown costs.
No canonical control writes, real journal changes, network, spend, installs or deployment.
Canonical journal inspection is read-only. Commit named files only; controller integrates.
