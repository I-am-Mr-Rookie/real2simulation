# S04c — Clerk configuration wiring

- Objective: wire the Next.js SDK with safe absent/invalid configuration, shared development Google + email OTP setup instructions; preserve fail-closed private routes.
- Requested lane/model: CODEX-2, GPT-6.1 Sol medium. Runtime: delegated Codex; exact model/effort not exposed. No routing changes.
- Start UTC: 2026-10-27T18:50:06Z; baseline main 82cb6739fe21ac8a23d3d9e73f287d6c0b35fc41. Stop by 19:20:06Z; no new implementation after 19:15:06Z.
- Owns: Build/web/src/shell/; Build/web/src/auth/; Build/web/src/app/; Build/web/package.json; Build/api/health/; Build/worker/health/; infra/railway/dev/. Run artifacts and serialized control updates per manual protocol.
- Dependency S04b DONE. No secret values inspected; key-name-only check found no Clerk keys. No new Clerk account/application or custom OAuth credentials authorized.
- Checks: auth configuration unit tests including malformed/partial config; production build and missing-config HTTP smoke; emitted browser JS scan using synthetic sentinel (no real secrets).
- Budget: <=30 minutes, zero Meta/GPU/service inference. Quota before: used70% five-hour/50% weekly. Tokens/subscription cost unknown.
- Skills: clerk-setup (official Next.js quickstart, no provisioning), test-driven-development, verification-before-completion. React-SPA patterns not applicable. Live Clerk testing requires development keys and is deferred if absent.
