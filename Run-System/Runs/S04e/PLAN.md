# S04e plan

- Objective: separate FastAPI API and worker health skeletons returning HTTP200 for local liveness; fail-closed readiness until real dependencies/worker exist.
- UTC start (host clock): 2026-10-27T20:01:09Z (client date Oct28 Asia/Dhaka).
- Requested lane/model: CODEX-2 / GPT-6.1 Sol medium; actual delegated Codex, exact identity/effort unavailable.
- Baseline main: 5775cb7529c084fb0197d72767ed327456830231; claim: 13ac386.
- Owns: Build/web/src/shell/; Build/web/src/auth/; Build/web/src/app/; Build/web/package.json; Build/api/health/; Build/worker/health/; infra/railway/dev/. Implementation limited to the two health directories; no web/deploy change.
- Checks: test-first HTTP contracts; actual loopback HTTP200 from both Uvicorn processes; readiness503 with no fabricated dependencies/heartbeat, safe revision metadata.
- Timebox: <=30m from start; no new implementation after minute25. No services/secrets/inference/GPU/deploys. OpenCodex-managed; not polled.
- Canonical controls serialized at claim/completion; preserve unrelated research and concurrent controls. No owner question expected.
