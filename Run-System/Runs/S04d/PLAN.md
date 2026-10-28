# S04d — guest library and private authorization boundary

- UTC start: 2026-10-27T19:11:44Z; implementation stop by19:36:44Z, run stop19:41:44Z.
- Requested CODEX-2 / GPT-6.1 Sol medium. Observable delegated Codex; exact model/effort unavailable.
- Baseline03092d4; current main before claimca3b62b; claimc093976. S04c DONE.
- Objective: preserve public guest library and install fail-closed, server-side private-resource authorization.
- Owns: Build/web/src/shell/; Build/web/src/auth/; Build/web/src/app/; Build/web/src/proxy.js; Build/web/package.json; Build/api/health/; Build/worker/health/; infra/railway/dev/.
- Serialized controls/report updates per manual protocol. Preserve concurrent S09d and untracked research/concept documents.
- Checks: negative/ownership unit tests; production HTTP guest200/private404 including forged identities; build + shell/auth/viewer regressions and browser secret-sentinel scan.
- No data store is implemented; private scenes remain unavailable even to authenticated callers. No invented scenes, credentials, external auth E2E or deployment.
- Budget: no service inference/GPU; tokens/coding cost unknown. Initial Codex shared quota70%5h/50%weekly used; halt above85%.
- Skills: TDD and verification-before-completion; Clerk setup applied to documented resource checks (no provisioning). SPA skill inspected, excluded for Next.js; nextjs-patterns absent from known skill roots.
- Questions: fallback only; none needed for reversible implementation.
