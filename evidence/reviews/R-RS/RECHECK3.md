# R-RS third recheck — R-RS-recheck3-orch74

**Verdict: CHANGES_REQUIRED. Review DONE; do not clear S12e.**

Reviewed main `35c9a9069e72078e7d51edeaf834a7139d6652e0`, including S12e-fix3-orch66. Assigned cross-vendor `gpt-6.1-sol/high`. Read-only product review: no Build/, tests/, evidence/S12, source registry or canonical control edits. All attack artifacts in `recheck3/` are explicitly synthetic; their reported MET is a reproduced bypass, **not** measured Gate RS success.

## F2-R3 [P1] Caller-authored tracker JSON is treated as accepted real evidence

**Locations:** `Build/real2sim/score.py:97–114,117–121,124–137,157–160`; structural validator `Build/pipeline/gpu_stages.py:131–163`.

`Tracked` accepts any readable file under the repository root. Its SHA256 is computed from that same caller-selected file and later compared with itself. There is no independent accepted tracking-run receipt or artifact-digest registry. `validate_segment` checks shape, stages, masks and identity labels, not that a job generated the file from the approved clip. Prefix agreement also compares two caller-authored objects. Thus the new path/checksum is integrity after selection, **not custody establishing real-scene eligibility**.

### Reproduction (no patched functions, subclasses or edited score results)

1. Reuse the previous review's synthetic polynomial-prefix fixtures and normal projectile/bounce/pendulum predictors. Declare actual approved PJ03 / BN01 / PD02 IDs and acquisition-registry hashes.
2. Commit each normal v2 prediction before invoking its loader.
3. Hand-author a tracker-shaped JSON containing the generated prefix and predicted suffix, correct declared IDs, bogus checkpoint/frame hashes, and full-image RLE masks. Each file explicitly warns `SYNTHETIC HAND-AUTHORED: no media/checkpoint/GPU read`.
4. Pass the ordinary native `Tracked(boundary, review_file, frame_pts)` to `score(..., "image-derived")`; feed its **unmodified** results to `gate()`.
5. All three trackers validate; prefix discrepancy is effectively zero; coverage is 5/5; all three independent public receipts pass; **Gate RS returns MET, median 0, no shortfalls**. No clip/checkpoint bytes or GPU job were used. Replacing the descriptive provenance with the exact literal `synthetic` does refuse, but a caller label is still the only distinction for these generated files.

Evidence: `recheck3/results.json:F2_R3_forged_native_Tracked`; persistent `*-SYNTHETIC-track.json`; runnable `recheck3/review.py`. This closes neither the original known-public-identity synthetic-evidence finding nor its custody requirement. It does **not** require per-pixel cryptographic attestation: an independently accepted run/artifact receipt binding clip/source, tracker artifact digest, presentation map and frame range would establish a meaningful trust boundary. Unknown caller-authored artifacts must remain diagnostic-only even when internally consistent.

**Required repair:** gate eligibility must consult independent accepted tracking custody, rather than infer acceptance from file location, a self-carried hash or successful structural validation. Keep explicit synthetic refusal and the existing identity/digest/path checks. Add this unpatched end-to-end case, not merely lambda-loader regressions.

## F2-C [P1] Native Tracked loader can validate a different prefix from the prediction's

**Locations:** `Build/real2sim/score.py:97–108,109–113,145–160,124–137`.

`score(target_boundary, ..., Tracked(other_boundary, ...))` never verifies that the loader is bound to the target boundary. The loader validates custody against **its own** `self.boundary`; the prediction validates against the separate argument. Evidence contains clip/source and prefix counts, but no committed training digest, and `gate()` re-reads only the suffix digest. Same-clip/source training transplants therefore survive.

### Reproduction and controls

- Shift the target synthetic training prefix by **0.03 image heights**, fifteen times `PREFIX_TOL=0.002`; generate its genuine new v2 prediction against the same five-frame seal. A correctly bound `Tracked(target_boundary, artifact, ...)` refuses with `prefix custody`.
- Instead pass the native `Tracked(original_boundary, artifact, ...)` to `score(target_boundary, ...)`. Scoring succeeds with RMS `0.029999999999999936`; `_eligible("projectile", result)` returns **True**. With the other two probe results the aggregate remains **MET**. No score/evidence dictionary is edited.
- Independently use the **existing genuine ST03 artifact**, not a forged track: shift a copied training record by 0.01 H. The correctly bound loader refuses; a loader bound to the original real boundary passes into the shifted prediction's `score()`, and `_tracking_ok` accepts. The real 7/466 coverage shortfall still prevents actual gate eligibility; it does not repair the missing training binding.
- Direct tolerance controls accept 0.0019 H and refuse 0.0021 H as configured. The noise tolerance itself is **not** the finding; bypassing which prefix is checked is.

