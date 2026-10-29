# S20a acceptance evidence — offline only

| Criterion | Owning artifact / fresh proof |
|---|---|
| One contract over existing spend sources | `Build/guardrails/CONTRACT.md` sections 1–3 map existing Meta, pipeline GPU, run envelope and cost-log receipts. No writer/parallel persistence added. |
| Meta includes historical + pending + conservative unbilled estimates | `accounting-cases.json`: synthetic $110 history + $2 pending + $3 conservative estimate + $4 final bill + $1 candidate = $120 => routine cap false; $109 history => $119 => arithmetic condition true. Not a live authorization. |
| $30 demo reserve protected | Routine threshold is $120, strictly less, out of $150. Test never admits the $120–150 reserve band for routine work. Demo authority is explicitly outside the helper. |
| Unknown/invalid cost and delayed billing | 17 accounting tests include unknown history, malformed sources, NaN/infinity/negative/bool, provisional bill retention, final-zero reconciliation, overrun and duplicate/mixed-provider refusal. |
| Upload quota/reserve contract | Contract section 4 defines a reversible 1 accepted upload/authenticated user/UTC-day default, idempotency, failure accounting, existing file/session limits, fail-closed state and public library exemption. Not runtime-enforced in S20a. |
| Modal/AWS boundaries | Contract sections 2–3 + `infra/failover/CONTRACT.md`; existing cost-log 5 tests and AWS default-off gates 7 tests pass unchanged. |
| Existing upload/pipeline behaviour preserved | 52 existing offline pipeline tests pass (synthetic media, fake paid transports). No paid or real media action. |

Runtime: Python 3.14.5; **81 total tests passed** (17 new + 64 existing), no installs.
`existing-pipeline-tests.txt` includes expected invalid-event diagnostic in a passing negative test.

Important handoff: source evidence still has post-response-only Meta recording and
nontransactional GPU append/check. Current global bill/credit coverage was not reconciled.
S20a DONE means the contract is defined and its arithmetic verified, **not Gate C**;
S20b must integrate serialized admission at every supported paid boundary and prove
guest library access during pauses. S20c/R-C/S20d remain separate.
