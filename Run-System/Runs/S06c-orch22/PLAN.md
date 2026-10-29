# S06c-orch22 PLAN — optional SAM 3D Objects path

Issued 2026-10-29T12:26:01Z, deadline 12:56:01Z (cutoff 12:51:01Z). Started 12:28:08Z.
Lane CODEX-1, model anthropic/claude-opus-5-5 high. Base main 0ca50f2. Branch run/S06c-orch22.

Objective: licence + VRAM review first; disabled-by-default SAM 3D Objects guard whose every
failure falls back to the primitive (box) mesh path; tests proving the primitive path stays usable.

Owns: Build/gpu/; infra/modal/; evidence/S06/; Run-System/Runs/S06c-orch22/.

Access check: evidence/owner/ has no SAM 3D Objects access/terms receipt (only S02, S05 GPU auth,
S07 SAM3/3.1 gating group). => no GPU job, no download, no terms/access request.

Checks: (1) python -m unittest in Build/gpu (new + existing); (2) offline gate receipt
evidence/S06/S06c/gate-default.json shows backend=primitive with reasons; (3) primitive boxes
validate against contracts/scene/scene.schema.json collider def.
