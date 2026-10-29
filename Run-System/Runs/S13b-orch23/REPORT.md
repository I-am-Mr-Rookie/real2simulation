# S13b-orch23 REPORT — DONE

- Task: S13b implement bucket upload validation. Lane CODEX-1; model anthropic/claude-opus-5-5 high.
- Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). Spend: $0; no bucket, account, credential, Modal job, network or install.
- UTC: issued 2026-10-29T14:32:07Z; worktree created 14:32:31Z; work stopped 2026-10-29T14:40:12Z; deadline 15:02:07Z.
- Branch run/S13b-orch23 from main f37121c; not merged (controller integrates). Canonical controls untouched.

## Changed (all inside Owns)
- Build/pipeline/uploads.py (new): UploadService(root, now) create/get/put_chunk/complete + UploadError(code, decision, committed_bytes) on a local filesystem store (stand-in bucket).
- tests/pipeline/test_uploads.py (new): 7 tests, SYNTHETIC bytes in a temp dir.
- contracts/jobs/CONTRACT.md: short S13b implementation paragraph. Schema/policy/version unchanged (no contract break).

## Acceptance evidence
- Interrupted upload resumes: chunk 0 committed, torn bytes (longer than the real remainder) appended without meta commit, new service instance on same store -> get() = committed_bytes 8 MiB, chunk 0 re-send = duplicate ack (no write), resume at committed_bytes, complete -> sha256 verified, job_id assigned, stored bytes == source, complete idempotent.
- Unauthorized rejected: wrong/empty/None/"../alice" owner -> UNAUTHORIZED on get/put/complete/create, error text has no upload_id; unknown -> NOT_FOUND.
- Invalid rejected: traversal/malformed upload_id; bad media type, size 0 / > 100 MiB / bool / float, bad sha256; gap (returns resume point 0), conflict, misaligned, wrong length, beyond size, negative offset, non-bytes body; content magic mismatch (mp4 bytes declared webm) -> session rejected then reject_closed; whole-file hash mismatch -> rejected, job_id null; expiry at TTL -> expired, put rejected, persisted. Every emitted session/ack validates against jobs.schema.json.

## Fresh checks
- python -m unittest tests.pipeline.test_uploads tests.pipeline.test_contracts -> Ran 15 tests, OK (7 new + 8 S13a).
- Mutation checks (temporary edits, reverted, git diff clean): removing truncate, owner check, first-chunk sniff, or whole-file hash check each makes the suite fail.
- unittest discover on tests/pipeline not usable (no package __init__); used the documented explicit module command.

## Ponytail (full) applied
- Reuse: chunk_decision, errors() and POLICY from S13a contracts.py drive every accept/reject and DTO check; no rule duplicated. Stdlib only (hashlib, secrets, os.replace, json); no dependency.
- Smallest complete: one module, one class, filesystem store only (in-memory not added: temp dir covers it and also proves restart resume). Errors reuse contract codes.
- Skipped: S3/bucket adapter, HTTP route, cross-process locking (shortcut comment), mp4 vs quicktime brand distinction (shortcut comment; ffprobe in validate), duration check (S13c), cleanup of expired/rejected dirs, rate limiting.

## Limits / risks
- SYNTHETIC fixture evidence only; no real clip, bucket, gate, real-scene or physical claim.
- Single-writer assumption per store: concurrent PUTs to one upload from two processes could race until a lock/queue (S13d) exists.
- Owner identity is a caller-supplied ID; real auth (session/JWT) must be bound at the HTTP layer.
- UNAUTHORIZED vs NOT_FOUND lets a caller probe existence of a random 128-bit upload_id; acceptable, revisit if the route wants uniform 404.

## Next
- Controller: review/merge run/S13b-orch23; S13c (ffmpeg keyframes) can consume complete sessions' data.part.

Communication: silent; one completion message to controller only.
