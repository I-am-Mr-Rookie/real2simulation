# R-RS recheck — R-RS-recheck-orch53

**Verdict: CHANGES_REQUIRED.** Review DONE; S12e/Gate RS is not cleared.

Reviewed Opus fix `ee4e14f93f5eb0284df62432bf838e22597366fe` on main snapshot `9d1a9ae` using assigned Sol/high. Product code, original review and canonical controls were not modified. Original direct F1–F4 probes now refuse, but two acceptance-integrity gaps remain. Neither finding alleges falsification of saved ST03 evidence.

## F1-R [P1] Bind custody metadata into the pre-observation commitment now

**Locations:** `Build/real2sim/score.py:38–53`, `Build/real2sim/predict.py:42–50`; `Build/real2sim/overlay.py:17–30`, `contracts/overlay/validate.py:65–77`.

The fixer explicitly documented this residual. It is a remaining **gate defect, not an acceptable limit for clearing R-RS**. Equality against the boundary does not bind metadata to the earlier commitment: the digest still covers only `[kind, model, trace]`.

Independent reproduction uses two ordinary prefix-fitted predictions with the same complete five-frame suffix identities but different clip IDs and training values. Save the foreign prediction's commitment, then change **only** its `clip_id` and `training_sha256` to the target's. No trace/model/kind/digest/commitment changes and no suffix access before the metadata edit. `predict.check()`, `score()`, overlay builder and overlay validator all accept. Score reports target clip, 100% coverage and **0 RMS**; the genuine target-prefix prediction against the same observations has **0.09999999999999983 H RMS** (>5%). Changing only the training hash for a same-clip wrong-training prediction is also accepted.

- Unchanged foreign commitment: `85b79e248ef0ece299f3721f88138b6a0a8f5e54cf8c8505a82b3ab95a7e4823`.
- Genuine target prediction: `739c125716b790f3b3c0b527e88db3f24b7ccb408f773b9c5b64d344902bc8ef`.
- Evidence: `recheck/reproductions.json:F1_residual_metadata_relabel_acceptance`; runnable `recheck/reproduce.py`.

**Required before clearance:** version new prediction commitments (v2, or equivalent independently committed custody envelope) to bind clip/source identity, training hash and complete suffix seal/count alongside kind/model/trace. Check that binding in score and overlay paths before observations. Add metadata-only relabel regressions. Preserve historical v1 artifacts/digests as explicitly legacy audited evidence; do not rewrite their old commitments or treat an unbound v1 object as new eligible evidence. Route repair to original S12c/d/e owners. No new physical calibration is implied.

## F2-R [P1] A caller's provenance string is still sufficient to count nonpublic fixtures

**Locations:** `Build/real2sim/score.py:33–36,64–80,89–100`.

The fix correctly rejects the original one-projectile-under-three-keys case and enforces kind, uniqueness and arithmetic coverage. However, the public-input requirement is now represented only by caller-supplied `provenance="image-derived"` plus a `SYNTHETIC*` clip-name blacklist. No source/approval identity reaches the gate and no accepted public-input receipt is checked.

Independent reproduction creates three **synthetic** prefixes named `REVIEW-NONPUBLIC-projectile/bounce/pendulum`, none present in `clips.csv`. It uses the normal projectile, bounce and pendulum predictor functions (distinct actual kinds/digests), scores each against its own simulated trace, and supplies the deliberately false `image-derived` string. The unedited `score()` outputs go directly to `gate()`: **MET, median 0, no shortfalls**. This does not require forging result dictionaries or aliasing a category. Bounce/pendulum model metadata even retains `synthetic` provenance.

Evidence: `recheck/reproductions.json:F2_nonpublic_synthetic_labeled_image_derived_gate`. This is an integrity failure of the internal acceptance API, not a claim that a remote attacker can invoke it, or that current ST03 was mislabeled.

**Required before clearance:** bind eligible scores to an independently checked approved/licensed public clip/source receipt (existing registry/owner receipts), including category eligibility, and carry that binding to aggregation. Fail closed for unknown/missing/synthetic sources regardless of names. Add this three-kind nonpublic-fixture regression. A stronger digest alone cannot make an unverified provenance declaration true. Original S12e owner should implement; no new rights/footage approval is granted here.

## Original findings: verified disposition

| Prior finding | Recheck |
|---|---|
| F1 direct wrong clip/training, precommitted subset, forged overlay suffix | Refused before suffix read where applicable; full seal/count checks work. **Metadata relabel remains open (F1-R).** |
| F2 one projectile aliased three times / same clip / forged coverage | Refused; distinct-category/clip checks work. **Public-source binding remains open (F2-R).** |
| F3 validator rejection fallback | **Closed for tested rejection paths:** wrong object 999, absent stages, missing masks each produce empty observations, null RMS and unscored shortfall. Relative-to-source mapping still yields valid real observations. |
| F4 NaN/Inf observations and category metrics | **Closed for tested cases:** nonfinite PTS/y refused, nonfinite category RMS shortfalls in every category; negative RMS refusal is covered by fresh regression suite. |

## Saved measured result and labels remain honest

- Read-only recomputation reproduces every score field in saved `evidence/S12/gate-rs/gate-rs.json`, including new `provenance="image-derived"`: **0.1981633916341227 H**, **7/466** frames, coverage **0.015021459227467811**, `scored=false`.
- Gate RS **NOT_MET**; all three category aggregates and median null. Every saved input-reference SHA matches; regenerated ST03 prediction still has its historical digest. The fix changed only additive projectile provenance in this artifact, not measurements.
- All **six** derived S12 JSON documents and nested `gate_m` fields are **NOT_MET**. Owning S07 actual gate remains **NOT_MET_INPUT_READINESS**, physics **NOT_RUN**. This is not calibrated-g, metric-scale or physical-accuracy success.

## Fresh checks and limits

- Adapted independent reproduction: **25** original/extended refusal assertions plus metric sanity, both residual bypasses, real-result/hash equality and label checks complete. Defect assertions passing mean the defects reproduced, **not** gate success.
- Replayed fixer's `refusals.py` separately: **10/10 refused**, JSON values exactly match its saved `refusals.json`.
- Canonical read-only `python -B -m unittest discover -s tests/prediction -v`: **35 OK** (existing simulator dependencies; no installation/junction).
- Isolated `python -B -m unittest discover -s tests/pipeline -p test_gpu_stages.py -v`: **6 OK**.
- Snapshot comparison: **26** tracked real2sim/overlay/prediction-test/simulator files match canonical content; only two simulator package JSON files differ in CRLF/LF bytes, with identical normalized content. Code/test bytes for the reviewed fix match exactly.
- Raw evidence: `recheck/reproductions.json`, `recheck/fixer-refusals-replayed.json`, `recheck/source-hashes.json`, `recheck/reviewed-fix.diff`; test outputs under `Run-System/Runs/R-RS-recheck-orch53/`.

Skipped product repairs, new commitments, full unrelated suites, fresh media extraction (unchanged source/errata path was already independently checked in original review), live tracking/GPU/API/deployment work. No service spend. Remaining risk: future false acceptance through F1-R/F2-R; keep parent uncleared and retain honest current NOT_MET/virtual-lab-only fallback.
