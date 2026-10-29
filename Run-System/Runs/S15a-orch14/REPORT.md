# S15a-orch14 — DONE

- Model: anthropic/claude-sonnet-5-5 high (assigned). OpenCodex-managed; not polled. Tokens/cost: unknown.
- UTC: issued 2026-10-29T11:22:02Z, deadline 11:52:02Z; work stopped 2026-10-29T11:27:47+00:00. Branch run/S15a-orch14 (worktree .worktrees/S15a-orch14).
- Files: Build/web/src/workspace/{workflow.mjs,fixtures.mjs,README.md}; tests/workspace/workflow.test.mjs; evidence/S15/{job_schema_diff.py,job_schema_diff.out.txt,workspace-tests.out.txt}.

## Result
Acceptance "upload/interview/run/fit/report state graph documented and tested": met.
- 15 phases, 18 events as a declarative graph (`G` table in workflow.mjs) with pure `reduce`; documented in workspace/README.md (diagram, consumed contracts, invariants).
- Tests (node:test, 8 pass): happy path; job rules (stale/equal revision, wrong id, status regression, terminal immutability, retry = new job id); spec validator fail-closed; run pause/resume/cancel/seed binding/malformed + gravity-key rejection/seeded replay; fit accepted only via parseFitReveal for expected session; EDIT_SPEC invalidates downstream and is blocked in flight; illegal events return same reference; every PHASE reached and every PHASE/EVENT documented in README.
- Differential check: parseJob verdict == integration.schema.json (Draft 2020-12) on 27 cases, 0 mismatches (it caught an extra-property gap, fixed). Shell test_contract.py: 7 OK.

## Ponytail (full)
Reuse: imported `parseFitReveal` (lab/fit-contract.mjs), shell job schema + examples.json (test input), shell/viewer public interfaces untouched, node:test as in tests/viewer. One reducer file, no framework, no deps, no manifest edits. Skipped: React/UI (S15b+), transport/polling, real S08 validator wiring (injected; stub in fixtures), S14 interview chip states (S15d), mystery mode, viewer mount.
Fixtures: visibly SYNTHETIC; fit value 1.25 m/s^2 is a deliberately non-physical inert placeholder passing parseFitReveal, not fitter output. No gate/real-scene/physical claim.

## Risks / unverified
- Hidden-g guard is key-name heuristic (gravity|hidden_g|mystery); real S10 redacted payload contract not consumed here.
- Run observations only shape-checked (finite time_s/position_m); not authenticated.
- No browser/React/dev verification; no deploys, installs, or edits outside Owns. Canonical controls untouched.
- Process note: apply_patch wrote first to canonical root (untracked); moved into worktree before commit, nothing tracked touched.
Communication: silent; one completion line to controller.

