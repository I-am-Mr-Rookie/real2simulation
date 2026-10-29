# S06g-orch30 PLAN
Objective: verify CPU dry-run works without GPU; add AWS adapter that is off by default and refuses activation unless region/spot/quota/budget gates pass.
Owns: Build/gpu/; infra/modal/; evidence/S06/; Run-System/Runs/S06g-orch30/.
Model: anthropic/claude-opus-5-5 medium (OpenCodex-managed; not polled). Issued 2026-10-29T15:41:54Z, deadline 16:11:54Z, cutoff 16:06:54Z.
Approach (Ponytail): reuse image_spec.dry_run as the CPU dry-run; copy sam3d_option.gate pattern (env flag + reasons list) for AWS; no boto3, no launcher.
Checks: unittest discover Build/gpu; image_spec.py rc=0; aws_adapter.py receipt; worker_timebox.py check.

