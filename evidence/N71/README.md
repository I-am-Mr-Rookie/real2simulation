# N71: Wonder picker and limits

Final controller instruction supersedes both earlier variants: **10 turns/user/day normally; 20 from Nov 5 through Nov 8, 2026, inclusive, Dhaka.** Wonder's model-only Meta API allowance is **$3/day normally; $6 on those judging days**. All four values are named constants together in `Build/agent/core.py`; the date window reuses `daily_cap.JUDGING`.

## Implementation

- `wonder` is selectable in the API and workspace, including the first-run settings and saved per-user browser preference. Sol remains hidden.
- Existing Gumloop-style picker: Wonder is Smartest, highest intelligence, slower and costlier than Spark. Bars use relative labels only. No price, latency or quota numbers added to the picker.
- A SQLite `wonder_turns` table beside `spend` counts one admission per authenticated owner and Dhaka day, not one per tool request. `BEGIN IMMEDIATE` serializes concurrent admissions. Counts persist across requests/processes and reset by day key.
- Wonder reservations retain provider `Meta Model API` and model label. Its allowance sums only Wonder reservations/settlements, including existing benchmark labels ending in the model id. Spark, transcription, Sol and GPU spending do not consume the Wonder-only allowance. Existing overall ledger cap remains enforced and GPU policy is unchanged.
- Either Wonder limit selects Spark standard for the current turn and returns the exact visible note `Wonder limit reached for today, using Muse Spark`. Tool outputs carry forward without repeating side effects, including through the existing hidden Sol fallback.
- Conservative admission policy: an admitted Wonder attempt counts even if the provider subsequently fails or its spend reservation is denied. It does not count extra tool steps; contributor turns do not count as Wonder.

## Verification

- Production-pinned CPython 3.12.12 environment: agent suite plus daily-cap tests, **222 passed, 464 subtests passed**. One existing Starlette/AnyIO deprecation warning. Final focused Wonder/fallback suite: **128 passed**.
- Workspace, shell and workspace-proxy Node suites: **212 passed**. Final focused picker/render checks: **18 passed**.
- `npm run build`: PASS. `git diff --check`: PASS.
- Boundaries tested at Nov 4 17:59:59 UTC / 18:00:00 UTC (Dhaka Nov 5), and Nov 8 17:59:59 UTC / 18:00:00 UTC (Dhaka Nov 9); exact turn limits and cap values checked. Concurrent user admissions and spend reservations cannot exceed their respective limits.
- One live Wonder smoke at `2026-11-02T20:03:24.951156+00:00`: `ask_user`, no fallback, 2,392 input / 290 output tokens. Reservation $0.11072800; usage-based ledger estimate **$0.01536800**. Recorded on the existing shared Meta spend ledger as `N71 smoke muse-wonder-1.0`; see `live-smoke.json`. No billing reconciliation implied. No GPU.

## In-app browser

The first two attachment attempts returned `Browser is not available: iab`; the controller was notified immediately. Koushik attached @Browser and testing then succeeded.

- Actual worktree `createLive` components and `useLive`, bundled with Next's installed webpack, served by the worktree API router at loopback `127.0.0.1:18171`.
- Explicitly synthetic local owner and provider reply; unrelated list/GPU endpoints are empty fixtures. No Clerk, real uploads, private projects or remote authentication were exercised. This is not DEV/deployment evidence.
- Normal human-style interactions: choose Wonder on first run, Continue, open picker, select Wonder, type/send a turn, inspect the visible note, close/reopen the agent, navigate all picker choices with Tab, Escape, and reload to verify the saved Wonder selection.
- Desktop **1280 x 800 CSS px** and mobile **375 x 812 CSS px**: Wonder/Smartest visible; intelligence high, speed low, cost high; dialog stays within viewport; fallback note fits without horizontal clipping. No browser warnings/errors. `browser-checks.json` contains DOM-backed geometry.
- Four unaltered screenshots remain local only under `runtime/`: `desktop-picker.png`, `desktop-limit.png`, `mobile-375-picker.png`, `mobile-375-limit.png`. Not committed per the worker's no-media-binaries contract.
- Browser viewport reset, QA tab closed, loopback server stopped. No deploy or push.

Reproduce the isolated UI fixture: `node evidence/N71/build-browser.mjs`, then `.venv/Scripts/python.exe -m uvicorn evidence.N71.browser_server:app --host 127.0.0.1 --port 18171`. The fixture intentionally exhausts only its synthetic owner's normal-day quota. `smoke.py` is a paid command, not a test; do not rerun without the task's live-call budget.
