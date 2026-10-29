# R-R — Gate R cross-vendor review (R-R-orch24)

**Disposition: CHANGES REQUIRED. S05f acceptance blocked; return defects to the S05 owner.**
The read-only review is complete; **Gate R remains FAIL**, not passed. Accepted S05e's recorded failure is honest and reproducible; that does not establish its evaluator is ready to approve new annotated inputs.

Reviewed snapshot: main `57deb4b5f316564f5747fe1a687120e878cbb567`, S05e authored by Opus and reviewed on assigned Sol/high. Line numbers below are worktree-relative at that snapshot. No implementation was edited.

## Findings

### F1 [P1] Real producer measurements are always discarded as unmeasured

**`Build/reconstruction/spike/gate_r.py:45-46`; producer `scene_frame.py:155-160`; fixture `test_gate_r.py:8-10`.**
`scene_frame.analyse(..., refs=...)` emits `metric_scale.status="calibrated"`; the evaluator accepts only `"FIT"`. After S05f adds the owner's permitted standard-object annotations, even a perfect known-object measurement is assigned `scale_rel_error=null`, so the gate cannot pass. Existing tests hide the integration defect by inventing a producer status. The `actual_producer_calibrated_status` probe uses the real producer with its existing synthetic NPZ fixture and scale exactly 1: 0/3 scale passes, FAIL, rather than 3/3. Its orientation fields are synthetic controls, not actual A4 measurements.

**Required owner fix:** use one producer/evaluator status contract and test actual producer output end-to-end. Preserve ABSTAIN/null; do not change results by relabelling unmeasured real inputs FIT.

### F2 [P1] Fixed quorum without fixed three-scene cohort permits false PASS

**`Build/reconstruction/spike/gate_r.py:72-77`, CLI cohort loop `:93-96`.**
The gate requires three planned clips but accepts any `frames` cardinality with at least two scale/orientation passes. `missing_third_scene` returns PASS for two entries; `two_of_four_scale_passes` returns PASS for only 50% scale success. The CLI checks only hashes of supplied entries, never that all expected scene IDs are present. Dropping an unmeasured/failed clip can therefore make an incomplete cohort look complete.

**Required owner fix:** freeze/validate the three expected IDs (including explicit abstained/ineligible entries), reject missing/extra/duplicate scene inputs, and test two-, three- and four-entry cases. If the approved cohort is intentionally changed, record that decision and its denominator rather than silently changing the sample.

### F3 [P1] Floor and measurement validity are not verdict prerequisites

**`Build/reconstruction/spike/gate_r.py:35-54`, especially `:49-54`; no `contracts/scene/validate_scene.py` call in this evaluator.**
The plan requires a floor plane, but `floor.status` is only echoed. `no_floor` changes every floor to ABSTAIN while preserving synthetic measured values: the verdict remains PASS. Impossible angles (-999 degrees and negative infinity) also PASS because only `angle<=5` is checked. Negative function/lifetime durations pass both GPU comparisons. These are malformed-input counterexamples, not claims about current real receipts: current producer floor/gravity behavior is consistent. The raw S05d result format does not receive the finite-number and structural validation implemented for final scene bundles.

**Required owner fix:** validate the evaluator's own input boundary: required statuses and fields, finite positive scale, finite physically valid angle, finite nonnegative/valid timing, reliable floor plus eligible gravity, and reference provenance. Invalid/inconsistent input must fail closed or error, never PASS. Test these cases without assuming final scene-schema checks cover this different format.

### F4 [P2] Rounding before GPU comparison accepts an over-budget measurement

**`Build/reconstruction/spike/gate_r.py:39-41,53-54`.**
The decision uses values rounded to 0.001 minute. A function and lifetime of **240.029 seconds** become 4.000 minutes and PASS despite the explicit <=240-second limit. `rounded_gpu_over_threshold` reproduces this. The current real receipts are comfortably below the successful-function threshold; this finding does not change their present classification.

**Required owner fix:** compare original seconds with 240 (and original amortized lifetime if retaining that secondary check); round only for display. Add exact-boundary and just-over-boundary tests.

### F5 [P2] Abstained gravity can be labelled as measured angular failure

**`Build/reconstruction/spike/gate_r.py:51-52,61-67`.**
If an A4 angle exists but gravity is ABSTAIN, orientation is rightly rejected, but the failure becomes `measured_above_threshold` even for **1 degree**. This is false failure attribution, not a false pass. `abstain_gravity_reason` reproduces the misleading category/value.

**Required owner fix:** distinguish unavailable/ineligible gravity or floor from a measured angle actually above five degrees, retaining the source reason. The current all-unmeasured real results have correct categories.

### F6 [P2] Inclusive 10% scale boundary is rejected by floating-point roundoff