Evidence: `results.json:prefix_custody,F2_C_real_artifact_wrong_boundary`.

**Required repair:** compare native loader custody to the exact scoring boundary before suffix access; carry/bind the target training, suffix identity/count and prefix cutoff into tracking evidence, and recheck those against the committed prediction/accepted custody at aggregation. A trusted-artifact list alone does not fix this independent mismatch (the real-artifact probe still applies).

## Earlier findings: disposition

| Finding | Fresh result |
|---|---|
| F2-R2 generic synthetic loader; wrong raw tracker identity | Narrow paths fixed: generic image-derived loaders are ineligible; explicit `synthetic` refuses; wrong raw clip/source identity refuses. **Overall custody/eligibility remains open: F2-R3 and F2-C above.** |
| F2-A [P2] positive approval grant parser | **Closed for reported/tested cases.** Full public-receipt calls refuse negated grant, unrelated historical mention, duplicate/missing grants and same-line revocation; actual positive grant accepts. |
| F2-L [P2] invalid licence identifiers | **Closed for reported/tested cases.** Finite allowlist refuses NC/ND, `pd-nc`, `pd-not-public`, malformed/unknown CC identifiers and unknown versions. No fresh legal/rights conclusion is inferred from a label. |
| F1-R / F1 prediction custody | **Remain closed on tested paths.** Nine v2 field changes, foreign prediction, metadata-only relabel, self-consistent truncated trace, overlay relabel, and v1 promotion refuse; score refusals occur before suffix access. F2-C is a separate missing loader-to-boundary binding, not a bypass of v2 hashing. |
| F2 category/duplicate/coverage checks | Category/receipt matching, duplicate prediction identity and forged coverage remain enforced; positive receipt controls are exercised without eligibility monkeypatching in the review probe. |
| F3 rejected tracker fallback | Wrong object, missing masks and missing stages return empty observations plus explicit unscored rejection; no centroid fallback. |
| F4 nonfinite arithmetic | Nonfinite observation PTS/y refuse; aggregate rejects NaN/Inf/negative RMS and inconsistent frame counts/coverage, with otherwise accepted receipt/tracking controls. |
| Path/digest/identity transplants | Relative and absolute escapes, wrong artifact SHA, observation digest and cross-identity evidence refuse. |

## Fresh checks and unchanged actual measurements

- `python -B evidence/reviews/R-RS/recheck3/review.py`: exit 0; produces `results.json`, `source-hashes.json`, three explicitly synthetic fixture files. `probe-run.txt` records the successful adversarial run. No production writer such as `score.main()` was called.
- Existing prediction suites: `test_score.py` **16 OK**, `test_boundary.py` **7 OK**, `test_predict.py` **5 OK**, `test_overlay.py` **8 OK**. Pipeline `test_gpu_stages.py`: **6 OK**. Logs beside the probe. These passing regressions do not negate the two unpatched P1 reproductions.
- Recomputed actual ST03 score matches **every** carried field in the saved artifact; aggregate equals saved result: **NOT_MET**, RMS **0.1981633916341227 H**, **7/466**, coverage **0.015021459227467811**, median null, all three categories shortfall.
- All 28 `gate_m` fields across existing S12 JSON remain `NOT_MET`; owning Gate M is `NOT_MET_INPUT_READINESS`, physics `NOT_RUN`. Source/evidence fingerprints are unchanged before/after probes.

Ponytail full: reused existing fixture constructors and production readers, standard-library assertions and isolated temporary directories; no dependency install, product fix, new custody framework, full unrelated suite, simulator dependency setup or GPU/API job. `test_params.py` was not rerun: no parameter-transfer code changed and this isolated worktree lacks simulator dependencies. No physical/calibration claim, saved measured success or actual evidence falsification is alleged. Next action: return both P1 defects to the original implementation owner; independent re-review is still required after repair.
