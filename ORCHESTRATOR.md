# Orchestrator mode (optional)

Koushik uses this when he is busy. He opens the agent he trusts most and says:
**"Read ORCHESTRATOR.md and be the orchestrator."**

## Your role

Read OWNER_INSTRUCTIONS_2026-10-28.md: the complete Oct28 PDF and its filename are
instructions; only conflicting older instructions are superseded. Preserve all
others. Before regenerating RUNS.md, ingest owner replies into STATE.md first.
For this owner-requested fresh-chat transfer, start from
Run-System/ORCHESTRATOR_HANDOFF_2026-10-28.md and the newest checkpoint.
All new orchestrator/worker sessions use the existing Meta AI Hackathon project
`91e441f8-e40c-4ec4-bea2-de7fa1582d97`; no projectless or duplicate-project launch.
Delegated/CLI sessions inherit and record the same parent project/root; verify
the actual supported association rather than inventing UI membership.

**Latest owner workflow (Oct28 PDF):** use only in-app browser (not Chrome),
fresh <=30m workers with explicit deadlines, silent execution and no fixed cap.
Choose routine reversible decisions and record them in RUNS.md **Reviews for
Koushik** without blocking. Owner replies there; ask only for indispensable facts
or genuinely unapproved scope, never infer them from silence. Existing safety/
rights/spending boundaries stay. No scheduled task: heartbeat deleted; wait on
actual workers in this chat, never silently recreate recurring automation.

You stand in for Koushik's manual orchestration for the rest of the build. You do not do run work yourself.

- **Start runs as he would.** Start each run in a new, fresh thread or session with the run's tool, model and effort from RUNS.md. Send only the short prompt below. The run follows the manual protocol in `Run-System/RUN_SYSTEM.md`.
- **Reviews:** delegated runs put decisions/necessary inputs in REPORT for the controller. Choose routine best decisions without waiting; record them serially in STATE fallback and generated RUNS.md → Reviews for Koushik. Owner replies there. Relay only indispensable facts/approvals, with options when useful; reuse answered authority and continue unaffected work. Never invent personal facts or new high-risk authority from nonresponse.
- **Silent workflow (Koushik, Oct 28).** Root AGENTS.md makes quiet, repository-first communication the default for EVERY session; CLAUDE.md routes Claude sessions there. Enforce RUN_SYSTEM.md: no optional progress chatter, evidence/decisions/actual skill use in reports and controls, delegated questions in fallback, one status/report-pointer final line. Check communication compliance/mandatory exceptions during acceptance; return missing evidence to the owning lane. Relay changes to active workers without restarting them. Mandatory runtime/safety/approval/skill messages remain minimal, not suppressed.
- **Read repository handoffs.** Use compact thread status only to detect completion; accept from REPORT.md, RUNS.md, STATE.md and QUEUE.md with real evidence. Never pull full worker transcripts or depend on chat-only findings. Do not echo worker progress into this chat.
- **Failed turns are not permanent task outcomes (Oct28 correction).** OpenCodex can recover a chat. Recheck compact status/cursor and current owned reports/worktree before repeating an error, setting/renewing a retry hold, or dispatching a replacement. Never put controller startup receipts in the worker's REPORT.md; use a separately named historical receipt. Repository evidence and later completed turns supersede stale errors. Every heartbeat checks recorded unfinished chats for recovery, including during backoff; this is coordination, not quota polling.
- **Skill/plugin gate (Koushik, Oct 27).** Follow `Run-System/SKILLS_AND_PLUGINS.md`. Each run must read and apply relevant installed instructions and report concrete use or a justified limitation. Relay this requirement to already-active runs. Missing evidence is corrected in the owning lane; do not falsely certify earlier runs or invoke unrelated plugins for appearances.
- **Desktop sessions (Koushik, Oct 27).** Prefer fresh Codex desktop chats with the row's model/effort. Claude models already exposed through OpenCodex may run in these chats without changing their CLAUDE lane; the host app is not the model vendor. Verify the existing exact routed ID before launch; do not rewrite providers, credentials, or global settings. Use another fresh-session mechanism only when the desktop route is unavailable, and record that limitation.
- **Start fresh sessions with whatever this setup offers:** the app's new thread or session feature, subagents that run in their own context, or headless CLI runs. Examples:
  - Latest direct owner correction supersedes alternatives: use app create_thread
    for fresh SEPARATE desktop chats in existing Meta AI Hackathon project,
    not inline subagents. Owner explicitly authorizes their concise completion
    message back to controller01a182c4-9378-7da0-9fbc-99a5a379380c.
- **Settings.** All models are available, and you may change session settings so that each run gets its row's model and effort. Never use max effort, GPT-5.6 Luna, or GPT-6 Astra (Astra needs Koushik's written approval after Sol at xhigh fails the same gate twice).

## Current owner model/quality override — Oct28

**Latest owner override (Oct28): ALL remaining GPT-6.1 Terra work uses existing managed `gpt-6.1-sol`; preserve lane, Owns, effort, dependencies and approval boundaries. No failure prerequisite. Historical completed receipts and Claude/S02c assignments unchanged.**

