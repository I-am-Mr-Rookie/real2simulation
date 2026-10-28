# S07f — PARTIAL: source response ready; independent acceptance pending

**Delivered:** adjudication of all six R-M findings, two verified summary-boundary
fixes, five additional regressions, actual Earth/Apollo/fallback decision. Required
other-vendor follow-up of gate changes is **not yet performed**; controller owns
that review and acceptance. No physical Gate M pass or S12 unlock.

## Actual decision

- Earth: **NOT_MET_INPUT_READINESS**, physics **NOT_RUN**; eight candidate rows,
  one scene/tracking-approved Earth candidate, **0 metric-approved / 0 eligible /
  0 measured**. g/error/coverage null. No denominator reduction or measured-failure
  claim. RP01 clock/projection holds remain, not a floor-contact requirement.
- Apollo AP15: owning manifest, metadata audit and approval receipt retain
  **NOT_TRACKABLE**, outside approved use; **NOT_RUN**, lunar g/error/coverage null.
  No Moon fit, fabricated 15% success, media decoding or new approval.
- Approved fallback scope recorded in `evidence/S07/S07f/DECISION.md`: lead with
  virtual lab/Mystery-g **simulated-only**; any Measure mode restricted to verified
  table-plane homography experiments. Currently **UNAVAILABLE**, not measured-ready:
  no metric grant, validated plane/homography/calibration/clock/custody/coverage.
  No fallback implementation or canonical scope/control change enacted here.

## Source response / smallest complete change

`evidence/S07/S07f/ADJUDICATION.md` classifies findings against their owning
contracts **before implementation**, rather than adopting reviewer suggestions.

- **F1 fixed:** summary qualification and mean relative error derive from finite
  g, not an inconsistent/missing/malformed caller error. Direct inclusive g-space
  5% endpoints avoid division roundoff; no tolerance or percentage change. The
  old nextafter(error) test mapped to the *same g* at both sides; replacement
  tests adjacent measured-g values above/below the real endpoints.
- **F2 fixed at the trust boundary:** raw labels cannot attest independence.
  `summarize(..., independence_verified=False)` defaults denied; only literal True
  from a trusted caller authenticating the **exact panel's independent recording
  provenance outside dictionaries** enables counting canonical case-sensitive IDs.
  Surrounding whitespace is rejected, not trimmed/case-folded. In-band claims and
  truthy substitutes do not authorize counting. This is NOT a new provenance
  authenticator or evidence that case-different recordings are independent.
- **F3 preserved intentionally:** standard uncertainty still leaves coverage null
  and adds the existing blocker, even with hypothetical verified group identity.
- **F4 not adopted as a new gate:** suffix isolation/RMSE diagnostic retained;
  prediction criteria belong to Gate RS/S14, not an invented Gate M threshold.
- **F5/F6 documented limitations:** conditional propagation can emit misleading
  numbers if external precision/systematic/small-error assumptions are falsely
  asserted. No universal residual/chi-square/relative-uncertainty cutoff follows
  from this schema. No threshold, interval multiplier or empirical coverage was
  invented or tuned to review examples; independent assumption/coverage review
  remains required for real use. These are NOT claimed physically resolved.

Ponytail full applied: grepped every summary/evaluator caller first; reused the
existing evaluator, trusted-caller default-deny pattern, fitter, uncertainty,
review reproducers, stdlib/unittest. Product logic changes only in gate_m.py;
docs in GATE_M.md/UNCERTAINTY.md and tests in test_gate_m.py. No duplicate fitter,
dependency, schema, helper framework, acquisition or unrelated source changes.

## Fresh verification

All logs below are in `evidence/S07/S07f/`. Synthetic policy fixtures and review
numbers are **not real measurements**. No full-project-green claim.

