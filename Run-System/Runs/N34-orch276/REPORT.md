# N34-orch276 REPORT
Status: DONE. DEV only. Branch run/N34-orch276.
Changed: API image installs Rapier 0.21.0 in Build/web/node_modules; build imports/initializes the actual physics.mjs; report banner uses the actual run engine; chip overlay reserves timer width at all viewports.
Staging: added transitive frame.mjs; worktrees reuse only manifest-hash-verified canonical SAMPLE bundle bytes. Initial API build failed safely on missing frame.mjs, then fixed and redeployed.
API: e5f1df87-3181-4683-9cbb-d6c4deb009b1 SUCCESS, source db6060d2a994f8f1f36f2507a64b07ecdf7a0c72.
Web: 1efdd9cb-47d5-42a3-a4ed-4ff314885210 SUCCESS, source 38f5ec6972c082cefab716f2b733c6ddeca37c86.
Updated deployments.json, verify.py API revision, verifier fixture.
Checks: 19 Python report/stager/verifier tests; 17 lab-editor Node tests; npm run build exit 0; git diff --check clean.
Live: python infra/railway/dev/verify.py exit 0, all 11 checks passed (20:34:02 UTC). API ready200, unauthenticated workspace401, worker ready503 intentional.
Smoke: headed Playwright Chromium, one fresh +clerk_test@example.com account, 424242, Standard, SAMPLE room, exactly 2 agent turns.
First drop: Rapier, SIMULATED g 9.809993 +/- 0.014 m/s^2; report banner and second reply explicitly name Rapier.
Screenshots: evidence/N34/dev-desktop.png and dev-375.png (local, not committed); visually inspected; mobile chip/timer rectangle overlap false at 375 px.
Paid: 20:32:38.623Z, muse-spark-1.3, 3 calls, 7722 in/1644 out, estimated USD 0.015942; 20:33:08.896Z, same model, 4 calls, 11487 in/2787 out, estimated USD 0.025422.
Paid total: 7 calls / 2 turns, USD 0.041364 estimate, existing API daily_cap reservation/settlement path; billing and live SQLite not independently read. No GPU/image calls.
Evidence: evidence/N34/README.md, smoke.json, live-report.md, verify.json. Screenshot hashes in README.
Skipped: production, physical calibration, broader product E2E, full repository secret scan; no push.
Risk: report-only second turn added another ball and reran; ball-2 surface_contact biased g. Preserved verbatim; agent behavior outside Owns. First single-ball smoke passed.
