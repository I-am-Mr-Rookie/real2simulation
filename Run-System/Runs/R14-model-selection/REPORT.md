# R14-model-selection — DONE (bounded independent audit; product defect remains)

## Finding / exact source

**One confirmed numerical root cause, three observable symptoms:** residual-square
underflow causes a wrong selected model, false exact-zero AIC metadata, and zero
RMSE despite representable positive RMSE. Synthetic valid finite input only.

- Times: `(-2,-1,0,1,2)` seconds.
- Positions: `2**-600 * (9,-8,-2,-8,9)` metres; zero declared standard uncertainty.
- Independent exact oracle: degree1 RSS `294*s²`, degree2 RSS `70*s²`, both
  strictly positive. The AIC difference `5*log(70/294)+2` is negative, so degree2
  wins. Expected degree2 RMSE `sqrt(14)*s` is representable and positive.
- Actual core: both RSS and RMSE zero; both AIC `-inf`; selected degree1.
  API reports success and `unavailable_exact_zero_rss` despite nonzero residuals.
- Root: `Build/fitter/core.py:142` squares residuals before summation;
  line147 derives RMSE from that underflowed RSS; lines170–173 call numerical
  zero exact; lines184–186 select the first equal `-inf`. API line164 labels
  every nonfinite score exact-zero without checking residuals.
- Existing covariance abstention is correct here; **not a covariance/QR audit
  or a re-report of the prior covariance defect**.

Parent fix direction: stable residual norm/log-RSS, or explicit numerical
abstention, with honest status. Do not tune noise, change model criteria, or force
unavailable covariance to appear valid. Frozen tests permit FitError/API error
rather than demanding support for unrepresentable squared quantities.

Additional precision hazard (not counted as a mandatory-policy defect): six
exactly linear pairs `t=1+i/10`, `y=1+2*t` select quadratic from residual roundoff
alone. Exact Fraction relation verified. No specified exact-fit tie/resolution
policy, so no arbitrary tolerance or new policy is imposed in regression tests.

## Scope / identity / timing

- Assigned CODEX-1 / existing managed `gpt-6.1-sol` / high. Exact runtime model
  identity not independently exposed. OpenCodex-managed; not polled. Observable
  tokens/costs unknown; no paid compute or API calls.
- Issue `2026-10-28T21:37:28.000Z`; first observed execution
  `2026-10-28T21:37:39Z`; cutoff `2026-10-28T22:02:28.000Z`;
  deadline `2026-10-28T22:07:28.000Z` / Dhaka `2026-10-29T04:07:28.000+06:00`.
  Actual stop/report timestamps are in TIMEBOX.json. Early DONE is justified by
  completed bounded acceptance, not a claim that the product is clean/fixed.
- Clean detached baseline `74c886f9b2cc1322dde152f5be5813f813904bc6`;
  branch `run/R14-model-selection`; assigned fresh isolated swarm14 worktree.
- Parent project `91e441f8-e40c-4ec4-bea2-de7fa1582d97`, canonical root
  `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`.
  Contract/root inherited and recorded. No independently verified child UI claim.
  One-time inline exception applies; no fanout, chat creation, merges or controls.
- Canonical AGENTS/STATE/QUEUE and relevant run reports R12, R13 and SWARM read;
  original full1800s timebox preserved. No scheduling/model/provider/config edits.

## Fresh verification / frozen evidence

All evidence below: `evidence/S11/model-selection-invariants/`.

| Check | Result |
|---|---|
| `python evidence/S11/model-selection-invariants/audit.py` | exit0; strict JSON actual responses, independent exact RSS and stable expected scores/RMSE in `audit.json` |
| `python -m unittest discover -s tests/fitter -p test_r14_model_selection.py -v` | **14 methods: 11 passing, 3 failing methods / 4 failure events**, exit1; `r14-tests.txt` |
| `python -m unittest discover -s tests/fitter -p test_api.py -v` | **9/9 PASS**; `api-baseline-tests.txt` |
| Six existing core residual/AIC/input tests, selected explicitly | **6/6 PASS**; exact command in `checks.json`, `core-selection-baseline-tests.txt`; no covariance/coverage rerun |
| `git diff --exit-code 74c886f -- Build/fitter contracts/fit tests/fitter/test_api.py tests/fitter/test_core.py tests/fitter/test_invariants.py tests/fitter/test_uncertainty.py` | PASS; product/contracts/existing tests unchanged |

The four failing events are core wrong selection, API false exact-zero metadata,
and degree1/degree2 zero RMSE. No expectedFailure, skipped tests, changed oracle,
weakened requirement or false GREEN claim. Exact dyadic scaling and analytic
orthogonality avoid fixture rounding ambiguity; ordinary AIC tolerance1e-10
across30 scale/permutation cases, residual1e-12; tiny RMSE relative1e-12 with
**zero absolute tolerance**. No arbitrary dimensional absolute floor.

Frozen test SHA256:
`37BD5CE0597FDF88FD989D3402BB467BF04F0B7BA0CD95C1A0F479606E506CBC`.
`audit.json` records exact product/test source hashes; `checks.json` records
actual commands/exits/durations. Final source/evidence assertions and timebox
check are saved in `verification.txt`.
Raw unittest failure output retains one trailing progress-line space; authored
source/docs pass whitespace checks. It is preserved rather than rewriting evidence.

## Verified semantics / limits / concrete Ponytail FULL application

- Read and applied the complete requested marketplace Ponytail skill. Reused
  unittest, API quantity shape and production public entry points; stdlib-only
  Fraction self-proof and analytic orthogonal fixture, not another QR solver or
  covariance framework. Evidence script imports the frozen test helpers rather
  than duplicating fixture/oracle code. No dependency/install/new feature.
- Independent checks cover both ordinary model winners/scores, residual sign,
  RSS/RMSE denominator `n`, rank/dof/sample counts, degree/sample admissibility,
  strict degrees/options, rank deficiency, exact-zero JSON and common-scale/row
  permutation invariance. Known declared-sigma/covariance behavior not re-audited.
- Degree1 requires at least2 samples, degree2 at least3 and sufficient distinct
  times. Zero residual dof is permitted interpolation, not proof of residual
  variance. No invented AICc/positive-dof requirement. Two-point degree1 plus
  fixed `(1,2)` selection correctly fails closed for inadmissible quadratic.
- API `degree` selects the returned fit/quantity; optional model selection is
  diagnostic. A returned quadratic fit/gravity alongside selected_degree1 is
  current consistent explicit-degree behavior, not asserted as a new bug.
- Intermediate `2**-540` has a core log-domain ValueError and readable API error;
  fail-closed, not another fail-open finding. Iterator/container exhaustiveness,
  arbitrary precision, statistical model adequacy and weighted AIC are not claimed.
- Skipped unrelated builds, simulator, covariance/QR implementation, hundred-seed
  regression, browser/native UI, real scenes, physical GateM/S12, GPU, deployment,
  publication, accounts/terms, credentials/environment values and quota checks.
- Communication: mandatory opening skill/runtime update plus three concise
  nonterminal finding/refinement notices; no optional progress/duplicate report
  chat, no unauthorized other-chat messages. Final is the required one-line pointer.
- Next: parent serially triages/fixes against frozen tests and performs appropriate
  review/integration. This audit does not merge, mark a queue row, or pass a gate.
