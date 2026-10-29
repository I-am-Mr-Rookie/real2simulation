# S01b owner receipt — Google, email OTP, guest access

- Recorded: 2026-10-29 13:02Z (19:02 Dhaka), by Codex from Koushik's chat confirmation.
- Owner statement (verbatim): "All right, everything is working properly, and I think
  the run is completed with flying colors." Earlier the same day he confirmed Google
  sign-in worked and that "everything is working fine now".
- Evidence class: owner observation (E2) in chat. No screenshots of the three flows were saved.
  No agent E2E sign-in was done; the agent handled no credential values.

## Agent-verified facts (no secret values read)

- Railway dev web `49f2938d-1566-480d-94e3-c9f7fefe24c2`, deployment
  `8ab5d816-d52a-4f5f-9d3f-13e3ee149f27` SUCCESS; source `790f976` on branch
  `run/S01b-account-nav-dev` (= `300cd20` + account-menu fix; main equivalent `c4a3149`).
- Both Clerk variable names present in the container with `pk_test_`/`sk_test_` formats; `/sign-in` renders Clerk.
- Clerk dev instance `ins_3LHWnymdMlpMzl1agaLWNkGGDS7`: Google ON; email sign-in with
  verification code ON; "Add password to account" ON; sign-up with password OFF; min password length 15.
- Header shows Clerk UserButton (Manage account / Sign out) when signed in, otherwise a "Sign in" link.

## Limits

- Dev only, development Clerk instance; not production or judging.
- Current `main` cannot deploy on Railway as staged: `/lab` imports `simulator/` and
  `lab/session-service.mjs` outside the `infra/railway/dev/stage.py` web allowlist
  (deployment `7e6e079d` FAILED). Fix in a separate run before the next main deploy.
- S04h (agent E4 sign-in/guest/health verification) remains a separate run.
