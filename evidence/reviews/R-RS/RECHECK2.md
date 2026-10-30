# R-RS second recheck — R-RS-recheck2-orch62

**Verdict: CHANGES_REQUIRED. Review DONE; S12e/Gate RS is NOT cleared.**

Reviewed main `d87fe75c440b5d27737ee373df8ab6f4bc6c96d3`, including merged WIP `9d168ce` and verified continuation `3822297`. Assigned cross-vendor Sol/high. No product code, contracts, source registries, existing evidence, or canonical controls were changed. The findings below do **not** allege that saved ST03 measurements were falsified.

## F2-R2 [P1] Registry identity still promotes synthetic observations into real Gate RS eligibility

**Locations:** `Build/real2sim/score.py:67–104,107–142,145–164`; tracker validation at `Build/pipeline/gpu_stages.py:131–163`.

The new receipt correctly checks that the **declared** clip/source is approved, licensed and category-appropriate. It never establishes that the prefix or observed suffix belongs to that source. `score()` accepts an unrestricted observation loader, while `_eligible()` ignores even an explicit `provenance="synthetic"`. `st03_observations()` does not close this gap: it discards the clip/source identities returned by `validate_segment()`, without comparing them to the committed boundary/receipt. That validator checks structure/object/stages/masks, not source custody.

### Independent reproduction

1. Generate ordinary synthetic polynomial prefixes and five-frame suffix seals, using **PJ03 / BN01 / PD02** and their actual acquisition-registry SHA256 values as the declared identities. No clip or tracker bytes are read.
2. Use the normal `projectile`, `bounce`, and `pendulum` predictors to make genuine v2 commitments **before** calling each observation loader. Bounce/pendulum parameter provenance explicitly says `synthetic`.
3. Score against the generated traces. Pass `provenance="synthetic"`; do not alter any score result or receipt. Feed those three original results to `gate()`.
4. Result: **MET; median 0; all three category RMS values 0; coverage 100%; no shortfalls**. Relabeling only the descriptive provenance to `image-derived` also returns MET.
5. Separately feed hand-authored synthetic tracker-shaped payloads through the actual `st03_observations()` → `validate_segment()` path. Their raw clip IDs and source hashes deliberately **differ** from the receipt. All three return `validate_segment OK`, and their scored outputs again yield **MET, median 0**. No checkpoint/media bytes or GPU were used.
6. Mutating only the existing real raw ST03 record's clip ID or source SHA also returns `validate_segment OK` with identical observations. Wrong object/missing stages/missing masks still reject correctly.

Evidence: `recheck2/results.json` → `known_public_identity_synthetic_observations`, `known_public_identity_false_image_label`, `synthetic_tracker_payload_wrong_source`, `tracker_identity_probes`. Runnable: `python -B evidence/reviews/R-RS/recheck2/review.py`.

**Disposition of declared limit:** a **remaining gate defect**, not an acceptable limit for clearing F2-R. It is reasonable not to cryptographically prove that every coordinate was extracted from specific pixels. It is not sufficient to call arbitrary/synthetic observations public evidence merely because the caller knows a public clip's ID and SHA. The cited tracker path demonstrably does not enforce the missing source relationship. This is an internal acceptance-integrity defect, not a claim of a remotely exposed endpoint.

**Smallest required repair:** preserve generic synthetic scoring, but keep it gate-ineligible; derive eligible prefix/suffix inputs through the existing accepted tracking-evidence path, with expected clip/source identity, artifact custody/hash, seal/timebase and validation outcome carried into scoring/aggregation. Compare tracker identities rather than discarding them. Do not treat adding or changing a caller string as sufficient proof, and do not invent a new arbitrary per-job approval requirement. Add the known-public-ID/true-SHA synthetic regression and wrong-source tracker regression. No new GPU job or secure-attestation system is necessary to fix this acceptance boundary.

## F2-A [P2] Approval parser accepts an explicit denial as a positive approval

**Location:** `Build/real2sim/score.py:45–47`.

The use check is a substring search across the entire Markdown file, not a positive grant in the authoritative Use block. Using an isolated copy of the three input registries under this review's Owns, both of these documents yield a valid PJ03 receipt:

- Existing approval changed only to `**Use:** NOT approved for local scene/tracking pipeline work ONLY`.
- `**Approved IDs:** PJ03.` followed by `**Use:** DENIED.` and an unrelated `Prior request: local scene/tracking pipeline work` line.

Thus a later owner refusal/restriction that retains the ID list or quotes the old request need not fail closed. The saved current approval is positive and unaffected; no actual revocation is alleged. Spaces in the ID list fail closed, as the fixer documented, but **not every semantic format change fails closed**.

