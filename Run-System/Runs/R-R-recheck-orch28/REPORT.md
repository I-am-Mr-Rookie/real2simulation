# R-R-recheck-orch28 — DONE (negative review; not CLEAR)

**Result: two P2 defects remain; return to S05 owner. Real Gate R remains FAIL, Fallback 2/scale UNVERIFIED recorded correctly.** Read [RECHECK.md](../../../evidence/reviews/R-R/RECHECK.md); do not interpret DONE as gate/code clearance.

## Contract / timing / scope

- Controller `01a1882d-3481-7ce3-8f88-45c942e341cd`, contract `R-R-recheck-orch28`, follow-up of accepted R-R. Parent project Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97` inherited from delegation; no new chat/project created or launcher association claimed.
- Assigned cross-vendor route **gpt-6.1-sol/high**, reviewing Opus S05f. Actual model identity not independently queryable. Coding quota **OpenCodex-managed; not polled**; tokens unobservable. CPU only; **$0 incremental GPU/API/service spend**, no paid calls/jobs/downloads.
- Issue **2026-10-29T15:35:05+00:00**, first observed clock 15:35:27Z; implementation cutoff **16:00:05Z**, full deadline **16:05:05Z / 22:05:05 Dhaka**. Actual completion timestamps in TIMEBOX.json. Full assigned read-only review completed early; unresolved implementation fixes belong to S05, not unfinished authorized worker implementation. No early-incomplete exception used.
- Base `3fe1eb3bd2161e712744f8ca77266904ac0dc474`, source S05f `02ad3b2`; branch `run/R-R-recheck-orch28`, worktree `.worktrees/R-R-recheck-orch28`. At 15:47Z, main `90d6f45` had **no differences in the four reviewed source/test files** versus this snapshot.
- All authored changes confined to `evidence/reviews/R-R/` and `Run-System/Runs/R-R-recheck-orch28/` in this worktree. Source/canonical controls/other lanes untouched. Original untracked owner PDF in canonical checkout preserved. No main merge or push; controller integrates.

## Findings / acceptance

- F1/F3/F4/F5/F6 original defects repaired with passing named regressions. F2 missing/extra/default-cohort and common-quorum cases repaired, but duplicate JSON keys are discarded before validation (**gate_r.py:123-128**) and duplicate/unknown timing IDs inflate lifetime/cost denominator (**:53-61**). Each P2 has a runnable synthetic reproduction and failing control. No present real receipt corruption asserted.
- Thresholds remain 10%, 5°, 240s, ≥2/3; EPS 1e-12 is roundoff-only. Same ≥2/3 clips must pass scale AND orientation; GPU all 3. Stricter all-three-orientation interpretation remains acknowledged, never silently resolved; current verdict FAIL under either.
- Q-S05e: inspected all 12 input views/contact sheets + paper zoom. RM02 aspect/jitter exactly reproduced; ambiguous identity makes ABSTAIN correct. Model-space jitter is **not independent proof of non-A4/Letter identity**. No accepted object length/orientation invented. RM05 remains gravity-ineligible.
- FAIL → Fallback 2/UNVERIFIED scale recorded correctly; no verification of textured fallback rendering or physical calibration claimed.

## Fresh checks / evidence

All Python commands used `-B`/`PYTHONDONTWRITEBYTECODE=1`; TEMP/TMP redirected to owned `evidence/reviews/R-R/recheck/tmp`. Python 3.14.5 and installed dependencies reused. Each command exited 0; CLI success is not gate success.

| Check | Fresh result; evidence in `evidence/reviews/R-R/recheck/` |
|---|---|
| In spike dir: `python -B -m unittest test_scene_frame test_gate_r test_rm02_result -v` | **20/20 OK**, spike-tests.txt |
| `python -B -m unittest discover -s contracts/scene -p 'test_*.py' -v` | **11/11 OK**, scene-tests.txt |
| `python -B evidence/reviews/R-R/probe_gate_r.py` | **11 reused owner regressions + independent numeric/default-cohort assertions pass**, repaired-probe.txt; old defective expectations replaced, historical counterexamples unchanged |
| `python -B Build/reconstruction/spike/gate_r.py --frames evidence/S05/S05f/RESULT.json evidence/reviews/R-R/recheck/GATE_R-rerun.json` | **FAIL, 0/3 scale, orientation, qualifying; GPU 3/3**, exact saved S05f JSON equality; gate-rerun.txt, rerun-equality.txt |
| `python -B Build/reconstruction/spike/scene_frame.py evidence/S05/S05d/manifest.json evidence/reviews/R-R/recheck/RESULT-rerun.json` | Exit 0; **exact saved producer JSON equality 3/3**; producer-rerun.txt empty because CLI prints nothing |
| `python -B evidence/reviews/R-R/recheck/evidence_audit.py` | Local NPZ custody **3/3**, sheets **3/3**, floor/gravity unchanged, references ABSTAIN, constants checked, RM02 aspect **1.2355822325**, conditional p5–p95 **[1.1686009169,1.3074544907]** reproduced; evidence-audit.json/.txt |
| `python -B evidence/reviews/R-R/recheck/reproduce_remaining.py` | Both residual defects reproduced (and unknown-job-ID variant); unique failing control versus duplicate CLI **FAIL→PASS**, single real scene lifetime **600s→200s** via denominator inflation; remaining-defects.json/.txt. Synthetic-only, not successful product evidence |
| `git diff --check` | Pass; normal CRLF warning only. Final receipt checked with worker_timebox.py; evidence saved with run. |

Frozen source/receipt/report hashes in evidence-audit.json; complete source delta versus reviewed R-R snapshot saved losslessly as gate-source-diff.json. A first staged diff check caught raw patch context-space lines in the generated text log; JSON escaping preserves the full patch without staging trailing whitespace. No source or threshold changed in this branch.

## Ponytail full / tools / decisions

Read and applied installed `C:/Users/HP/.codex/plugins/cache/workspace-directory/ponytail/5.3.3/skills/ponytail/SKILL.md`, canonical instructions and manual/timebox policies. Read prior R-R, S05f, S05e reports. Traced evaluator CLI, producer, tests, actual NPZ/manifest/receipts, owner Q-S05e and approved-plan threshold text.

Smallest complete change: replace obsolete review probe with existing `GateR` tests plus small independent assertions; reuse original traceability `read/sha`, diagnostic `edges` and existing synthetic fixture helpers. New evidence scripts contain assert-based controls, stdlib + installed numpy only. Imported S05 diagnostic without running its writing main. No competing S05 fix, dependency, framework, abstraction, new object standard, GPU rerun, or optional browser/tool work.

Controller next: read D1/D2, return validation changes to S05 owner and re-review; preserve real FAIL/fallback/physical holds. No new owner question or consent needed for this review. Canonical controls intentionally not edited.

## Communication / integration

One mandatory brief Ponytail/work notice; one authorized nonterminal finding callback after reproductions; one exact concise completion callback/final pointer. Higher-priority Ponytail skipped/risk line is the minimal final-format exception. No optional progress narration, worker launches, quota polling or automation. Worktree/branch retained for controller; ignored run folder force-staged by exact owned path only, no ignore-policy change.

**Skipped/not checked:** GPU/API/live billing, new footage/standards/licence refresh, fallback rendering, physical calibration. **Risk:** malformed duplicate/unknown scene inputs can still false-PASS; this review is DONE but NOT CLEAR.
