# R14-service-boundary — bounded independent audit

- Objective: audit exact-source local lab request/response boundaries and shared-session fit state; freeze minimal independent regressions/counterexamples only. No product changes, control writes, merges or service/network use.
- Requested lane/model: CODEX-1, managed gpt-6.1-sol, high; runtime identity not independently attested. OpenCodex-managed; not polled.
- Issue: 2026-10-28T21:37:28.000Z. Cutoff: 2026-10-28T22:02:28.000Z. Deadline: 2026-10-28T22:07:28.000Z / 2026-10-29T04:07:28.000+06:00. First observed clock: 2026-10-28T21:37:46Z. Verified complete audit may finish early; no early incomplete terminal result.
- Baseline: 74c886f; branch run/R14-service-boundary; initially clean isolated worktree C:/Users/HP/.codex/worktrees/swarm14-service-boundary/2026-10-26 - Meta Global AI Developer Hackathon.
- Canonical root: C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon. Canonical main observed 55a3d2e during intake; audit remains pinned to assigned baseline.
- Parent project: Meta AI Hackathon, 91e441f8-e40c-4ec4-bea2-de7fa1582d97, inherited contract/root; parent-visible UI corroboration reported by launcher, list_threads projectId null. No independent child UI association claimed.
- Exact Owns: this run directory; evidence/S10/service-invariants/; tests/lab/r14-service-invariants.test.mjs. Read scope: Build/lab/session-service.mjs, Build/web/src/app/api/lab/route.js and relevant tests/helpers.
- Apply Ponytail FULL: reuse Node test runner and existing controlled-bridge pattern; smallest complete independent assertions, no dependencies or product refactor. Keep expected error and success oracles independent from implementation output.
- Checks: request allowlist/shape and body byte boundary; malformed bridge response rejection; concurrent failed/completed fit deduplication, retries, cache/expiry/session replacement. No duplicate abort/process-tree or production bundle tests; privacy is another worker.
- Acceptance: exact-source confirmed counterexample or bounded clean evidence, fresh targeted CPU checks, honest limits, report/timebox, owned-only commit. Confirmed findings immediately reported nonterminal for parent fixes; no fanout.
- Safety: no paid work, real scenes, physical gates, deployments, browser/UI, installs, credentials/config/routing changes or environment-value reads.
