# Measured agent effort comparison

120 scored turns: ten cases for each of four model variants at high, xhigh and max.
132 paid turns including the twelve-case harness correction described in PROTOCOL.md.
264 API calls, 2026-11-02 05:30:21 through 05:39:42 UTC (call start times).
Total full-rate estimated spend: **$1.03593911**, below the **$1.50** cap.
The scored subset costs $0.97370928; superseded attempts remain charged in the total.

Every row: zero genuine normal-request refusals; the off-topic request was refused without tools.
Manual inspection confirms this, including Sol's curly-apostrophe refusals.
Valid calls below mean schema-valid, not a guarantee of a usable final answer.
Guard blocks count response steps, including a blocked ask_user followed by correction.

| Model | Effort | Valid calls | Guard blocks | Usable endings | Median turn s | Estimated scored USD |
|---|---|---:|---:|---:|---:|---:|
| Spark 1.3 | high | 12/12 | 1 | 10/10 | 10.805 | 0.11744706 |
| Spark 1.3 | xhigh | 12/12 | 1 | 10/10 | 8.383 | 0.11800204 |
| Spark 1.3 | max | 11/11 | 0 | 10/10 | 14.784 | 0.11777903 |
| Spark contributor | high | 11/11 | 0 | 10/10 | 9.892 | 0.00716660 |
| Spark contributor | xhigh | 11/11 | 0 | 10/10 | 10.432 | 0.00751544 |
| Spark contributor | max | 11/11 | 0 | 10/10 | 10.987 | 0.00794180 |
| Muse Open | high | 11/11 | 0 | 10/10 | 5.636 | 0.09826306 |
| Muse Open | xhigh | 11/11 | 0 | 10/10 | 4.317 | 0.09043458 |
| Muse Open | max | 11/11 | 0 | 10/10 | 3.796 | 0.08898107 |
| Sol | high | 11/11 | 1 | 10/10 | 8.112 | 0.09319590 |
| Sol | xhigh | 11/11 | 1 | 9/10 | 7.470 | 0.10324230 |
| Sol | max | 11/11 | 0 | 9/10 | 11.491 | 0.12374040 |

Usable endings include final replies, off-topic refusals and questions for genuinely vague input.
Sol xhigh resize and Sol max fit ended with an empty model reply after successful tool execution.
These are NOT normal-request refusals, invalid calls, or failed tool operations.
Spark high/xhigh vague questions each hit the number guard once before correction.
Sol high/xhigh fit replies each hit the number guard once before correction.
No observed benchmark turn blocked twice; escalation is tested offline rather than staged in live data.

## Decision
Retain the requested high defaults and Sol xhigh on twice-blocked-number fallback.
Contributor high is cheaper/faster with equal usable outcomes. Sol high is cheaper and avoids the observed
higher-effort empty replies. Spark xhigh has a lower median but no better guard or outcome rate.
Muse Open max looks promising: cheaper on all ten paired cases and faster on seven. However this is one
ordered high/xhigh/max sweep, with shared provider caching and three concurrent turns, not randomized repeats.
That cannot isolate effort from warm-cache or server-load effects. No sufficiently clear causal advantage
justifies overriding the owner's baseline. No further paid trials were needed to complete the requested grid.

Costs use existing product input/output prices, include reasoning in total output, and do not deduct cache discounts.
They are conservative token-price estimates, not invoices. Gateway-reported usage costs, where present, remain
in the raw per-call usage metadata. All API reservations and settlements also exist in the shared daily ledger.
No production deployment, GPU work, or physical/calibrated measurements occurred.
