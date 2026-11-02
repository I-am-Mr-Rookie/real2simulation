# N46-orch291
Status: DONE
Primary https://real2simulation.up.railway.app and custom https://real2simulation.rookiecoders.tech live; old web-dev-cd80.up.railway.app retained too.
Cloudflare: only real2simulation CNAME and its _railway-verify TXT added, DNS-only; exact targets in evidence/N46/FINDINGS.md and Cloudflare receipts.
Railway custom domain verified, certificate VALID; default trust-store/hostname TLS validation passes on both new hosts.
Real Gmail OTP sign-in completed separately on both new hosts with Koushik's selected existing account; /workspace Connected on both. Account ID only in real-gmail-check.json; no account created.
Headed Playwright Chromium: /lab, /library, Clerk widget and fixed-code test-account sign-in pass on both hosts; private API health 200. Real Gmail check additionally used headed in-app Chromium.
Updated only five named live-reference files; deployments.json changes limited to web domain fields. No API-domain or app-code change.
Controller redeployed N44 API during this run; verifier correctly rejected its stale revision pin. Refreshed the pin to known local controller commit ccb8b5d5; kept metadata revisions untouched as required.
Checks: python infra/railway/dev/verify.py exit 0, 17/17; python evidence/N46/test_verify.py 2 tests PASS; git diff --check PASS; targeted staged-text secret scan PASS.
Paid calls: 0. No inference, deployment, purchase, production change or Clerk setting change.
Skipped: web build (no app changes), proxied mode (DNS-only works); screenshots/cache remain local and uncommitted per contract.
Risk: existing infra/railway/dev/test_verify.py is outside Owns and already stale at dispatch (API revision and old-host transport); focused N46 tests cover both new hosts. See FINDINGS.md.
