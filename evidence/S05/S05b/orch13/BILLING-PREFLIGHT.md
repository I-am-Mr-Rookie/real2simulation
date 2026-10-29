# S05b-orch13 billing/headroom preflight (before GPU)

Observed ~2026-10-29T11:01Z, signed-in ChatGPT in-app browser, read-only, modal.com/settings/koushiksadhakjeet/usage (Overview tab).
- Plan Starter ($30 included compute credits/month). Billing cycle Oct 1-Oct 31, 2026.
- Cost summary: Total spend $0.00; total usage $0.01; credits applied -$0.01; header Credits badge $129.99.
- Usage this billing period: "$0.01 in credits - $0 in charges", $0.01 / $155.
- Usage limit $155 "Set by Modal", total usage limit with credits included.

No-paid-overage reasoning: a job bounded at <=$1 all-in draws from $129.99 remaining credits; charges stay $0 unless
usage exceeds credits by >$128. This is credit coverage for this bounded job, NOT an account-wide hard cap claim.
No setting, plan, limit, payment or credit was changed. CLI before launch: `modal app list --json` = [] and
`modal container list --json` = [] (Modal 1.6.3, uv-cached Python3.11, MODAL_TOKEN_* key names present; values not read out).
