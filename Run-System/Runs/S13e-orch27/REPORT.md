# S13e-orch27 REPORT — Connect Muse Wonder understanding

Status: **DONE** (fixture-first + bounded live). Model: anthropic/claude-opus-5-5 high; coding quota OpenCodex-managed; not polled.
UTC issued 2026-10-29T15:30:59Z, work start 15:31:21Z, end 2026-10-29T15:40:13+00:00. Base main 7aff0fa, branch run/S13e-orch27.

## Changed (Owns only)
- Build/pipeline/understand.py (new): `understand` JobRunner worker. Video once -> explicit keyframe-image fallback;
  `sample()` caps to 4 evenly spaced keyframes (first+last) before any paid call; ffmpeg downscale <=512 px;
  reply validated by the S14 agent-response contract (number-free); writes understanding.json, returns sha256.
  S13d key forwarded as provider `Idempotency-Key` (`<key>#video` / `<key>#keyframes`). Live CLI ledgers every call,
  guard 6 calls / USD 1 -> `SPEND_PAUSED`.
- tests/pipeline/test_understand.py (new, 7 tests, fake post, SYNTHETIC frames): cap 600->4, video ok single call + key,
  HTTP 400 -> keyframes fallback, transport error + no-video skip, numeric reply rejected (PROCESSING_FAILED retryable),
  budget guard, JobRunner integration (user retry job-2 reuses `out:`, no second Muse call).
- contracts/jobs/CONTRACT.md: "Understand stage (S13e)" section.
- Run evidence: ledger.jsonl, live-1-understanding.json, live-2-understanding.json (text only; no media committed).

## Ponytail (applied, full)
- Reused, not rewritten: `muse.build_request`/`output_text`/`validate_response` (S14 request + numeric-claim ban),
  `record_muse` price constants, `muse.ask_user` as the valid test fixture, S13c `keyframes.extract` for live frames,
  S13d `StageError`/`JobRunner`/`MemoryStore` (idempotent reuse comes for free from `out:`), ffmpeg (existing dep).
- Smallest complete: one module + one test file; no new client, schema, config, deps or wrapper classes.
- Shortcut comments: per-media worst-case token assumption (IMAGE 3000 / VIDEO 60000) until billed usage reconciled.
- Skipped: feedback re-ask of video (contract said try video once), Redis client, contracts/agent edits (not owned).

## Fresh checks
- `python -m unittest tests.pipeline.test_contracts tests.pipeline.test_uploads tests.pipeline.test_keyframes tests.pipeline.test_jobs tests.pipeline.test_understand` -> Ran 37, OK.
- S13c extract on ST03 (approved ID, Pexels, evidence/owner/S02/APPROVAL.md): 7 keyframes, 18.13 s (frames in %TEMP%, not committed).
- Live Meta Model API, muse-wonder-1.0, ST03 only, 2 stage runs = **4 calls** (cap 6), est **USD 0.16773** (cap 1; billed unknown),
  tokens in 15440 / out 2503. Ledger: Run-System/Runs/S13e-orch27/ledger.jsonl.
  - Video (`input_video` data URL, 5.4 MB mp4): HTTP 200 both times, 4995 input tokens; reply clearly described the
    motion (apple released/falls) but **failed the contract 2/2** with the same issue:
    `questions[0].chips: free_text has no chips` -> explicit keyframe fallback taken.
  - Keyframe fallback (4 frames): HTTP 200, **validated 2/2** (free_fall candidate, landing-surface chips question,
    "scale and gravity are unknown"). understanding.json records input_mode=keyframes, fallback_used=true, all attempts.

## Limits / risks
- Video modality: provider accepts it and the model sees motion, but no video reply has validated yet; root cause is a
  Muse schema-conformance quirk (free_text question with empty `chips`), owned by S14/contracts/agent, not S13e.
  Fix options for controller: S14 validator/schema tolerance for empty chips, or one feedback re-ask on video (+1 call/job).
- Whether the provider honours `Idempotency-Key` is unverified; the guaranteed no-double-spend is JobRunner `out:` reuse.
- Cost per call is list-price estimate x1.5, not billed. One clip, two runs: not a reliability rate.
- Model output is description only; no measurement, gate, physical or calibrated claim. No Modal/GPU, installs or deploys.
- Communication: silent; one completion message to controller as authorized.

Next: S13f (SAM masks + Modal reconstruction) consumes understanding.json; controller decide video-chips fix above.

