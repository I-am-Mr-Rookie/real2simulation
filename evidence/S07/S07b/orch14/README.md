# S07b-orch14 runtime evidence (private Modal, ST03 prefix)

Result: sanitized SAM3.1 track for approved ST03 training prefix f58-76 (scope scene_tracking, evidence/owner/S02/APPROVAL.md) -> result.json `record`.
Not calibration, not Gate M, no physical g.

## Root cause (orch13 propagate_in_video 0-batch RuntimeError)
- orch13 log: propagation reached 18/19 frames, failed on the LAST prefix frame (tensor [5184, 0, 256]).
- Upstream sam3 f1647e8 `sam3_multiplex_detector.forward_video_grounding_multigpu`: forward `valid_frame_end = min(num_frames, start + max_frame_num_to_track)` is EXCLUSIVE; chunk for frame 18 clamps to [18,18) -> backbone over 0 frames -> empty sam2 features -> expand error in video_tracking_multiplex.py:1321.
- Our adapter sent `max_frame_num_to_track = len - 1` (=18). Fix: omit it (upstream example sends only type+session_id; session already contains only the prefix). Not a model/GPU/FA3/async/rope issue.

## Runs
| run | app | outcome |
|---|---|---|
| 1 | ap-fSQiiTH0CIYD3TbQdeRirP | fix verified: all 19 frames tracked (track 7.2 s). Emitted object_id=0, which per prefix stream boxes is a STATIC ground apple (y~0.82) -> result-run1.json (not used) |
| 2 | ap-ygEqG7VZ0n2krxmdzXuMDh | container started 11:37:42Z, no remote output for ~5.5 min (stuck); stopped by me 11:43:2xZ (`modal app stop --yes`), containers [] -> containers-after-run2-stop.json |
| 3 | ap-4ffnhkGQGjNikZQgCzj9wc | object_id=2 (falling apple, chosen from PREFIX-only run1 boxes y 0.32->0.77): stages preflight..tracked, 19/19 frames, missing_frames [] -> **result.json** |

## Track observations (measured, uncalibrated pixels)
- y_px 475.2 (f58) -> 1083.0 (f76), accelerating; x_px ~134-138.
- Repeated identical centroids f59=f60, f65=f66, f71=f72 and PTS gap f75->f76 (2.5025->2.569233 s): source-frame duplication/drop in the rendition, recorded as-is via the PTS map (no correction). Downstream fitter must use pts_s, not frame index.

GPU: NVIDIA A10 23 GB; retries=0, max_containers=1, timeout 900 s, single_use. containers-before [] / containers-after [] (11:45:2xZ). apps-before/after.json saved.
Builder overrides: use_fa3=False (Hopper-only kernel); upstream default use_rope_real kept (not needed after root cause). Shim: drop offload_state_to_cpu kwarg (orch13).
Preflight exit 2 = only the setuptools 80.9 deviation from lock (pkg_resources); einops/psutil/pycocotools now pinned in image layer.
Frames: ffmpeg JPEGs in OS temp outside repo; per-frame SHA256 + PTS in result.json. No media/checkpoint bytes committed. Secret `real2simulation-hf-read` by name only.

