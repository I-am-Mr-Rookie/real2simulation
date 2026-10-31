# Strict worker timebox — latest owner correction, Oct28

Applies to EVERY new worker, model, lane, review, cleaner and continuation.
Supersedes conflicting "finish early when PARTIAL", 15/20-minute controller
contracts, and treating a short PARTIAL report as an accepted completed session.
Separate desktop chats in the same existing project remain mandatory.

## Dispatch: deadline IN the handout prompt

1. Immediately before each create_thread, controller records actual UTC dispatch
   time and an absolute deadline exactly30 minutes later. Include BOTH timestamps,
   deadline in Asia/Dhaka, and minute25 implementation cutoff IN THE USER-VISIBLE
   HANDOUT PROMPT, not merely in an on-disk contract. Do not reuse an older clock
   for serial launches or give a later worker a shortened leftover window.
2. Use `python Run-System/worker_timebox.py issue <ID>` to calculate a fresh
   timebox; persist the output with the exact sent prompt/contract and actual
   returned chat ID. Launch latency counts in the declared wallclock; no hidden
   extension, reset, resume loop or work beyond the deadline.
3. Handout must say: "Use the full available window for unfinished acceptance
   criteria. NO terminal PARTIAL/BLOCKED before the deadline without a controller-
   approved safety/user-stop exception. Send a nonterminal blocker message instead
   and keep doing useful authorized checks/recovery within Owns. At minute25 start
   no new implementation; verify, repair existing work and finalize evidence.
   Stop task work by the deadline and report the actual result honestly."

## Worker: outcomes, not elapsed-time theatre

- Verified DONE may finish early ONLY when EVERY assigned acceptance criterion is
  met, fresh verification is saved, and no known owned work remains. Completion
  of a narrow child contract is distinct from a still-PARTIAL parent product gate.
- Incomplete work: continue root-cause investigation, supported recovery, missing
  tests, direct source verification, edge cases and evidence cleanup within Owns.
  Do not quit because a first attempt failed, a proposed answer sounds plausible,
  or a short first report exists. Do not pad time with useless tests, polling,
  compute spend, idle sleep disguised as work or unrelated tasks.
- True authority/access/external dependency block: promptly send ONE concise
  **NONTERMINAL BLOCKER** callback with evidence, exact unmet prerequisite,
  alternatives tried and safe remaining work. Controller may resolve within
  existing authority, adjust Owns safely or explicitly put the worker in a
  waiting state until the original deadline. No fabricated progress. Mere access
  friction or a missing optional tool is not automatically terminal.
- Stop risky actions immediately when safety, privacy, resource shutdown or owner
  stop requires it. The controller may authorize an EARLY STOP for that reason;
  record the actual exception. Thirty minutes NEVER expands spending, credential,
  rights, privacy, deployment or tool permission. Do not delay a needed GPU stop.
- At deadline, stop operations and return DONE/PARTIAL/BLOCKED honestly; do not
  hide failure, rename PARTIAL to DONE, backdate times or overrun to meet a label.
  The final report can be written/sent after work stops; state both times.

## Controller acceptance: enforce, don't merely remind

- Every report includes `TIMEBOX.json`: id, issued_at, deadline_at,
  work_stopped_at, reported_at, status, and optional controller_exception.
  UTC timestamps include offsets. Deadline-issued MUST equal1800 seconds.
- Run `python Run-System/worker_timebox.py check <TIMEBOX.json>` plus actual
  chat/receipt review before accepting/integrating a worker. The script checks
  arithmetic/report ordering, not truth of self-reported effort or acceptance.
- EARLY PARTIAL/BLOCKED is **NOT ACCEPTED** absent a documented approved exception.
  Before original deadline, send it back to the same chat to use remaining time;
  do not start a duplicate worker or reset its clock. If already expired, preserve
  the report as historical noncompliance, not retroactive work; a genuinely needed
  continuation gets a fresh separate chat and full new scoped30-minute contract.
- Do not mark a worker DONE because it messaged a report pointer. Read the actual
  results and acceptance evidence. Deadlines checked through bounded waits on
  actual chats, no scheduled task/dispatcher/quota polling.

Earlier reports remain truthful historical evidence; this rule is prospective,
not permission to rewrite their timestamps or pretend more work occurred.

## Completion message when the messaging tool is missing (Oct31, from S15ae-orch191)

If the controller-messaging tool (send_message_to_thread) is unavailable when a
worker finishes, end the chat with the exact completion line as the final answer
(the app relays it to the controller) and say so in REPORT.md. If that also fails,
send it as a nonterminal blocker once tooling returns. A line only in REPORT.md is
not a report.
