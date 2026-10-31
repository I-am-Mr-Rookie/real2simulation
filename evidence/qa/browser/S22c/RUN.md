# S22c Gate D fresh-account run 1: BLOCKED (no in-app browser)

Verdict: FAIL/NOT RUN. The full flow was not executed, so there is no timing against the <5 min target.

- Account letter used: none. Sign-up method: none. No account was created.
- Blocker (P1, environment): cua_repl cannot reach the in-app browser from this chat.
  - createBrowserTab("iab", url, {visible:false}) threw "Browser is not available: iab" at 13:57Z and again at 14:19Z.
  - cua.listBrowsers() returned []. cua.getState() listed only native apps.
  - Chrome was not used (owner rule: in-app browser only). No other browser was substituted.
- Controller messaging tool was not available in this chat, so no nonterminal blocker could be sent.
- Only HTTP probes were run (no login, GET only), 2026-10-31T13:58Z:

| Path | Status | ms |
|---|---|---|
| / | 200 | 867 |
| /library | 200 | 432 |
| /lab | 200 | 417 |
| /sign-up | 200 | 224 |
| /api/library/manifest | 200 | 359 |
| /workspace | 404 (anonymous, unauthenticated GET) | 249 |

Probes show the DEV site is up. They are not evidence of sign-up, upload, interview, fit or report behavior.
No screenshots, console logs or labels were captured. No defects against the app were observed.
Next action: run S22c where iab is exposed (a chat created by the app for this project), reusing evidence/owner/S22/S22-FRESH-ACCOUNT-AUTH-2026-10-31.md.

