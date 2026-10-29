# S06d-orch23 PLAN

- Objective: Modal scene job entry point (approved scene id -> MapAnything on S06b runtime -> contracts/scene bundle); validate one artifact.
- Lane/model: CODEX-1, anthropic/claude-opus-5-5/high. Worker UTC start 2026-10-29T14:33:07Z (issue 14:32:31Z), deadline 15:02:31Z, cutoff 14:57:31Z.
- Owns: Build/gpu/; infra/modal/; evidence/S06/; Run-System/Runs/S06d-orch23/.
- Acceptance: (1) offline bundle from existing RM02 MapAnything npz passes validate_scene; (2) unit tests; (3) <=1 A10G smoke, cap $0.30, retries 0, ledger, no containers after.
- Holds: SAM 3D off; scale estimated/nominal; gravity unknown; no Gate R/physical claim; bundle media gitignored (no raw-media redistribution).