Evidence: `results.json:approval_parser`; full `public_receipt()` calls, not just isolated regex matching. Required: recognize the supported **positive scoped grant** from the authoritative section (or an exact reviewed approval receipt), rejecting negated/unrecognized Use text and unrelated mentions. Do not reinterpret a refusal as authority.

## F2-L [P2] Licence regex recognizes invalid identifiers as allowed public licences

**Locations:** `Build/real2sim/score.py:31–32,48–49`.

Full receipt calls on isolated copies accept `pd-nc`, `pd-not-public`, `CC-BY-999.99`, and `CC-BY-.`. These are arbitrary strings matched by `pd-[a-z-]+` / `[0-9.]+`, not evidence of a permitted licence. Standard `CC-BY-NC-4.0`, `CC-BY-ND-4.0` and `CC-BY-NC-SA-4.0` correctly refuse. No current approved clip was found to have one of the malformed labels; this is a fail-closed validation defect on future/corrupted metadata, not a claim that current footage is unlawfully licensed.

Evidence: `results.json:licence_regex,licence_full_receipt`. Required: a finite supported identifier/version allowlist consistent with the already accepted source/licence evidence; reject unknown PD suffixes and malformed/unknown CC versions. A matching label alone still is not legal verification of rights.

## Disposition of earlier findings

| Finding | Fresh result |
|---|---|
| F1 / F1-R custody relabeling | **Closed for tested paths.** V2 commits kind/model/trace/clip/source/training/seal/count. Nine single-field edits, foreign predictions, full metadata-only relabels, overlay relabels and a self-consistent rehashed subset refuse before suffix reads. |
| Legacy v1 promotion | **Closed on supported tested routes.** V1 remains audit-readable; score and overlay builder refuse; default overlay validator rejects v1; every category aggregate refuses a v1 result. Historical v1 files remain byte-equivalent to pre-fix history. |
| F2 alias/category/coverage | Category matrix and cross-category receipt reuse refuse; duplicate prediction identities and forged coverage refuse. Missing/duplicate CSV rows, missing/duplicate registry hashes, absent approval and wrong experiment refuse. Nonpublic synthetic IDs refuse. **Known-public identity synthetic evidence remains open (F2-R2).** |
| F3 fallback after tracker rejection | **Closed for original tested rejection paths:** wrong object, absent stages and absent masks return empty observations/unscored shortfall. Identity validation is a separate remaining F2-R2 issue. |
| F4 nonfinite arithmetic | **Closed for tested paths:** nonfinite observation PTS/y refuse; all categories reject NaN/Inf/negative RMS with otherwise valid public receipts. |

## Saved measurements and Gate M remain unchanged

- Independent ST03 recomputation matches **every score field** and the saved aggregate, with all saved input hashes matching.
- RMS **0.1981633916341227 H**; scored **7/466** sealed frames; coverage **0.015021459227467811**; `scored=false`. Numerical fields are identical to pre-fix2 snapshot `9d1a9ae`; new receipt/commitment metadata does not change them.
- Saved Gate RS is **NOT_MET**, all category aggregate errors and median null. The synthetic MET results above exist only in clearly labeled review evidence; the actual gate artifact was not regenerated or edited.
- Recursively inspected all **18 JSON files** under `evidence/S12`: all **28** `gate_m` fields are **NOT_MET**. Owning S07 actual Gate M remains **NOT_MET_INPUT_READINESS**, physics **NOT_RUN**. No calibrated/physical success claim.

## Fresh verification

- Independent `review.py`: exit 0; **28 named refusal probes**, category/registry/arithmetic controls, all three new findings, real-result/hash equality and recursive Gate M checks. Passing defect assertions mean **reproduced defects**, not product success.
- Fixer's original `replay.py`: exit 0; parsed JSON **exactly equals** its saved `replay.json`. Its narrower F1-R/F2-R probes now refuse as claimed.
- Canonical read-only `python -B -m unittest discover -s tests/prediction -v`: **37 OK**, using existing simulator dependencies; no dependency install/junction.
- Isolated `python -B -m unittest discover -s tests/pipeline -p test_gpu_stages.py -v`: **6 OK**.
- `verify_sources.py`: **27** reviewed source/test/simulator files match canonical; 25 byte-identical, two simulator package JSON files differ only in CRLF/LF. Three historical v1 artifacts unchanged from pre-fix history. Details: `source-hashes.json`; full merged source/test diff: `reviewed-fix.diff`.

Skipped product repair, fresh media extraction, live tracking/GPU/API/deployment, and unrelated suites. No service spend. Remaining risk: internal false Gate RS eligibility; retain S12e PARTIAL and the honest measured NOT_MET/virtual-lab-only fallback until repaired and independently rechecked.