**`Build/reconstruction/spike/gate_r.py:46,50`.**
For raw predicted/true ratios 0.9 and 1.1, `mpu=1/ratio` yields computed error `0.10000000000000009`; both mathematically exact 10% cases fail the inclusive <=10% condition. The two `inclusive_scale_boundary_*` probes reproduce this (all three synthetic scenes fail instead of passing). This does not affect the actual unmeasured inputs but makes the documented threshold slightly stricter at its boundary.

**Required owner fix:** use a documented machine-precision-safe inclusive comparison with exact-boundary and clearly-outside controls; do not solve this by coarse display rounding or materially widening the gate. Orientation's exact 5-degree boundary and GPU's exact 240-second boundary were checked and accepted correctly.

## Threshold-policy clarification (not silently rewritten by reviewer)

- Final plan S05 (HTML line 109 at this snapshot) explicitly grants **>=2/3 to scale**, then requires floor found and gravity agreeing with A4 normal within 5 degrees. S05e `GATE_R.md:6` acknowledges it **applied >=2/3 to orientation too**; its REPORT names that ambiguity. The owner's Q-S05e answer changes admissible size provenance, **not this quantifier**. Obtain a controller/owner interpretation or retain the conservative per-clip requirement before a PASS. Do not treat this review as approval of a relaxed orientation threshold.
- Even under a 2/3 orientation interpretation, separate aggregate counts can pass when only one clip meets both scale and orientation (`disjoint_criterion_passes`). Record whether per-criterion counts or a common qualifying cohort is intended. This is a policy ambiguity, not claimed as a proven violation of an explicit common-cohort rule.
- GPU 3/3 applies to successful-job function times plus the disclosed amortized-lifetime check. RM02 **all attempts total 320.39 seconds (>4 minutes)** versus successful attempt 161.73 seconds. This retry exclusion is disclosed in S05e; report successful-run feasibility and cumulative pipeline cost separately, never imply the latter met four minutes. No live billing was checked and no new compute was run.
- The scale formula is correct **for raw MapAnything metric output**: with known true length L and model length d, `mpu=L/d`, so `abs(1/mpu-1)=abs(d-L)/L`. It is not independent validation of already-rescaled geometry. A held-out reference is needed if S05f claims post-calibration accuracy; do not require one merely to measure the original model's raw scale error.
- `angle_deg` treats plane-normal sign as immaterial via `abs(dot)` (`scene_frame.py:48-49`), appropriate for an unoriented plane. An A4 size standard alone does not establish the sheet was horizontal; an independently justified orientation reference is still necessary.

## Evidence traceability / positive checks

- Fresh rerun of the real evaluator: **FAIL, scale 0/3, orientation 0/3, GPU 3/3**, six unmeasured failures. Original and rerun SHA256 both `5f500258fdb152b31673677ac417ff509062ad27aa8015eabec64adb32d16c16`.
- S05d RESULT hash labels match S05c receipts **3/3**; actual local NPZ bytes at the recorded S05b-orch14/S05c-orch19 manifest paths also match **3/3**. The RM02 successful ledger output hash matches as well. `traceability.json` freezes hashes for reviewed code, receipts, manifest, controls, licence review and approval.
- Model receipts identify the Apache checkpoint `facebook/map-anything-apache`, code `3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9`, weights `00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a`. Existing S05 licence review and scoped owner approval are recorded; this review did not refresh upstream legal terms or expand media rights.
- `clips.csv` NO/unapproved values are historical broad flags. `evidence/owner/S02/APPROVAL.md` explicitly approves RM02/RM04/RM05 for scoped local pipeline work and retains final/public/physical holds. Do not mistake the CSV for missing local authority or the approval for calibrated/public-ready status.
- All three S05d manifest `refs` lists are empty. `scene_frame.py:153-154` always emits A4 ABSTAIN. Actual NPZ custody therefore **does not** establish any known-object identity, annotated dimension or orientation measurement. RM05 stays gravity-ineligible; its numerical floor FIT must not override S05d's visual unreliability note.
- Fresh existing spike tests **11/11**, scene-contract tests **11/11**. The review-only script confirms **14 cases plus scale-formula/boundary assertions**, including existing correct baseline/ABSTAIN controls and reproducible defects. These are synthetic counterexamples only; passing the probe means the reviewed defects reproduced, **not that product acceptance passed**.
- No production caller of `gate_r.evaluate` was found beyond its CLI and `test_gate_r.py`. The CLI exits zero even when JSON verdict is FAIL: process success/tests green must never substitute for reading `verdict`. No currently deployed gate consumer was established.

## Handoff

See `S05f-REQUIREMENTS.md` for the exact Q-S05e additions and acceptance checklist. S05 owner repairs F1-F6 and records threshold interpretation, then R-R rechecks those changes before S05f acceptance. No changes to other lanes, canonical controls, or gate status were made here.

**Not checked:** new visual object identification/annotations, live Modal/billing, source video bytes, upstream standards/licence freshness, real orientation or physical behavior. **Risk:** the recorded FAIL is safe, but new inputs can expose false-positive/false-negative paths until the owner fixes the evaluator.
