# N36 model ids and pricing (checked 2026-11-01 UTC)

| Model | Route | Id (source) | USD per 1M in / out used in code |
|---|---|---|---|
| GPT-6.1 Sol (hidden fallback) | Merge gateway, MERGE_BASE_URL + /responses | `gpt-6.1-sol` (Merge GET /models, 288 models listed) | 2.10 / 10.50 |
| Muse Open | Baseten, BASETEN_BASE_URL + /chat/completions | `meta-models/muse-spark-open-1026` (Baseten GET /models; equals BASETEN_MODEL) | 1.25 / 4.25 |

- Sol: OpenAI list price $2.00 / $10.00 per 1M tokens ([OpenAI pricing](https://platform.openai.com/pricing)); Merge Gateway
  Pro bills vendor cost plus 5% ([Merge plans and pricing](https://docs.merge.dev/merge-gateway/cost/pricing)), so 2.10 / 10.50.
  Not verified against a Merge invoice.
- Muse Open: Baseten GET /models `pricing` field: prompt 0.00000125, completion 0.00000425 USD per token.
- Long-context surcharge not modelled: run_turn input is capped far below 272K tokens (MAX_TEXT, MAX_HISTORY, MAX_STEPS).

