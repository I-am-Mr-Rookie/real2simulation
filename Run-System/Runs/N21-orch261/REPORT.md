# N21-orch261 REPORT
Status: DONE. Model anthropic/claude-opus-5-5/high. Branch run/N21-orch261 (base cf6d17b2).
- F1 cap bypass: verified fixed (http_post/http_post_file/hosted_sam/live_room reserve on daily_cap); added zero-outbound test on exhausted cap.
- F2 one GPU pool: Build/api/gpu start() now blocks (BEGIN IMMEDIATE) until the job is head of the ONE queue across reconstruct+track; TimeoutError after 1800 s. ondemand.py docstring states the contract.
- F3 ffprobe: video_seconds fails closed (503 VALIDATOR_UNAVAILABLE) when missing; non-finite/<=0/timeout -> 415. No infra edits (N11 adds ffprobe).
- F4 quota race: Store.add runs check+insert+move inside BEGIN IMMEDIATE; rollback deletes moved bytes.
- F5 number guard: signed comparison (-9.81 no longer backs 9.81), "2-5" read as range; ask_user question+options now checked.
- F7 transcription: Content-Length and streaming cap before buffering (413); BFF AUDIO_CAP aligned to 4_000_000 bytes.
- F6 namespace: N09 BFF already maps agent/* to /workspace/agent/* (incl. agent/lab); no change needed.
- start_room_build wired to the N08 POST /internal/workspace/rooms route body (same store, checks, GPU queue).
- Live workspace: removed legacy approved-clip uploader, "Sample pipeline" heading and its rail shortcut; honest LIVE_NOTICE.
Checks: pytest tests/n21 gpu agent api-storage/test_storage guardrails lab lab-editor reconstruction + health: 215 passed, then the 2 failures (test isolation, expected handler set) fixed and rerun 10/10; node --test proxy_files + shell-workspace + workspace + web-private: 193/193; npm run build: exit 0.
Not run: tests/agent/test_muse.py, tests/guardrails/test_live_admission.py (pre-existing collection ImportError, untouched).
Paid calls: none.
Deferred: F5 unit/label/uncertainty matching (needs typed result rendering, a UI contract change); F2 residual idle billing of the other function's warm container (needs merged Modal function/image, redeploy); stale-job lease for crashed processes (shortcut comment); in-flight multipart spool reservation (F4 second half); upload-view.mjs copy and workspace-shell 'Clips' item (not owned; hidden in live mode).
Risks: a crashed GPU job blocks the queue up to 30 min; uploads now return 503 on any image without ffprobe until N11 lands.
