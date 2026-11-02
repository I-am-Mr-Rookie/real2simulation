# Worker contract (Nov 1; replaces reading RUN_SYSTEM.md, ORCHESTRATOR.md, old reports)

Read this file, your task, and the files you touch. Do NOT read STATE.md, QUEUE.md, RUNS.md or old
run reports unless your task names them. Save tokens: no repo-wide scans, no reading large logs.

## Setup
1. Root: C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon (project 91e441f8-e40c-4ec4-bea2-de7fa1582d97).
2. FIRST: `git worktree add .worktrees/<RID> -b run/<RID> main` and write only there (absolute paths for apply_patch).
   Shared node_modules: junction Build/web/node_modules to the canonical one; never npm install unless the task says.
3. You are the only worker on this run. Write only your Owns paths. Never edit canonical controls (STATE, QUEUE, RUNS, AGENTS).

## Timebox
Your prompt gives issue time, deadline and cutoff (30 or 60 min). Stop implementing at the cutoff.
Finishing early is fine when DONE. Do not stop early with PARTIAL/BLOCKED; use the time or send a short blocker message.
Write Run-System/Runs/<RID>/TIMEBOX.json: id, status, issued_at, deadline_at, implementation_cutoff_at,
work_stopped_at, reported_at; check with `python Run-System/worker_timebox.py check <file>`.

## Work rules
- Ponytail full: smallest complete change, reuse existing code, no new dependency unless the task allows it.
- Honest product: numbers only from code, fitter or API output; keep labels (RECORDED, SIMULATED, MEASURED,
  MODEL-ESTIMATED, what-if, scale unverified); show uncertainty; never stage results.
- Secrets: .env key names only; never print values. Paid calls: use the minimum, log each one
  (UTC, model, units, cost) in your REPORT. No purchases, posts, submissions or account-setting changes.
- UI text: no em dashes. Owner clips are private except OWN07 snippets; no real emails in screenshots.
- Browser checks (Koushik, Nov 2): QA, verification and UI checks use the in-app ChatGPT browser (its own cursor), using the
  product like a person: click, scroll, type, resize, look for bugs, wrong numbers and awkward UX, not only scripted asserts.
  Playwright Chromium headed only for automated test scripts, or for human-style QA only if Koushik says so.
  Browser control is enabled by the [@Browser](plugin://browser@openai-bundled) plugin invocation in your dispatch prompt. If it
  reports "Browser is not available: iab" (try once more, no loop): send the controller one line
  "<RID> BROWSER NEEDED: <exact error>", finish the non-browser parts, then end your turn and wait. Only Koushik can attach
  the browser in some cases; he invokes the plugin in your chat and the controller reissues your timebox.
  Never Chrome. Test accounts email+clerk_test@example.com, code 424242, DEV https://real2simulation.up.railway.app
  (also https://real2simulation.rookiecoders.tech). The in-app browser holds Koushik's signed-in accounts: do not open his
  private projects, the DEV room bd7162322f3c4c978383bf797aac2f6e or the N06 clip, and change no account settings.
- Checks: run the tests for what you touched, plus `npm run build` in Build/web if web changed. No deploy unless the task says.

## Finish
- Commit with `git add -f` of named files only (never `git add -f .`, no caches, no media binaries).
- Run-System/Runs/<RID>/REPORT.md, at most 20 lines: status, what changed, checks run with results,
  paid calls, skipped, risks.
- Silent chat. Send one message to the controller chat 01a1882d-3481-7ce3-8f88-45c942e341cd, exactly:
  `<RID> <DONE|PARTIAL|BLOCKED> - <absolute REPORT.md path>`. If messaging is unavailable, make that line your final answer.
- Koushik's standing approval (Nov 2): this controller message is explicitly authorized for every worker run. Send it with
  send_message_to_thread without asking; do not withhold it as "needs user approval". Only if the tool truly fails
  (error, not policy doubt) fall back to the final-answer line. Reason: the message saves the controller discovery time.
