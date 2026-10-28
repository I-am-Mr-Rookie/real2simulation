# S04c — DONE (configuration wiring, not live authentication)

## Receipt
- Requested CODEX-2 / GPT-6.1 Sol medium; observable delegated Codex session, exact runtime model/effort unavailable. No routing/provider/settings changes.
- UTC start 2026-10-27T18:50:06Z; verification end 2026-10-27T19:03:24Z; client date Oct28 Dhaka.
- Baseline82cb673; claimcc36f33; taskd95f95647ea5769491cae0182f8db7b26d8593b7 rebased on concurrent S09c controls, verified and fast-forwarded to main. Unrelated research/concept files and concurrent S09c preserved.

## Changes
- Pinned @clerk/nextjs7.9.21 (registry peer ranges accept installed Next16.4.3/React19.3.1); conditional root ClerkProvider; prebuilt catch-all sign-in/sign-up; nav link; no custom Google OAuth code or client secret.
- server-only configuration boundary; pure syntax parser rejects missing/partial/malformed/mixed-environment keys without returning secrets. No fake identity. Private layout/leaf still deny, even with configured Clerk.
- Request-rendered root avoids stale build-time Clerk provider after runtime config removal. Small performance trade-off: public pages no longer static until later auth composition design.
- Added config tests, browser asset scanner, production HTTP missing-config and synthetic-config modes; documented env names, existing instance and remaining auth boundaries in Build/web/src/auth/README.md.

## Evidence
- TDD RED: config test initially fails missing module; GREEN4/4 after implementation. Sign-up smoke RED404 then route added. Stronger missing-runtime assertion RED exposed stale provider from static prerender; force-dynamic root fixes it. Failed Windows smoke also emitted Node UV handle assertion during cleanup; passing runs do not.
- Production webpack build succeeded in worktree with synthetic public key + noncredential server sentinel; emitted browser scan30 JS/map assets PASS, sentinel absent. HTML/RSC smoke also checks sentinel absent.
- Missing-config HTTP smoke: /, icon, /library, /sign-in and nested factor route, /sign-up200; private/unknown paths404; forged session + user header still404. Synthetic-config SSR smoke same boundaries200/404 with prebuilt page titles. No real Clerk session, OAuth or email generated.
- Shell Python7/7; auth Node4/4; viewer regression24/24 on main (includes concurrent S09c artifact loader); diff check PASS. Checks rerun after rebase, not only before commit.
- Fresh canonical-main npm install/build exit0 with synthetic sentinel; missing-config + synthetic-config HTTP smoke PASS; emitted assets30/30 clean. No real keys used in any build or smoke.
- Clerk CLI3.3.0 read-only `apps list` found existing Real2Simulation dev app; `api --fapi /environment --app app_3LHWo2Ia88IuLU1EbEccvw7PR01 --instance dev` confirms Google enabled/authenticatable and email first-factor + verification email_code. Selected schema confirms development shared Google credentials need no client ID/secret. Custom-credential state not read, so shared-credential policy is not a verified setting. No instance mutation.
- `clerk doctor --json`: host state/login valid; web project not linked, env file absent; CLI update available, not installed. Root env key-name-only inspection found no Clerk keys. No values printed/copied/retrieved.

## Limits / next
- No live Google/OTP E2E, credential validity, server session/ownership enforcement, deployment or gate proof. S01b/S04h/S22 own those checks. No accounts/apps/terms/users created; no env pulls, secret retrieval, uploads, publication, service inference or GPU.
- Next16 src/proxy.js is outside task Owns: intentionally absent. S04d needs owner approval for that path before adding Clerk middleware/server auth; fallback Q3 in STATE. Until then all private paths remain denied.
- Existing instance requires secure owner/service provisioning of the two documented env names; not credential copying by this run. No root lockfile outside Owns; transitive resolution remains unfrozen (existing S04b limitation).
- Worktree was explicitly local per manual protocol; clean contained worktree removed after verification. Branch retained for recovery.

## Skills/plugins
- clerk-setup: read instructions, detected Next.js, checked official quickstart and Google/email documentation; manually wired SDK without unauthorized CLI init/provisioning. Official quickstart's init-first suggestion is subordinate to no-account/app/credential-copy boundaries.
- clerk-cli: inspected installed binary/help, doctor, selected existing app and public Frontend API/schema instead of raw credential-bearing HTTP. Skipped update (not authorized), env pull/link/mutations (unnecessary/outside boundaries).
- test-driven-development and verification-before-completion: read skills, observed red cases above, ran real build/HTTP/asset/tests before completion and after rebase/main.
- clerk-react-patterns read but not applied (SPA-only; this is Next). clerk-testing read; live Playwright/Clerk testing-token setup deferred: no development keys, no owner sign-in. Relevant nextjs-patterns skill not installed; official documentation + installed SDK source used.
- Worktree/branch lifecycle instructions inspected; explicit project manual-worktree and fast-forward protocol used. No design/browser plugin needed for configuration/HTTP checks; no native UI requested. Quota plugin before/after used.

## Costs
- Quota before/after used70% five-hour /50% weekly (shared, not per-run); reset1793132283. Tokens and coding subscription cost unavailable. Meta/service-inference/GPU $0; public Clerk config reads only. Historical balance unknown, unchanged.
