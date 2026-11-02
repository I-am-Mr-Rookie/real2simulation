# N70 Wonder lab-agent benchmark

Reuses [N51 protocol](../N51/PROTOCOL.md), its ten requests and `benchmark.py` without changing their prompts,
tool schemas, instructions, real workspace/lab/fitter handlers, simulated seed scenes, output budget (4000)
or step cap (6). The N51 harness now exposes run id, cap and cutoff constants; its original defaults remain intact.
N70 imports it, selects only `muse-wonder-1.0`, writes here and reserves against the canonical shared daily ledger.
No user uploads, picker/UI changes, automatic Sol fallback, GPU or deployment.

Run `high` first. Run `max` only if the complete high sweep has an invalid tool call, more than one guard-blocked
response step, a failed/empty/step-limited ending or a normal-request refusal. One corrected guard step by itself
is not failure (Spark high also had one in N51). Both sweeps share a $3 hard admission cap, counting settled
and in-flight reservations. Failed calls retain the full reservation. No new calls after 20:04 UTC Nov 2.
Three concurrent turns maximum, as N51, but one selected configuration means these requests run sequentially.

Schema validity is the count of JSON/schema-valid attempted calls, including `ask_user`; it is not handler success.
The off-topic refusal correctly has no tool-call denominator. Latency is wall time for the whole user turn,
including all tool executions, API steps and corrective guard retries. Tokens sum every API step, including
reasoning output. `turns.jsonl` keeps every attempt, safe usage metadata and reservation IDs/units; the scored
view uses the latest attempt per (model, effort, case). No keys or raw HTTP credentials are logged.

## Prices checked Nov 3 Dhaka

[Meta list pricing](https://dev.meta.ai/docs/pricing-rate-limits): Wonder standard mode $4 input, $0.20 cached
input, $20 output per million tokens. No Wonder contributor variant. [Reasoning docs](https://dev.meta.ai/docs/reasoning)
support high/max on Responses `reasoning.effort` and bill reasoning as output.
The shared ledger conservatively prices all Wonder input at $4/M, including cached tokens, exactly as N51 did
with its own rates. Report both this conservative estimate and the cache-adjusted list-price estimate from API
`usage.input_tokens_details.cached_tokens`. Neither is an invoice or a claimed measured billing charge.

N51 comparison rows remain historical measurements, not new calls. Its Spark rate was $1/$5 per million;
today's published Spark standard rate is $1.25/$4.25. Preserve N51's original totals and identify that difference
rather than silently rewriting historical evidence. One ordered sample per request, different provider load
and cache state, no randomized repeats: latency and quality differences are descriptive, not causal.

## Commands

```powershell
python evidence/N51/benchmark.py --self-check
python evidence/N70/benchmark.py --self-check
python evidence/N70/benchmark.py --root 'C:\Users\HP\Documents\Hackathon\2026-10-26 - Meta Global AI Developer Hackathon'
python -m pytest tests/agent/test_core.py tests/agent/test_fallback.py -q
```

Scope: core model price/effort tables only; existing callers, exported tiers, configuration and fixtures stay unchanged.
Offline checks cover default high on each tool-loop step, no picker exposure, Meta Responses routing and full
reasoning-output reservation/settlement. The controller owns cross-vendor spend review before merge.

## Harness correction

Initial `drop` and `pendulum` calls used the real lab handler's labelled server RK4 fallback because the new
worktree lacked the canonical node_modules junction. N51 used Rapier. After adding the prescribed shared
junction, those two cases alone were rerun against Rapier in a fresh isolated runtime. Initial runtime was
reversibly moved to `runtime-initial`, not deleted. Both attempts remain in JSONL, calls.csv and the shared
ledger; only the latest Rapier attempt is scored. No paid attempt was discarded from total spend.
