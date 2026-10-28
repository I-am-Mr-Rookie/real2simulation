# Real2Simulation — Windows PC Run System

Owner: Koushik Sadhak Jeet (solo indie). Repository: `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`.
Worktrees: `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/<RID>`.
Canonical plan: `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/08 Real2Simulation/final plan.html`.

## How Koushik runs the build (read this first)

**Managed-recovery reconciliation (Oct28):** a failed turn does not prove a
chat/task will remain failed. Controller must recheck compact chat status and
the actual owned report/worktree before repeating a failure, extending a hold
or replacing a worker. Check recovery during backoff, without polling quota.
Startup-error receipts belong in a separately named historical file, NEVER in
place of a worker REPORT.md. Later report/commit evidence supersedes stale errors.

**Coding-subscription quota — owner correction, Oct 28:** OpenCodex manages
usage/allowance for existing managed desktop routes. Workers and orchestrators
do not poll coding quota or pause at usage percentages; the old 85% rule is
superseded. Report `OpenCodex-managed; not polled`, continue dependency-ready
assigned runs, and report actual runtime/dispatch capacity failures without
retry churn or bypass. No provider/credential/global-policy changes, resets,
purchases or lane swaps are authorized. Meta/API spend and AWS gates remain.
The optional disabled dispatcher's structured-error stop protocol is unchanged;
this instruction neither enables it nor weakens runtime permission checks.

Koushik orchestrates by hand. He opens `RUNS.md`, picks a run, opens the right agent with the
right model and effort, and says only `Complete run S05a` or `Complete the next run`.
He runs no commands and does no Git work himself. That message is his authorization for that run.
Sometimes he hands orchestration to one trusted agent instead; that agent follows `ORCHESTRATOR.md`
and starts every run the same way, in a fresh session.

Every run is a fresh session with its own context window. Everything a run needs is on disk:
AGENTS.md, this file, STATE.md, its QUEUE.md row, DECISIONS_LOG.md, API_BUDGET.md and
the step contract in QUEUE.md. Nobody pastes long prompts and nobody needs `/compact`.

Before run work, follow [SKILLS_AND_PLUGINS.md](SKILLS_AND_PLUGINS.md): select relevant
installed skills/plugins, read their instructions, apply them, and report actual use.
Naming a skill or listing a plugin is not evidence of using it.

## Every session: silent, repository-first communication

Root AGENTS.md's silent workflow applies automatically to EVERY session, whether
human-started, delegated, resumed or reviewing; no launch-prompt reminder needed.
CLAUDE.md routes Claude sessions to the same instructions. These rules also apply
to orchestrator-started sessions and live dispatcher workers (Koushik, Oct 28).
Read-only smoke probes retain their exact required sentinel replies.
The repository is the handoff; an unread worker chat is not a communication channel.

- Omit optional progress chatter, running commentary, skill announcements and
  conversational questions. Follow higher-priority runtime requirements for any
  mandatory brief update, safety message or human confirmation; keep those minimal.
- Put actual changes, check commands/results, decisions, limitations, routing/cost
  evidence and skill/plugin use in the run's REPORT.md. Keep it concise and actionable;
  link bulky evidence instead of repeating logs, policies or the report in chat.
- Delegated workers put owner questions in STATE.md's fallback and continue independent work.
  Dispatcher workers instead use REPORT/RESULT owner_questions under their existing
  no-canonical-write boundary. Never wait for a reply in an unattended worker chat.
- Preserve PLAN, report, control updates, actual verification and approval boundaries.
  Quiet operation is not permission to hide a blocker or omit evidence.
- Finish with one line only: `<ID> <DONE|PARTIAL|BLOCKED> — <REPORT.md path>`.
  The final line is a completion signal, not acceptance evidence or next-run advice.
  The orchestrator reads the report and canonical controls, not worker transcripts.
- Human-started interactive runs retain necessary async questions below, not optional
  progress narration or multi-line completion summaries. All run workers use the
  one-line completion signal. Required direct user answers remain concise.
- Include communication compliance/mandatory exceptions in REPORT.md. Acceptance
  requires repository evidence and the correct final signal, not chat-only claims.

## Manual run protocol (default)

When you receive `Complete run <ID>` or `Complete the next run`:

