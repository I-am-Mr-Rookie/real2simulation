# R15-model — DONE (scoped S11l recovery; parent integration pending)

## Result

Recovered R14's uncommitted residual-underflow repair and completed one further
same-root edge: a rounded subnormal norm could still turn representable positive
RMSE into zero and distort AIC. A shared three-line stdlib helper now keeps the
maximum-residual scale separate through RMSE division and AIC logarithms. Normal
RSS summation remains unchanged; tiny RSS is recovered from the stable norm when
representable. AIC is still `n*log(RSS/n)+2*rank`, with unchanged exact-zero ties.
No valid domain restriction, epsilon/noise inflation, new model criterion or
forced covariance validity was introduced.

API reports numerical zero RSS with nonzero residuals as `rss_status=underflow`,
retains finite AIC and positive representable RMSE, and reserves exact-zero AIC
metadata for all-zero residuals. It reuses the existing `_sigma2` guard for null
unrepresentable residual variance. Legacy IID requests reuse uniform declared
position sigmas rather than silently treating lost RSS as an explicit `sigma=0`;
existing residual floors, timing exclusion and zero-dof behavior remain tested.

## Fresh evidence / acceptance

Evidence: `evidence/S11/model-selection-recovery/R15/`; commands, UTC check starts,
exits and source hashes are in `checks.json`. No frozen oracle was edited.

| Check | Result |
|---|---|
| Frozen `test_r14_model_selection.py` | 14/14 PASS; SHA256 `37bd5ce0597fdf88fd989d3402bb467bf04f0b7ba0cd95c1a0f479606e506cbc` unchanged |
| `test_r14_model_recovery.py` | 6/6 PASS, including newly failing-before subnormal-norm case |
| Existing core / API / uncertainty / invariants | 13 + 9 + 10 + 13 = 45 PASS |
| Impacted `test_pipeline.py` / `test_session_bridge.py` | 4 + 10 = 14 PASS; synthetic local caller checks, not UI |
| Frozen independent `audit.py` | exit0; strict JSON, all four analytic choices/AIC/RMSE independently checked |
| Frozen audit/oracle `git diff --exit-code HEAD -- ...` | PASS |
| Authored source whitespace | PASS |

Total **79 passing methods**, no skips or weakened oracle. Coverage tests retain
their Student-t95%/90-of100 contract; no changed seed search or threshold. At
scale `2**-600`, degree2 wins, both AICs are finite, degree2 RMSE is approximately
`9.017094464795466e-181`, RSS is numerical zero marked underflow, and covariance
remains unavailable. At `2**-540`, representable subnormal RSS is retained without
claiming an unavailable residual floor is zero. The new four-point minimum-
subnormal case previously returned RMSE0 for two one-ulp residuals; final RMSE is
the correctly positive minimum subnormal. This is residual-statistic evidence,
not a claim of accurate fitted coefficients at every binary64 subnormal scale.

## Recovery provenance / identity / timing

- Inherited branch `run/R14-model-fix`, HEAD `36bc33d62dbdb42b35e24a4e5cfaa03fe6e59fdd`;
  created `run/R15-model` without reset. Preserved all existing uncommitted edits
  and root-level recovery evidence. Original R14 worker is authoritatively absent;
  no duplicate was launched. R14-model-fix has an old plan but no terminal report
  or verified actual stop timestamp. Those remain unknown, not backdated. Its
  historical passing logs were not accepted as fresh DONE.
- Actual R15 first observed execution `2026-10-29T07:23:56Z`; new issue
  `2026-10-29T07:23:41.000Z`, cutoff `07:48:41Z`, deadline `07:53:41Z` / Dhaka
  `13:53:41+06:00`. Original new1800s window is preserved in `TIMEBOX.json`, which
  records actual work-stop/report preparation times. Early DONE is justified by
  all scoped acceptance checks passing with no owned implementation remaining.
  Report/commit housekeeping follows source/test work-stop; no implementation
  started after the cutoff. Latest owner stop is `10:00Z` / 16:00 Dhaka.
- Assigned CODEX-1 / managed `gpt-6.1-sol` / high; exact runtime identity is not
  independently exposed. OpenCodex-managed; not polled. Observable tokens/costs
  unknown; no paid compute/model jobs or API calls.
- Inherited Meta AI Hackathon project `91e441f8-e40c-4ec4-bea2-de7fa1582d97` and
  canonical event root; child UI project binding not independently verified.
  Canonical AGENTS/STATE/QUEUE, timebox policy, original audit report/recovery plan,
  relevant owner/protocol/plan context and the full requested Ponytail were read.
- No shared controls/main, frozen oracles or other worker Owns were changed.
  Source identity is pinned by `checks.json` hashes and this branch's scoped Git
  commit; parent must read the actual commit/report before serial acceptance.

## Ponytail FULL / skips / risks / next

- Concrete reuse: existing centred QR, fit/API shapes, `_sigma2` and covariance
  guards, Python `math.hypot`/log, and untouched independent analytic R14 oracle.
  The one shared norm-parts helper fixes both statistic callers without a new
  dependency, generic numerical framework, QR rewrite or unrelated option.
- Traced callers in fitter core/API and lab pipeline/session bridge. Kept the
  inherited fix only after fresh regression; added one independently failing-
  before regression for the remaining numerical edge, then reran impacted checks.
- Skipped full builds, UI/native review, instrument quantizer integration,
  real-scene/physical GateM/S12, GPU/model jobs, installs, deployment/publication,
  accounts/terms, credentials/env values, providers/routing/policy and quota.
  Local tests are not product/physical readiness or an independent vendor review.
- Existing roundoff-only exact-fit model-choice hazard remains documented by the
  frozen audit: no owner-specified tolerance policy, so no invented tie rule.
  Squared covariance may genuinely be unrepresentable while RMSE/AIC remain valid.
- Parent next: independently review this precise source, integrate quantizer work
  separately, serialize native gate review/IAB375 and main fast-forward. No merge,
  control update or parent gate acceptance was performed here.
- Communication: minimal mandatory opening/skill update and two nonterminal
  findings for pipelining; final one-line report pointer, no other-chat messages
  or fanout. No new owner question or permission was needed. Two incidental
  read-only inspection commands failed (quoting, console Unicode); corrected
  with a here-string and UTF-8, not hidden as product verification failures.
