# F-CODEX-1-1 — DONE (read-only evidence review)

## Result / scope

Read-only review of finished CODEX-1 S05a/S08a–h scene/spec contracts, validators and analytic references. Evidence only in `evidence/fillers/CODEX-1/1/`; no product/test/other-lane edits. Concrete checklist: `CHECKLIST.md`.

- Two reproduced edge cases worth a follow-up: free fall raises OverflowError for an invalid huge integer sample time; accepted sub-coordinate-resolution drop returns identical initial/impact world positions.
- Reproduced documented setup/oracle domain split and result evidence-string reuse across changed inputs. These are explicitly integration requirements, not newly claimed validator bypasses or persisted-data bugs.
- Reading-only observations: contact remains disabled; repeated validation rehashes/rescans scene assets; codec/rights checks retain documented downstream boundaries. No performance or real-media behavior inferred from code reading.

## Fresh evidence

| Command | Observed result |
|---|---|
| `python -B evidence/fillers/CODEX-1/1/probes.py` | Exit0, eight synthetic observation records; `probes.json`. Exit0 means observations reproduced, not product correctness. |
| `python -B -m unittest discover -s tests/spec -p 'test_*.py' -q` | Exit0,91 tests in15.590s, OK; `spec-regression.txt`. |
| `python -B -m unittest discover -s contracts/scene -p 'test_*.py' -q` | Exit0,11 tests in4.113s, OK; `scene-regression.txt`. |
| Same three commands in isolated run worktree | Probe exit0; spec91 OK18.598s; scene11 OK2.446s. Receipts `spec-worktree.txt`, `scene-worktree.txt`. |
| Post-rebase probe; main probe and both suites | Rebase already current; probe exit0. FF main probe exit0,91 spec tests OK13.712s,11 scene tests OK2.543s; `probes-main.json`, `spec-main.txt`, `scene-main.txt`. |

Initial probe invocation exited1 at the documented excessive-displacement setup guard in P3 ramp. Corrected only the review probe's timestep to0.0001 s; rerun reproduced the intended domain split. No production check was modified. `-B` prevents bytecode writes outside Owns. All fixtures are existing CODEX-1 synthetic data, mutated only in memory.

## Protocol / communication

- First recorded UTC20:37:13 on2026-10-27; client date Oct28 Asia/Dhaka. Initial main bfb4f5ad4513c9fe0d4ec979155adfbaac6be5dc. Main advanced concurrently to21ad09c.
- Initial deviation: evidence/probes authored on canonical main before claiming the TODO row or creating isolation. Controller corrected this; preservation and normal claim/worktree/FF lifecycle now required. No product/test changes or analysis restart.
- At20:42 UTC controller reserved canonical writes for CODEX-2 first. This worker has not edited/staged/committed shared controls and will wait for the explicit write window; unrelated RUNS.md modification and CODEX-2 evidence are untouched.
- Controller granted the exclusive canonical window after CODEX-2 finish a67dc96. Claimed IN PROGRESS via d94fc4b; created ignored `.worktrees/F-CODEX-1-1` on explicit `run/F-CODEX-1-1` using the repository's required local Git worktree path. Verified resolved source/destination before moving the exact own evidence directory into isolation; no evidence lost or other-lane files moved. Repeated probes/suites there before staging.
- Mandatory developer/skill announcements were the only chat narration; otherwise silent. No other-chat messages, owner questions, or approval requests. No decision needing Koushik; fallback unchanged. No quota polling.

## Skills/plugins actually used

- Installed Superpowers `verification-before-completion/SKILL.md`: fresh independent probes, existing-suite receipts and explicit separation of observation/code-reading claims from runtime gates before completion.
- Installed Ponytail5.3.2 `ponytail-review/SKILL.md`: connected owned-module/tests/docs reading, concrete reproductions, smallest proposed remedies, plain-language checklist; documented limitations separated from bugs. User-named owned modules replace the skill's default diff scope; no other-lane callers read.
- Installed Superpowers `using-git-worktrees/SKILL.md`: applied isolation detection, ignored-directory verification and explicit run branch; repository/user-selected Git worktree lifecycle overrides the native-tool/default placement preference. Baseline and fresh isolated suites verified.
- Superpowers `using-superpowers` read: explicit delegated-task exemption applies. Repository skill/plugin checklist applied. No implementation, TDD cycle, external research, browser/native UI, provider/Clerk/Railway/GitHub plugin or new dependency needed; no skill/plugin installed/enabled.
- Root AGENTS, README, owner tasks, applicable approved-plan S08/S10/S11/S14 sections, current queue/state/decisions/budget/rubric, run protocol and latest S04g/S04f/S04e reports consulted. S08h/S05a reports used only to establish finished owned scope. No history/memory lookup.

## Routing / cost / limitations

Requested CODEX-1 / GPT-6.1 Sol medium; actual delegated Codex session, exact runtime model/effort/tokens/task dollars unavailable. OpenCodex-managed; not polled. New Meta/service-inference/GPU calls0; coding dollars unknown, historical balance unchanged/unverified. No service/deployment/account/credential/policy/rights/approval changes.

No actual reconstruction, physical experiment, integrator/simulator, fitter, gate, real footage, performance benchmark, API/browser/other-lane integration or end-to-end success claim. Existing synthetic unit-suite success proves only those offline checks.

Next: implement findings only in a separately authorized owned-code run; no implementation authorized here. Final integration and UTC end are appended after fresh FF/main checks, not assumed in advance.

## Final integration / acceptance

- Claim d94fc4b after controller-granted serialization window; evidence task commit c7b7787b169dc548b1549be04069c35738009e42 on run/F-CODEX-1-1; rebase already current, then verified fast-forward to main. Evidence diff contains only the assigned Owns path. `git diff d94fc4b -- Build contracts tests` empty: no product/test changes.
- Main checks completed20:46:39Z on2026-10-27, within the original15m from first recorded20:37:13Z. Initial baseline and post-correction isolated/main checks retained separately. Final control commit records DONE and keeps all event gates NOT RUN.
- Final controls/cleanup check20:47:32Z: runs_view generated36/193 DONE; diff check clean. `python Run-System/validate_controls.py` exited1 at its legacy S03-only assertion `Product source must not exist in S03` because Build already exists. This helper is not valid as a current product-phase acceptance check; no bypass/edit made and no passing result claimed. Correct generated-view check retained. Verified the exact resolved run-worktree path is under `.worktrees`, checked it clean, removed via `git worktree remove`; run branch retained.
- Serial canonical controls: only own QUEUE row, generated RUNS, own STATE recovery receipt, API_BUDGET allowance receipt and RUN_LOG appended under the granted window. Other lane's finished controls/evidence untouched. Final report remains in assigned Owns, matching controller report-pointer expectation.
- Communication compliance checked: evidence on disk, no owner question required, no other-chat messages, no duplicated chat report; only mandatory skill/developer updates and final one-line status. Initial lifecycle deviation and its correction are explicit above, not hidden.
