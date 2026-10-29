# S06f-orch25 PLAN

Objective (QUEUE S06f): exercise one licensed room clip on Modal; actual scene completes or failure evidence captured;
target <=5 min including cold start. Lane CODEX-1; anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled).
Base main ba5f668; branch run/S06f-orch25. Issued 2026-10-29T15:23:14+00:00; deadline 15:53:14+00:00;
minute-25 cutoff 15:48:14+00:00. Worker start 15:23:49Z.

Owns: Build/gpu/; infra/modal/; evidence/S06/; Run-System/Runs/S06f-orch25/.

Steps
1. Reuse accepted S06d/S06e scene_job.py unchanged; input RM04 (approved, Pexels, not RM02) 4 frames from the S05c
   manifest .worktrees/S05c-orch19/evidence/S05/S05c/input.json (SHA256-verified by load_frames; same frames S05c already
   ran on Modal; no new/personal media).
2. Ledger reservation (cap $0.50) + pre billing read; ONE A10G run, retries 0, documented uv command (+numpy +jsonschema).
3. Verify containers [] / app stopped; validate scene bundle; reconcile billed read-only with cost_log.py; check <=300 s.
Not claimed: Gate R, calibration, physical evidence.
