# N46 DEV domains

## Live outcome
- Primary: https://real2simulation.up.railway.app
- Custom: https://real2simulation.rookiecoders.tech
- Retained alias: https://web-dev-cd80.up.railway.app
- All three route to web service `49f2938d-1566-480d-94e3-c9f7fefe24c2`, DEV environment `c5823a28-5118-49d8-b4d6-9851fa8ccc45`, port 8080. API/worker domains unchanged.
- Railway CLI and `generate_domain` return existing domains without trying to create another. The documented public GraphQL `serviceDomainCreate` **does** support another generated domain: created it, then renamed it to the previous host. `second-generated-domain.json` and `railway-domains.json` record this. The old alias briefly disappeared during the first rename and was restored.
- No deployment, purchase, model/API inference call, or Clerk configuration change.

## Cloudflare additions
Only these previously absent exact names were added. No other DNS record was changed or deleted. Both are DNS-only, TTL auto.

| Name | Type | Target |
|---|---|---|
| `real2simulation.rookiecoders.tech` | CNAME | `47g8adl9.up.railway.app` |
| `_railway-verify.real2simulation.rookiecoders.tech` | TXT | `railway-verify=2cb266041531e724df4dd1bfec04de818931d0e8ab967de2de80ed2c60884d7a` |

The TXT is public domain-ownership proof, not a credential. Cloudflare record receipts contain only these two hosts. Railway reports verified and `CERTIFICATE_STATUS_TYPE_VALID`. `tls.json` records Python default trust-store and hostname validation for both new hosts; no certificate bypass or insecure flag.

## Checks
- `python infra/railway/dev/verify.py`: exit 0, 17 checks, both new hosts including `/lab`, `/library`, `/sign-in` and private-route fail-closed behavior; API/worker checks retained. Receipt: `verify.json`.
- `python evidence/N46/test_verify.py`: 2 offline tests pass, including a failure on every checked path on either host. It reuses existing service fixtures with their stale API revision corrected in memory, not on disk.
- `node evidence/N46/browser-check.cjs`: exit 0, headed Playwright Chromium, isolated contexts per host. `/lab` and `/library` render, Clerk widget loads, existing DEV test account signs in using the documented development email code, private workspace renders connected, authenticated `/api/workspace/health` returns 200. No uncaught browser errors. Receipt: `browser-check.json`.
- Real email check: after the in-app browser became available, Koushik selected an existing account. Requested a separate real sign-in code on each host, read each from the signed-in Gmail inbox, and completed both sign-ins. Both private workspaces render Connected. Receipt: `real-gmail-check.json`, account ID only. No account creation, codes, real email addresses, inbox exports or private clips saved to evidence.
- Retained old host: HTTPS `/sign-in` returned 200 and the expected heading after restoration.
- `git diff --check`: pass.
- The controller deployed API commit `ccb8b5d5c66c925eea3578e4b0488adf27e5c822` during this run (03:46 UTC). An end-of-run verifier check correctly rejected the stale N34 revision pin; saved that failure as `verify-during-controller-deploy.json`. Updated only the verifier API pin to the known local controller commit and repeated checks; deployment receipt: `concurrent-api-deployment.json`. Kept deployments.json revision/deployment metadata unchanged as required by the domain-fields-only scope.
- Screenshots of sign-in/workspace were inspected locally; no real emails shown. PNGs are deliberately not committed per worker contract.

## Scope and limits
- Changed only the five named live-reference files plus `evidence/N46/` and the worker report/timebox. Deployment metadata changed only web domain fields. No application code, dependency, export, historical evidence, old capture script, or API domain change.
- The in-app browser was initially unavailable to the hidden worker. Opening Gmail queued the tab; it became available after owner interaction. Real Gmail OTP verification then completed on both hosts in the headed in-app Chromium browser using Playwright, with an accessibility fallback for one timed-out code entry. No Chrome control was used. The separate scripted Chromium check still honestly labels its fixed-code fixture as not testing email delivery.
- The literal contract default `email+clerk_test@example.com` does not exist. Used an existing DEV test fixture from a read-only, credential-redacted Clerk user lookup instead; no account was created or modified.
- Existing `infra/railway/dev/test_verify.py` already failed at the dispatch base: it pins API revision `db6060d2...` while the verifier pins `e5bcfcc5...` (8 tests, 71 failed assertions/subtests observed before edits). Its web transport also assumes the old hostname and 11 checks. It is outside Owns and was left unchanged; the focused N46 regression covers the new transport matrix.
- No web build: no application code changed. No proxy-enabled certificate test: DNS-only was requested and passes.

## Sources
- [Railway domain API](https://docs.railway.com/integrations/api/manage-domains)
- [Railway CLI implementation](https://github.com/railwayapp/cli/blob/master/src/commands/domain.rs)
