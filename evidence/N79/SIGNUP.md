# N79: fresh DEV sign-up investigation

## Result

- **PASS for fresh synthetic-email DEV registration:** after Koushik's direct action-time approval, verification completed and the new account opened its private workspace on Nov 3 around **08:49 Dhaka / 02:49 UTC**. No Protect error was reproduced. Real judge email delivery, Google OAuth and production remain unverified.
- Target: https://real2simulation.rookiecoders.tech, inspected in the ChatGPT in-app browser on Nov 2-3 UTC / Nov 3 Dhaka. This is DEV, not production acceptance.
- Signed out the existing fixture after checking its identity. Did not open any project or clip.
- Fresh address: `n79-20261102-2357+clerk_test@example.com`.
- The ordinary email sign-up form accepted that address and reached `/sign-up/verify-email-address` at approximately 23:56 UTC. Visible heading: **Verify your email**. It requests the code, with Continue available.
- No Protect challenge, CAPTCHA, allowlist error, redirect loop, domain error or other product blocker appeared before verification or during the approved completion.
- Initial closeout was PARTIAL: final verification awaited Koushik's direct action-time confirmation, and the controller instructed no account creation while that confirmation was pending. The later direct answer **Create the DEV test account** superseded that hold. The historical initial timebox is preserved, not rewritten as a passing run.
- **Continue with Google** is offered on both sign-up and the separately visited `/sign-in` page. Google OAuth was not clicked or completed, so its end-to-end result remains unverified.

## Approved completion follow-up

- Fresh bounded follow-up: `CONFIRMATION_TIMEBOX.json`, issued **02:47:46 UTC**, deadline **03:17:46 UTC**, acknowledged by the controller. Koushik's exact test-account approval was received directly in this chat, not inferred from a controller relay.
- The retained old tab handle returned `browser.user is unavailable`. A fresh tab in the same in-app browser worked. Submitted the **same approved synthetic email**, reached email verification again, then entered the documented development test code. No testing token or challenge bypass was used.
- Browser redirected to `/workspace/dev-fixture-68b68242c0776fa5c2b7babe10ae9769a78adab5b406aa40b7cf453adfd97530`. Visible heading: **Private workspace**, with first-account **Choose how the agent runs** onboarding, Standard and Muse Spark selected by default.
- Opened the account panel read-only and checked that its email exactly matched the approved N79 address, then closed the panel. This verifies that the workspace belongs to the newly verified account, not the old fixture. No project or clip was opened.
- Onboarding Continue was not clicked; no mode or model setting changed, no prompt or upload sent. The new persistent test account remains available and the workspace tab was retained for handoff.

## Read-only dashboard evidence

Already-signed-in Clerk dashboard selected **Real2Simulation / development**: application `app_3LHWo2Ia88IuLU1EbEccvw7PR01`, instance `ins_3LHWnymdMlpMzl1agaLWNkGGDS7`, matching the repository's auth notes. Settings inspected around 23:57-23:59 UTC. No toggles, values or policies were changed; detail dialogs were closed with Cancel, never Save.

| Surface | Observed state |
|---|---|
| User & authentication, Email | Sign-up with email on; require email on; verify at sign-up on; email verification code selected |
| Access mode | **Open** selected; Waitlist and Invite-only not selected |
| Allowlist | Off |
| Protect, Blocklist | Off |
| Challenge suspicious sign-ups | Active; Enable checked; **Suspicious** selected, not All |
| Require Device Intelligence checks | Active; Enable checked |
| Device Trust | Active |
| Lock accounts after failed sign-ins | Active |
| Prevent user enumeration | Active |
| Block disposable email addresses / email subaddresses | Both inactive |
| Block risky email domains / sign-ups by country / suspicious network types | All inactive |
| Challenge residential proxies / shared-infrastructure, email-domain and IP sign-up limits | All inactive |
| SSO connections, Google | **Used for sign-in**, **Shared credentials** |

Application Logs corroborated `sign_up.created` and `sign_up.email_address.created` at **Nov 3 05:56:12 Dhaka / Nov 2 23:56:12 UTC**, subject `sua_3LZZuVhlQ1xCexQ5Z2QiLFyAF8Y`. The selected creation event payload contained this run's synthetic email. These events establish an attempt, not a completed account. Real emails, IP addresses and unrelated event payloads are not retained here.

## Cause and comparison with N57