| Command/check | Result / evidence |
|---|---|
| `python -m unittest discover -s tests/measurement -v` baseline | **59/59 PASS**, baseline-measurement.txt. |
| `python evidence/reviews/R-M/repro.py` before/after | Before: inconsistent g/error and raw aliases pass. After: both denied; F3–F6 and math checks unchanged. review-repro-{before,after}.json. Original reviewer files untouched. |
| Gate-only discover with `-p test_gate_m.py -v`, F1 RED/GREEN | RED: 3 decision failures and 5 missing-error exceptions; GREEN **14/14**. red-F1.txt / green-F1.txt. No syntax/import/environment failure masquerading as RED. |
| Gate-only discover, F2 RED/GREEN | RED: raw-label panel incorrectly passes (1 behavioral failure); 14 exceptions additionally expose the absent explicit keyword API. GREEN **16/16**. red-F2.txt / green-F2.txt. |
| Final measurement discover | **64/64 PASS**, measurement-tests-final.txt; F1 remains denied even when external independence is explicitly True. Coverage regression does not rely on default-denied independence to pass. |
| Every Git-tracked Python test directory, separate `python -m unittest discover -s <directory> -v` | **225 tests: 224 pass, 1 dependency error** across 8 suites. measurement64, spec91, scene11, spike4, shell7, Railway7, Run-System25 pass; API health15/16. repository-python-tests.txt and python-suite-exits.json. |
| `node --test` every Git-tracked `*.test.mjs` outside archive | **39 pass / 1 file-load failure**, repository-node-tests.txt. |
| `python -m Build.measurement.gate_m --output evidence/S07/S07f/actual-gate-m.json` | Expected **exit1**, NOT_MET_INPUT_READINESS; eligible0, measured0/3. Before/after actual artifacts and gate-{before,after}.txt retained. |
| `python evidence/S07/S07f/check_evidence.py` | **PASS**; verification-final.txt / verification.json: unchanged actual-source outcomes, 16 consumed-source fingerprints, F1 denied with explicit independence, F3–F6/math unchanged; AP15 NOT_RUN. |
| `git diff --check` | Source PASS; staged check identified trailing spaces on 3 unittest subtest log headers only, normalized without changing results; final staged/post-commit checks below. |

Broader failures (pre-existing in S07a/d reports, freshly confirmed here):
`test_postgres_probe_uses_read_only_query_and_bounded_connection` cannot import
**psycopg**; `tests/viewer/three-renderer.test.mjs` cannot import this checkout's
**Build/web/node_modules/three/build/three.module.js**. No installs or unrelated
fixes. Uvicorn/websockets deprecation warnings also remain in the health log.

Fresh canonical comparison: 13/16 consumed files byte-match, approval receipt
differs **only CRLF/LF**, and two fingerprints are expected owned edits
(gate_m.py, UNCERTAINTY.md). Initial strict raw-hash check stopped on the receipt;
byte diff confirmed EOL-only, then normalized comparison passed. Failure receipt
retained in verification-initial-raw-hash.txt. Raw media not reopened/hashed.

## Runtime, scope and communication

- CODEX-1; requested existing managed **gpt-6.1-sol/high**. Actual backend model /
  effort not independently exposed; observable tokens/coding cost **unknown**.
  Coding quota **OpenCodex-managed; not polled**. New Meta/API/GPU jobs/spend0;
  ongoing infrastructure charges/balances not verified.
- First exact UTC clock **2026-10-28T12:06:54Z**; conservative start12:06:00Z,
  implementation/tests complete by12:15:00Z; final closeout clock below. No new
  implementation after minute25; session below30m.
- Only assigned `C:/Users/HP/.codex/worktrees/s07f-gate-decision/2026-10-26 - Meta Global AI Developer Hackathon`
  used for work, branch **run/S07f**, clean entry/base/main
  **a0b603df930920d7f6b1c1f0c3d128c8ec4ac529**. Canonical instructions/controls
  read-only. Main later advanced to24776585 by controller; no rebase/merge here.
- Only dispatched Owns changed. Run PLAN/REPORT are force-added individually
  because Runs is ignored. Controller owns canonical controls and merges;
  commits deliberately **UNMERGED**. No fanout/other-chat messages.
- Read/APPLIED receiving-code-review (verify and classify before fixes),
  systematic-debugging (reproducer/callers/root cause; EOL diagnosis), TDD plus
  writing-good-tests (real summary behavior, separate RED/GREEN, literal expected
  errors and measured boundary values), verification-before-completion (fresh
  combined tests, unchanged source result/fingerprints, scope checks). Ponytail
  concrete reuse/minimal-change choices above, not discovery-only compliance.
- Communication: mandatory higher-priority initial skill/pre-tool notice only;
  otherwise silent repository-first evidence, no duplicated chat report. Final
  response is one status/absolute REPORT line. No owner questions needed; any
  later question belongs in this owned report for controller fallback relay.

## Skips, risks and next

Skipped installs, live SAM/GPU/media work, browser/UI/build/deployment/E2E,
generic calibration hunts, new coverage/noise/linearization gates, and all source
or approval changes. No secrets, accounts, terms, publication, purchases, provider,
credential, routing, permission-policy or canonical control changes.

**Controller next:** other-vendor follow-up of F1/F2 gate changes, including the
external exact-panel independence trust contract and boundary regressions; only
then decide acceptance/integration and record canonical fallback decision. Preserve
metric/calibration/coverage holds and S12 lock. Unsupported conditional assumptions
remain a physical-risk limitation, not a gate success or new consent request.
