# S05d-orch21 PLAN
Issued 2026-10-29T12:17:18+00:00; deadline 12:47:18+00:00; cutoff 12:42:18+00:00. anthropic/claude-opus-5-5/high; OpenCodex-managed, not polled.
Objective: per-clip floor plane fit + residual, gravity direction, metric scale with uncertainty from a source-backed known object, or explicit ABSTAIN with the exact missing reference, for RM02/RM04/RM05 MapAnything npz. CPU only.
Owns: Build/reconstruction/spike/; contracts/scene/; test-data/synthetic/scene/; evidence/S05/; Run-System/Runs/S05d-orch21/.
Checks: (1) synthetic unittest recovers plane/gravity and cited-reference scale, abstains without one; (2) real-run RESULT.json byte-identical on rerun; (3) floor-normal sensitivity across seeds/inlier bands.