1. **Pick the run.** `<ID>` is a QUEUE.md task ID (S05a, R-S07, F-CLAUDE-1…). For "the next run",
   run `python Run-System/runs_view.py`, open RUNS.md and take the first run under "Ready now"
   for your vendor (Codex: CODEX-1, then CODEX-2; Claude Code: CLAUDE). Skip runs marked in progress.
2. **Check it fits.** Its dependencies must be DONE and its lane must match your vendor. If the
   vendor is wrong, or a dependency is not DONE, stop and reply in one line with the run Koushik
   should start instead. If only the model or effort differs from the row, say so in one line and continue.
   KOUSHIK rows are never done by an agent; if Koushik says one is done, mark it DONE with his words as evidence.
   Vendor follows the selected model, not the host app: Koushik approved existing
   OpenCodex Claude models in fresh Codex desktop chats for CLAUDE rows. This is
   not a lane reassignment; record requested routing separately from observable runtime identity.
3. **Claim it.** In the main folder set the row's Status to `IN PROGRESS`, run
   `python Run-System/runs_view.py`, and commit both files on main (`chore(run): start <ID>`).
4. **Work in a worktree.** `git worktree add .worktrees/<ID> -b run/<ID> main`. Touch only the row's
   Owns paths. One objective, 30 minutes at most; at minute 25 start nothing new.
   Use the skills that fit (test-driven-development, systematic-debugging, verification-before-completion).
5. **Prove it.** Run the row's acceptance checks with real commands. Never weaken a check or
   present a fixture as product evidence. Numbers shown to users come only from the fitter or simulator.
6. **Merge it.** Commit on `run/<ID>`, rebase on main, rerun the checks, then fast-forward main
   and remove the worktree. If a check fails or the rebase conflicts beyond the time box, leave the
   branch unmerged and finish as PARTIAL.
7. **Record it, on main.** Set the row's Status to DONE, PARTIAL or BLOCKED. Update STATE.md
   (completed IDs, last merged SHA, last verified command and result, gate numbers, blocker, next action,
   Meta spend, model and effort used). Append one line to Run-System/RUN_LOG.md. Write
   `Run-System/Runs/<ID>/REPORT.md` (objective, changes, commands and results, limits, next).
   Include skills/plugins actually used, evidence of application, and relevant unavailable/skipped tools with reasons.
   Log any D1/D2 decision in DECISIONS_LOG.md. Run `python Run-System/runs_view.py` and commit
   (`chore(run): finish <ID>`). If `.git/index.lock` exists, another run is committing: wait and retry.
8. **Reply:** every run uses the one-line completion signal above, including
   human-started runs. Do not repeat the report or next-run advice in chat.

## Questions for Koushik (async, inside the run)

For human-started interactive runs, ask Koushik in the run itself when you really need him, using your tool's question feature
(Codex: its ask-the-user input tool; Claude Code: AskUserQuestion). Each question is one line with
2 to 4 options, your recommended option first and marked, plus the free-text answer so he can write his own.

- **Ask early, then keep working.** While a question is open, finish every part of the run it does not block.
  Never sit idle waiting for an answer.
- **Still unanswered when the rest is done?** Wait a little for the answer if the tool lets you continue
  meanwhile. Otherwise, parts that can be undone cheaply take the recommended option, logged in
  DECISIONS_LOG.md as "unanswered, used A". Parts that truly need Koushik stay undone: finish as PARTIAL
  and write the question to the fallback.
- **Fallback** (no question tool, headless or orchestrator-started runs, or still unanswered): add it under
  STATE.md → Owner questions as
  `- [ ] Q<n> [<run ID>] Question? A (recommended) … · B … · C … · current: A`.
  RUNS.md lists these under "Questions for Koushik". When Koushik answers, the next run that sees it
  marks it `[x]`, writes his answer after it, and applies it.
- Routine, reversible choices are yours: decide, log them, and don't ask.
Never do the Koushik-only actions listed in AGENTS.md; leave them unresolved and say so.

Parallel runs: at most 2 at once, never two in the same lane, and only when their Owns paths do not
overlap. The PC has about 2 GB of free memory, so prefer 1 when builds are heavy.

## Automatic dispatcher (optional)

`Run-System/dispatcher.py` is an optional unattended scheduler built in S03. Koushik does not need it.
It has its own stricter protocol (sections below): workers do not merge, and an operator accepts
results with `--accept`. Do not mix the two protocols on the same run.
`Run-System/validate_controls.py` is the S03-time control check; it assumes no product code yet.

