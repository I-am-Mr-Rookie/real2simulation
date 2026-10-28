# R11-browser-gate — REPORT

Status: **DONE** — no P0–P2 findings. Narrow gate review of the S10n normal browser compute + public/private DTO transport.

- Code head reviewed: `694df9a0fd1fd1949cedec396de69a73ff1bad35` (main `5e0fd65`); diff `main..HEAD` of Build/lab/session-bridge.py, Build/lab/session-service.mjs, Build/web/src/lab/{browser-simulator.mjs,BrowserSimulation.jsx,LabClient.jsx}, tests/lab/{browser-simulator,session-service,ui-contract}.test.mjs, tests/lab/test_session_bridge.py.
- Reviewer: this native session (Anthropic Claude agent). `spawn_agent` was not in this session's tool catalog, so no extra sub-agent was spawned; no Claude Code used. One review only.
- UTC start 2026-10-28T20:37:59Z; end 2026-10-28T20:41:32.7031235Z. Tokens/cost: unknown; coding quota OpenCodex-managed; not polled. No GPU/API/paid spend.
- Ponytail FULL applied: reviewed for reuse/smallest change. Concrete: browser path reuses existing `consumeValidatedTrajectoryArtifact`/`trajectoryFromValidatedArtifact` (Build/simulator/trajectories.mjs) and `extendedTrajectoryFromValidatedArtifact` (extended-templates.mjs), which import only `rk4.mjs`: no copied physics, no Rapier in browser graph. DTO = the actual Python `export()` artifact, forwarded unchanged; no new wrapper type. Recommended no change (smallest correct = none).

## Gate criteria

1. **Mystery never publishes setup/gravity/seed/DTO, errors or stale transitions — PASS.**
   - session-bridge.py:80-83 adds `browserSimulation`/`gravity` only when `not mystery`; session-service.mjs:74-77 forwards DTO only for `!request.mystery` (an injected DTO in a Mystery reply is dropped — test session-service.test.mjs:177).
   - Fresh probe (evidence/probe-output.txt): Mystery free_fall/projectile response keys = limitations,mode,observationHash,observations,sessionId,source,status,template,units; strings `browserSimulation, validatedSetup, seed, gravity, private, setup, magnitude_m_s2` absent. Mystery ramp → only `mystery_supported_for_ballistic_templates_only`.
   - Errors: service returns fixed codes only (session-service.mjs:95); BrowserSimulation.jsx `catch` renders a fixed message, never raw error/input. browser-simulator.mjs rejects non-`normal` mode before reading the artifact (verified, `browserRejectsMystery: true`).
   - Stale: LabClient version/abort guards (lines 29-50, 57-73) unchanged and tested; BrowserSimulation result is keyed by payload identity (`result?.payload === payload`), so a prior trace never displays for a new session; mount condition LabClient.jsx:101 `session.mode === 'normal' && session.browserSimulation`.
2. **Normal DTO from actual validated Python export, bounded <=2000, real four engines — PASS.**
   - Probe: all four normal DTOs have producer `contracts/experiment/validate_experiment.py`, 3.5–3.8 KB; browser traces free_fall/projectile/ramp 201, pendulum 1001 samples; `rk4-fixed-step`, simulated, synthetic.
   - Bound enforced three times: bridge (session-bridge.py:40-46, integer horizon, steps < 2000), service `normalBrowserSetup` (session-service.mjs:20-34, same exactness, seed 42/g 9.81/synthetic), browser (browser-simulator.mjs:15-18 pre-engine, :23-26 post-engine samples <=2000). Engines additionally enforce exact integer horizon (trajectories.mjs:7-10, extended-templates.mjs:7-10).
3. **Labels/limitations + safe normal-only mount — PASS.** BrowserSimulation.jsx: "Simulated · synthetic · RK4-only. No contact response or free drag.", SVG title "computed in browser with fixed-step RK4", table caption "not the full trace", status "NORMAL mode only"; compute only on explicit button click.

## Findings (P3 only, non-blocking)
- P3 Build/web/src/lab/BrowserSimulation.jsx:29 — wording "free drag" is ambiguous; consider "no drag/air resistance". Cosmetic.
- P3 Build/web/package.json:8 `next build --webpack` + next.config.js sets only `turbopack.root`; importing `../../../simulator` outside the app root is unverified for the webpack build here. Parent owns actual browser/375px checks; flagged as risk, not claimed.
- P3 browser-simulator.mjs:16-17 pre-engine check uses `Math.round` without exactness; harmless because engines reject non-integer horizons and server checks exactness.

## Fresh checks (saved in evidence/)
- `node --test tests/lab/browser-simulator.test.mjs tests/lab/session-service.test.mjs tests/lab/ui-contract.test.mjs` → 51 pass, 0 fail (node v24.18.0) — evidence/node-tests.txt.
- `python -m unittest tests/lab/test_session_bridge.py` → 10 tests OK (pytest not installed; unittest used) — evidence/python-tests.txt.
- `node evidence/probe.mjs` (independent leak/bound probe through real bridge) → evidence/probe-output.txt.
- `plotPoints` edge checks (empty/1-point/flat) return safe domains; no render crash path.

## Skipped / limits
- No actual browser, 375px, Next build or bundle check (parent-owned). No R10 numeric/contact/cancellation re-audit. No installs, product edits, controls, merges, deploys.
- Communication: silent; single final line only.

