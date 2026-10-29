# S06a-orch19 PLAN

Issue 2026-10-29T11:47:42Z; deadline 12:17:42Z (Dhaka 18:17:42); cutoff 12:12:42Z. Worker start 11:48:40Z.
Lane CODEX-1, model anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Base main 526ec0c.

Objective: reproducible pinned MapAnything Modal GPU image (prebuilt deps + baked Apache weights) and a CPU/dry-run contract,
so later jobs (S05c/S06b-d) skip the ~155s per-container pip+weights setup measured in S05b-orch14.

Owns: Build/gpu/; infra/modal/; evidence/S06/; Run-System/Runs/S06a-orch19/. Build/reconstruction/spike/ referenced read-only.

Steps: (1) Build/gpu/image_spec.py offline dry run + unit test; (2) Build/gpu/modal_image.py image definition + CPU check;
(3) one CPU-only Modal image build + check (<= $0.50, retries 0, ledger, stop + containers []); (4) infra/modal/README.md contract; REPORT.
