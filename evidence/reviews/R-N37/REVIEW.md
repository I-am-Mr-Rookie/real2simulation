# R-N37: N35/N36 security and spend review

**Verdict: changes required before claiming hard-cap and fallback-policy compliance.**

Reviewed main snapshot `a932d0f724ac55fdc3872abe179af595f8b1a858`, including merged N35/N36, their named REPORTs, `evidence/N36/PRICING.md`, and the shared daily-cap implementation. Read-only application review: no product code, paid calls or deployments changed. Line references below refer to this snapshot, not a later main.

## Findings

### F1 [P1] Missing usage releases the entire paid-call reservation

- **Location:** `Build/agent/core.py:458-462`; also `Build/agent/core.py:411-412`.
- **Failure:** a successful gateway response without `usage`, or with either token count omitted, is charged as zero for the missing counts. `finally` settles that amount and immediately frees reserved headroom. A paid provider response is not evidence that the call was free. This undermines both the Merge $2/day limit and the shared global cap even though admission itself is serialized correctly. Baseten normalization also manufactures zero counts when usage is missing.
- **Reproduction:** offline transport returned valid text with no usage for 200 calls. All were admitted; cumulative reserved estimates were **$11.31564000**, but the ledger settled **$0**. This demonstrates unlimited release of unknown liability, not a measured invoice overage. See `probes.json: missing_usage_repeated`.
- **Smallest fix:** only replace the conservative reservation when both usage counts are present and validated nonnegative integers. Preserve the reservation for missing/incomplete usage, including through `_from_chat`; do not normalize unknown usage to zero. Add absent/partial-usage tests for both gateways.

### F2 [P2] Status reaping races heartbeat/start and can refund a started job

- **Location:** `Build/api/gpu/__init__.py:95-101,105-118,199-206`.
- **Failure:** `start()` holds `BEGIN IMMEDIATE`, but `status()` calls `_reap()` in autocommit mode. Its SELECT and conditional UPDATE are separate transactions. A heartbeat/start can commit between them. The UPDATE checks only `finished_at`, not the heartbeat observed, and settlement uses the stale `started_at` from the SELECT. This can mark a freshly renewed running job dead and classify it as never started, refunding its reservation while its runner can still dispatch. It also releases the queue early.
- **Reproduction:** actual concurrent `gpu.start(t=89)` and `gpu.status(t=91)` on an initially unstarted row with heartbeat at t=0. A barrier held the start transaction before COMMIT until status read the old row. Status then reaped the committed start, retaining database `started_at=89` and `heartbeat_at=89` but settling its **$1.50** reservation to **$0**. This is deterministic interleaving of the real functions, not a paid GPU experiment. See `probes.json: lease_real_concurrency`.
- **Current reach:** `live_room.py` does not attach reservations, so the zero-settlement branch is latent for that caller; its reservations remain conservative. Incorrect live-job failure/queue release is already reachable. Attaching the reservation without fixing this race would expose the refund defect.
- **Smallest fix:** wrap status reaping and its active-job read in `BEGIN IMMEDIATE`/COMMIT, matching `start()`, then settle after commit. Add the concurrent renewal/start regression. An atomic expiry UPDATE returning the current started state is an alternative, not an additional requirement.

### F3 [P2] Structured refusals are treated as empty replies and sent to Sol

- **Location:** `Build/agent/core.py:207-209,280-292,405-410`.
- **Failure:** `_message_text()` reads only `output_text`; a Responses message containing a `refusal` content item becomes empty. `_from_chat()` similarly drops `message.refusal`. The resulting `no_tool_call` triggers the hidden fallback, violating the explicit never-on-refusal rule. Existing refusal tests cover only refusal prose encoded as ordinary text.
- **Reproduction:** both a Responses structured refusal and a Baseten-style chat refusal produced `[muse-spark-1.3, gpt-6.1-sol]` with reason `no_usable_tool_call`. See `probes.json: responses_refusal, chat_refusal`.
- **Smallest fix:** preserve and explicitly recognize refusal signals before empty-answer and numeric-guard recovery. Return a terminal refusal with no fallback. Add tests for both response formats.

