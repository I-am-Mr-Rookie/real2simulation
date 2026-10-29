# S20a failover handoff — OFF, no switch implemented

The single accounting authority is `Build/guardrails/CONTRACT.md`; do not create
an AWS-specific parallel ledger or treat a provider swap as fresh headroom.

S20c owns implementation. Default provider remains Modal; AWS selection must be
explicit and disabled by default, never automatic on quota/cap/auth/runtime failure.
Reuse `Build/gpu/aws_adapter.py` gates, not a competing AWS launcher.

Current root AGENTS/API_BUDGET receipts record us-east-2 G/VT spot 8-vCPU approval
and a $50 EC2 budget; on-demand remains zero/pending. These are authority/config
receipts, not evidence that this run launched an instance or reverified live credits.
Do not ask for the same approval again; validate actual applicable quota, region,
spot-only selection, budget receipt, available credit, bounded all-in cost and stop
before an authorized future session. No account/policy/terms/billing changes here.

AWS must refuse wrong region, on-demand, missing/stale/malformed gate evidence,
unknown headroom and an unbounded session. Stop every session, including failures.
The $50 gross budget alert is not a hard spend cap or authorization to exceed credits.
Failover cannot replace or refill the independent Meta $120 routine/$30 reserve envelope.

No AWS configuration, environment variable, cloud resource or existing adapter changed.
