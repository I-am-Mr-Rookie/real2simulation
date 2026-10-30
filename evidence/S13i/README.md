# S13i evidence — API upload + job routes, RECORDED replay

Offline unit evidence only. No GPU, Modal, AWS, Meta or network call; nothing deployed or mounted.

- [tests-api-workspace.txt](tests-api-workspace.txt): 14/14 OK (S14i 7 + S13i 7), python -B, Python 3.14.
- [tests-pipeline.txt](tests-pipeline.txt): tests/pipeline 53/53 OK (pipeline untouched; regression check).

## Routes (prefix /internal/workspace, every route behind require_owner)
| Method | Path | Behaviour |
|---|---|---|
| POST | /uploads | {media_type,size_bytes,sha256}; sha must be in approved_shas() else 422 INVALID_INPUT; UploadService.create |
| GET | /uploads/{id} | resume point (committed_bytes) |
| PUT | /uploads/{id}/chunks/{offset} | raw body -> UploadService.put_chunk (duplicate/reject decisions as contract) |
| POST | /uploads/{id}/complete | whole-file sha check, then RECORDED replay via JobRunner; returns upload, job, provenance |
| GET | /jobs/{job_id}?after=N | S13g job_progress + provenance {executor: recorded, label: "RECORDED S13h-orch46", live: false} |

Other owner's upload/job -> 404 NOT_FOUND (same as missing). UploadError INVALID_INPUT -> 422 with decision/committed_bytes.

## Approved-sha gate
approved_shas() = registry evidence/clips/S02c-acquisition.json sha256 for clips listed in clips.csv AND granted by
evidence/owner/S02/APPROVAL.md (reuses Build.real2sim.score.approved). Tracked files only, so it works in the API
image where gitignored media is absent. Note: clips.csv owner_approved column is NO for every row; the S02 grant
file is the existing approval authority (same as score.py / scene_job.py / modal_track.py).

## RECORDED replay — material finding
evidence/S13/S13h/live/timing.json records validate, keyframes, segment, reconstruct, viewable(=package) with UTC
times, but "understand": "not run (Meta spend outside S13h budget)". Contract STAGES order is
validate, keyframes, understand, segment, reconstruct, package, so an RM04 replay emits validate + keyframes with the
original UTC timestamps (+00:00 -> Z only) and then fails understand DEPENDENCY_UNAVAILABLE ("understand was not run
in RECORDED S13h-orch46"), stamped with the actual replay time. Segment/reconstruct/package are never replayed and
no output/time is invented. The job therefore never reaches ready. Controller decision needed to reach the viewer:
(a) S13j/live capture records an understand stage for RM04, or (b) a contract change allowing a recorded-skip of
understand. Not decided here (would alter the S13a contract / invent a stage result).

## Hand-offs
- S04m: mount create_router() from Build/api/workspace/jobs.py; add redis (redis-py; 8.0.0 installed locally, not in
  the API requirements) and set REDIS_URL (unset -> per-process MemoryStore, shortcut) and WORKSPACE_UPLOAD_DIR
  (unset -> OS temp dir/r2s-uploads; ephemeral). Names only; no values.
- S14i scene resolver: NOT provided. No job can reach ready (finding above), so an owner has no scene to resolve;
  a resolver also needs base_spec/template that no S13 artifact carries. Leave analysis._no_scenes until a ready
  job exists; then the resolver is a store lookup job:<id>:owner -> scene bundle.
- SPEND_PAUSED: the recorded executor has no paid path, so no reservation is made; a future live executor must use
  Build/pipeline/gpu_stages.reserve, whose SPEND_PAUSED StageError JobRunner already records as never-retried.

