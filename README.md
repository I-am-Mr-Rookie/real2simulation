# Meta Global AI Developer Hackathon: Real2Simulation

**Private source repository:** [I-am-Mr-Rookie/real2simulation](https://github.com/I-am-Mr-Rookie/real2simulation). The normal `main` branch contains the project source; local input videos are excluded and remain recoverable from the original private backup release. See [GitHub Backup.md](GitHub%20Backup.md) for cloning, media recovery and history details. Sync is by explicit commit/push, not an automatic background service.

Koushik Sadhak Jeet · solo · indie developer track · building Oct 27 – Nov 4, 2026
**Submission due Nov 4, 9:00 PM ET = Nov 5, 8:00 AM Asia/Dhaka.** Plan stop-work: Nov 4, 6:00 PM Dhaka (Koushik's finals start Nov 5). Nothing submitted yet.

## Start here

0. [START.md](START.md) and [RUNS.md](RUNS.md): how to start runs, and the run checklist.
1. [tasks for the owner.md](tasks%20for%20the%20owner.md): what only Koushik can do, as a checklist.
2. [final plan.html](08%20Real2Simulation/final%20plan.html): the approved build plan, its checkpoints and the Executor handoff.
3. [Event Rules and Participant Guide.md](Event%20Rules%20and%20Participant%20Guide.md): rules, rubric, prizes, dates in ET and Dhaka time.

## Folder map

| Path | Purpose |
|---|---|
| [01 Research](01%20Research/) | Event research from the application phase (dates, selection). Still useful for event facts. |
| [07 Project Reselection](07%20Project%20Reselection/Project%20Shortlist%20and%20Winner%20Patterns.md) | Why AttemptLens was dropped: idea shortlist, winner patterns, rubric re-rank |
| [08 Real2Simulation](08%20Real2Simulation/) | [Concept page](08%20Real2Simulation/Real2Simulation%20Concept.html), [concept notes and AWS status](08%20Real2Simulation/Concept%20Notes.md), [final plan](08%20Real2Simulation/final%20plan.html) |
| [Build Notes.pdf](Build%20Notes.pdf) | Koushik's handwritten notes on build tools, skills, and model lanes |
| [archive](archive/) | Everything from the AttemptLens phase: application, AttemptLens plan, review pack, VM and Run System workspace, teammates' test data, harness specs. Reference only. |
| `.env` | Local secrets (gitignored). Never print or commit. |

## Current state (Oct 27)

- Sign-in: the Clerk dev instance uses shared Google credentials and email OTP (passwords optional); no custom Google OAuth client. Production Google is deferred to S22 if time allows. Judges use guest access and the demo account. Google and OTP sign-in are untested end to end; see [Concept Notes](08%20Real2Simulation/Concept%20Notes.md#google-sign-in-setup-status-oct-27).
- Direction approved: Real2Sim + virtual lab + Mystery-g. Name: Real2Simulation.
- Credit forms submitted; Baseten and Meta Model API keys are in `.env`. Koushik reports a live muse-spark-1.3 test returned HTTP 200 with `pong` (44 tokens) and that all Meta Model API tasks, including billing, are complete. Billing details have not been independently verified; an alert does not stop billing.
- Modal and Fireworks credential fields are populated in local `.env`; Modal token authentication and Fireworks authenticated model listing passed on Oct 27. GPU execution and inference remain untested. Clerk and Railway will be managed through their CLIs, and Railway also through its plugin. Koushik reports GitHub CLI and plugin authenticated; no independent authentication check has been made.
- Railway **dev** deploys are approved. Judging and other deploys still require separate approval; see [decisions log](DECISIONS_LOG.md).
- The Run System will run on Koushik's PC; the AWS VM stays stopped.
- AWS GPU quota: two us-east-2 requests pending.
- Pivot (Oct 27): Koushik films nothing. The demo and benchmarks use licensed public clips (NASA, Wikimedia Commons, Pexels, Pixabay); prediction vs reality uses held-out frames of those clips. Owner work is about 4 hours in total.
