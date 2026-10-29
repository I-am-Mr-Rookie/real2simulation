# Gate R — S05e-orch23 evaluation (CPU only, existing outputs)

**Verdict: FAIL (not passed).** Scale 0/3 and orientation 0/3 are *unmeasured* (input missing), not measured-above-threshold; GPU time 3/3 measured PASS. No GPU job, no new reconstruction, no object size supplied by the agent.
Machine record: [GATE_R.json](GATE_R.json) (sha256 5F500258…2D16C16, identical on rerun). Evaluator: `python Build/reconstruction/spike/gate_r.py evidence/S05/S05e/GATE_R.json` (asserts S05d npz hashes == S05c receipt hashes).

Thresholds (final plan S05): known-object size within 10% on >=2/3 scene clips; floor found and gravity vs A4 plane normal <=5 deg (applied as >=2/3); GPU <=4 min/scene.

| Clip | Floor (S05d) | Gravity dir | Scale vs known object | Gravity vs A4 | GPU fn time (unamortised) | App lifetime amortised / whole job | Cost (amortised) |
|---|---|---|---|---|---|---|---|
| RM02 | FIT, 11.1 deg from camera-down prior; 8/9 variants <=1.75 deg, 1 outlier 18.2 deg | estimated | UNMEASURED | UNMEASURED | 2.70 min PASS | 3.15 / 3.15 min | $0.0572 |
| RM04 | FIT, 3.6 deg from prior; 9/9 <=0.50 deg | estimated | UNMEASURED | UNMEASURED | 2.97 min (2-scene job) PASS | 2.18 / 4.37 min | $0.0324 |
| RM05 | numeric FIT but visually UNRELIABLE (S05d overlay: equipment, no deck; 3/9 variants no fit) | ABSTAIN (ISS, microgravity) | UNMEASURED | UNMEASURED (cannot exist) | 2.97 min (2-scene job) PASS | 2.18 / 4.37 min | $0.0324 |

GPU basis: Modal A10 receipts — RM02 orch14 attempt 2 (ap-TqJh…, function 161.7 s, launch->stop 189 s); RM04+RM05 S05c (ap-Pez2…, function 177.9 s for both, launch->client end 262 s, an upper bound; Modal shows the app stopped earlier). Excludes the failed RM02 attempt 1 (158.7 s GPU, client DeserializationError, npz not retrieved) and the two orch13 L4 admission timeouts (no container billed). Including RM02's failed attempt, RM02 GPU total was ~5.3 min — a *pipeline* failure cost, fixed (`str(torch.__version__)`), not steady-state per-scene time. Whole-job lifetime for the 2-scene job (4.37 min) exceeds 4 min only if one scene is charged all of it. Inference itself was 0.72–1.20 s/scene; model load dominates.

## Failure inspection (itemised)
1. **Scale, all 3 clips — unmeasured.** MapAnything emits a model-metric factor (1.375/1.710/0.876) but nothing in any clip has a source-backed dimension tied to pixel endpoints (S02d audit): RM02 "Room; scene-only"; RM04 Pexels classroom, no documented desk/door/A4 size; RM05 ISS hatch/handrail dimensions unverified. Camera heights ~1.18/1.39 model units are plausibility only, not evidence.
2. **Orientation, all 3 clips — unmeasured.** No A4 sheet (or any annotated horizontal/vertical reference) in any clip; floor normals exist for RM02/RM04 but there is no independent reference to compare against. The 11.1/3.6 deg floor-vs-camera-down angles are not a ground truth.
3. **RM05 is structurally ineligible for the orientation criterion** (microgravity; no floor). It can never count toward 2/3 for gravity, so 2/3 requires both RM02 and RM04 (or a replacement gravity-bound clip).
4. **RM02 floor robustness:** small visible floor (6.9% inliers); one sensitivity variant (seed 2, band 0.04) jumps 18.2 deg to a different plane. RM04 is the most reliable reconstruction.
5. **Pipeline failures already fixed upstream:** orch13 L4 admission timeouts (no GPU), orch14 attempt-1 client deserialisation. No remaining GPU-side failure on the 3 scenes.

## Fallback assessment (for S05f; not decided here)
- **Fallback 2 (planes + boxes textured with frames)** — feasible now for RM02/RM04 from existing outputs: floor plane + gravity direction in model units. Scale would be MapAnything model-metric, must be labelled *unverified*. Does **not** make Gate R pass; removes the need for metric scale only for the visual scene, not for physics claims. RM05 has no floor -> not usable for a gravity scene.
- **Fallback 1 (keyframe + SAM 3D Objects + one question: desk height)** — the answer supplies scale for a user's own room; for these public clips any desk height would be invented, so it cannot produce a Gate R measurement. SAM 3D Objects not run (access accepted, checkpoint/runtime unverified).
- Recommended S05f choice on current evidence: Fallback 2 for RM02/RM04 with "scale unverified" labelling, unless the input below arrives first.

## Exact input that would let Gate R be measured (and possibly pass)
For **>=2 gravity-bound clips** (RM02, RM04, or licensed replacements with clips.csv + owner approval):
1. **Scale:** one object per clip with a documented length — `{view, p0:[row,col], p1:[row,col], length_m, length_sd_m, source}` (the existing `scene_frame.known_object_scale` ref schema) — where `source` is a citation (licence page, manufacturer/standard spec explicitly identifying that object) and the endpoints are pixel annotations on the 518x294 MapAnything view. A second, held-out object per clip makes the 10% check independent of the reference used to set scale; with only one, the check compares MapAnything's own metric output against the reference (what gate_r.py does: `|1/mpu - 1|`).
2. **Orientation:** a planar reference of known orientation per clip — e.g. an A4 sheet lying on a horizontal surface with its 4 corner pixels annotated in one view (needs a small A4-normal fit; `scene_frame.py` carries the `shortcut:` for this) — or an annotated plumb/vertical edge, with its source/justification.
3. Owner/controller decision needed: the plan allows "standard sizes, not tape measurements" (door, A4, ball), but S02d judged an unspecified-country standard door height *not* source-backed. Whether a visually identified standard object counts must be decided by Koushik/controller; the agent did not assume it.

No new GPU is required for any of this: annotations are applied to the existing npz on CPU.
