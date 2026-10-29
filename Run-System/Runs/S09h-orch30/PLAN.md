# S09h-orch30 PLAN

- Lane/model: CLAUDE, anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Parent project 91e441f8-e40c-4ec4-bea2-de7fa1582d97.
- Issued 2026-10-29T15:42:54+00:00; deadline 16:12:54Z (Dhaka 22:12:54); cutoff 16:07:54Z. Base main 90d6f45.
- Objective: load three real scene bundles (RM02, RM04, RM05) through the existing viewer with a scale-UNVERIFIED label; verify in tests + IAB (desktop, 375 px).
- Owns: Build/web/src/viewer/; tests/viewer/; evidence/S09/; Run-System/Runs/S09h-orch30/.
- Approach (Ponytail): reuse Build/gpu/scene_job.py --npz offline (CPU) for all three bundles; reuse createArtifactLoader/adapter/three viewer unchanged; one banner constant + one ternary.
- Checks: node --test tests/viewer; browser-smoke.mjs regression; IAB visual at 1280 and 375 px.
