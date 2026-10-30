# S07-chunktrack-orch67 REPORT — PARTIAL (mode DONE; PD02 measured < 1.25 periods; BN01 re-seed stopped)

Lane CODEX-1 (S07/S12); assigned anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Branch run/S07-chunktrack-orch67 from main a2fa169.
Issued 05:07:12Z; UTC start 05:07:53Z; implementation stopped 05:30Z (billing read 05:34Z), work_stopped/reported at deadline; deadline 05:37:12Z. Tokens unknown. Modal: 3 jobs, retries 0; Meta/AWS spend 0.

## Change (Build/measurement/runtime/modal_track.py, +~90 lines)
- `--chunk N` (default 0 = unchanged single-session path, orch14 defaults/args unchanged): `chunk_spans` (1-frame overlap, tail >=3 frames),
  `track_chunks`: one SAM session per chunk (close + `torch.cuda.empty_cache` + per-chunk peak reset), chunk k+1 re-seeded by text prompt and
  keeps the object whose frame-0 mask has max IoU (>= 0.5) with chunk k's selected last-frame mask; below threshold FAILS CLOSED (rest missing,
  `stopped` recorded). Overlap frame keeps the earlier propagated mask. Per-chunk provenance: local/source frames, PTS (existing presentation-map
  `_pts`), local object id, IoU, observed, seal_sha256 over [source, pts, frame_sha256], peak VRAM, elapsed.
- Merged selected-object stream goes through existing `tracking.sanitize_responses` (same record) and the same `log` rows (stream/RLE masks
  format unchanged; only the selected object, as object_id). timeout 900 -> 1500 s (reservation basis below).
- tests/measurement/test_modal_track.py: +3 tests (spans; re-seed follows target across per-session id swaps + merged passes sanitize_responses;
  low IoU fails closed), 2 existing assertions updated for the new `chunk=0` arg. evidence/.../summarize.py: measured summary + validate_segment call.

## Modal jobs (A10G, standing auth evidence/owner/S05/GPU-AUTHORIZATION.md; PD02/BN01/PD04 approved in evidence/owner/S02/APPROVAL.md)
| clip / span | app | chunks | frames observed | validate_segment | peak VRAM | remote s | est. USD* |
|---|---|---|---|---|---|---|---|
| PD02 f0-438 (whole clip) "gold ball" | ap-aWSShryM8nygn84r9uzF5G | 30, re-seed IoU min 0.984 | **439/439** (PTS 0-14.6 s) | full **OK** | 17.14 GB | 216 | 0.080 |
| BN01 f3385-3560 "ball" | ap-XZl3qSj8FbdV0I07l0chXv | 3, stopped at chunk 2 (f3415: no re-detection, IoU 0) | 31/176 (14.170-14.295 s) | full rejected (f3416 missing); observed subset OK | 17.14 GB | 55 | 0.020 |
| PD04 f0-599 "ball" | ap-SHTDPOF4taWCluMdzjl8Zc | 2, stopped | 0/600 (prompt found no obj 0) | rejected | 17.09 GB | 54 | 0.020 |
*cost_log.cost(remote_elapsed_s, A10G, 2 CPU, 16 GiB) only; excludes cold start. Modal billing report read 05:34Z (billing-post.json; hourly, may still
accrue): billed PD02 0.0879, BN01 0.0251, PD04 0.0263 = **0.1394 USD**.
Reservation per job 0.56 (1500 s cap), total 1.68 <= 2.50. Containers before [] (containers-before.json), after [] (containers-after.json,
containers-after-PD04.json); apps-after.json shows both first apps stopped, tasks 0.

## Measured findings (no gate claims; Gate M and Gate RS remain NOT_MET)
- Memory bound works: VRAM is per-chunk (~17.1 GB on 16-frame chunks, mostly model), independent of segment length; PD02 439 frames vs prior ~26-frame/19 GB ceiling.
- PD02: whole clip tracked but only **1 x-direction reversal** in 14.6 s (x 408-1294 px) => ~0.5-1 period; the clip itself cannot give >= 1.25 periods. Need another pendulum clip (PD06 9.5 s Foucault likely worse; PD03 Newton cradle 60 s; PD04 needs a correct prompt).
- BN01: text re-detection failed at chunk boundary f3415 (ball in fast motion) though propagation held it; fail-closed stopped. Next: re-seed with
  box/mask prompt from previous mask (SAM3 add_prompt boxes) instead of text — needs API check; or smaller first-chunk boundary choice.
- Outside Owns (not edited): validate_segment rejects any missing frame and assumes stream index == source index; summarize.py maps relative -> source like S12e score.py.

## Fresh checks
- `python -m unittest tests.measurement.test_modal_track` -> 11 OK (evidence tests-measurement.txt). `python -m unittest tests.pipeline.test_gpu_stages` -> 6 OK (called).
- `python -m unittest discover -s tests/measurement` not runnable (tests/measurement not a package; pre-existing).

## Ponytail (full)
- Reused: existing session calls (start/add_prompt/propagate/close), `sanitize_responses` for the merged record, existing `log` rows/mask_rle,
  `_pts` presentation map, frame SHA list, cost_log.cost, validate_segment. One CLI flag; default path byte-identical behavior.
- Skipped: mask/box re-seed (unverified API), automatic retries/prompt search, Build/pipeline fixes, PD03/PD06 jobs.
- PD02 identity check: SAM centroid vs S02c template-box centre over 439 frames median 5.2 px, p95 13.2, max 14.2 (PD02-vs-S02c-template.json; rough reference, not ground truth) => obj 0 is the gold bob throughout.
- Risks: text re-seed fails on blur/occlusion (fails closed, loses tail); chunk-0 object_id is caller-chosen "first detection".

Communication: silent; one completion line to controller.

