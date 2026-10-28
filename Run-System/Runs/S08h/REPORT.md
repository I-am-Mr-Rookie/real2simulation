# S08h — DONE

## Receipt

- Objective: schema regression, ten deliberately invalid specs and all four
  analytic oracles. S08a–S08h now meet S08's offline acceptance, not Gate P.
- Requested CODEX-1 / GPT-6.1 Sol medium; observable delegated Codex session,
  exact runtime model/effort unavailable. No routing/settings changes.
- First retained UTC clock18:44:17 on2026-10-27 (preflight began earlier);
  verification finished by18:48 UTC, report18:48 UTC; client date Oct28 Dhaka.
- Initial inspected main41e0033; concurrent S09b claim preserved; S08h
  claim6fc1dec. Task commit/rebased and verified fast-forward:
  47875e7cb3d145e325898f8c4d7eacd153b05aa7.

## Changes

- tests/spec/fixtures/ten_bad_specs.json: exactly ten named single-field
  mutations spanning structural, dimensional, domain, scene and step safety.
- tests/spec/test_s08_acceptance.py:12 tests (ten individually named rejection
  tests plus manifest and four-template acceptance). Every bad spec starts from
  a successful factory/oracle baseline, then rejects at BOTH setup and oracle
  boundaries with readable reasons and no mutation. All four factories and
  oracles checked for independent analytic values, repeated-call equality,
  provenance, simulated labels and null unpropagated uncertainty.
- contracts/experiment/README.md documents the reproducible acceptance command
  and evidence limits. No product API/schema/physics behavior changed.
- PLAN/REPORT and serialized QUEUE/STATE/budget/log/view updates on main.

## Actual checks

| Command | Result |
|---|---|
| python -m unittest discover -s tests/spec -p test_s08_acceptance.py -v |12 PASS,2.665s; all ten rejection names visible |
| python -m unittest discover -s tests/spec -p 'test_*.py' -q |91 PASS worktree21.729s; main21.906s |
| python -m unittest discover -s contracts/scene -p 'test_*.py' -q |11 PASS worktree2.211s; main2.295s |
| git rebase main; targeted acceptance after rebase |Already up to date;12 PASS4.486s |
| git diff --cached --check; git diff main...HEAD --check; git diff --check |PASS; only Windows LF/CRLF notices |
| git merge --ff-only run/S08h |PASS |

An earlier full-suite invocation completed but its output was omitted by a
combined tool-result budget; repeated once to retain readable evidence above.
Two exploratory test filename reads missed nonexistent paths; directory listing
resolved the real names. Neither required a product change.

## Skills/plugins

Read/applied installed Superpowers verification-before-completion
(`superpowers/7.0.1/skills/verification-before-completion/SKILL.md`): fresh
targeted/full checks before commit and main acceptance. Tests-only task; no
new implementation requiring a TDD RED stage. Local Git worktree per manual
protocol. Codex app get_usage_limits before/after. Browser/native control,
GitHub/Railway, external research, model services and GPU skipped: entirely
offline existing-contract regression; no installs or unrelated changes.

## Limits/cost/next

No integrator, contact simulation, measured/real-scene evidence or Gate P run.
Ramp positive-acceleration domain and pendulum <=0.1rad linearized domain remain.
Repeated authoritative asset hashing is an existing validation cost; not changed
or benchmarked as product latency. No owner question or new scope decision.

Meta/service/GPU $0 new calls; historical balance unknown. Coding tokens,
subscription task dollars and Claude quota unavailable. Shared Codex before/after
used70%5h/50%weekly, reset1793132283; not per-task cost attribution. No resets.
No secrets/private/archive data, uploads, deployments, accounts, purchases,
terms, publication or submission. Unrelated untracked research/concept files and
concurrent S09b claim preserved. Clean local task worktree removed after merge.

Next: orchestrator chooses a ready authorized lane from RUNS.md; S09b remains
in progress, S04c ready; clip-dependent work remains gated by owner Q2.
