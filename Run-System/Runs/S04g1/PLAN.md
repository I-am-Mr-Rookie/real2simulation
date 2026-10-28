# S04g1

- Objective: reject incorrect/missing dev endpoint service/status labels while preserving pinned revision, readiness dependencies and worker503 behavior.
- UTC start: 2026-10-27T20:52:03Z (claim); initial read-only bootstrap preceded claim.
- Owns: infra/railway/dev/ only; this run's PLAN/report/evidence plus serialized canonical recovery controls.
- Lane: CODEX-2; requested GPT-6.1 Sol medium; exact runtime model/effort unavailable.
- Acceptance: offline regression red then green; read-only live HTTP checks; no deployment/config/auth/routing/credential change.
- Timebox: 15m; use stdlib tests with synthetic HTTP transport, never gate evidence.
- Checklist: claim/isolate; reproduce; minimal fix; verify; request serialized FF/control window; report and commit.
