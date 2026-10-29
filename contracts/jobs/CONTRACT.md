# Job contracts 1.0.0 (S13a)

Contracts only. No upload, bucket, queue, GPU or scene has run against them.
Examples are SYNTHETIC. Not gate, real-scene or physical evidence.

Files: [jobs.schema.json](jobs.schema.json) (`urn:real2simulation:jobs:1.0.0`,
Draft 2020-12: `upload_session`, `chunk_ack`, `stage_event`),
[policy.json](policy.json) (numbers), [examples.json](examples.json).
Executable rules: `Build/pipeline/contracts.py`; tests: `tests/pipeline/`
(`python -m unittest tests.pipeline.test_contracts`). Breaking change = new major
version + new `$id`; schema maxima must equal policy (tested).

## File limits (contract decisions, not measured capacity)

| Limit | Value | Why |
|---|---|---|
| Size | 1 B – 100 MiB | short clip; fits <6 min upload-to-scene target |
| Chunk | 8 MiB, last chunk = remainder | S3 multipart minimum is 5 MiB |
| Types | video/mp4, video/quicktime, video/webm | declared type; `validate` stage must sniff/ffprobe |
| Duration | <= 60 s | enforced by `validate` (S13b/c); session cannot know it |
| Session TTL | 24 h, then `expired` | no resume after expiry; start a new upload |

Spend/quota gates (Meta cap, Modal <$5 upload pause) stay S20; they surface as
`SPEND_PAUSED`.

## Resumable upload

Client creates a session (size, sha256, type) and PUTs chunks at
`offset = committed_bytes`. Server rule (`chunk_decision`): `accept` only at
the committed offset with exact length; re-send of a committed chunk with the
same sha256 is `duplicate` (ack, no write); different bytes = `reject_conflict`;
ahead of committed = `reject_gap`; misaligned/oversized = reject; closed session
= `reject_closed`. After interruption the client GETs the session and resumes
from `committed_bytes`. `complete` (whole-file sha256 verified) assigns `job_id`;
`rejected` carries an error. Authorization failures are HTTP errors, never a
session disclosing another user's IDs (S04g rule).

S13b implementation: `Build/pipeline/uploads.py` (`UploadService`, local
filesystem store standing in for a bucket; tests `tests/pipeline/test_uploads.py`,
SYNTHETIC bytes). Server hashes each chunk itself; bytes are fsynced before the
atomic `meta.json` commit, so a crash mid-chunk resumes at `committed_bytes` and
torn bytes are truncated. Owner/upload IDs must match the `id` pattern (no path
traversal). Errors: `UploadError(code, decision, committed_bytes)`; owner
mismatch = `UNAUTHORIZED`, unknown = `NOT_FOUND`, chunk rejects/limits =
`INVALID_INPUT`. First chunk is magic-sniffed (MP4/MOV atoms, WebM EBML) and a
mismatch rejects the session; whole-file sha256 mismatch on `complete` rejects.
Duration and real container parsing remain the `validate` stage (S13c/ffprobe).

## Stage events and retry

Stages, in order: validate → keyframes → understand → segment → reconstruct
(runtime `S06a-gpu-image/v1`) → package. Events per job: `revision` 1,2,3…
(consumers ignore equal/older, as S04g); each stage is `started` then
`succeeded` (needs `output_sha256`) or `failed` (needs `error`).

- Retry inside a job: only after a `failed` event with `retryable: true`, code
  not in `never_retry` (INVALID_INPUT, UNAUTHORIZED, NOT_FOUND, SPEND_PAUSED) and
  `attempt < max_attempts` (validate 1; paid understand/segment/reconstruct 2;
  keyframes/package 3). Backoff 5 s then 30 s.
- `idempotency_key = <stage>:<sha256 of stage input>`, constant across attempts.
  Workers must reuse an existing succeeded output for the same key instead of
  recomputing or re-spending (S13d implements; also across jobs).
- Otherwise the failure is terminal. The shell job is then `failed` and never
  transitions; a user retry creates a new job ID (S04g rule) and reuses keyed outputs.
- `job_snapshot` projects events onto the S04g shell job DTO: no events =
  `queued` rev 0, in progress or retry pending = `running`, package succeeded =
  `ready` (scene supplied by caller), terminal failure = `failed` with
  `{code, message}`. Cancellation is a later user action, not a stage event.
- `job_deadline_s` 360 is the <6 min target to be measured in S13h, not a result.

## Keyframes stage output (S13c)

`Build/pipeline/keyframes.py` (`python -m Build.pipeline.keyframes CLIP_ID PATH OUT_DIR [CLIPS_CSV]`)
writes `kf_NNNNNN.jpg` + `manifest.json` (`kind: keyframe_manifest`, 1.0.0):

- `keyframes[]`: `index`, `file`, `pts` (stream timebase ticks), `time_s`,
  `time_source` (`pts`, else `best_effort_timestamp`), `pict_type`. Keyframes =
  decoder keyframes (`-skip_frame nokey`); times are the clip's original presentation
  times from ffprobe, never `index/fps`, so VFR and nonzero start offsets survive.
- `provenance`: copied from the clip's `clips.csv` row (`clip_id, title, source_url,
  creator, licence, licence_url, attribution, adaptation_notes, status, owner_approved`).
  Missing row, empty or NC/ND licence, or a path other than the row's `local_path` = INVALID_INPUT.
  Provenance is not use approval; scoped approval lives in `evidence/owner/S02/APPROVAL.md`.
- `source`: file name, sha256, ffprobe format/codec/size/timebase/rates/start/duration;
  duration over `max_duration_s` or no video stream = INVALID_INPUT. `vfr_hint` is advisory.
- Stage `output_sha256` = sha256 of `manifest.json`. Keyframes/manifests are media
  derivatives: never committed.

## Job lifecycle and retry (S13d)

`Build/pipeline/jobs.py` (`JobRunner`, tests `tests/pipeline/test_jobs.py`, SYNTHETIC workers):

- Store: redis-py-shaped calls only (`set nx/ex`, `get`, `delete`, `rpush`, `lrange`).
  `MemoryStore` for tests; no Redis client is installed, so a real `redis.Redis(decode_responses=True)`
  is a drop-in that has NOT been exercised. Keys: `job:<id>:events` (JSON stage events, appended only
  after `check_events` accepts the whole sequence), `out:<idempotency_key>` (stage output sha256,
  written once), `claim:<idempotency_key>` (lease, SET NX EX `lease_s`, default 900 s).
- Reuse: an attempt whose key already has `out:` emits `started`/`succeeded` with that output and
  never calls the worker, within a job or across jobs (user retry = new job ID).
- Duplicate dispatch: a live lease on the key raises `Busy` before any event or dispatch. A
  `started` event without outcome (crash) is closed from the store: recorded output = `succeeded`,
  else `failed` `PROCESSING_FAILED` retryable, counted against `max_attempts`.
- Retries follow `_retry_allowed` + `backoff_s`; never_retry codes are forced non-retryable.
  Terminal jobs return their `failed` snapshot and never dispatch again.
- At-least-once limit: a paid call that ran but crashed before `out:` was written can be dispatched
  once more (bounded by `max_attempts` 2); workers must forward the key as the provider's
  idempotency key. Lease must exceed the stage runtime. Spend caps remain S20 (`SPEND_PAUSED`).

