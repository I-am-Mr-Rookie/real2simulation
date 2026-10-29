# S07b-orch13 runtime evidence (private Modal, ST03 prefix)

Script: Build/measurement/runtime/modal_track.py (+ resolve_imports.py). Ephemeral `modal run` only.
Result: PARTIAL — runtime reached checkpoint verify, model load, session start and text prompt; propagation failed. No track output.

| run | app | outcome |
|---|---|---|
| 1 | (local) | Windows charmap console error before job |
| 2-3 | ap-XCIt.., ap-M5t6.. | container import IndexError (my path bug) |
| 3b | ap-RF18.. | local unpickle of torch str (my bug) |
| 4 | ap-7Nyp.. | **preflight exit 0 (source_ok+dependency_ok, exact lock)**; checkpoint 3502755717 B, SHA256 0567debe..1cb6 MATCH pinned; import fail: pkg_resources (setuptools 84) -> result-run4.json |
| 5 | ap-a4oi.. | setuptools 80.9 pinned (lock deviation, dependency_ok now false); missing einops |
| 6 | ap-kkF4.. | missing pycocotools (sam3 imports train/ COCO loader) |
| 7 | ap-Bw9h.. | model loaded (19 s, load_local_predictor re-verified size+SHA); upstream start_session passes offload_state_to_cpu rejected by multiplex init_state |
| 8 | ap-09dw.. | shim drops that kwarg; FA3 kernel (Hopper-only, not installed) fails on A10 |
| 9 | ap-CkS0.. | use_fa3=False; session+prompt OK; propagate_in_video RuntimeError expand size 1 vs 0 in video_tracking_multiplex._prepare_memory_conditioned_features (JSON accidentally deleted in my cleanup; modal-run9.log keeps output) |
| 10 | ap-4ku4.. | diagnostic, prefix f58-76: add_prompt returned **3 objects** (so not zero detections); same propagation RuntimeError -> result-run10.json |

GPU allocated: NVIDIA A10/A10G 23 GB (L4 requested first, A10G fallback). retries=0, max_containers=1, timeout 900 s.
Stop: apps-after.json all 11 s07b-orch13 apps stopped, tasks 0; containers-after.json `[]` (2026-10-29T11:19:48Z).
Frames: ST03 source frames 50-70 (runs 2-9) / 58-76 (run 10), ffmpeg -q:v 2 JPEG to OS temp outside repo; per-frame SHA256 + PTS map in result-run*.json. No media/checkpoint bytes committed.
Secret: Modal `real2simulation-hf-read` by name; value never read/printed (rg hf_ token pattern: 0 hits).

