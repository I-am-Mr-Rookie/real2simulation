# R10-S10-fix — DONE (scoped simulation hardening only)

## Contract / timing
- Requested lane/route: CODEX-1, managed Sol/high. Runtime model identity not independently exposed; no route/model/provider change or quota query.
- Project: `91e441f8-e40c-4ec4-bea2-de7fa1582d97`, inherited from the controller handout; no launcher/project-binding operation performed here.
- Existing worktree `C:/Users/HP/.codex/worktrees/swarm10-s10review/2026-10-26 - Meta Global AI Developer Hackathon`; fresh branch `run/R10-S10-fix` from `0db90bae35d9dd1c9c23a032644e0311fb843975`. No merge/rebase/main/control edits.
- Issued/start 2026-10-28T20:03:18.139Z; original deadline 2026-10-28T20:33:18.139Z; minute25 cutoff 2026-10-28T20:28:18.139Z. Actual implementation/verification stop and report timestamps: [TIMEBOX.json](TIMEBOX.json). DONE may finish early because all assigned criteria passed.
- **Controller timing correction applied:** correct Dhaka deadline is **2026-10-29T02:33:18.139+06:00**, not the handout's erroneous 07:03 value. UTC issue/deadline/cutoff unchanged; no clock reset or extension.

## Changes / Ponytail full applied
Read canonical AGENTS/STATE/QUEUE/timebox policy and the explicitly supplied `C:/Users/HP/.codex/.tmp/marketplaces/ponytail/skills/ponytail/SKILL.md`. Inspected every direct caller (`contact-runs.mjs`, Python acceptance's embedded Node diagnostic), contact tests and integration tests before editing.

- Compute floor center once; reject JS derived overflow and float32 overflow before constructing Rapier geometry.
- Reject initial penetration with unknown first-touch time; do not manufacture `[0,0]`. Strict equality still permits true initial touch. Positive exact-touch and just-above regressions cover zero and translated floors; no arbitrary epsilon admits penetration.
- Reuse existing validators with `Math.fround` representability checks on Rapier-bound scalars, dimensions and every consumed position. Reject positive dimensions/density/gravity/timestep collapsing to float32 zero. JS RK4 samples remain unrounded; velocities are not sent to Rapier.
- No new dependency, wrapper, output schema, contact response or fallback policy. Only two source/test files changed; all other new files are in the two owned run/evidence folders.

## Fresh evidence / commands
Evidence base: [contact-hardening](../../../../evidence/S10/contact-hardening/).

| Check | Observed result |
|---|---|
| `node evidence/S10/contact-hardening/repro.mjs` before/after | Both audit defects reproduced before, rejected after. Raw installed Rapier stores finite JS ±1e40 as ±Infinity; wrapper now rejects those inputs. True initial touch remains accepted. `before.json`, `after.json`. |
| `node --test tests/simulator/contacts.test.mjs` before fix | 3 expected failures, 6 passes (`tests-red.tap`); positive initial touch already passed. |
| Same contacts command after fix | **9/9 pass**, including overflow/underflow and later-sample float32 rejection (`contacts.tap`). |
| `node --test tests/simulator/*.test.mjs tests/lab/contact-integration.test.mjs` | **32/32 pass** (`simulator-contact-integration.tap`). |
| `python evidence/S10/contact-hardening/verify_acceptance.py` | Actual Python→Node analytic acceptance **15/15**, four-template regression **4/4**; actual deterministic, seed-bound replay passes. Threshold remains **0.005**. Six contact dt/template cases bracket analytic impact; no jitter/fallback observed. `acceptance.json`, `regression.json`, `acceptance-summary.json`. Existing acceptance artifacts untouched. |
| `$env:PYTHONPATH = (Join-Path (Get-Location) 'tests/spec'); python -m unittest tests.lab.test_acceptance tests.lab.test_regression tests.simulator.test_s10_adapter` | **5/5 pass** (`python-unittest.txt`); explicit test import path resolves audit's prior adapter invocation issue without source/config changes. |
| `node evidence/S10/contact-hardening/compare_baseline.mjs` | **10/10** valid ballistic/contact/initial-touch/no-contact cases: full output and replay records exactly identical to pinned `0db90ba`; seed changes still change replay hashes (`baseline-comparison.json`). |
| `git diff --check`; audit-path diff against base | Clean whitespace; historical Claude audit reports unchanged. Final precommit scope/timebox checks are in `FINAL-CHECK.txt`; branch tip is the scoped deliverable commit. |

## Boundaries / remaining action
- This child fix is DONE, **not Gate P acceptance**, contact response, physical Gate M, real-scene or S12 readiness. Parent must obtain the separately required native Claude targeted re-review; no Claude dispatch performed here.
- Float32 checks prevent conversion overflow/positive underflow, not arbitrary-scale conditioning or every possible internal engine arithmetic issue. Existing contact/displacement/footprint semantics remain intact.
- Skipped unrelated service-abort timing issue, UI/service/fitter/config/control changes, broader physics redesign and extreme-scale stress. No paid compute, secrets, accounts, terms, deployment, publishing or remote operations.
- Costs/tokens unknown; **OpenCodex-managed; not polled**. No owner questions needed.
- Communication: mandatory developer updates/skill announcement only; evidence on disk; final one-line status. No optional cross-chat messages.
