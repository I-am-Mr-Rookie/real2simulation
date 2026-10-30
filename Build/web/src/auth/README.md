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

**S04i development repository:** `scene-repository.js` is server-only and reads
one deterministic `dev-fixture-<SHA256 of verified user ID>` record per user.
`/workspace` derives that ID from Clerk's session, then redirects to its guarded
scene leaf. Metadata and payload reads both filter by the verified owner.
The payload omits owner identity. There is no global fixture owner, HTTP-supplied
identity, persistence, upload, asset/job endpoint or mutation. It is visibly
FIXTURE/SYNTHETIC and mounts S15's public React interface in `upload.idle` with
no fabricated scene artifacts, run or fit values. Full workflow service wiring
remains separate from this route mount.

The repository is available only in local NODE_ENV development/test, or the
existing Railway environment named exactly `dev` (including a production-built
Next server there). A named non-dev Railway environment overrides local mode.
An unlabelled production environment denies; there is no new enable/bypass flag.
Existing Clerk configuration is still required and ownership checks always run.

`src/proxy.js` uses standard `clerkMiddleware()` only on `/workspace/:path*`;
public library, sign-in and health paths do not match. Missing configuration
continues to the denying leaf; middleware errors uniformly deny. Clerk handshake
redirects, when needed for real session refresh, remain SDK-controlled rather
than hand-authored. The prior S04d proxy-hang finding requires bounded request
checks; S04i evidence records these independently from real session E2E. The
local 127.0.0.1 bind reproduced a loop of localhost same-route rewrites (diagnostic
channels saw no Clerk/JWKS host). Consistent localhost bind/request origins and
the deployment's 0.0.0.0 bind both pass bounded synthetic-config requests, with
the SDK unchanged. The smoke script now uses the consistent origin and can
also check the Docker bind via `--container-bind`.

S01b/S04h/S22 must prove actual Google/OTP and logged-out flows with development
keys; no authenticated end-to-end flow was run. Production Google is deferred,
and shared development credentials are not a production configuration.

## Checks

```powershell
node --test Build/web/src/auth/config.test.mjs
node --test Build/web/src/auth/access.test.mjs
node --test tests/web-private/*.test.mjs
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
