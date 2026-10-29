# R-R recheck — S05f (R-R-recheck-orch28)

**Verdict: CHANGES REQUIRED — two P2 input-validation defects remain. Not CLEAR.**

Read-only cross-vendor review is complete. S05f's original counterexamples are repaired for well-formed inputs, but F2's explicit duplicate-input requirement is incomplete. Return the defects below to the S05 owner; no source was edited. **Real Gate R remains FAIL**, scale/orientation/qualifying **0/3**, GPU **3/3**. The review can be DONE without clearing the gate implementation or passing Gate R.

Reviewed source: main snapshot `3fe1eb3bd2161e712744f8ca77266904ac0dc474`, S05f implementation commit `02ad3b2`; Sol/high reviewing Opus-authored changes. Source line numbers below refer to this snapshot. All new evidence is in `recheck/`; prior FINDINGS, counterexamples and traceability remain historical, unchanged.

## Remaining defects

### D1 [P2] Reject duplicate scene JSON members before validating the fixed cohort

**`Build/reconstruction/spike/gate_r.py:123-128` (especially :123); fixed-cohort check :49-50.**

The CLI uses ordinary `json.loads`, which silently discards earlier duplicate keys. A four-entry frame JSON with RM02 twice, RM04 and RM05 therefore becomes a three-key dictionary before the cohort check. The reproduction supplies a failing first RM02 and a passing later RM02; the unique failing control is FAIL, but the actual CLI accepts the duplicate file and emits PASS (two qualifying clips). Hash checks still pass because both synthetic entries carry the correct existing NPZ hash. These are deliberately synthetic measurements, not modified real results.

Required S05 repair: reject duplicate JSON members at deserialization, before information is lost; add a CLI regression for conflicting duplicates, alongside the existing two-/three-/four-ID tests. `test_f2_fixed_cohort` currently cannot exercise duplicate mapping keys.

### D2 [P2] Validate unique, in-cohort timing scene IDs before amortizing lifetime/cost

**`Build/reconstruction/spike/gate_r.py:53-61` (especially :54, :56-57).**

The denominator is the unchecked length of `job["scenes"]`, and repeated assignments overwrite `per_scene[s]`. In the synthetic reproduction a single RM02 job has function 160s and lifetime 600s: correctly FAIL. Repeating RM02 three times changes its amortized lifetime to 200s and the overall verdict to PASS. Two unknown scene IDs instead of repeats produce the same false PASS. Cost allocation is similarly diluted. Current saved receipts have proper unique scene IDs; this is a remaining evaluator input-boundary defect, not evidence of corrupt live billing or a newly failed real timing result. The default receipt builder currently constructs unique lists, but `evaluate` itself accepts these malformed jobs.

Required S05 repair: validate nonempty unique scene lists against the approved cohort before counting, reject conflicting scene coverage instead of silently overwriting, and add duplicate/unknown-ID regressions with a failing control. Do not change the 240s limit or legit two-scene amortization.

Reproduce both: `python -B evidence/reviews/R-R/recheck/reproduce_remaining.py`. The assertions **confirm residual defects**, not correctness; evidence: `recheck/remaining-defects.json`, `duplicate-frames.json`, `duplicate-cli-result.json`. PASS in that last file is synthetic counterexample evidence only.

## Original F1–F6 disposition

| Finding | Recheck | Fresh regression / source |
|---|---|---|
| F1 producer status | Fixed | `test_gate_r.py:54` uses actual `scene_frame.analyse` including reference and A4 fitting, yielding 3/3; evaluator accepts `calibrated` at :65-72. ABSTAIN retained. |
| F2 cohort/quorum | **Partially fixed; D1/D2 remain** | :67 rejects missing/extra scene IDs, real default roster frozen; :77 rejects disjoint scale/orientation successes. Duplicate keys/job membership are not covered. |
| F3 floor/numeric validity | Original cases fixed | :82/:87 reject floor ABSTAIN, impossible/nonfinite angle, invalid scale/time/status. Independent probe also checks NaN/±Infinity/boolean angles and both timing fields. Provenance still requires the annotation/identity evidence, not status strings alone. |
| F4 pre-compare rounding | Fixed | :104; 240.029s fails and 240s passes. Independent probe checks both function and amortized-lifetime boundaries. |
| F5 failure attribution | Fixed | :111; ABSTAIN gravity with a 1° angle is `ineligible`, retaining source reason, not an angular exceedance. Real RM05 is ineligible. |
| F6 inclusive scale boundary | Fixed | :117; 0.9/1.1 raw length ratios pass, 0.8999/1.1001 fail. Independent probe confirms formula and nearer outside values 0.89999999/1.10000001. |

