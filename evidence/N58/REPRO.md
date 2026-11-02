# Local verification harness

Use an isolated worktree. No private environment file or provider credentials are loaded.

1. Run `python evidence/N58/local_api.py` (18558); it needs the canonical ignored public RM04 bundle and seeds a private local SQLite store under `evidence/N58/local-data`.
2. Temporarily copy `local-workspace.jsx` to `Build/web/src/app/(public)/lab/n58-check/page.jsx`, build/start web on loopback 18559. This renders the real components, not a fake screenshot. Remove that exact file afterward and rebuild. Never commit the temporary route.
3. `python evidence/N58/local_proxy.py` (18560) allows in-app browser checks without browser interception. It supplies a synthetic local identity and blocks paid routes. This proxy is test-only and loopback-bound.
4. `node evidence/N58/browser-check.cjs` drives headed installed Playwright Chromium against the compiled app with equivalent test interception. It writes JSON receipts and local-only PNGs. It deliberately does not request microphone permission or invoke paid services.
5. Run Node suites with `node --import ./evidence/N58/resolve-deps.mjs --test tests/workspace/*.test.mjs tests/shell-workspace/*.test.mjs tests/lab-editor/*.test.mjs tests/lab/*.test.mjs tests/web-private/*.test.mjs tests/web-workspace-api/*.test.mjs`. The test-only loader resolves the existing web Rapier dependency for root-level tests; no dependency is installed.
6. `python -m pytest tests/api-storage evidence/N58/test_stage.py -q`; `npm run build` from Build/web after removing the harness route.

The synthetic token in these scripts is not a credential and grants no real service access. Final authentication remains the existing private route and Clerk middleware. Stop the three loopback servers after checks.
