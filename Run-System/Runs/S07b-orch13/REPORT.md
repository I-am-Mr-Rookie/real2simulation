# S07b-orch13 — PARTIAL (runtime advanced; no track output)

- Model: anthropic/claude-opus-5-5 high (assigned). OpenCodex-managed; not polled. Tokens/cost of model: unknown.
- UTC: issued 10:56:09, work 10:56:37–~11:21, deadline 11:26:09. Branch run/S07b-orch13 @7303bc5, worktree C:/Users/HP/.codex/worktrees/s07b-orch13.
- Evidence: evidence/S07/S07b/orch13/README.md (run table), result-run4.json, result-run10.json, modal-run*.log, apps/containers before/after.

## Achieved (fresh, on Modal Linux/Py3.12 GPU)
1. Existing preflight.py on pinned sam3 f1647e8: **exit 0** with exact lock (run4); later runs dependency_ok=false only because of the setuptools pin below.
2. Gated checkpoint via provisioned secret name: facebook/sam3.1@daa6319 sam3.1_multiplex.pt, **3502755717 B, SHA256 0567debe…41cb6 = pinned** (5 independent downloads; load_local_predictor re-verified).
3. SAM3.1 multiplex predictor **built and loaded on A10 (19 s)**; start_session + text prompt "apple" on approved ST03 prefix (frames 50–70, scope scene_tracking, evidence/owner/S02/APPROVAL.md) accepted.
4. **Not achieved:** propagate_in_video raises RuntimeError (expand 1 vs 0, video_tracking_multiplex.py:1321). Run10 diagnostic: add_prompt found 3 objects on f58, so not zero detections. No sanitized track emitted.

## Runtime gaps found (recorded, not hidden)
- Base lock incomplete: sam3 imports pkg_resources (needs setuptools<81), einops, pycocotools, psutil(guess). Installed --no-deps; versions in result.json freeze.
- Upstream f1647e8: base start_session passes offload_state_to_cpu that multiplex init_state rejects -> driver shim.
- use_fa3=True default needs Hopper FA3 -> driver passes use_fa3=False (functools.partial in driver; tracking.py unchanged).
- Remaining: propagation 0-batch error; zero-detection hypothesis ruled out (3 objects). Likely multiplex tracker path at f1647e8 without FA3/rope settings, or an object-ID/multiplex bucket issue. Next: read video_tracking_multiplex.py:1290-1330 around B, try use_rope_real/multiplex_count settings or one bounded H100+FA3 run.

## Budget / stop
11 ephemeral apps, retries 0, max 1 container, A10 ~$0.000306/s. Conservative all-in reservation **$0.50** (cap $2); exact billing NOT observed; no paid-overage cap claimed. All s07b-orch13 apps stopped tasks 0; containers [] at 11:19:48Z. Another worker's s05b apps observed, untouched.

## Ponytail
Reused tracking.py, preflight.py, lock, existing secret, S05b uv+modal 1.6.3 route unchanged. One driver (modal_track.py) + tiny import resolver; workarounds live in driver, not adapter. Skipped: tracking.py/test edits, lock regeneration, FA3 install, H100. Checks: tests/measurement/test_tracking.py 14 passed (uv py3.12); ast syntax ok; token-pattern scan 0.
Risks: lock now known incomplete; resolver installs unpinned (shortcut comment); not calibration, not Gate M. Own bugs cost 3 extra short runs (charmap, path, pickle) and I deleted run9 JSON in cleanup (log kept).
Communication: silent; one completion line to controller.

