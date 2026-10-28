# Dev-auth preflight observations — Oct28

Live browser inspection window: 2026-10-28 14:28:09–14:34 UTC (20:28–20:34 Dhaka).
Surface: actual **ChatGPT in-app browser**, browser ID2, authenticated service UI. No Chrome, connector fallback, native automation, clipboard, credential-value access, console logs or cookies/tokens.
These are selected safe UI labels/statuses, not full DOM exports or screenshots of credential pages.

## Railway — exact existing DEV web

[Variables](https://railway.com/project/b07b0d66-2001-4ccc-915d-7d226744d189/service/49f2938d-1566-480d-94e3-c9f7fefe24c2/variables?environmentId=c5823a28-5118-49d8-b4d6-9851fa8ccc45)

- Authenticated project view: Real2Simulation; selected environment **dev**.
- Project `b07b0d66-2001-4ccc-915d-7d226744d189`; environment `c5823a28-5118-49d8-b4d6-9851fa8ccc45`; service **web** `49f2938d-1566-480d-94e3-c9f7fefe24c2`.
- Service is Online, public domain `web-dev-cd80.up.railway.app`.
- Latest displayed deployment: **ACTIVE**, **Deployment successful**, `a7ea1564-fbe6-418e-bb29-7db3b8f45a02`; message `S04g event-only source 300cd2096f9e32bcdf3433520b36b67f709df0d5`, via CLI. This matches the existing deployments.json receipt. It is not a new rebuild.
- Variables page fully loaded: **No Environment Variables**; **8 variables added by Railway** (platform-generated group was NOT expanded).
- Exact required-name checks, repeated after loading: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` **ABSENT**; `CLERK_SECRET_KEY` **ABSENT**.
- No Raw Editor, add/edit/reveal/copy, platform-variable expansion or deploy action used. Project access and exact selected target verified; account email was not retrieved.

## Clerk — exact existing development app

[Email configuration](https://dashboard.clerk.com/apps/app_3LHWo2Ia88IuLU1EbEccvw7PR01/instances/ins_3LHWnymdMlpMzl1agaLWNkGGDS7/user-authentication/user-and-authentication)

- Signed-in account menu names **Koushik Sadhak Jeet**, organization **Koushik's Organization**.
- App **Real2Simulation**, `app_3LHWo2Ia88IuLU1EbEccvw7PR01`; instance `ins_3LHWnymdMlpMzl1agaLWNkGGDS7`.
- Read-only environment switcher: **Development selected**; no production instance selected/created.
- Email: Sign-up with email ON; Require email address ON; Verify at sign-up ON; email verification-code checkbox ON; verification link OFF.
- Sign-in with email ON; Email verification code switch ON; email verification link OFF.
- [SSO connections](https://dashboard.clerk.com/apps/app_3LHWo2Ia88IuLU1EbEccvw7PR01/instances/ins_3LHWnymdMlpMzl1agaLWNkGGDS7/user-authentication/sso-connections) contains row: **Google / Social provider / Used for sign-in / Shared credentials**.
- No settings were changed. API keys page not opened; no value retrieved or provisioned. Password settings not inspected because no policy change was authorized/needed.
- Initial direct app URL without instance returned404; recovered via visible **Go home**, then existing Real2Simulation link. One SSO table selector timed out while the page was loading; safe rendered-row inspection succeeded. Neither error establishes an account/access failure.

## Public dev routes

1. [Sign-in](https://web-dev-cd80.up.railway.app/sign-in): **Sign-in unavailable**. Text: Authentication is not configured; demo library remains available without sign-in. Clerk sign-in form not available.
2. Followed **Browse the demo library** to [Library](https://web-dev-cd80.up.railway.app/library): **Demo library**, **No demos are published yet. Guest browsing needs no account**, **Viewer not connected**, **No scene has been loaded**.

Rendered public navigation succeeds without entering identity or performing login. This is UI availability, not HTTP-status instrumentation, authenticated-session validation, scene playback, successful Google/OTP or owner E2E acceptance. No browser session storage/cookies inspected.

## Source and guidance checked

- Existing `Build/web/src/auth/{config.mjs,server-config.js,AuthProvider.jsx,server-access.js,access.mjs}` and public sign-in page: both names required, syntactic validation only, sign-in fails closed when unavailable. Private metadata repository is still intentionally absent; wiring credentials alone does not enable private-scene access.
- Installed `@clerk/nextjs`7.9.21, Next16.4.3 from package.json. No install/build/source change.
- [Official Next.js quickstart](https://clerk.com/docs/nextjs/getting-started/quickstart) inspected; existing authentication must not be replaced casually, and server secret must not enter client code. New-app CLI provisioning is outside this existing-app contract and was not run.
- [Official Playwright testing guidance](https://clerk.com/docs/guides/development/testing/playwright/overview) inspected; integration uses `@clerk/testing` and setupClerkTestingToken. No testing token created, bypass enabled, test user/signup/OTP or storage-state export performed.

## Decision

**No redeploy.** BOTH-name prerequisite fails; existing build is old but a rebuild alone cannot fix absent configuration. No need for a redundant dev-deploy consent request. Separate explicit scoped authority and a supported secret-safe provisioning/transfer workflow are required before moving the existing development credential pair into this exact Railway DEV web service. The next worker must not solve that by printing keys, copying them through model/clipboard, creating another app, or changing Google/OTP policy. After secure provisioning, verify names, rebuild only this existing dev web within its contract, then inspect sign-in. Human S01b Google/OTP acceptance remains separate.
