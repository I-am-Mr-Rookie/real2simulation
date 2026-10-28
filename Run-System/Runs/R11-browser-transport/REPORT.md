# R11-browser-transport — DONE (narrow transport contract)

## Identity / time

- Lane/model: CODEX1; assigned managed Sol HIGH. Runtime model identity is not independently exposed; no model/provider/policy change.
- Worktree: C:/Users/HP/.codex/worktrees/swarm10-browser-transport/2026-10-26 - Meta Global AI Developer Hackathon.
- Branch: `run/R11-browser-transport`; base `72b1cbf55b4cdf914496dde644dd3aec745885fa`.
- **Exact tested code head: `1eaa870bd3109731f00819962b476a4e405c1b9c`**. Subsequent run-report/receipt commit changes metadata only.
- Parent project supplied by handout: `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; canonical C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon. No launcher/project change; association not independently verified.
- Issued 2026-10-28T20:19:40.032Z; first tool UTC 20:19:48.3710152Z; work stopped 2026-10-28T20:31:24.4810790Z; reported 2026-10-28T20:32:08Z.
- Full deadline 2026-10-28T20:49:40.032Z / Oct29 02:49:40.032 Dhaka; cutoff 20:44:40.032Z. Early narrow DONE: all owned acceptance met, not an early incomplete receipt.

## Change / concrete Ponytail FULL use

Read requested Ponytail FULL plus current canonical AGENTS/STATE/QUEUE/timebox policy and relevant source/callers. Reused the SAME actual Python S08 `export` already computed once inside `_start`: no second export, duplicate physics, model-authored setup or new dependency.

- Bridge emits `browserSimulation:{mode:'normal',validatedSetup:artifact}` ONLY for normal mode. Mystery keeps its existing internal private object but gets neither the new DTO nor authored public gravity.
- Bridge rejects nonfinite/fractional or >2000-point fixed-step horizons before spawning Node. Existing observation/body/process limits remain.
- Service admits normal DTO only from the fixed local bridge, checking expected export envelope, requested template, synthetic provenance/scene match, normal seed42/g9.81, and <=2000-point horizon. It adds the field only under `!request.mystery`; public allowlist/error envelopes retained.
- Unchanged: fixed request allowlists, first-order uncertainty/model carry, trusted fit reveal, abort propagation, TTL/session identity checks, capacity and process-close accounting.
- Authorship labels are NOT producer authentication. Trust is the fixed local Python producer invoking the actual validator; no caller-controlled artifact/editing input was added.

Owns changed: the two bridge/service files, their two existing test files, evidence/S10/browser-transport/, and this run directory only. No merge/rebase/main/control update.

## Fresh verification

Python 3.14.5 / Node v24.18.0.

| Command | Result |
|---|---|
| `python -m unittest discover -s tests/lab -p 'test_*.py'` | **17/17 PASS**, including actual pipeline/regression/acceptance |
| `node --test tests/lab/session-service.test.mjs` | **32/32 PASS**, final source/tests |
| All simulator + lab Node test files (PowerShell enumeration in evidence README) | **62 PASS; 2 contact-file load failures**: existing Rapier dependency absent in this fresh worktree |
| `git diff --check`, staged whitespace check, code-head working-tree comparison | PASS |
| `python Run-System/worker_timebox.py check Run-System/Runs/R11-browser-transport/TIMEBOX.json` | TIMING PASS; controller still verifies actual evidence |
| Fresh actual four-template public DTO capture | free_fall/projectile/ramp 201 observations each, pendulum 1001; actual validated exports |

Actual four-template DTOs equal actual Python exports; export wrapper confirms one production export per start. Ballistic Mystery tests cover seeds 0,1,2^31,2^32-1 on BOTH templates, no bridge DTO or authored public gravity, no service DTO even if injected into a trusted-reply test double, nested/error/exception redaction and normal-to-Mystery transition. Mode branches apply independently of all seed values; tests do not claim exhaustive 2^32 enumeration.

Existing stale-fit-after-eviction/expiry/hashing, abort-before/after-start, retry, four-process capacity, bounded-body/output, timeout/close and production-route-disabled checks remain green. Exactly 2000 horizon points admitted; 2001/fractional/invalid horizons rejected.

Evidence: [browser transport](C:/Users/HP/.codex/worktrees/swarm10-browser-transport/2026-10-26%20-%20Meta%20Global%20AI%20Developer%20Hackathon/evidence/S10/browser-transport/README.md). Raw logs and actual NORMAL DTO JSON tracked beside it; no Mystery private payload saved.

## Skips / risks / next owner

- Broader contact tests could not import `@dimforge/rapier3d-compat`; no installation, contact repair or whole-suite pass claim. The narrower required service tests pass. Existing Node typeless-package warning left untouched.
- Fixed normal seed/gravity checks intentionally reject future editable setups; revise only with approved editor scope.
- Parent still owns child browser-module integration, LabClient mount, actual IAB375px and final native-Claude targeted gate review. No browser/physical/gate success claimed here. Claude Code never used.
- Physical M/S12, real scenes, paid GPU, deploy/publish, accounts/terms/credentials remain locked. No external service, private file or secret operation.
- Tokens/cost: unknown/unobservable. **OpenCodex-managed; not polled**.
- Communication: silent except mandatory initial work update, required Ponytail announcement and material broader-test limitation. No optional duplicated summary or unsolicited cross-chat message; no owner question needed.
