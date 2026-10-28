# F-CODEX-2-1 — DONE (analysis deliverable only)

## Result

Completed the bounded, read-only review of finished CODEX-2 shell/auth/health/dev-packaging modules. One reproduced verifier acceptance defect; intentional auth/worker limitations and concrete readiness/hardening follow-ups are distinguished in [CHECKLIST.md](CHECKLIST.md). No product/test, deployment, live-auth or other-lane edits. Worker readiness remains503, including with successful synthetic dependency checks. No event gate passed or production readiness inferred.

## Scope and evidence

- Owns: `evidence/fillers/CODEX-2/1/`, plus authorized serial run-lifecycle controls/report pointer. Changes: PLAN, checklist, report, offline reproduction and receipts/source hashes; control completion is recorded below.
- UTC start20:38:06 on2026-10-27 (Oct28 Dhaka); final verification time in `verification.txt`; within15m.
- Initial main SHA `bfb4f5ad4513c9fe0d4ec979155adfbaac6be5dc`. Main advanced during concurrent orchestration; reviewed application/infra sources were unchanged against that baseline. Unrelated untracked references, other-lane evidence and concurrent RUNS changes preserved.
- Read current AGENTS, README, owner checklist, applicable final-plan section, manual protocol, queue/state/decisions/budget/rubric and latest S04g/S04f/S04e reports. Historical live-deployment claims were treated as prior reports, not freshly verified runtime state. No archive or other-lane product source inspected.

| Fresh command | Result |
|---|---|
| `node --test Build/web/src/auth/config.test.mjs Build/web/src/auth/access.test.mjs` | Exit0;8/8 pass. `auth-checks.txt`. Pure policy/config checks, not real sessions. |
| `python -B -c "import runpy; runpy.run_path('evidence/fillers/CODEX-2/1/reproduce.py', run_name='__main__')"` | Exit0; `offline-observations.json`; empty stderr. All probe/HTTP adapters synthetic and patched locally; environment cleared during health checks. Worker503 verified; wrong service/status verifier acceptance reproduced. |
| `git diff --quiet bfb4f5ad4513c9fe0d4ec979155adfbaac6be5dc -- <reviewed source directories>` | Exit0; no reviewed-source drift. Source SHA256 manifest in `source-hashes.json`. |
| Final report/evidence/scope verification | `verification.txt`. No source/runtime changes. |

An initial content read incorrectly combined LiteralPath with Path (failed, corrected by literal leaf read); a Windows rg wildcard argument failed (corrected with `-g '*.Dockerfile'`). Neither changed files or affected results. No build/install, live verifier, external-resource health checks or full health suite run; those exceed this offline review or can call downstream services.

## Skills/plugins actually applied

- `clerk-react-patterns`: read skill plus hooks/protected-routes references; used its provider/loading/server-boundary distinctions to avoid equating UI or client auth with authorization. Actual app is Next.js/server-component based, so no SPA router/hook recipe was imposed; no applicable hooks existed to change.
- `clerk-testing`: read skill and official [Playwright testing guide](https://clerk.com/docs/guides/development/testing/playwright/overview); used development-only/isolated-session requirements to frame the future E2E checklist. No Clerk setup/testing-token/user flow executed, no account created, no credentials accessed. External access was public documentation only, with no project payload.
- Superpowers `verification-before-completion`: read and applied fresh offline checks, source drift/hash verification, and explicit separation of synthetic replay from live/deployed evidence.
- Superpowers `using-git-worktrees`: read after protocol correction; checked existing attachments, created native managed worktree, selected exact `run/F-CODEX-2-1` branch, migrated only authored Owns evidence and reran both offline checks there. No dependency installation needed for these checks. Exact worktree path appears in PLAN.
- Browser/native UI, Railway, GitHub and remote review plugins not used: no relevant authorized live/UI/remote operation; no plugin install/enable or secondary model call. No speculative history search.

## Serialized controls / acceptance handoff

Initial lifecycle deviation: the filler was not claimed and evidence was authored on main, incorrectly treating evidence-only scope as an exemption from the manual lifecycle. At20:41 UTC the orchestrator explicitly corrected this. Preserved authored evidence and unrelated files; requested a serialized control window, migrated only this Owns directory to native managed worktree `run/F-CODEX-2-1`, and reran auth8/8 plus offline replay successfully. No product fix or new deployment is authorized by acceptance. Final claim/FF/control receipts are in `verification.txt` and canonical run report pointer. No owner question is required; fallback unused.

Correction completed under explicit control window: claim ab35f954; post-rebase evidence39d23e1b313875fea83eef247a108c38d8d3f498; main FF succeeded and both offline checks passed again. Canonical controls/pointer updated serially. Native archive refused because this is the task's protected primary checkout; retained clean, without bypass. No implementation scope broadened.

Requested lane/model: CODEX-2 GPT-6.1 Sol medium. Actual delegated Codex runtime exact model/effort, tokens and coding cost not exposed. Coding allowance: **OpenCodex-managed; not polled**. Meta/GPU/inference calls0; no new service provisioning or deploys; ongoing pre-existing Railway costs unknown.

Communication compliance: evidence on disk; no repeated status or duplicated report. Two mandatory skill/pre-tool updates emitted (Clerk review, then worktree correction). One authorized coordination message requested the serialized control window; no speculative delegation. Otherwise silent; final response is the required one-line report pointer. Next action after integration: return the reproduced verifier defect and readiness checklist to CODEX-2 under separately authorized work.
