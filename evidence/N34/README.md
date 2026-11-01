# N34 DEV readiness evidence

- API deployment: e5f1df87-3181-4683-9cbb-d6c4deb009b1, source db6060d2a994f8f1f36f2507a64b07ecdf7a0c72.
- Web deployment: 1efdd9cb-47d5-42a3-a4ed-4ff314885210, source 38f5ec6972c082cefab716f2b733c6ddeca37c86.
- Both staged with infra/railway/dev/stage.py and uploaded using railway up --detach from their fresh staged directories.
- API image installs only @dimforge/rapier3d-compat@0.21.0 in a Node build stage, copies node_modules into Build/web, then imports and initializes Rapier through the real physics.mjs module during the build.
- First API build 751dc38e-6a23-493c-b4e5-80bc67aeaf7c failed before deployment: N29 physics.mjs imports frame.mjs, missing from the old allowlist. Added it, tested staging, and redeployed successfully. Worktree staging also now finds the canonical ignored display bundle, still requiring every copied file's committed manifest hash.

## Live smoke

1. Headed Playwright Chromium, isolated context, one fresh n34-<nonce>+clerk_test@example.com account, code 424242. Chose Standard.
2. Opened the SAMPLE room lab, with 5,000 recorded points and 63 MODEL-ESTIMATED collision boxes. Scale and gravity remained unverified.
3. Turn 1: "Drop a 5 cm ball from 1.2 m and measure g". Tool result explicitly names Rapier, SIMULATED g 9.809993 +/- 0.014 m/s^2, floor_contact.
4. Turn 2: "Write the lab report and name the simulation engine used." Agent reply and actual report banner both name Rapier. No more agent turns.
5. Captured desktop at 1280 x 900 and mobile at 375 x 812. DOM overlap assertion compares every chip rectangle with the timer: false; document scrollWidth 360 <= viewport 375. Visually inspected both screenshots.

smoke.json contains actual responses, tool results, usage and DOM rectangles. live-report.md is the actual second-turn report. verify.json records all 11 live checks passing at 20:34:02 UTC.

## Paid calls

| Response UTC | Model | Calls | Input tokens | Output tokens | Estimated USD |
|---|---|---:|---:|---:|---:|
| 2026-11-01T20:32:38.623Z | muse-spark-1.3 | 3 | 7722 | 1644 | 0.015942 |
| 2026-11-01T20:33:08.896Z | muse-spark-1.3 | 4 | 11487 | 2787 | 0.025422 |

Total 7 calls, 19,209 input / 4,431 output tokens, estimated USD 0.041364 using the existing code's price table, not a billing assertion. API transport reserves/settles each call through daily_cap; live SQLite ledger was not independently inspected. No GPU or image calls; report illustration false.

## Screenshots (local, intentionally not committed as media binaries)

- dev-desktop.png: 330201 bytes, SHA-256 64170d54d4eff284c80bae3cf79b66d76e1ae4482756b8326f094d0066c6c5fc.
- dev-375.png: 266474 bytes, SHA-256 88303752fdcb957f31ab982adcf229c1de903e2cb53439f03cc423b305c47cb2.
- Directory: C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/N34-orch276/evidence/N34/.

## Limits

The second report-only turn unexpectedly called lab_add_object and lab_run again, duplicating the ball. Ball-2 then had surface_contact and g 10.11877 +/- 0.014, inconsistent with the scene setting. This is preserved in the evidence, not presented as successful calibration. Agent behavior is outside N34 Owns; no fix attempted. First-turn single-ball result is the free-fall smoke result.
Production, physical calibration, broader product E2E, provider billing and the full repository secret scan were not checked. DEV only; worker ready503 remains intentional.
