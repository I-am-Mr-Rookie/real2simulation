# S04a — DONE

## Authorization, objective and execution

Authorized: `Complete run S04a. Orchestrator mode: questions to the fallback.`
Objective: document isolated viewer, job and guest-library integration contracts
and fixture mount points. S01a/S01c/S03 DONE at preflight. CODEX-2; planned GPT-6.1
Sol / medium. Actual delegated Codex runtime identity/effort not exposed; no model,
provider, credential, permission or global configuration changes.

- UTC start 2026-10-27T18:00:46Z; main verification 18:06:56Z;
  receipt commit 2026-10-27T18:08:18Z (d41915c); final receipt correction follows.
- Initial main observed 8cc491dc98bbb176147a5b7328dc447ffeb33e9a, advanced through
  concurrent orchestrator commits; claim 72cd5bb. Prior reports read S08c/S08b/S08a.
- Native managed worktree created at
  `C:/Users/HP/.codex/worktrees/s04a/2026-10-26 - Meta Global AI Developer Hackathon`;
  changed detached checkout to run/S04a. Platform placement overrides manual
  .worktrees convention. Always used returned directory explicitly for task work.
- Initial task ef7dd6d rebased on latest main; verified task tip
  **3ed13f124fffc8b56de057072de556b89c351ba7** fast-forwarded into canonical main.
  Concurrent orchestrator communication changes and S08d claim preserved.
  S08d product commit e2c6843 landed before S04a's receipt commit; preserved,
  not accepted by S04a. Its owning worker maintains its own controls/evidence.
- Ten task files all within exact QUEUE Owns set. Canonical controls/PLAN/REPORT
  are serialized lifecycle exceptions. Four unrelated untracked research/concept
  paths left untouched. No remote/publication or archive-data import.

## Deliverables and decisions

- `Build/web/src/shell/README.md`: import direction, owner map, public/private
  routes, three UI slots, injected framework-independent viewer mount/dispose API,
  abort/stale-callback policy, scene-v1 units, job lifecycle and library boundary.
- `integration.schema.json`: closed Draft2020-12 versioned viewer/job/library
  DTOs. Guest viewer/public library cannot structurally reference private scenes.
  Ready job requires result, failed requires sanitized error, other states cannot
  expose a result. Safe opaque IDs; reject unknown versions/extra fields.
- `examples.json` and `fixture-mounts.json`: explicitly synthetic DTOs and a
  read-only repository mapping to existing S05a scene, not a copied artifact.
- `test_contract.py`: real schema validation, negative boundary cases, and fixture
  resolution. No mocks, external fetches, real jobs or renderer claims.
- `Build/web/src/auth/CONTRACT.md`: server-derived identity, allowlist vs private
  ownership, missing-config fail-closed behavior and sanitized errors.
- `Build/web/src/app/CONTRACT.md`: reserved route groups and composition seam.
- API/worker health contracts: liveness vs dependency readiness, 503 for unavailable
  dependencies, revision evidence, no paid probes or credential leakage.
- `infra/railway/dev/CONTRACT.md`: dev-only integration handoff, builds on Railway,
  no actual resources or deployments asserted.

D1 recorded in DECISIONS_LOG: shell DTO is NOT full S13 job-stage/upload contract;
S18 owns final rights/provenance library manifest. Scene-v1 stays authoritative;
no package/lockfile, viewer/workspace implementation or cross-lane edits. DTO
audience/access are not proof of authorization. Mystery mode remains disabled
until S10 defines a redacted payload; hiding gravity in UI is insufficient.

## Verification (actual commands/results)