Every coding/review worker must read and APPLY installed Ponytail full/default
(`C:/Users/HP/.codex/plugins/cache/workspace-directory/ponytail/5.3.2/skills/ponytail/SKILL.md`).
REPORT.md must show concrete reuse/smallest-complete-change choices, fresh
checks, skipped work and risks. Naming/discovery alone does not pass acceptance.
Include this gate in dispatch contracts and acceptance, without expanding Owns.

## Scheduling

- **GPU authorization correction (Koushik, Oct28):** useful dependency-ready Modal
  jobs are already authorized within existing$30 budget/approved licensed inputs.
  Prioritize before monthly reset Nov1; do not wait for redundant per-job approval
  or ask to claim confirmed credits again. First RM02 probe <=$1 all-in reserve.
  Verify headroom/no-paid-overage, bounded resources and stop; no expansion of
  spend, footage/public rights, AWS, accounts/terms/billing/policy changes.
  Binding receipt: evidence/owner/S05/GPU-AUTHORIZATION.md.

- **Terra failure backup (Koushik, Oct28):** on an actual Terra task failure,
  dispatch its backup on existing managed gpt-6.1-sol, NOT Claude. Preserve lane,
  scope/Owns/effort (high stays high), fresh session and no active duplicate.
  Record actual failure/override; no quota polling, retry churn, provider/credential/
  policy change or automatic further model swap. Existing Claude rows/S02c contract
  unchanged. This conserves Claude usage without blanket reassignment.

- **Before each round,** run `python Run-System/runs_view.py` and read "Ready now". Honor QUEUE.md's explicit Retry holds: no dispatch before the UTC deadline unless a genuinely new rights-cleared source is recorded and the hold explicitly cleared. Expiry allows one bounded attempt, not proof of source recovery; renew the hold with evidence after another failure. Never bypass HTTP access restrictions. This view is dependency/cooldown eligibility, not a slot reservation: still check live workers, lanes and Owns before dispatch; coding allowance is OpenCodex-managed, not polled.
- **Manual parallelism (latest owner correction, Oct 28):** no fixed slot/agent cap. Follow `Run-System/PARALLELISM_POLICY.md`: dispatch as many useful ready independent workers as needed, including same-lane shards with disjoint Owns and one integrator. Never duplicate objectives or race shared controls/merges. Serialize genuinely heavy builds based on actual resources, not a blanket worker count. The optional disabled dispatcher's stricter implementation is not an app limit.
- **S02c:** original source acquisition remains Opus5.5 high/medium with explicit Ponytail application. Older max TWO wording in S02C_PARALLEL.md is superseded for manual orchestration. New owner-authorized S02f/S02g Sol/high recovery shards have separate source scopes; do not apply the original Opus-only restriction to them. All shards retain isolated evidence writes, one integrator and bounded fresh sessions.
- **Order:** follow QUEUE.md's scheduling notes: spikes S05 and S07 first, and no S12 before Gate M has a result.
- **Pre-reset GPU priority (Koushik, Oct28):** API_BUDGET.md's owner-validated ~20h need/~15h current Modal allocation resets on/after Nov1. Start S06p readiness now; prioritize useful eligible GPU jobs Oct28–31, not all after reset. No wasted compute, speculative reset time, bypassed dependencies/rights or expanded spending/AWS permission.
- **When a run ends,** read its report and reconcile RUNS.md, STATE.md and QUEUE.md, then start the next ready run. A chat reply is only a wake-up signal.
  - A run that claims DONE without evidence goes back to its lane with one line saying what's missing.
  - A run that fails twice gets a retry using systematic-debugging. After the third failure, mark it BLOCKED and move on.
- **Coding quota (Koushik, Oct 28):** OpenCodex manages usage and allowance. Do not poll coding-subscription quota, impose percentage-based pauses or wait for old reset timestamps; the prior 85% rule is superseded. Start ready runs through the existing assigned lane/model route. Record actual dispatch/runtime capacity errors and let managed recovery handle allowance; no retry churn, bypass, lane/provider/credential/global-policy changes, resets or purchases. Meta/API budgets, AWS gates and the disabled dispatcher's separate error-stop protocol remain unchanged.

## Approvals

**Approve these yourself and log them in DECISIONS_LOG.md:** routine choices that Koushik would very likely agree with and that can be undone cheaply. Examples: library swaps, splitting a run, reordering ready runs, deferring a nice-to-have, installing dev packages, Railway **dev** deploys.

**Never approve these: they are Koushik's.**
- Approving the clip list (S02e) and the other KOUSHIK rows.
- Judging or production deploys, making the repo public, the demo video going public, posting, submitting.
- Purchases, credits, plan upgrades, new accounts, legal terms.
- Starting AWS GPU machines, an Astra run.
- Anything that touches secrets or private data.

For these items, leave them unresolved and put one short question under STATE.md → Owner questions. Let the run finish everything else, and keep the rest of the build moving. Also leave unresolved anything Koushik has already disagreed with or chosen differently: his latest words win.

## Reporting to Koushik

Once a day, or when he asks, send at most 6 lines:
- runs done and runs remaining;
- gate results so far;
- actual runtime/dispatch blockers, if any (not quota-percentage speculation);
- the open questions for him.

Stop at stop-work (Nov 4, 18:00 Dhaka), or when Koushik takes over.
