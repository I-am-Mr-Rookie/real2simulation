# S05f-orch25 REPORT — DONE

Lane/model: CODEX-1 / anthropic/claude-opus-5-5 high. Coding quota: OpenCodex-managed; not polled. Tokens: unknown (unobservable). Cost: $0 (CPU only; no GPU/API).
UTC start 2026-10-29T15:22:52Z (issued 15:22:22Z) · end 2026-10-29T15:33:44+00:00 · deadline 15:52:22Z. Base main `ba5f668`; branch `run/S05f-orch25`, worktree `.worktrees/S05f-orch25`. Not merged (controller acceptance).

## Result
- **Gate R: FAIL → Fallback 2 recorded** (planes+boxes textured, scale UNVERIFIED). Scale 0/3 unmeasured, orientation 0/3 (RM02/RM04 unmeasured, RM05 ineligible), GPU 3/3 ≤240 s successful runs (RM02 cumulative 320.39 s disclosed). Fallback 1 not applicable (desk height would be invented). Details/metrics/licence: [GATE_R.md](../../../evidence/S05/S05f/GATE_R.md), [GATE_R.json](../../../evidence/S05/S05f/GATE_R.json).
- **R-R F1–F6 fixed** in `Build/reconstruction/spike/gate_r.py`; probes converted to 8 new regressions in `test_gate_r.py` (11 total). Map: [REVIEW_PACKET.md](../../../evidence/S05/S05f/REVIEW_PACKET.md).
- **Q-S05e applied:** all 12 NPZ input views inspected (contact sheets). Only candidate = RM02 paper sheets; scale-free 3D aspect 1.236 (p5–p95 1.169–1.307) excludes A4 1.414 → ABSTAIN. RM04/RM05 no standard object. No size invented; thresholds unchanged.
- `scene_frame.py`: reference endpoint validation + audit trail in output; new CPU `a4_plane` fitter (needed for any future orientation measurement; abstains under microgravity).

## Files (all in Owns)
Build/reconstruction/spike/{gate_r.py,scene_frame.py,test_gate_r.py,test_scene_frame.py}; evidence/S05/S05f/{GATE_R.md,GATE_R.json,RESULT.json,REVIEW_PACKET.md,contact_sheet.py,frames.json,frames-RM0{2,4,5}.png,rm02-view0-paper-zoom.png,rm02_paper_diagnostic.py,rm02-paper-diagnostic.json,spike-tests.txt,scene-tests.txt}; this run dir.

## Fresh checks
- `python -B -m unittest test_gate_r` → 11 OK; `test_scene_frame` → 5 OK.
- Full spike discover: 83 run, 82 OK, 1 pre-existing import error (`test_modal_scenes`: `modal` not installed locally; untouched) — [spike-tests.txt](../../../evidence/S05/S05f/spike-tests.txt). contracts/scene: 11 OK.
- Producer rerun RESULT.json: floor/gravity/NPZ hash identical to S05d 3/3. Gate CLI asserts NPZ hashes == S05c receipts.

## Ponytail
Reused existing evaluator/producer/CLI/manifest, `synth_npz` fixture and `refit`/`angle_deg`; no new deps (numpy/PIL already present). Smallest changes: status contract aligned to producer's existing `calibrated` (not a new enum), fixed cohort as one constant, EPS constant for boundary, unrounded compare by keeping raw seconds. A4 fitter uses bbox shortcut (comment marks upgrade). Skipped: schema/validate_scene reuse for raw S05d format (different format; inline `_num` checks instead), new GPU job, automated detector.

## Limits / risks / next
- R-R re-review required before acceptance (packet ready). `evidence/reviews/R-R/probe_gate_r.py` now fails by design (asserted old defects).
- Common-cohort policy is the conservative interpretation; controller/owner may confirm (outcome FAIL either way).
- RM02 identity diagnostic uses model geometry (aspect scale-free, but model distortion possible); jitter interval excludes model error. Abstention is the safe direction.
- DECISIONS_LOG/QUEUE/STATE not edited (canonical controls); proposed DECISIONS_LOG line in GATE_R.md.
- Not checked: external standards freshness, live billing, browser UI (none needed). No physical/calibrated/real-scene claim.
- Communication: silent; one completion line to controller only.
