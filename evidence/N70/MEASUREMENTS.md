# N70: Wonder lab-agent benchmark

## Verdict: ADD

**Recommend Wonder high as an optional model, not a new default.** All 11 attempted tool calls were schema-valid
(100%, matching Spark high's 12/12), zero number-guard blocks, all ten requests had usable endings, and median
whole-turn latency was **7.857 s**, below the requested approximately 60 s. Maximum observed turn: 23.570 s.
The off-topic request was correctly refused without tools; the genuinely vague request used `ask_user`.
Manual review found successful handlers, preserved SIMULATED/THEORY labels and uncertainty on fit/run replies.

**Estimated cost per scored turn: $0.03029440 conservative full-rate, or $0.01882600 cache-adjusted list price.**
These are usage-derived estimates, not invoiced charges. Wonder's conservative per-turn estimate is higher
than every historical N51 row below; this small benchmark does not demonstrate a harder-task advantage.
No model was added to the picker/UI and no default, provider route, credential or deployment was changed.

## Scored requests

Ten requests, 20 API calls, 51,636 input tokens and 4,820 output tokens (including reasoning).
Costs sum all response steps in a user turn, not just the final reply.

| Request | Valid tool call | Guard blocks | Turn s | Input tokens | Output tokens | Full-rate USD | Cache-adjusted USD |
|---|---|---:|---:|---:|---:|---:|---:|
| add_ball | Yes (1/1) | 0 | 9.979 | 5,056 | 400 | $0.02822400 | $0.01951440 |
| add_ramp | Yes (1/1) | 0 | 9.643 | 5,051 | 520 | $0.03060401 | $0.02189440 |
| drop | Yes (2/2) | 0 | 16.996 | 8,022 | 679 | $0.04566801 | $0.02824880 |
| pendulum | Yes (2/2) | 0 | 23.570 | 8,085 | 496 | $0.04226000 | $0.02338160 |
| fit | Yes (1/1) | 0 | 7.955 | 5,712 | 1,027 | $0.04338800 | $0.03467840 |
| move | Yes (1/1) | 0 | 7.759 | 5,032 | 385 | $0.02782800 | $0.01040880 |
| resize | Yes (1/1) | 0 | 6.312 | 5,025 | 242 | $0.02494001 | $0.01623040 |
| delete | Yes (1/1) | 0 | 7.257 | 4,879 | 272 | $0.02495600 | $0.01624640 |
| vague | Yes (1/1) | 0 | 4.884 | 2,384 | 586 | $0.02125600 | $0.01254640 |
| off_topic | N/A (correct refusal) | 0 | 3.153 | 2,390 | 213 | $0.01382000 | $0.00511040 |

## Comparison with N51

N51 rows are its historical scored results, not new paid trials. All rows use the same ten requests.
Valid calls are schema validity, not a claim of calibrated physics. Usable endings include questions and
off-topic refusals. Cost/turn below uses each run's conservative original full-rate ledger basis.

| Model | Effort | Valid calls | Guard blocks | Usable endings | p50 turn s | Input tokens | Output tokens | Estimated USD/turn |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Spark 1.3 | high | 12/12 | 1 | 10/10 | 10.805 | 55,622 | 12,365 | $0.01174471 |
| Spark 1.3 | xhigh | 12/12 | 1 | 10/10 | 8.383 | 55,637 | 12,473 | $0.01180020 |
| Spark 1.3 | max | 11/11 | 0 | 10/10 | 14.784 | 52,874 | 12,981 | $0.01177790 |
| Muse Open | high | 11/11 | 0 | 10/10 | 5.636 | 56,847 | 6,401 | $0.00982631 |
| Muse Open | xhigh | 11/11 | 0 | 10/10 | 4.317 | 56,847 | 4,559 | $0.00904346 |
| Muse Open | max | 11/11 | 0 | 10/10 | 3.796 | 56,847 | 4,217 | $0.00889811 |
| Sol | high | 11/11 | 1 | 10/10 | 8.112 | 34,789 | 1,918 | $0.00931959 |
| Sol | xhigh | 11/11 | 1 | 9/10 | 7.470 | 34,918 | 2,849 | $0.01032423 |
| Sol | max | 11/11 | 0 | 9/10 | 11.491 | 32,904 | 5,204 | $0.01237404 |
| Wonder 1.0 | high | 11/11 | 0 | 10/10 | 7.857 | 51,636 | 4,820 | $0.03029440 |

Sol's two non-usable endings were the already-reported N51 empty replies, not invalid tool calls.
N51's Spark historical estimate used $1 input/$5 output per million, whereas the current official list is
$1.25/$4.25. That historical basis is preserved, not silently repriced.

## Spend and evidence

All attempts: **12 turns, 26 API calls, 67,721 input and 6,163 output tokens**.
**Total conservative ledger estimate $0.39414403**, below the **$3 hard cap**, including the two superseded
RK4 attempts. Cache-adjusted list-price estimate for all paid attempts: **$0.26204080**.
Scored subset total: $0.30294403 conservative, $0.18826000 cache-adjusted.
Per-call UTC, model, latency, tokens, reservation IDs and conservative settlements are in [calls.csv](calls.csv)
and [turns.jsonl](turns.jsonl), joined to the canonical shared daily ledger. One ledger unit is $0.00000001.

[Meta list pricing](https://dev.meta.ai/docs/pricing-rate-limits), checked Nov 3 Dhaka: Wonder standard is
$4/M input, $0.20/M cached input and $20/M output. Cache-adjusted cost uses API
`usage.input_tokens_details.cached_tokens`; total output includes `output_tokens_details.reasoning_tokens`
without adding those reasoning tokens twice. [Meta reasoning documentation](https://dev.meta.ai/docs/reasoning)
confirms Responses `reasoning.effort` high/max and that reasoning is billed as output.

`max` was not run: high had no invalid calls, guard blocks, failed endings or normal-request refusals.
The brief RK4 harness mismatch was not model unreliability; corrected Rapier attempts passed too.
See [PROTOCOL.md](PROTOCOL.md) for the correction, exact inherited protocol and limits.

## Verification and limits

- Required agent tests: **127 passed**, one unrelated pytest/anyio deprecation warning.
- N51 and N70 benchmark self-checks passed; cap boundary includes in-flight reservations.
- Corrected drop and pendulum outputs explicitly report the same Rapier engine as N51.
- Raw token sums, ledger IDs/costs and latest-attempt scoring were checked against generated summaries.
- One ordered sample per request, not a statistical reliability estimate. N51 used concurrent model variants;
  N70 has one selected configuration and runs sequentially. Provider load and cache differ. No causal speed claim.
- No deployment, GPU, browser QA, picker changes or physical/calibrated measurement. Runtime scratch is not committed.
