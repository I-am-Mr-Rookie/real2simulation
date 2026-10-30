# S12f-orch97 PLAN

- Task: QUEUE S12f — label prediction outputs; choose honest prediction fallback from ACCEPTED Gate RS result.
- Lane/model: CODEX-1, anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Parent project 91e441f8-e40c-4ec4-bea2-de7fa1582d97.
- Issued 2026-10-30T06:49:37+00:00; deadline 07:19:37Z; cutoff 07:14:37Z. Branch run/S12f-orch97 from main 83143a8.
- Objective: code-owned decision (<=5% shown; 5-10% shown with measured error; >10% or unmeasured -> virtual lab only) computed from re-scored gate-rs.json; explicit measured/simulated/SCALE_UNVERIFIED/SYNTHETIC labels per output; threshold test; fallback JSON + review packet.
- Owns: Build/real2sim/fallback.py; tests/prediction/test_fallback.py; evidence/S12/S12f-fallback.json; evidence/S12/S12f-REVIEW-PACKET.md; Run-System/Runs/S12f-orch97/.
- Checks: python -B -m unittest discover -s tests/prediction; python -B -m Build.real2sim.fallback; worker_timebox check.