### F4 [P2] Provider bad-input errors are classified as fallback-eligible outages

- **Location:** `Build/agent/core.py:379-382,241-249`.
- **Failure:** every HTTP error except 402/429 becomes `ModelUnavailable`, including 400/413/422 invalid request, context/input-size and validation failures. `run_turn()` therefore sends such failed input to Sol. Local `ValueError`/Pydantic tests do not cover this transport path. Malformed conversation/tool history can also cause an upstream bad-request response.
- **Reproduction:** mocked actual urllib transport raised HTTP 400; the real transport classifier and `run_turn()` produced `[muse-spark-1.3, gpt-6.1-sol]`, reason `api_error`. No network request was made. See `probes.json: http400`.
- **Smallest fix:** distinguish non-retryable provider input/validation errors from availability failures and propagate them without fallback, using a sanitized error. Keep quota/billing exclusions. Test at least 400, 413 and 422 as well as existing 402/429 coverage.

### F5 [P2] Rejected routing-tool attempts can themselves activate the paid fallback

- **Location:** `Build/agent/core.py:157-159,296-298,323-325,239-249`.
- **Failure scenario:** an injection that persuades the primary model to emit an unallowlisted `call_fallback` tool twice does not execute that tool, but both rejections increment `bad_steps`, which invokes Sol through `no_usable_tool_call`. Thus the tool allowlist prevents direct execution/tier mutation, but does not establish the requested stronger property that injection cannot induce fallback spending.
- **Evidence boundary:** a mocked primary emitting that routing tool twice deterministically produced `[muse-spark-1.3, muse-spark-1.3, gpt-6.1-sol]`. No real-model obedience or attack success rate was tested. See `probes.json: injected_routing_tool_simulation`.
- **Smallest fix for this path:** make unallowlisted-tool/security rejections terminal and ineligible for fallback, distinct from malformed arguments to known lab tools. Add that regression. More generally, retaining fallback on model-controlled empty/number-guard failures cannot provide an absolute injection-proof spending guarantee; that stronger requirement needs a server-owned eligibility/approval decision, not another prompt instruction.

## Required checks and remaining boundaries

