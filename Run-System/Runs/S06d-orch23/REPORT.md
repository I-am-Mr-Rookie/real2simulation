# S06d-orch23 REPORT — DONE

Lane CODEX-1; model anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). UTC start 2026-10-29T14:33:07Z,
end 2026-10-29T14:50:27+00:00 (deadline 15:02:31Z). Base main f37121c; branch run/S06d-orch23 (not merged; controller integrates).

## Result
- New Build/gpu/scene_job.py: approved scene id -> SHA256-verified frames -> A10G scene_job on S06b RUNTIME_IMAGE
  (load_model, pinned Apache weights, offline cache) -> npz -> contracts/scene bundle, validated by validate_scene
  before returning. Offline mode converts an existing MapAnything npz without Modal.
- One real-scene artifact validated twice: RM02 offline (existing S05b recovery8 npz) and RM02 via ONE Modal A10G
  job: PASS rm02-mapanything-s06d schema=1.0.0 synthetic=False (evidence/S06/S06d/validate.txt).
- GPU job ap-DwCMDeReYWQYBxl3xvR2IO: rc 0, function 20.96 s, client 14:46:02->14:47:21Z, peak 7.78 GB,
  image not rebuilt, billed $0.0066139 (hourly CSV, may lag) vs cap $0.30; retries 0; container list empty and app
  stopped/0 tasks after (post-verify.txt). Ledger: evidence/S06/S06d/job-ledger.json.

## Files
Build/gpu/scene_job.py, Build/gpu/test_scene_job.py, infra/modal/README.md (S06d section),
evidence/S06/S06d/{.gitignore, job-ledger.json, run-log.txt, post-verify.txt, billing-pre/post-today-hourly.csv,
tests.txt, validate.txt, scene-RM02-gpu.json, scene-RM02-offline.json}. Bundle media (PLY colours from licensed
frames, npz) kept in gitignored evidence/S06/S06d/local/ — no raw-media redistribution. The committed scene-*.json
copies are manifests only; validate them in local/RM02*/ where their assets are.

## Checks (fresh)
- python -m unittest discover -s Build/gpu: 16 OK (3 new: synthetic-array bundle validates, axis/quaternion, unapproved ids refused).
- python -m unittest discover -s contracts/scene: 11 OK. python Build/gpu/image_spec.py: rc 0 (pins unchanged).
- validate_scene.py on both bundles: PASS. Points lie at z<0 (in front of -Z camera) — axis conversion sane.

## Ponytail (applied, full)
- Reuse: RUNTIME_IMAGE + load_model (S06b), image_spec pins (S06a), validate_scene (contracts/scene), S05c
  infer() kwargs, S05 npz key layout, S05d confidence-half filter, clips.csv + APPROVAL.md ids, S06b uv/modal 1.6.3
  and billing/container-check procedure. No new deps, no image layer change (python-source mount only).
- Smallest complete: one file + one test; empty surfaces/colliders (no object source) instead of invented ones;
  scale "estimated", gravity unknown; camera time_s = view index.
- Skipped: SAM 3D (off by default; object_meshes not wired — no object bounds yet), floor/gravity (S05d owns),
  cold-start/cost instrumentation (S06e), RM04/RM05 runs, viewer visual check, vertical_fov from intrinsics (fixed 50).

## Limits / risks
- Not Gate R, not calibrated scale, not physical evidence; vertical_fov_deg is a placeholder 50, not derived.
- Approval scope text says "not third-party upload"; the job re-sent the SAME RM02 frames S05b already ran on
  Modal under standing GPU auth (no new/personal media). Controller should confirm this reading.
- Billing CSV may lag; recheck. torch-hub dinov2 code is fetched at runtime (as S06b) — network dependency.
- Communication: silent; one completion line to controller only.

Next: S06e (cold-start/GPU-seconds/cost fields in this job's receipt).
