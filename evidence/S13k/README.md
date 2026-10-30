# S13k — RM04 replay: recorded understand + scene resolver

RECORDED replay only; no live run, Meta/GPU/network call, spend or deploy in this run.

- `jobs.load_understanding(sha)`: the single `valid:true` spec in evidence/S14/S14g-fix3-live.json with `source_sha256 == sha` (RM04: 8231fbca…). UTC = the one HTTP-200 `spec-RM04` row of S14g-fix3-ledger.jsonl: **2026-10-30T05:06:04Z** (single timestamp; used for both understand started/succeeded). Ambiguous/absent -> "time not recorded" (events then carry replay time).
- `recorded_runner`: understand (not run in S13h) is filled from that record; output_sha256 = sha256(accepted_text) (recorded Muse output text, not a pipeline understanding.json, which never existed for this run). provenance.stage_labels: understand = "RECORDED S14g-fix3", every other stage = "RECORDED S13h-orch46"; provenance.understand.recorded_utc. Job reaches `ready`; shell result scene = {scene_id: job_id, access: private, evidence: reconstructed}.
- Without a matching S14g record the replay still stops at understand with DEPENDENCY_UNAVAILABLE (tested).
- `jobs.scene_resolver(store)`: (owner, scene_id=job_id) -> (recorded base_spec, recorded scene_context, ROOT) only for a READY job owned by owner; other owner / missing / not ready -> None (404). S04m mounts `analysis.create_router(scene_resolver(store))` with the same store as `jobs.create_router(store)`.
- Material limit: the recorded scene_context is not an authoritative scene bundle (S14g already recorded "validate_setup not run"), so POST scenes/{id}/spec returns 422 INVALID_INPUT "invalid authoritative bundle" — honest, never a default. GET questions returns 200. A real RM04 bundle is a separate task.

Tests: [test-output.txt](test-output.txt) — 16 api-workspace tests OK (Python 3.14).
