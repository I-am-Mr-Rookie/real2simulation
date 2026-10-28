# R14-instruments-audit — DONE (bounded independent audit)

**One P2 shared quantizer defect demonstrated; controller's minimal candidate
independently passes22/22 tests and312 oracle observations.** Baseline remains
red intentionally. DONE means audit complete, not merged product, vendor-review,
physical calibration, Gate M/S12 or deployment acceptance.

## Identity, original window and ownership

- Assigned CODEX-1, managed `gpt-6.1-sol` / high. Runtime model/effort identity is
  not independently exposed. OpenCodex-managed; not polled. Tokens/costs unknown;
  no paid/model/network/GPU jobs invoked.
- Issued `2026-10-28T21:29:08.000Z`; first observed clock/start `21:29:17Z`.
  Original cutoff `21:54:08Z`; deadline `21:59:08Z` / Oct29 `03:59:08+06:00`.
  Task checks/work stopped **2026-10-28T21:43:35Z**. Report/commit administration
  follows; actual report timestamp is in TIMEBOX.json. No exception or clock reset.
  Early DONE is valid because all bounded acceptance criteria are met, including
  the later semantics clarification and independently checked candidate.
- Assigned worktree: `C:/Users/HP/.codex/worktrees/swarm14-instruments-audit/2026-10-26 - Meta Global AI Developer Hackathon`.
  Initial status clean; base `74c886f9b2cc1322dde152f5be5813f813904bc6`;
  branch `run/R14-instruments-audit`. Parent main never changed.
- Evidence/test commit: `a78eb0227e854bd4091d178a1836ba0a55af20f5`;
  a subsequent receipt-only correction records raw transcript whitespace accurately.
