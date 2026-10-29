# R-R second recheck — CLEAR (D1/D2 implementation only)

**Verdict: CLEAR. No remaining D1/D2 defects or new input-boundary bypass found in the repair's changed lines. Real Gate R still FAIL; this is not a physical/calibration or product-gate PASS.**

Reviewer: assigned gpt-6.1-sol/high, cross-vendor review of Opus-authored S05f-fix-orch32. Reviewed main snapshot `47afeeedbe39891855f4fdb95a67bbb9a2d11913`, repair `56604618585aa0bce91e37c146cf5542c3c9bf38`. Production source, saved results and canonical controls were read-only. File:line references below are from this snapshot.

The contract's `recheck/RECHECK.md` pointer does not exist; the merged prior review is `evidence/reviews/R-R/RECHECK.md`. Its original two P2 findings are the review baseline; a historical-status banner now points here.

## Disposition

| Prior finding | Source check | Independent fresh result |
|---|---|---|
| D1 [P2]: last-wins duplicate JSON scene/member keys | `Build/reconstruction/spike/gate_r.py:44-54`, CLI `:141` | Rejected before information loss via `object_pairs_hook`; used for **all three** CLI inputs. **7 real CLI rejection checks**: top-level and nested/escaped-equivalent key duplicates in frames, S05c and orch14; original conflicting RM02 counterexample. Nonzero exit, explicit duplicate-member error, **no output created** in fresh temporary paths. Unique-bad control actually executes and remains FAIL. |
| D2 [P2]: duplicate/unknown job IDs dilute denominator or overwrite prior coverage | `Build/reconstruction/spike/gate_r.py:67-71` | Nonempty list, uniqueness, cohort membership and cross-job disjointness checked **before** amortization. **11 direct rejection checks**: repeats, unknowns, empty/string/null, wrong scalar types/spelling/whitespace and overlap in both orders. Original 600s failing control remains FAIL; pre-fix repeated/unknown-ID false-PASS inputs now reject. |
| Preserve legitimate two-scene amortization | Existing arithmetic `:72-78`, guarded by `:67-71` | Valid RM04+RM05 job still gives **262/2 = 131s** and **$0.06/2 = $0.03** each; function time **178s stays unamortized**. Synthetic common-cohort 2/3 control PASS; 480s lifetime/2 and 240s function boundaries inclusive, immediately above FAIL. Missing timing coverage FAIL. Real two-scene receipt passes validation and complete real result is unchanged. |

Changed-line boundary inspection found no acceptance bypass: decoded escaped-equivalent keys compare equal; every object nesting is checked; malformed IDs cannot inflate the denominator; overlap cannot replace prior timing regardless of job order. Non-hashable IDs raise TypeError rather than ValueError, but **fail closed** (two additional probes); no new PASS. No severity/file:line defect to return to S05 owner.

## Unchanged thresholds and honest real result

`snapshot_audit.py` compares the repair's pre/post threshold assignment ASTs and asserts exact runtime values: **10%, 5 degrees, 240s, 2 qualifying clips out of the fixed 3, EPS 1e-12, RM02/RM04/RM05**. No threshold, quorum, eligibility or roster relaxation; no source diff in the review branch.

Fresh real CLI output (`GATE_R-rerun.json`) is **parsed-equal AND byte-identical** to `evidence/S05/S05f/GATE_R.json`: **FAIL**, scale **0/3**, orientation **0/3**, qualifying **0/3**, GPU **3/3**. Input receipt hashes and full reviewed production diff are frozen in `snapshot-audit.json`. Fallback 2 and unverified-scale/physical holds stay unchanged.

## Fresh checks (all evidence in this directory)

| Command (repository root unless specified) | Result / evidence |
|---|---|
| Spike cwd: `python -B -m unittest test_gate_r -v` | **14/14 OK**, `gate-r-tests.txt` |
| Spike cwd: `python -B -m unittest test_scene_frame test_gate_r test_rm02_result -v` | **23/23 OK**, `targeted-spike-tests.txt` |
| `python -B -m unittest discover -s contracts/scene -p 'test_*.py' -v` | **11/11 OK**, `scene-tests.txt` |
| Spike cwd: `python -B -m unittest discover -p 'test_*.py' -v` | **86 entries: 85 OK, 1 import error**, `spike-tests.txt`; `modal` not installed, `test_modal_scenes` cannot import. Same recorded error in S05f-fix-orch32; not a new failure and not claimed green. |
| `python -B evidence/reviews/R-R/probe_gate_r.py` | **14 owner tests + independent numeric/cohort checks PASS**, `repaired-probe.txt`; count now reflects actual suite size. |
| `python -B evidence/reviews/R-R/recheck/reproduce_remaining.py` | **PASS: repaired assertions**, `repaired-reproduction.json/.txt`; synthetic-only. Old defect expectations superseded, historical side files untouched. |
| `python -B Build/reconstruction/spike/gate_r.py --frames evidence/S05/S05f/RESULT.json evidence/reviews/R-R/recheck2/GATE_R-rerun.json` | Exit **0**, verdict **FAIL**, `gate-rerun.txt`; command success is not gate success. |
| `python -B evidence/reviews/R-R/recheck2/snapshot_audit.py` | **PASS**, `snapshot-audit.json/.txt`: threshold AST equality, real byte equality, pre-fix false-PASS sensitivity controls, fail-closed malformed types. |
| `git diff --exit-code HEAD -- Build/reconstruction/spike contracts/scene` / `git diff --check` | Source unchanged / clean whitespace. |

Python used `-B`/`PYTHONDONTWRITEBYTECODE=1`; temporary CLI/test writes stayed under the owned review subtree. CPU only, **$0**; no service/GPU/API call, dependency installation, quota polling or source fix.

**Skipped/not checked:** Modal-dependent test module (missing package), live GPU/API/billing, broader unchanged-source audit, new footage or physical/calibration success. **Risk:** CLEAR is limited to D1/D2 repair; real Gate R remains FAIL and the full spike discovery is not green in this environment.
