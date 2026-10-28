# S08i — DONE (local numeric validation repair)

Fixed both independently reproduced P1/P2 from CODEX-1 filler reviews; no
simulator, calibrated physics or product-gate acceptance claimed. New real safety
leaf, not a recovery-count inflation. CODEX-1 Sol/medium requested; actual backend,
effort/tokens/cost unavailable. OpenCodex-managed; not polled. Solo existing chat,
same project/root inherited; no delegation/schedule/dispatcher.

## Smallest complete change

- Free-fall sample validation compares allowed range BEFORE math.isfinite, like
  sibling oracles: signed10**1000 becomes field-specific ValueError, not leaked
  OverflowError. No new conversion/helper or changed valid samples.
- Shared setup validator checks stop-plane Y strictly below world-origin Y for
  both free-fall/projectile; positive-but-rounded-away heights fail closed with
  exact parameter path. No arbitrary minimum height or weakened geometry gates.
- Tests: two signed giant times preserve inputs; both templates/two origins
  reject ULP/8 displacement and accept one-ULP controls. Docs explain numeric,
  not physical/calibration scope. Five authored source/test/doc files, no dependency.

## Fresh evidence

evidence/S08/numeric-guards/: red free-fall9 tests with2 expected arithmetic
errors, setup14 with4 expected missed rejections; production fix then full
spec93/93 PASS normal and optimized. Scene11/11 and measurement65/65 PASS.
Source diff check PASS. Existing full repository suite sweep in preceding
S07b-recovery5: spike60, shell7, staging14, Run-System31 PASS; health15 pass/1
ERROR missing psycopg. These unrelated health deps were not installed/hidden.
Additional node viewer sweep: see viewer.txt; missing installed three package
prevents three-renderer.test.mjs import. This is not an application/UI pass;
remaining tests' exact count/commands recorded in closeout below. No live browser.

Ponytail full + TDD/writing-good-tests + verification-before-completion applied:
existing shared validation and test fixtures, first observed red then green,
hand-derived ULP controls, no generic representability abstraction or unrelated
API/renderer work. All examples synthetic; no model-authored physical numbers.

## Limits / timing

Issued16:37:20Z; full deadline17:07:20Z, minute25 cutoff17:02:20Z; actual earlier
owner/session stop16:58Z and implementation cutoff16:53Z govern. Exact stop/report
in TIMEBOX. Verified DONE early allowed. No service/model/GPU/API/download/media/
credential/deployment/remote push; no new spend/reservation. Historical$2.85/$30,
all physical gates and S12 unchanged. No owner question. Silent apart from
mandatory initial/skill/changed-finding updates; all evidence/report on disk.
Installed-dependency HTTP/render tests and actual simulator/runtime remain
unverified. Rebased/main integration recorded below before canonical acceptance.
