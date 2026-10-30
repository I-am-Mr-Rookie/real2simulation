# S16h — sidebar open-weight evidence checkpoint

**Offline checkpoint only. No live calls, spend, credentials or dashboard access.**
Machine-readable facts and RFC6901 JSON pointers: [S16h-checkpoint.json](S16h-checkpoint.json).
This completes the scoped checkpoint/refusal, not parent S16 deployment or bonus acceptance.

| Classification | Actually evidenced | Source / JSON pointer |
|---|---|---|
| Measured, historical | **One** pinned Baseten Muse Open call, HTTP **200**, **1,176 tokens** (774 prompt + 402 completion); local dev adapter returned validated synthetic cards | `evidence/S16/S16e-orch108-live.json`: `/model_id`, `/request_count`, `/http_status`, `/response_model_matches_pin`, `/usage_measured`, `/result/status`, `/validated_card_mapping` |
| Unknown | Baseten dollar cost is **UNKNOWN**, not $0; balance unobservable | Same: `/cost_usd` = null, `/cost_basis`, `/balance` |
| Owner-confirmed, not measured balance | Q17: organizer key carries $100 restricted Muse Open credit, no account/dashboard; **never sign in** | `STATE.md`, `OWNER Q17 ANSWERED (Oct30 ~13:28 Dhaka)`; live receipt `/credit`, `/balance`; `Run-System/Runs/S16e-orch108/REPORT.md` |
| Offline only | Explicit Fireworks fallback configuration and exact model/response validation, fake success and failure; **never live-called** in these receipts | `evidence/S16/S16f-orch111-offline.json`: `/mode`, `/live_requests`, `/fireworks_model_availability_verified`, `/cases/2`, `/cases/3`, `/cases/4` |
| Offline measured tests | S16g **100 tests PASS**, safe invalid-patch and provider-failure behavior; no real inference | `evidence/S16/S16g-orch116/unittest.txt` final summary; `behavior.json`: `/label`, `/live_requests`, `/patch_errors`, `/search_results` |
| Offline implementation/test | Explicit Meta Spark fallback **refusal**, no implicit provider chain; bonus dropped | `Build/sidebar-tools/library_search.py:search`; `tests/sidebar-tools/test_fireworks.py` two S16h regression tests; `evidence/S16/S16h-unittest.txt` fresh final summary |

## When both open providers fail

QUEUE's intended next route is **Muse Spark on the Meta API**, only through explicit
trusted configuration, dropping the open-weight bonus claim. Baseten and Fireworks
already fail closed without automatic switching. No other provider/model is allowed.

**No sidebar Meta Spark adapter existed.** The smallest allowed fix is a deliberate
explicit-config refusal, not an invented live integration:

1. Trusted host selects `SIDEBAR_SEARCH_PROVIDER=meta`.
2. Adapter returns readable `error/not_ready`: Meta Spark fallback is not wired;
   explicit Meta API integration is required; no provider called; open-weight bonus dropped.
3. Receipt stays `provider=null`, `model=null`, `state=not_requested`,
   `meta_bonus_claimed=false`; no cards or numeric tool outputs.
4. Even complete Baseten/Fireworks configuration cannot cause dispatch through this
   branch. Other selections remain refused; failures never trigger automatic Meta calls.

This is the controller-authorized **explicit-config refusal** alternative, **not a
working Meta Spark route**. A future real Meta fallback needs explicit host integration,
bounded validation and tests before use. There are no new live endpoint/model/key
settings, secret reads, provider-policy changes or dependency installs here.

## Claim limits

- **No open-weight or Meta bonus claimed** (`false` in checkpoint; adapter's
  `meta_bonus_claimed` remains false on every route). The single Baseten live call
  supports only its narrow historical adapter-use claim, not eligibility or deployment.
- Fireworks synthetic ranker ID is a fake test resource, not verified hosted Muse Open.
- Legacy S16e receipt predates `execution`; it is preserved unchanged, not retrofitted.
- Synthetic metadata cards remain simulated, scale-unverified and non-physical evidence.
- Current provider availability, live Meta fallback, deployed sidebar UX and judging
  acceptance remain **unverified**. No source receipt implies those outcomes.

Skipped live calls, pricing/balance research, browser sign-in and web deployment.
Risk: until an explicit Meta adapter exists, both-open-provider outages leave search unavailable.