- `evidence/N57/receipts.json`, receipt `new-account-blocked`, records **2026-11-02T11:16:43.137Z**, path `/sign-up/protect-check`, with **Verification didn't complete. Please try again.** N57 used headed automated Playwright Chromium on the Railway hostname, not this run's in-app browser/custom-host combination. Its URL field still names a workspace while its explicit path field names the challenge, so do not treat that URL as a clean navigation trace.
- That historical failure is a verification/challenge failure, not evidence of invite-only access or an allowlist. Current access settings are Open with no allowlist or enabled blocklist. Current challenge and Device Intelligence protections are active.
- Read-only Application Logs also contain `protect.sign_up.challenged`, event `01a19bf8-f980-7cb8-aad6-aa8bb6fd2e78`, at **Nov 2 17:15:47 Dhaka / 11:15:47 UTC**, subject `sua_3LY5QqUOs7DJrpzYL6XgGxh97xN`. Filtering to that subject shows a creation event and an email-added event at the same time. The creation payload was checked to contain an N57-prefixed `+clerk_test@example.com` address without retaining its full value. This corroborates a Protect challenge immediately before N57's 11:16:43 failure. No event identifying the underlying suspicion signal was exposed in the selected payload.
- Seven-day filters for `protect.challenge.failed` and `sign_up.captcha.failed` returned **No events found**. This absence is not proof that the browser challenge succeeded; the browser may fail before submitting a result. No completed account event appeared in the historical subject's visible event sequence.
- **Inference, not a proved historical root cause:** automated-browser/device/network verification is a plausible explanation for N57. This run did not reproduce it. Current settings cannot establish which rule fired at the earlier time, or whether an asset, network or browser issue caused it.
- Clerk documents that suspicious sign-ups may get a Turnstile challenge and that failed challenges prevent account creation. Device Intelligence is a separate background check; sign-in success does not prove new sign-up readiness. See [Challenge suspicious sign-ups](https://clerk.com/docs/guides/protect/bot-protection), [Require Device Intelligence checks](https://clerk.com/docs/guides/protect/protections/require-device-intelligence), and [Protect requirements](https://clerk.com/docs/guides/protect/getting-started).

## Repository inspection

- `Build/web/package.json`: `@clerk/nextjs` pinned to `7.9.21`.
- `Build/web/src/auth/AuthProvider.jsx`: standard Clerk provider, local sign-in/sign-up paths, fallback redirect to `/workspace`.
- `Build/web/src/app/(public)/sign-up/[[...sign-up]]/page.jsx`: prebuilt `<SignUp routing="path" path="/sign-up">`, not a custom email/Google flow. Missing configuration explicitly renders unavailable rather than fake success.
- Matching sign-in page uses prebuilt `<SignIn>`; `auth/appearance.js` is presentation only. No repository-side invite rule or custom CAPTCHA flow was found in this wiring.
- `Build/web/src/proxy.js` matches private workspace and workspace API routes only, not `/sign-up`; it does not enforce a sign-up allowlist.
- `Build/web/src/auth/config.mjs` validates key syntax, not live instance settings. No credential values were read.
- `Build/web/next.config.js` configures a service-worker header but no app CSP. This is not proof about every live response header or external security layer.
- `Build/web/src/auth/README.md` and `infra/railway/dev/README.md` describe the development instance, shared development Google credentials and earlier existing-account verification. `evidence/N46/FINDINGS.md` verifies domains and existing-account sign-in, not brand-new judge registration. None supersedes this fresh attempt or proves production readiness.

## Smallest next step for Koushik

**No code change or auth-policy change justified by this attempt.**

1. Completed after direct approval: the named DEV test account was created, its identity checked, and its private workspace opened. No signup fix is currently justified by this reproduction.
2. Before declaring judge readiness, complete one consented new-user test with a real judge-like email or Google identity. A fixed-code synthetic address does not test email delivery, Google consent or a new browser/device.
3. If `/sign-up/protect-check` fails again, record the exact UTC time and browser, then inspect matching Clerk `protect.sign_up.challenged`, `protect.challenge.failed`, `protect.sign_up.blocked` and legacy CAPTCHA events. Check ClerkJS/Protect requirements and blocked challenge assets. The current server-side rule responsible for N57 is not proved.
4. Only if that evidence identifies a real integration defect, fix that defect or request Clerk support. Do not disable bot/Device Intelligence protection, broaden access, add an allowlist exception or use a Testing Token to claim real-judge readiness. Such policy changes require a separate owner decision and are outside this run.

## Local evidence and scope

Screenshots are local-only, not committed: `C:/Users/HP/.codex/visualizations/2026/11/02/01a19def-4a05-7d30-b96f-91547ed6bf9c/N79/` contains `verify-email.png`, `verify-email-final.png`, `access-mode.png`, `protections.png`, `blocklist.png`, `google-offered.png`, and successful follow-up `account-created-workspace.png`. No real email is shown in these captures. Dashboard overview/log screenshots containing personal data were not saved. The original `verify-email-final.png` records the initial paused state, not the final follow-up outcome. The dashboard and separate sign-in inspection tabs were closed.

No paid inference, deployment, push, user deletion, auth setting/policy edit, CAPTCHA solving, Testing Token injection or private-project inspection. Real email delivery, new-user Google OAuth and production remain unverified.