## Fixed lanes and routing

**Latest owner override (Oct28): ALL remaining GPT-6.1 Terra work uses existing managed `gpt-6.1-sol`; preserve lane, Owns, effort, dependencies and approval boundaries. No failure prerequisite. Historical completed receipts and Claude/S02c assignments unchanged.**

Every coding/review worker must read and APPLY installed Ponytail full/default
(`C:/Users/HP/.codex/plugins/cache/workspace-directory/ponytail/5.3.2/skills/ponytail/SKILL.md`).
REPORT.md must show concrete reuse/smallest-complete-change choices, fresh
checks, skipped work and risks. Naming/discovery alone does not pass acceptance.

**Latest manual parallelism override (Koushik, Oct28):** no fixed agent/slot cap.
See PARALLELISM_POLICY.md. Independent same-lane shards are allowed with isolated
Owns and one integrator; serialize shared controls/merges and heavy local builds
based on actual resources. This supersedes old max2/one-per-lane manual text, not
the disabled dispatcher's separate implementation. S02f/S02g are owner-authorized
Sol/high recovery; original S02c remains Opus-only. No duplicate objectives or
uncontrolled recursive fan-out, quota polling or safety/budget scope expansion.

**Standing Terra-failure backup (Koushik, Oct28):** actual Terra failure authorizes
existing managed gpt-6.1-sol backup, not Claude, keeping original lane/Owns/scope/
effort (Terra-high -> Sol-high). Fresh session only after original stopped.
Record actual failure/override; no quota polling, retry churn, provider/credential/
global-policy changes or further automatic swap on Sol failure. Other Claude
assignments and S02c Opus-only contract unchanged; no retroactive S02d change.

**S02d-only override, Q6 answered Oct28:** Koushik "go with A" authorizes
`anthropic/claude-opus-5-5` / high on the existing managed desktop route,
retaining CODEX-2 ownership. Supersedes S02d Terra/high vendor/model check only.
Read canonical `Runs/S02d/CONTROLLER_RECOVERY.md`; reuse clean worktree2f7dba8.
No provider, credential, policy, spending or owner S02e approval changes.

**Latest owner override (Oct28): S02c uses Opus 5.5 / high via the existing desktop
OpenCodex route `anthropic/claude-opus-5-5`. Its CODEX-2 ownership and Owns set
are unchanged; this supersedes medium and the default Terra/high mapping for S02c only.
No duplicate full-task workers, provider/credential/global-policy change or quota
polling. A model override affects subsequent turns, not an already-running turn.
Later owner instruction permits multiple isolated Opus high/medium S02c shards
under S02C_PARALLEL.md: isolated CODEX-2 same-lane shards,
one integrator. Shards do not edit canonical controls or auto-merge.**

| Lane / work | Exact CLI model ID in config | Effort |
|---|---|---|
| CODEX-1 coding | gpt-6.1-sol | medium; high gate code, xhigh escalation |
| CODEX-2 coding | gpt-6.1-sol | medium |
| CODEX-2 browsing/screens only | gpt-6.1-sol | high |
| CLAUDE viewer, judgment, script, cross-vendor review | claude-opus-5-5 | medium |
| CLAUDE workspace UI | claude-sonnet-5-5 | high |
| CLAUDE PWA/report | claude-haiku-5-5 | high |

Codex IDs/efforts are present in the installed model cache. Claude full IDs are plan-derived, **not live-verified**; unsupported ID stops the worker, with no alias/substitution.
Optional GPT-6 Luna high is a mechanical subagent only, not an independent lane; never silently reassign.
No GPT-5.6 Luna. Astra is unplanned; at most1 written-approved run after two same-gate Sol-xhigh failures.
No max effort. Code reviews cross vendors without transferring source ownership.

`dispatcher_config.json` holds only model IDs and optional executable paths, no secrets.
Native codex.exe and claude.exe are found from PATH. No shell wrappers, installs, auto-auth, provider changes or permission bypasses.
Installed CLI help confirmed Codex exec/model/config/JSON and Claude print/model/effort/stream-json flags.
A parsed flag or local model cache is not proof of provider availability; smoke evidence is labelled separately. Koushik approved scoped workspace-write on Oct27 via his annotated "y". Dispatcher Codex runs explicitly use --sandbox workspace-write in their own worktrees; global read-only/on-request settings and approval behavior are unchanged. No bypass flags. Smoke probes explicitly use read-only. Product dispatch remains off until separately started.

