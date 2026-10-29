# S07b-orch14 — DONE (sanitized ST03-prefix track emitted; not calibration, not Gate M)

- Model: anthropic/claude-opus-5-5 high (assigned). Coding quota OpenCodex-managed; not polled. Model tokens/cost: unknown.
- UTC: issued 11:27:38, work 11:28:50–11:46:21, deadline 11:57:38 (Dhaka 17:57:38). Branch run/S07b-orch14, worktree .worktrees/S07b-orch14. Not merged (controller integrates).
- Evidence: evidence/S07/S07b/orch14/README.md, result.json (canonical track), result-run1.json, apps/containers before/after, launch-utc.txt, test_tracking.txt; modal-run*.log git-ignored on disk.

## Root cause + fix
- orch13 run10 log: propagation 18/19 then failure on LAST prefix frame ([5184, 0, 256]).
- Upstream f1647e8 sam3_multiplex_detector.forward_video_grounding_multigpu: forward valid_frame_end = min(num_frames, start + max_frame_num_to_track) is exclusive -> chunk [18,18) empty -> 0-batch backbone features -> expand error (video_tracking_multiplex.py:1321).
- Adapter sent max_frame_num_to_track=len-1. Fix (tracking.py, 1 line removed + why-comment): omit it, matching upstream example request (session holds only the prefix, so holdout unchanged). TRACKING.md + test updated (assert key absent).

## Result (Modal A10, run3 ap-4ffnhkGQGjNikZQgCzj9wc)
- stages preflight/checkpoint(3502755717 B, SHA256 0567debe…41cb6 pinned)/model_loaded/tracked; 19/19 frames f58–76, missing_frames []; record has frame_index, pts_s, x_px, y_px, source SHA256, licence, provenance, approval scope scene_tracking.
- Object: text "apple" yields 3 objects; run1 (fix verified, object 0) showed obj 0/1 static ground apples; obj 2 falls y 475->1083 px. Driver OBJECT_ID=2 chosen from PREFIX-only stream boxes (no suffix consulted).
- Observed source duplicates f59=f60, f65=f66, f71=f72 and PTS gap f75->f76; kept as-is; fitter must use pts_s.

## Spend / resources
3 jobs: run1 ~47 s remote, run2 container stuck ~5.7 min with no output (stopped by me, `modal app stop --yes`), run3 ~47 s. A10 ~$0.000306/s => GPU ~$0.15; conservative all-in reservation $0.50 (cap $2). Exact billing NOT observed; no paid-overage cap claimed. retries 0, max_containers 1, single_use. containers [] after run2 stop and after run3 (11:45:2xZ). Other workers' apps untouched (s05b container seen earlier, not mine).

## Ponytail
Reused tracking.py/preflight/lock/secret/orch13 driver + uv+modal 1.6.3 route. Smallest complete root fix: delete one request key in shared adapter (not a driver workaround); dropped the no-op async override. Added only a masks-free per-frame obj-id/box log for object audit and a pin line (pycocotools==2.0.11 with einops/psutil).
Checks (fresh): test_tracking.py 14 passed, 26 subtests (uv py3.12 + pytest); ast ok; hf_ token-pattern scan 0 hits; containers [].
Skipped: lock regeneration (requirements-linux-py312.txt still lacks setuptools<81/einops/psutil/pycocotools -> preflight exit 2 on dependency check only); use_rope_real=False and H100/FA3 (unneeded after root cause; upstream default kept); resolve_imports.py still a shortcut.
Risks: object id order from detector is not guaranteed stable across runtimes — downstream should check the falling trajectory, not trust id 2 blindly. Pixel coordinates uncalibrated; not Gate M; no physical g.
Communication: silent; one completion line to controller.

