# Gate RS cross-vendor review — R-RS-orch49

**Verdict: CHANGES_REQUIRED.** Review completed; this is not Gate RS acceptance.
Snapshot: main `5e95fe216f129cb35295637ba36de0b4406aec45`, isolated branch `run/R-RS-orch49`.
Reviewer assigned GPT-6.1 Sol/high; reviewed Opus S12a–e source and reports. No product changes.

**Existing measured shortfall is reproducible and honest:** ST03 diagnostic RMS **0.1981633916341227 H**, 7/466 frames (**1.502%** coverage), `scored=false`; all three category aggregates are null, median null, Gate RS NOT_MET. Gate M remains **NOT_MET** in all six derived JSON documents and their nested gate labels. No calibrated/physical success was found. The defects below permit future false acceptance; they do not establish that the saved ST03 result was falsified.

## Findings — return to original S12 owners

### F1 [P1] Bind the scored prediction to the complete frozen boundary

- Locations: `Build/real2sim/score.py:30–45`, `Build/real2sim/predict.py:42–50`; overlay backstop `Build/real2sim/overlay.py:17–25`, `contracts/overlay/validate.py:64–74`.
- `score()` checks prediction digest and its declared suffix hash, but not prediction clip/training hash or the actual trace's identities against the complete seal. Coverage divides by the supplied trace length rather than independently verified suffix count. The digest covers only `[kind, model, trace]`, not custody metadata.
- Fresh reproduction: a normally generated, precommitted prediction for a **different clip and different training data** sharing suffix timestamps scores 0 under the original clip's name. A precommitted **one-row trace for a five-frame seal** passes and reports 100% coverage, not 20%. These probes do not mutate predictions after their supplied commitment.
- Related overlay hole: replacing only `suffix_identity_sha256` with 64 zeroes leaves the digest valid; `overlay.build()` accepts it despite the original boundary having a different suffix hash. Its frame-map check is alignment, not a complete suffix-seal check.
- Required: before loading observations, compare clip/training binding and require trace `(frame, PTS)` identities to equal the complete sealed suffix exactly, with count consistency. Apply the corresponding suffix check in the builder/contract. Add wrong-clip/wrong-training/precommitted-subset/forged-suffix regressions. Preserve historical artifacts; version new commitments if changing the digest format.
- Owners: S12c/S12d/S12e. Evidence: `reproductions.json` keys starting `F1`.

### F2 [P1] Three dictionary keys are not three eligible motion categories

- Location: `Build/real2sim/score.py:52–60`.
- `gate()` trusts caller-supplied `scored` and dictionary keys, without checking each result's `kind`, source/provenance or category eligibility. A valid score from **one synthetic projectile**, aliased under projectile/bounce/pendulum, returns `MET`, median 0, no shortfall. No new synthetic data is substituted in the saved real artifact; the reproduction exposes the acceptance API.
- Required: validate category-to-kind binding and eligible public-input provenance, carry source/eligibility information into score results, and validate coverage rather than accepting an arbitrary `scored=true`. Missing, mismatched or synthetic-only categories must remain shortfalls. Add this one-projectile-for-three-categories case. Keep the specified median policy; do not silently change it to a maximum.
- Owner: S12e. Evidence: `reproductions.json:F2_one_synthetic_projectile_used_for_all_categories`.

### F3 [P1] Do not score observations rejected by the existing validator

- Location: `Build/real2sim/score.py:77–85`.
- A broad exception handler bypasses `validate_segment()` and returns raw record centroids based only on stream ID membership. It does not limit fallback to an explicitly safe failure class.
- Fresh reproduction on a copy of the actual tracked result: change `record.tracking.object_id` from 2 to **999**, retaining stream ID 2. Validator rejects `record tracks object 999, expected 2`, yet the fallback returns all 26 observations and yields the **same seven-frame RMS**. Invalid identity, checkpoint/stage or mask validation must not become numerical evidence merely because a diagnostic rejection string is recorded.
- Required: fail closed into an explicit unscored shortfall on validation rejection. Keep the already-needed relative-to-source index mapping, not this permissive fallback. Add a wrong-record-object regression. No pipeline-lane fix is necessary to remove this S12 bypass.
- Owner: S12e. Evidence: `reproductions.json:F3_wrong_object_validation_failure_scores_anyway`.

### F4 [P2] Reject nonfinite observations and category metrics

- Locations: `Build/real2sim/score.py:37–49,54–60`.
- `abs(NaN - sealed_pts) > 1e-6` is false, so NaN observed timestamps pass alignment and can score zero with full coverage. A `scored=true, normalized_rms=NaN` third category counts as present; with two zero values the gate reports `MET` and does not even list that category as a shortfall.
- Required: finite numeric/type validation at scoring and aggregation boundaries (including nonnegative RMS), before alignment/coverage/median. Invalid categories are unscored, not present. Add NaN/Infinity regressions.
- Owner: S12e. Evidence: `reproductions.json:F4_nonfinite_data_accepted`.

## Checks that passed

### Prefix-only prediction and S12c errata re-seal