| Command / stage | Observed result |
|---|---|
| `python -m unittest discover -s Build/web/src/shell -p test_contract.py -v` RED | 7 failures: explicit missing-contract assertion before schema existed |
| Same check, first implementation | 6 PASS, fixture path ERROR; parent index resolved one directory above checkout |
| Diagnose/fix | Stack path identified exact off-by-one; changed HERE.parents[4] to [3], used explicit UTF-8 reads; no weakening of expected fixture boundary |
| Same check GREEN | 7/7 PASS before commit, after rebase and on fresh canonical main |
| `python contracts/scene/validate_scene.py test-data/synthetic/scene/room-v1/scene.json` | PASS initially, after rebase and on main; explicitly synthetic/not Gate R |
| `python -m unittest discover -s contracts/scene -p 'test_*.py' -q` | 11/11 baseline and after rebase PASS |
| `python -m unittest discover -s tests/spec -p 'test_*.py' -q` | 39/39 worktree regression PASS |
| `python -m unittest discover -s Run-System/tests -p 'test_*.py' -q` | 17/17 baseline PASS |
| `git diff --cached --check`; `git diff main...HEAD --check`; `git diff --check` | PASS; path list manually checked against QUEUE Owns |
| `git rebase main`; `git merge --ff-only run/S04a` | Successful, no conflicts; main fresh shell checks PASS |
| `python Run-System/runs_view.py` | 13/193 DONE; 3 ready; zero owner questions |

No single aggregate product-test command exists yet; relevant suites above were
run explicitly. Line-ending normalization warnings are Git CRLF notices, not test
failures. No TypeScript compile/build asserted: no app/package implementation.

## Skills/plugins actually used

Read `Run-System/SKILLS_AND_PLUGINS.md` and selected installed Superpowers skills
under `C:/Users/HP/.codex/plugins/cache/openai-curated-remote/superpowers/7.0.1/skills/`:

- `using-git-worktrees`: verified Git isolation and ignore rule, listed attached
  artifacts, used native create/status tools and returned path; baseline checks.
- `test-driven-development` plus `writing-good-tests.md`: authored negative schema
  checks first, observed RED, implemented minimal contract, ran GREEN/regressions.
- `systematic-debugging`: traced actual missing fixture path to parent-index
  calculation; smallest correction then full shell check. Reference was read
  during failure handling; no broad refactor or speculative changes.
- `verification-before-completion`: fresh post-rebase and canonical-main checks,
  reviewed changed-path isolation before DONE receipt.
- `using-superpowers` read; dispatched-subagent exemption applies, so no workflow
  use claim beyond selecting applicable skills above. Run protocol itself supplies
  execution/finish checklist; no separate brainstorming/design exercise needed.
- Codex app `get_usage_limits`, `list_artifacts`, `create_worktree`,
  `get_worktree_creation_status`, `archive_worktree` actually called. Native archive
  refused: **The task's primary checkout cannot be removed.** Clean managed checkout
  retained recoverably; no manual deletion or bypass attempted.
- GitHub skipped: no remote/review task. Railway skipped: no resource/deployment
  scope in S04a. Clerk CLI skipped: contract only, no configuration reads/changes.
  Design/browser/computer plugins skipped: no runtime UI or reference research.
  No dependency/skill/plugin installation needed.

## Limits, cost and next

S04a acceptance met, NOT parent S04. No running routes, authorization enforcement,
job processing, viewer, health endpoint, private asset transport, Mystery-g safety,
Railway or E4 evidence. JSON schema is structure only, never an access-control
barrier. All product gates R/M/P/RS/A/C/D/S remain NOT RUN.

No secrets read, personal/archive data, footage acquisition, service inference,
GPU, uploads, accounts, terms, purchases, deployment or publication. New Meta/
service/GPU spend $0; historical Meta balance unknown. Coding tokens/task dollars
and Claude quota unavailable. Codex before/after used70%5h /50%weekly, remaining
30% /50%, reset1793132283; shared account, not task attribution.

S04b (CODEX-2 Sol medium) and S09a (CLAUDE Opus5.5 medium) dependency-ready;
verify model/lane availability and obtain next run authorization. S08d concurrently
IN PROGRESS, not accepted here. No owner decision needed; fallback remains clear.
