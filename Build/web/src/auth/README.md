# Clerk wiring (S04c)

Next.js SDK pinned in package.json. Root provider and prebuilt `/sign-in`, `/sign-up` use
only a public publishable key. `server-config.js` is guarded by `server-only`;
its result never contains the secret. Configuration syntax is checked, not
credential validity. Missing/partial/invalid config renders an explicit
sign-in-unavailable page; `/library` stays public and private routes stay 404.
No implicit keyless app creation, custom Google client, demo identity or JWT parsing.
Root composition is request-rendered so removing runtime configuration cannot
leave a stale, build-time Clerk provider on otherwise static public routes.

## Existing development instance

Read-only CLI inspection on Oct28 Dhaka found the existing Real2Simulation app
`app_3LHWo2Ia88IuLU1EbEccvw7PR01`, development instance
`ins_3LHWnymdMlpMzl1agaLWNkGGDS7`. Public Frontend API `/environment` reports
Google enabled/authenticatable and email first-factor/verification `email_code`.
No configuration changes, user creation, credential retrieval or new app occurred.

Use Clerk's shared **development** Google credentials (no custom Google client)
and email verification code for sign-in and sign-up. Those are instance settings,
not JSX component props. Do not add Google secrets to the application.
The selected instance's existing custom-credential state was not read; shared
credentials are the approved policy, not an independently verified field.

Required deployment key **names only**:

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` — public; available at build time.
- `CLERK_SECRET_KEY` — server only; never prefix with NEXT_PUBLIC.

Provision securely through the authorized service workflow, never copy secrets
between worktrees or print them. Rebuild after changing the public key (Next.js
inlines public env at build time). Do not use `clerk init` here: it could create
an unapproved app. Root `.env` is not auto-loaded by the nested Next.js project.
CLI login exists but the local web project is not linked and has no Clerk env file.

## Guest/private boundary (S04d)

Public pages, including `/library`, do not run a session proxy, so an invalid
session cannot turn guest browsing into a sign-in wall. Private resource
authorization is local to the server data boundary, not delegated to a proxy.

The workspace leaf calls server-only `requirePrivateScene`. Its pure policy
requires valid IDs, verified session-token identity, exact owner/scene/access
metadata and denies on missing configuration, missing records or dependency
failure. It returns a minimal grant, never storage roots or the scene payload.
Callbacks are trusted server dependencies, never request parameters. Check again
at every job/asset read or mutation; do not rely on a layout, proxy or old grant.

**No private repository is wired.** An absent server metadata lookup denies before
identity retrieval (no needless provider work for unavailable scenes), and
the private layout retains independent unconditional denial. Authenticated private
access is intentionally unavailable; there is no test-user or fixture bypass.
Future integration must wire Clerk's required session-context proxy and replace
the absent lookup with ownership-filtered trusted metadata, review the boundary,
and prove real owner/nonowner/session E2E before removing layout denial. Do not
add an env flag to enable private access. An attempted Next16/Clerk proxy stalled
configured private HTTP requests in this run (also with no identity lookup);
standalone middleware returned200. It was removed rather than shipping a hanging
boundary. Root cause within the Next/SDK integration is unresolved; real session
verification is not claimed. Missing context/errors will still deny at the guard.

S01b/S04h/S22 must prove actual Google/OTP and logged-out flows with development
keys; no authenticated end-to-end flow was run. Production Google is deferred,
and shared development credentials are not a production configuration.

## Checks

```powershell
node --test Build/web/src/auth/config.test.mjs
node --test Build/web/src/auth/access.test.mjs
npm run build --prefix Build/web
npm run smoke --prefix Build/web
node Build/web/src/auth/bundle-check.mjs
```

Build with the noncredential `sk_test_S04C_SYNTHETIC_SERVER_SENTINEL` environment
sentinel to strengthen the last check. The scanner checks emitted browser assets
and source boundaries, not real credential validity or authenticated behavior.
No lockfile was added outside Owns; transitive versions are not frozen (S04b limit).

Official references consulted: [Next.js quickstart](https://clerk.com/docs/nextjs/getting-started/quickstart),
[resource-local checks and proxy](https://clerk.com/docs/reference/nextjs/clerk-middleware),
[server auth](https://clerk.com/docs/reference/nextjs/app-router/auth),
[Google](https://clerk.com/docs/guides/configure/auth-strategies/social-connections/google),
[email strategies](https://clerk.com/docs/guides/configure/auth-strategies/sign-up-sign-in-options).