## Dispatcher: starting (PowerShell)

```powershell
Set-Location -LiteralPath 'C:\Users\HP\Documents\Hackathon\2026-10-26 - Meta Global AI Developer Hackathon'
# Offline harmless fixture: no model calls, root QUEUE/STATE unchanged
python .\Run-System\dispatcher.py --dry-run

# Optional one real Sol coding-subscription worker, harmless marker only
python .\Run-System\dispatcher.py --smoke

# Later, ONLY after Koushik authorizes starting the product build:
# Edit STATE.md: Dispatch enabled = YES, Quota halt = NO.
python .\Run-System\dispatcher.py --run --max-runs 2
```

Without `--max-runs`, the dispatcher continues until no ready tasks remain or a stop condition occurs.
Use `--max-parallel 1` while this PC has less than2GiB free RAM. Hard maximum is2.
`--timeout-seconds` may shorten, never extend, the1800s hard ceiling.
`python .\\Run-System\\dispatcher.py --stop` requests termination and disables dispatch; Ctrl+C also terminates active process trees. Worktrees are retained for recovery.
Changing STATE Dispatch enabled to NO stops active work and prevents new starts.

## Dispatcher: worker lifecycle

1. Validate actual Git root, QUEUE rows/timeboxes/DAG and STATE. Lock to one dispatcher instance.
2. Read latest statuses; select first dependency-ready TODO per available CODEX-1/CODEX-2/CLAUDE lane, max2 total. Never run KOUSHIK tasks.
3. Check active Owns overlap; allocate unique `run/<RID>` branch and independent Git worktree from main.
4. Start a **fresh** `codex exec` or `claude -p` process; one-line prompt via stdin, no resumed conversation. Workers bootstrap from RUN_SYSTEM plus their worktree PLAN.json. Exact model/effort follows row and whitelist.
5. Write sanitized PLAN metadata; claim task as PARTIAL (never RUNNING). Raw stdout/stderr is streamed in memory only and never echoed/persisted.
6. Deadline uses monotonic time from run preparation. Hard timeout <=task timebox and <=1800s; kill full Windows process tree via taskkill /T /F.
7. On a structured quota/rate-limit error, stop new dispatch, kill remaining workers, set Quota halt=YES and Dispatch enabled=NO. Do not retry/re-route/spend-reset. Operator verifies provider reset before clearing.
8. Append start/end metadata to RUN_LOG; write ignored per-run JSON receipts; update STATE serialized in main loop. Tokens/quota are unavailable unless observed, not zero.
9. Successful live exit remains PARTIAL pending actual review, tests and fast-forward integration. Exit0 is not acceptance. No auto-merge or push.
10. Operator reviews worker report/diff, reruns targeted checks and fast-forwards verified branch on main. Then:
```powershell
python .\Run-System\dispatcher.py --accept TASK-ID --merged-sha VERIFIED-SHA --check-note 'Actual checks and results'
```
Acceptance requires PARTIAL status and commit ancestry on main; note/merge verification is an operator responsibility, not fabricated by scheduler.
Unmerged PARTIAL results block dependents; unrelated ready tasks may proceed.
Unknown approvals or unavailable services stay blocked; no invented DONE states.

## Evidence and safety

A parent dependency requires all its leaf tasks and required reviews DONE.
S01/S04 bootstrap and S09 fixture exceptions are explicit in QUEUE, not generalized bypasses.
Synthetic fixtures never count as product gate success. Gate R/M/P/RS/A/C/D/S remain NOT RUN.
S12 never starts without actual Gate M pass/fallback evidence.
Judging candidate deployment before S22 and frozen promotion S23 each require written owner approval.

No secrets, private exports, personal uploads, public repo/media/post/submission, account creation, legal acceptance or purchase.
Service inference also requires known billing and spend reservation. Meta policy $120 routine stop +$30 reserve; runtime cap waits for S20.
AWS off pending quota confirmation and owner-created $50 EC2 alert; us-east-2 only, stop after sessions.
Existing dev deploy permission is not permission to deploy during S03.

Raw child output is deliberately not retained because it may contain credentials.
REPORT/RESULT written by workers must be reviewed/sanitized before committing. Ignore runtime Runs and keep harmless worktrees until reviewed.
The dispatcher never recursively deletes worktrees. After review, use safe Git/app worktree archival/removal explicitly; do not erase unknown files.
A stale dispatcher.lock records PID: verify it is dead before removing that exact file. Never delete it to force parallel schedulers.
Keep parent workspace and archived source unchanged; repository was relocated, not flattened.

