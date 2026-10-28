# R-M2 independent review — S07f source response (run/S07f 233e5e2, impl 893dfbe vs a0b603d)

Verdict: **BOUNDED ACCEPT** of the F1–F6 response. No reachable pass-escalation bug
found. Three low-severity, fail-closed or trusted-caller observations below; none
blocks acceptance. Nothing here approves S12, physical Gate M or calibration.

Source: `C:/Users/HP/.codex/worktrees/s07f-gate-decision/2026-10-26 - Meta Global AI Developer Hackathon`
(read-only; `git status` clean before/after). Reproducers: [probe.py](probe.py) →
[probe-output.json](probe-output.json) (synthetic only; run from source root).

## Checks per finding

| R-M | Check (gate_m.py lines) | Result |
|---|---|---|
| F1 | L85-89 qualify from finite `g_m_s2` in g-space; L105-107 mean error from g; caller `relative_error` ignored | PASS. Inclusive both edges (`hi_edge` true, `nextafter` false; test L108 lower). NaN/inf/bool g excluded (L78). Declared errors None/str/NaN/-1/99 ignored (test L98). |
| F2 | L81-83 count only if kwarg `is True`; canonical str IDs, case-sensitive | PASS. Per-trial `independence_verified=True` in dicts → 0 (`dict_self_flag`). Truthy 1/'yes'/None and an object with `__eq__`→True all deny (`eq_true_obj`). 'A ' / NBSP padding rejected; 'A'/'a' distinct only under trusted flag. Actual CLI calls `summarize(trials)` (L192) → default deny. |
| F3 | L66 coverage blocker always appended; L89 `not blockers` | Intentional abstention preserved; no k/interval invented. Evaluator cannot pass via real path — correct under S07d. |
| F4 | GATE_M.md S07f section | Suffix RMSE stays diagnostic; no Gate RS threshold imported. Correct ownership. |
| F5/F6 | UNCERTAINTY.md L95-104 | Conditional-limit text only; no chi-square/relative/multiplier cutoff invented. Acceptable; physical validity remains unresolved hold. |

## Findings (prioritized; all LOW)

1. **L1 – exact-type check misclassifies float subclasses as "input readiness".**
   `gate_m.py:78` `type(g) in (int, float)`. A `float` subclass (e.g. `numpy.float64`)
   yields `measured_count=0`, `status=NOT_MET_INPUT_READINESS`, `physics_evaluation=NOT_RUN`
   (`float_subclass` probe). Fail-closed, not reachable today (`free_fall.py` returns
   plain float; CLI never fits). Risk: a future fitter returning NumPy scalars would be
   mislabelled as not run rather than measured. Fix when integrating: coerce with
   `float()` at `evaluate_record` L61, keep the bool exclusion.
2. **L2 – "canonical ID" only means `str.strip()` whitespace.** Zero-width-space
   ('\u200bA' vs 'A') and NFC/NFD ('é' vs 'e\u0301') count as distinct
   (`zwsp_ids`, `nfc_nfd_ids` = 3). Only matters when a trusted caller passes
   `independence_verified=True`; that caller already owns provenance (documented
   GATE_M.md L66-72). Documented trusted-caller limit, not a reachable bug.
3. **L3 – reported error exceeds .05 at the inclusive edge.** `hi_edge_err` /
   `lo_edge_err` = 0.05000000000000008 while the trial qualifies. Documented
   (GATE_M.md L63-64). Downstream consumers must use `gate_passed`/`qualifying_count`,
   never re-threshold `mean_relative_error`.

Fail-loud, acceptable: non-dict trials → AttributeError; generator → TypeError
(L90 `len`). Four trials, unmeasured third, truthy coverage 1, string blockers all deny.

## Actual decision review

Fresh CLI regeneration (to %TEMP%) is JSON-equal to `evidence/S07/S07f/actual-gate-m.json`:
`NOT_MET_INPUT_READINESS`, physics `NOT_RUN`, 8 candidate records (FF01-04, ST03,
RP01-03), scene-approved 1 (ST03), metric-approved 0, eligible 0, measured 0/3.
AP15: clips.csv `UNAPPROVED_CANDIDATE`, scale `APPROXIMATE_SOURCE_PRIOR_ONLY`,
cadence `ARCHIVE_TRANSCODE_CADENCE_UNVERIFIED`; DECISION.md NOT_TRACKABLE/NOT_RUN,
no Moon fit — consistent. Calibrated table-plane fallback recorded **UNAVAILABLE**;
virtual lab/Mystery-g **simulated-only**. DECISION.md asserts no S12 unlock, no
physical pass, no new thresholds — consistent with source. Nothing here infers approval.