- `Boundary` stores training rows plus suffix hashes/count, not suffix values; `fit_prefix()` uses only training. Existing spy tests and changed-suffix-value tests pass for projectile/bounce; synthetic pendulum continuation is also unchanged by suffix-value changes. Real bounce/pendulum were not evaluated.
- S12a froze 465 identities, quarantining f77 because buggy f76 PTS overlapped it. Errata commit `5718f235a599186984994a4877162e86d5cad6e0` corrects f76 to 2.535867 s before S12c's fit/commit; f77 is 2.569233 s. S12c explicitly supersedes the old seal and freezes 466 identities f77–542. Original evidence remains unchanged.
- **Independent media check closes the reported off-by-one uncertainty:** hash-verified local ST03 source is `7239da801ff407cf5ff047fceb82351724ad35985be298ffcb0e4ba1a53df051`. Fresh ffmpeg extraction of f76 reproduces the original prefix's last JPEG hash `3bb5ce284a7d93239e2ca5e54142a23a751fddcf962b0f58b57401ac5d21c977`; f77 hashes differently. The old bug was PTS labelling, not the last prefix image being a held-out image. No source/video bytes were copied into review evidence.
- Current ST03 prediction regenerates to the committed digest `c81e0f94c110eb229502b37d03c29ec36b11621ed8ca97015f9e671508c9d1b0`; trace identities equal the full actual seal. All input SHA-256 references in the saved Gate RS artifact match current bytes.

### Commit/observation ordering (UTC)

| Evidence | Time / interpretation |
|---|---|
| S12a boundary `3d3c7032` | 21:00:30 commit, before S12 prediction |
| S07 errata `5718f235` | 21:26:01 commit, before corrected fit |
| S12c prediction `8cf86ab8` | **21:32:56 commit**, before both suffix jobs |
| S12d overlay `62fc6fe2` | 21:39:47 commit, same prediction digest |
| S12e job1 reservation/launch receipt | 21:43:19; CUDA OOM, no returned stream observations |
| Original metric commit `81996b02` | **21:44:10**, before successful job2, but after job1 attempt started |
| S12e successful job2 receipt | **21:46:40**; result recorded by 21:49:22 |
| Rebased metric `45c65909` / result `3485ce88` | 21:50:53 committer times; original metric object still exists, with identical PLAN blob |

The local Git/ledger evidence supports predictions preceding suffix observations and a documented pre-observation errata re-seal. It is not an externally timestamped attestation. Do not cite the rebased metric's author date alone, or claim metric registration preceded *every tracking attempt*. No evidence of suffix-to-prediction leakage was found in the saved ST03 path.

### Normalization, coverage and labels

- For valid finite rows already divided by source image height, `sqrt(mean((y_pred-y_obs)^2))` is exactly RMS `|dy|/H`; absolute value before squaring is unnecessary. A fresh constant 0.03 H offset gives 0.03 RMS. No extra division occurs.
- Coverage exactly 80% is eligible, 60% is not; missing/unscored categories yield a null median and NOT_MET. The ordinary arithmetic is sound; F1–F4 concern what it accepts as valid input.
- Median over three eligible categories intentionally permits one high-error category. This is the requested median policy, not a guarantee that each category is <=5%. Report per-category errors, missingness and first-five diagnostics without selecting the latter as the gate value. Image-height normalization is not the older plan's motion-range/period normalization; retain the current scale-free label, not an equivalence claim.
- Gate M NOT_MET is enforced in all derived artifacts/overlay validation. `g` is image-height/s², not calibrated gravity; OLS bands hold clock/scale fixed. Synthetic pendulum and bounce tests are software checks only. Historical abstained params-ST03 remains historical, not a newer valid-parameter contradiction.
- Reporting correction: S12e's phrase "2 of 3 categories unscored" understates eligibility loss: **three categories are gate-ineligible**, although projectile has a partial diagnostic. The saved JSON already handles this correctly.

## Fresh verification and reproducibility

- `python -B evidence/reviews/R-RS/reproduce.py` — **10 assertion groups complete**, including the four defect reproductions and independent real-result/hash checks. This is a review probe: passing a defect assertion means the bug was reproduced, not that the gate passed. Output: `reproductions.json`.
- Isolated worktree `python -B -m unittest discover -s tests/prediction -v` — 30 run, 28 pass, 1 failure + 1 error, both because that fresh worktree lacks ignored simulator Node dependencies. No install or forbidden Build junction was added. Output: `prediction-tests.txt`.
- Same command read-only in canonical checkout, which has those dependencies — **30/30 pass**. All five reviewed modules, overlay validator, pipeline validator and prediction test files byte-match the review snapshot; see `source-and-frame-identity.json`. Output: `prediction-tests-canonical.txt`.
- Canonical `python -B -m unittest tests.pipeline.test_gpu_stages -v` — **6/6 pass** (mocked/local tests, no paid jobs). Output: `pipeline-validator-tests.txt`.
- Media identity: `ffmpeg -v error -i <canonical ST03.mp4> -vf "select=eq(n\,76)" -frames:v 1 -fps_mode passthrough -q:v 2 -f image2pipe -vcodec mjpeg pipe:1` fed directly to SHA-256; repeated for f77. No file emitted. Source hash uses Python `hashlib.file_digest`. Output: `source-and-frame-identity.json`.
- Git original/rebased object inspection saved in `chronology.txt`; job times come from existing `evidence/S12/gate-rs/gpu-ledger.jsonl`.

## Disposition / limits

Return F1–F4 to original S12 owners; do not clear parent Gate RS completion until scoped fixes and cross-vendor re-review. Keep current measured-shortfall/fallback labels; there is no verified real bounce/pendulum success or calibrated physics result. No Build/contracts/tests/canonical-control file was edited, no merge performed, and no Modal/Meta/AWS service or spend used.

Skipped: implementation fixes, new acquisition/tracking, UI/rendering, external timestamp verification and unrelated suites. Risk: saved NOT_MET remains valid, but present acceptance helpers are not safe for a future MET claim until these checks are repaired.