`probe_gate_r.py` now runs repaired expectations (11 reused owner regressions plus independent assertions), not old defect expectations. No dependency/framework/product code added. Its green result does **not** clear D1/D2.

## Thresholds and interpretation

Constants remain **10%, 5°, 240s, two of three**; fixed cohort RM02/RM04/RM05, including explicitly abstained ISS input. `EPS=1e-12` is an explicitly disclosed floating-point boundary repair, not a substantive tolerance increase. Saved source diff and audit assert the constants. Function timing is unamortized; container lifetime is amortized over legitimate scenes, as before. Failed RM02 attempts remain separately disclosed (320.39s cumulative versus 161.73s successful function); no billing was refreshed.

Common-cohort policy is stated in `gate_r.py:44-48,109-112`, machine JSON and `evidence/S05/S05f/GATE_R.md:41-43`: the **same ≥2/3 clips** must pass scale AND orientation; GPU must pass all three, orientation requires floor FIT and gravity estimated. This is stricter than the old independent-quorum implementation. The plan's possible all-three-orientation interpretation is not resolved by calling this policy conservative; the packet explicitly acknowledges that interpretation. Both readings FAIL on current inputs. Controller/owner confirmation is needed before representing a future PASS as resolving that plan ambiguity.

## Q-S05e abstention and fallback

- Visually inspected all three four-view contact sheets and RM02 paper zoom. No sufficiently identified/cited standard object was established in RM04/RM05; no regulation ball was identifiable. This does not claim every small object in low-resolution images is exhaustively identified.
- Recomputed RM02 aspect **1.2355822325**, conditional jitter p5–p95 **[1.1686009169,1.3074544907]**, using existing local NPZ and supplied corners. Owner-provided A4 ratio 297/210 lies outside; Letter ratio 279.4/215.9 lies inside. **ABSTAIN is sound**, because identity remains ambiguous and no physical dimension/orientation is counted. However, this is a reconstruction-dependent diagnostic with ±2px jitter only, not an independently calibrated identity test: it cannot prove the sheet is non-A4 or is Letter. Model error/anisotropy, corner choices and sheet pose are not covered by that interval. A paper standard also does not alone prove horizontality. No new standard was accepted or freshly verified externally.
- Existing local NPZ hashes match receipts/frames **3/3**; contact-sheet hashes match **3/3**. Fresh producer output exactly matches S05f RESULT; floor/gravity match S05d and all references remain ABSTAIN. Evidence: `recheck/evidence-audit.json`, `RESULT-rerun.json`, `rerun-equality.txt`.
- **FAIL → Fallback 2 is correctly recorded**, not Gate R PASS. `GATE_R.md:30-35` labels model scale UNVERIFIED, skips invented desk-height calibration/Fallback 1, and keeps RM05 visual-only. This review verifies the decision/labels, not implementation or rendering of a textured planes/boxes fallback. No physical/calibrated/production success is established.

## Fresh checks

Spike **20/20**, scene contracts **11/11**, repaired probe **11 reused tests plus extra assertions**, all green. Actual gate CLI exit 0 but JSON **FAIL**, exactly equal to saved S05f JSON. Producer CLI exit 0 and RESULT exactly equal. Logs and reproducible scripts are in `recheck/`. Test success/process exit is not gate success.

**Skipped/not checked:** GPU/API/live billing, new footage/standards/licence refresh, fallback UI/rendering, physical calibration. **Risk:** current FAIL/fallback labels are honest, but malformed duplicate/unknown scene inputs can still yield a false PASS; return D1/D2 to S05 before declaring this review CLEAR.