- Parent project/canonical root and exact Owns/original timebox are in PLAN.md.
  Same inherited project ID `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; parent visible-UI
  corroboration was supplied, but child UI association was not independently
  verified. One-time owner inline exception, not a new desktop chat/worker.
- Only owned run files, `evidence/S11/instrument-invariants/`, and
  `tests/instruments/test_r14_invariants.py` are committed. No product edits,
  main merge, canonical controls, manifests, routing or config changes.

## Finding and semantic decision

Detailed source lines, exact hex/decimal inputs, observed/expected, independent
derivation and caller propagation: [FINDINGS.md](C:/Users/HP/.codex/worktrees/swarm14-instruments-audit/2026-10-26%20-%20Meta%20Global%20AI%20Developer%20Hackathon/evidence/S11/instrument-invariants/FINDINGS.md).

`Build/instruments/synthetic.py:44` adds0.5 before floor, moving a strictly
below-half value up and moving an exact odd lattice point by one tick. All four
public instruments reproduce it, including negative camera coordinates and an
exact minimum-subnormal-resolution lattice point. Three frozen regression methods
cover18 failing instrument/channel subcases; they were **not** marked expected
failures or altered to match product output.

The owner's later semantic question was independently resolved from existing
camera fixture `test_synthetic.py:19–23`: `1.25` with resolution`0.1` explicitly
expects`1.3`. Exact rational division of stored binary64 values would instead
give`1.2000000000000002`; that candidate changes established behavior. An added
explicit compatibility regression covers this familiar decimal tie in all
instruments; the dyadic Fraction oracle and three original regressions are unchanged.

Controller's split-floor decision on the **existing binary64 quotient** is the
smallest compatible root fix; it removes premature rounding, preserves signed
half-away behavior and the existing finite-ratio rejection envelope. No arbitrary
epsilon, exact-decimal policy, new uncertainty model or calibration claim was added.

## Fresh commands and results

Run commands from the assigned audit root; all CPU/local. Full outputs are linked,
not duplicated here.

| Command/check | Fresh result/evidence |
|---|---|
| `python evidence/S11/instrument-invariants/probe.py` | Baseline18/18 frozen channels fail;72/294 dyadic sweep observations mismatch. `probe.json` pins baseline hashes and exact observations. |
| `python -m unittest discover -s tests/instruments -p test_r14_invariants.py -v` | Final12 methods:9 pass,3 frozen methods fail (18 subcase failures); exit1. `r14-unittest.log`. |
| `python -m unittest discover -s tests/instruments -p 'test_*.py' -v` | Final22 methods:19 pass, same3 frozen methods fail; exit1. Original10 methods remain green. `all-instruments.log`. |
| `python -m unittest discover -s tests/lab -p test_pipeline.py -v` | 4/4 pass, real S08->Node->instruments->fitter, including CLI/two ballistic templates. `pipeline-unittest.log`. |
| `python -m unittest discover -s tests/lab -p test_session_bridge.py -v` | 10/10 pass, actual local bridge observation/fitter path. `session-bridge-unittest.log`. |
| `python evidence/S11/instrument-invariants/verify_candidate.py '<controller worktree>'` | **22/22 pass**, all312 frozen+sweep observations match; source SHA256 unchanged before/after. `candidate-unittest.log`, `candidate-verification.json`. |
| AST parse of the3 new Python files; authored-file whitespace check; product diff vs baseline | PASS; product source unchanged. Full diff check flags6 trailing spaces emitted by unittest in the two intentionally failing raw logs; preserved verbatim, not an authored-code failure. |
| `python Run-System/worker_timebox.py check Run-System/Runs/R14-instruments-audit/TIMEBOX.json` | TIMING PASS; full original1800-second window preserved, verified DONE early. |

Candidate check loaded the unchanged audit test file externally against
`C:/Users/HP/.codex/worktrees/swarm12-covariance-fix/2026-10-26 - Meta Global AI Developer Hackathon`,
branch`run/R14-quantizer-fix`, HEAD`55a3d2e63dace18539fcd62ff3dbb28c287ab402`
with an **uncommitted instrument edit**. Actual tested product SHA256:
`3f216767bb4d7b16541955d169c699668daf54ef228c1626b37e33fe7c7ba78d`.
Quantity and pipeline hashes equal baseline. This is snapshot verification, not
a claim the edit belonged to that commit or was integrated. Parent owns final pin,
commit/integration, controls and required native vendor review.

## Concrete Ponytail FULL application

Read full requested installed Ponytail, current canonical controls/timebox policy,
three recent reports and actual instruments/contract/callers/tests. Reused
`validate_quantity`, `Quantity`, public instrument exports, existing synthetic
setup/PLY fixture, actual pipeline/fitter and standard-library unittest/Fraction.
No installation or new abstraction/dependency. One owned test module and two small
repeatable evidence scripts; full repetitive observation data stays in linked JSON.

Verified each numeric input boundary, signed/nonnegative domains, finite extreme
outputs, explicit uncertainty preservation, seeded reaction replay, independent
error semantics and units at the actual fitter boundary. A new actual-pipeline
test checks every sample using nonzero bias and nondefault explicit uncertainty.
No inference that reaction std equals declared uncertainty. The bug was reported
nonterminal immediately when requested, enabling parallel controller fixing.

## Limits, cleanup and communication

- Reused existing canonical simulator dependencies through an owner-permitted
  worktree-only `Build/simulator/node_modules` junction; no manifests/install.
  A guarded **nonrecursive link cleanup command was rejected by tool policy
  before execution**. No bypass attempted. The ignored junction remains and its
  target is still present; no dependency bytes were deleted or committed.
- Scientific/task checks completed by the recorded stop; no background service,
  compute/model/GPU job or additional worker was launched. Tests' subprocesses
  returned normally. No coding-quota query, secrets/env values or private media.
- Mandatory exceptions to silence: initial required runtime update, required
  Ponytail announcement, owner-requested nonterminal finding and requested semantic
  assessment. Otherwise no optional progress narration or duplicated chat report;
  final response is the required single report pointer.
- Skipped covariance/QR/underflow re-audit, exhaustive arbitrary floating grids,
  physical/calibrated success, UI/deploy/publication/account/terms work. Deterministic
  sweep counts are not statistical coverage or a physical gate.
- Remaining risk: baseline is intentionally still defective until the controller's
  separately owned fix and tests are integrated/reviewed. Candidate snapshot is
  verified; no later source revision or runtime deployment is attested here.

No owner input required. Next action belongs to controller: integrate frozen tests
with the pinned shared fix and complete the required narrow native review.
