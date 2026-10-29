# Gate R checkpoint — S05f-orch25 (CPU only; existing S05b/S05c NPZ; no new GPU job)

**Verdict: FAIL → Fallback 1 not applicable to these public clips → FALLBACK 2 recorded (planes + boxes textured with frames; scale labelled UNVERIFIED).**
Thresholds unchanged. Machine record: [GATE_R.json](GATE_R.json) from repaired evaluator; producer rerun [RESULT.json](RESULT.json)
(floor/gravity/NPZ hash identical to S05d for 3/3 clips — deterministic seed).

Commands (worktree root):
`python -B Build/reconstruction/spike/scene_frame.py evidence/S05/S05d/manifest.json evidence/S05/S05f/RESULT.json`
`python -B Build/reconstruction/spike/gate_r.py --frames evidence/S05/S05f/RESULT.json evidence/S05/S05f/GATE_R.json` → `FAIL {"scale_passes": 0, "orientation_passes": 0, "qualifying_clips": 0, "gpu_passes": 3, "clips": 3}`

## Per-clip metrics (fixed cohort RM02/RM04/RM05; RM05 retained, not dropped)

| Clip | Floor | Gravity | Standard-object identity (Q-S05e) | Scale raw err | A4 vs gravity | GPU fn s (≤240) | Lifetime s amortised | Cost amortised |
|---|---|---|---|---|---|---|---|---|
| RM02 | FIT (S05d caveat: 6.9% inliers, 1/9 variant outlier 18.2°) | estimated | 2 paper sheets on desk → **ABSTAIN** (see below) | unmeasured | unmeasured | 161.73 PASS (ap-TqJhwZi4v9ucIKg16ZKh1E) | 189.0 | $0.05715 |
| RM04 | FIT | estimated | no standard object visible (whiteboard, shelf, desks, cabinet: no cited standard) → **ABSTAIN** | unmeasured | unmeasured | 177.9 PASS (ap-Pez26JXXUV7H31WyJvvrF8, 2-scene job) | 131.0 (262/2) | $0.03241 |
| RM05 | numeric FIT, visually UNRELIABLE (S05d) | ABSTAIN (ISS microgravity) | ISS hatch/handrail: no cited instance standard → **ABSTAIN** | unmeasured | **ineligible** | 177.9 PASS (same job) | 131.0 | $0.03241 |

GPU: successful-function times only; failed RM02 attempt retained separately — RM02 all attempts cumulative **320.39 s (>4 min)**, a pipeline-failure cost, never claimed as meeting 4 min. Whole 2-scene job lifetime 262 s (upper bound, client end). No billing re-check; no new compute.

## Standard-object identity packets (owner Q-S05e rule: cited standard + per-clip identity evidence + pixel endpoints; abstain if ambiguous)

Frames inspected: every MapAnything input view (4/clip, 294×518 NPZ `view*_img_no_norm`) → [frames-RM02.png](frames-RM02.png), [frames-RM04.png](frames-RM04.png), [frames-RM05.png](frames-RM05.png); hashes in [frames.json](frames.json) (`contact_sheet.py`).

- **RM02 (only candidate).** View 0, right sheet on front desk; corners (row,col) [226,257] [202,343] [217,435] [247,357] on [rm02-view0-paper-zoom.png](rm02-view0-paper-zoom.png); ±2 px jitter. Scale-free 3D aspect from model points = **1.236 (p5–p95 1.169–1.307)**; ISO 216 A4 = 1.414 is **outside**, US Letter 1.294 inside. Source (Pexels 6671552) does not state paper size. Plane fit RMS 0.0017 model units (desk+sheet bbox). Identity confidence: LOW → **ABSTAIN**; no length_m assigned, no scale/orientation counted. [rm02-paper-diagnostic.json](rm02-paper-diagnostic.json). Standard citation not needed because identity rejected (ISO 216 210×297 mm is the owner-provided basis; not freshly verified this run).
- **RM04.** No paper sheet, ball or object with an identifiable governing spec in any view. ABSTAIN.
- **RM05.** ISS interior; hatch dimensions would need an instance-specific NASA spec citation not available here; gravity ineligible regardless. ABSTAIN.
- **Regulation ball:** none visible in any clip.

## Fallback decision

- **PASS:** not met (0/3 qualifying).
- **Fallback 1** (keyframe + SAM 3D Objects + one desk-height question): the question supplies scale only for a user's own room; for public clips any desk height would be invented → cannot produce a Gate R measurement. SAM 3D Objects runtime unverified. Not applied.
- **Fallback 2 — APPLIED (recorded):** planes + boxes textured with video frames, from existing outputs: RM02/RM04 floor plane + gravity direction (model units); RM05 visual-only, no gravity scene. Scale = MapAnything model-metric, labelled **unverified** (metric_scaling_factor 1.375/1.710/0.876 are model outputs, not measurements). Does not make Gate R pass; no physical/calibrated/real-scene claim. Experiment flow unchanged (plan S05).
- Proposed DECISIONS_LOG line for controller (canonical control not edited here): *"2026-10-29 S05f: Gate R FAIL (scale 0/3, orientation 0/3 unmeasured; RM05 ineligible; GPU 3/3 ≤240 s successful runs, RM02 cumulative 320.39 s). Q-S05e standard-object rule applied: RM02 paper sheets abstained (3D aspect 1.24 excludes A4); no other standard objects. Fallback 2 adopted, scale unverified. MapAnything weights facebook/map-anything-apache (Apache-2.0) per S05a."*

## Licence decision

Model: `facebook/map-anything-apache` (Apache-2.0), code `3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9`, weights `00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a` — per [../LICENSE_REVIEW.md](../LICENSE_REVIEW.md) (S05a; not refreshed this run). Clips: RM02/RM04 Pexels licence, RM05 NASA PD (`clips.csv`), used under scoped local-pipeline approval `evidence/owner/S02/APPROVAL.md`; final/public/physical holds unchanged. Frame PNGs here are local evidence derivatives of approved clips; no publication.

## Threshold interpretation (recorded, not relaxed)

Conservative common cohort: a clip qualifies only if scale AND orientation pass; PASS needs ≥2/3 qualifying + GPU on all 3. Orientation requires floor FIT + gravity estimated. Stricter reading (orientation on all 3) is impossible with RM05 in cohort and would also FAIL now. Controller/owner may confirm; outcome unchanged either way.
