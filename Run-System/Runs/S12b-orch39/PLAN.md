# S12b-orch39 PLAN

Lane CODEX-1 · anthropic/claude-opus-5-5/high · issued 2026-10-29T21:13:53Z · deadline 21:43:53Z · cutoff 21:38:53Z.
Objective: transfer fitted parameters (g, speed, friction, restitution) into the existing simulator with provenance + 1σ uncertainty
retained; missing/abstained params refused (never defaulted). Gate M NOT_MET; image-height units only.
Owns: Build/real2sim/, tests/prediction/, evidence/S12/, Run-System/Runs/S12b-orch39/.
Reuse: boundary.fit_prefix (S12a), fitter jacobian_covariance, simulator runContactAwareTrajectory (RK4 + Rapier contacts).
Checks: unittest tests/prediction; module main on real ST03 (expected: abstain, fit withheld by S12a); worker_timebox check.