| Check | Assessment |
|---|---|
| Client selects Sol through API/UI | Direct selection blocked. `Turn.tier` is `Literal["spark", "open"]` (`Build/api/agent/__init__.py:14-18`); core independently rejects other tiers (`core.py:227-232`). UI choices/serialization omit Sol (`live.mjs:9-14`). Offline API probes rejected `sol`, the full Sol id, `Merge` and `SOL` with 422. Extra client `model`/`fallback` fields did not control dispatch; a supplied system history role was dropped. |
| Only the three owner-listed failure classes | Trigger table is confined to API error, no usable call and number guard. Classification defects F3/F4/F5 prevent signing off on the exclusions. Ordinary refusal text and valid `ask_user` do not trigger fallback. |
| Cap/quota/input exclusions | Local CapExceeded/ValueError and HTTP 402/429 are excluded by current branches/tests. Provider invalid input is not, per F4. Provider-specific quota/refusal encodings beyond these formats were not live-verified. |
| Sol/global admission race | `_reserve` checks both sums and inserts inside one `BEGIN IMMEDIATE` transaction (`core.py:415-439`), using the same ledger as `daily_cap.reserve`. With one shared SQLite file, 40 concurrent attempts at $0.20 admitted exactly 10 Sol reservations totaling $2. A mixed-provider 100-attempt race at $0.25 admitted exactly 40 totaling $10. No admission race was found; settlement F1 breaks the overall spend guarantee. No distributed/replicated deployment topology was verified. |
| Private daily_cap helpers | Current units, schema, Dhaka date and total sum are consistent; the private-helper duplication is coupling, not a demonstrated extra cap bypass. Tests do not certify future schema/API changes. |
| Claimed approximately 10 concurrent Sol calls | Not a concurrency limit and not a fixed reservation. With the actual minimal `run_turn("Hi")` request, code computed 6,942 bytes and a **$0.0565782** reservation at the checked-in rates, permitting **35** outstanding such reservations from an empty $2 ledger. Ten is correct only for assumed $0.20 requests. Larger history/tool outputs reduce admission; settled cheaper calls free headroom. Correct the operational claim; add an explicit concurrency gate only if the owner actually requires one. |
| Credentials to client/log | No direct credential-return/log path found in the reviewed code. Keys are read for Authorization server-side; proxy token is attached only on the Meta route (`core.py:368-382`). Both gateway transports omitted the proxy header in fake-credential probes. Fake secrets embedded in provider error reason/body were neither returned in exception text nor logged. BFF forwards selected headers and uses server auth (`route.js:31-62`). This is code/offline evidence, not a browser bundle, live log or infrastructure audit. |
| Prompt injection changes tier | Primary dispatch comes from validated server tier, not prompt/history/tool content, and tool handlers are allowlisted. Direct switching is blocked; indirect paid fallback inducement is not ruled out, per F5. |
| Reaper double charge | `daily_cap.settle` updates only `actual IS NULL` under a write transaction (`daily_cap.py:81-94`), and reaper ignores already-settled ids. Existing once-only settlement tests pass. Queue/ledger settlement is not one transaction: a crash between them can retain conservative liability, but does not refund an already-started job by itself. F2 is the separate stale-read refund issue. |
| Missing live-room reservation handoff | `live_room.py:213` enqueues without rid; each attempt reserves only after start at :219 and settles at :234. A crashed process leaves an open spend row counted at its full estimate (`daily_cap.py:53-54`), so this omission is **not presently a free-run/global-cap bypass**. It prevents crash settlement/reconciliation. Because there may be two separately reserved GPU attempts on the same queue job, merely passing one initial rid to enqueue is not a complete fix: attach the currently active reservation atomically per attempt, or explicitly document/reconcile conservative orphan rows. Fix F2 first. |
| Remote GPU lifecycle | Lease expiry changes local bookkeeping; it does not cancel a detached Modal input. A crashed caller can leave an old remote attempt running while a later job starts, especially across per-function/per-GPU pools. Full worst-case reservation is necessary. The daemon heartbeat also proves process-thread liveness, not forward progress; a hung live runner can hold the queue indefinitely (`gpu/__init__.py:135-142`). Modal's remote timeout alone does not stop that local heartbeat. These are documented/structural boundaries, not verified remote termination. |

## Verification

- Python 3.14: `python -m pytest -p no:cacheprovider tests/agent tests/gpu tests/guardrails/test_daily_cap.py tests/reconstruction/test_live_room.py -q`: **154 passed, 464 subtests passed**, one third-party pytest deprecation warning. `pytest.txt`.
- Node: all `tests/shell-workspace/*.test.mjs` plus `tests/workspace/live.test.mjs`: **41 passed**. `node.txt`. Initial attempt lacked React in the new worktree; linked the existing canonical node_modules per contract, then reran successfully. No install.
- Additional assert-based offline probes: structured refusals, HTTP 400 classification, missing usage, real start/status interleaving, concurrent cap admission, client tier tampering, rejected routing tools, fake-credential transport/error hygiene. `probes.json` records outputs; all final assertions passed. An initial probe hit a Windows temporary-SQLite cleanup handle error, corrected by explicitly closing the probe's own connections before rerunning.
- No application/test/config changes. No paid requests, deployment, secret-value reads or credential provisioning. No web build because no web code changed.
- Skipped live model/prompt-injection trials, browser/bundle inspection, remote cancellation, production topology/logs and invoice reconciliation. Prices and concurrency calculations use checked-in code rates, not verified invoices. **Findings remain unfixed.**