## Recovery after every run

STATE: completed IDs, branch/merged SHA, actual verification command/result, gate outcomes, blocker, next action, deadline mode, Meta spend, actual model and observable tokens/costs. Coding quota: OpenCodex-managed; not polled.
RUN_LOG: start/end UTC, RID/task/lane/model, CLI argv without secrets, worktree, duration, exit/status.
Runs/<session>/SUMMARY.json distinguishes offline versus actual CLI smoke versus live.
Review observable cost calibration on Oct29, without quota polling; >2x cost drift needs a logged routing decision, no silent lane swap.
Freeze Nov3 18:00; submission mode Nov4 10:00; owner stop Nov4 18:00 Dhaka; organizer deadline Nov5 08:00.

## Known limitations

- This is a safe scheduler/worker launcher, not an automatic evidence reviewer or merge service.
- Current service balances, runtime product gates and Claude endpoint availability are unverified.
- Browser workers require an available supported computer/browser surface inside the fresh CLI; flag support alone does not prove that surface works.
- Approval-sensitive tasks need specific recorded permission before execution. STATE fields Judging candidate approval, Fresh QA identities ready, Judging promotion approval, Public video approval and Public repo approval default NO; their sensitive rows are skipped until exact YES. The scheduler does not infer permissions from narrative TODO text.
- Offline dry run substitutes a harmless Python child for the planned CLI command; actual CLI smoke is a separately labelled check.

## Dispatcher: worker protocol (only for runs started by dispatcher.py)

The launch prompt is only `Complete run <RID> (task <ID>, lane <LANE>).`.
1. Read this file. Open `Run-System/Runs/<RID>/PLAN.json` in THIS worktree. It supplies mode, canonical_root, task, branch, scope, timeout and Owns paths. It contains no credentials.
2. Read AGENTS, STATE, QUEUE, DECISIONS_LOG, API_BUDGET and JUDGE_RUBRIC from canonical_root. The current control checkout wins over stale worktree copies. Read-only access to controls does not authorize edits to them.
3. A manifest is a task descriptor, not authority to bypass owner constraints. Obey its bounded scope and acceptance. No separate orchestrator, resumed session or /compact is used.
4. For mode=smoke: this is authorized S03 READ-ONLY verification. Read `Run-System/tests/fixtures/MARKER.txt` in this worktree. If and only if its line is `S03 harmless dispatcher verification`, reply with exactly `S03_SMOKE_OK`, then exit. No file writes, credentials, other APIs, commands that change configuration, merges, pushes, accounts, deployments or product work.
5. For mode=live: work only in task.owns plus your own `Run-System/Runs/<RID>/REPORT.md` and RESULT.json. Never edit the canonical checkout, other lanes, shared queue/state/logs or permission/provider/auth config. One objective; <=task.minutes, always <=30min. At minute25 start no new implementation.
6. Verify with targeted real checks. Do not fake a feature, weaken a gate, call a fixture E4, or use model text as measured/simulated numbers.
7. REPORT: objective, actual changes, commands/results, limitations, next action, actual model/effort, observable tokens/quota or unavailable. RESULT: task_id, status (DONE/PARTIAL/BLOCKED), checks (command/exit_code/result), limitations, and optional owner_questions.
8. Owner questions are rare, genuine blockers only. Put at most2 in RESULT as `{"question":"one concise question","blocking":true}`; the dispatcher transfers them to canonical STATE Owner questions for a once-daily digest. Never request or include credential values. Routine choices are made reversibly and logged; no speculative questionnaire.
9. Commit only verified task-owned changes on the run branch if appropriate. Do not merge/push or mark the central queue DONE. On quota errors exit and report category without credentials.
10. No secrets/private archive data/personal files, unlicensed footage, account/terms/purchase/publication/submission or unapproved environment deployment. Existing dev approval is not permission to deploy during S03. Meta routine cap120/reserve30 and AWS-off constraints remain unchanged.

The offline fixture uses a harmless Python child to test process scheduling and writes only an explicitly named dry-run marker. It does not pretend to be a Claude/Codex inference. Actual smoke is separately labelled. All live tasks remain disabled until owner authorization and suitable CLI write permission.
