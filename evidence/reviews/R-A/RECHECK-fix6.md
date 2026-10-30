# R-A fix6 recheck — CHANGES_REQUIRED

Reviewed main `cbdb02092ea166e04834b3cc1f13d8a2123ff60a` (fix6), assigned `gpt-6.1-sol/high`, CLAUDE cross-vendor lane. Offline product-read-only review; incremental spend **$0**. Review complete; **Gate A not cleared**.

## Closure decisions

| Check | Decision |
|---|---|
| F1-R3 bare-label amount laundering | **CLOSED for all eight prior gap probes.** Runtime and independent oracle refuse them; four failed attempts yield tool-only fallback. Includes `one whole minute: <gravity q>`, `a full second: <duration q>`, full-second/gravity, full-radian, full-metre and punctuation variants. |
| Earlier F1-R/F1-R2 | **PRESERVED.** Exact twenty prior cases: sixteen numeric claims refused, four benign strings preserved; eighty surface checks agree. |
| CITE forgery | **PRESERVED.** Twelve private-use-marker/surface checks refused; three JSON-escaped trial cases exhaust four attempts and fall back. |
| Benign pronoun / double-check / unit labels | **PASS.** `This one fits the scene.`, `Please double-check the fit.`, and amount-free `in seconds` / `in metres` labels still pass. |
| Q16=A packet reporting | **PASS for the saved sample.** Exact amended label, numeric-contract 10/10, setup 0/10, thirty unchanged turns and zero oracle flags. |
| Remaining `in <units>` path | **OPEN — P1 F1-R4 below.** Ordinary explicit-one measurements still pass both detectors and display without fallback. |

## F1-R4 — [P1] `in <units>` licenses ordinary explicit-one measurements

Both production validation and the independent oracle accept these SYNTHETIC model responses with actual references into the saved simulator outputs:

```text
The elapsed time in seconds is one: 0.2 ± 1e-06 s (simulated)
The elapsed time is one in seconds: 0.2 ± 1e-06 s (simulated)
The elapsed time in seconds is a full one. Tool result: 0.2 ± 1e-06 s (simulated)
The distance in metres is one: 0.1962 ± 1e-06 m (simulated)
```

The prose claims **one second/metre** while the cited tool values are **0.2 s / 0.1962 m**, respectively. This is not a unit-dimension mismatch, harmless pronoun, missing reference or unsupported physical criterion. Two additional variants (`a single one` after `in minutes`, and `one in metres`) reproduce the same root cause.

- All six pass `validate_response`, display via `safe_reply`, incur **zero trial rejections**, and **do not fall back**. Both detectors return `None`.
- Each passes on reply segments, question prompts, chip labels and candidate rationales: **24 affected surface checks** within the 64-check extension.
- Six real Gate A helper calls independently report **attempts=1, model_reply_shown=true, invented=null, blocked=[]** and display the conflicting amount. Those helper calls are offline synthetic response injections, not new model calls or additions to the saved thirty-turn packet.
- Controls containing `two`, a digit, an amount inside `in one second`, or the original `a full second:` are refused and safely fall back. Amount-free labels and pronoun-one remain allowed. A modified unit-only label (`in whole seconds`) is conservatively refused; not counted as an invented-number finding.

**Root cause:** `contracts/agent/validate.py:58` masks an `in <units>` chain without checking whether the surrounding clause asserts an amount. The remaining `one` is permitted by `_NUMBER_WORDS` at lines 33–48 because its numeric exception only covers nearby `point` or an immediately following unit. `numeric_issue` at lines 70–84 therefore sees neither the unit nor a prohibited amount. Independently, `evidence/S14/S14g_fix_oracle.py:53` only recognizes `one` immediately before a unit, while `_bound` at lines 61–65 accepts the unit based on preceding `in`. Separate implementations share the same conceptual blind spot.

**Why P1, not a request for universal English detection:** this is ordinary, unambiguous, same-dimension amount prose on the central no-invented-number trust boundary, and the gate-counting oracle also misses it. One bounded root cause is reported, not six separate defects. The clean recorded sample does not close this reproducible enforcement failure. Q16 expressly retains numeric-language review.

**Required, bounded:** prevent these explicit amount assertions from becoming valid merely because a unit occurs in an `in <units>` phrase. Preserve benign labels/pronouns where safely supported, or use the existing code-owned/tool-only narrative when unconstrained prose cannot be verified. Cover the disclosed same-dimension examples at runtime, oracle and visible surfaces. No universal blacklist, new dimension framework or physical calibration criterion requested. Implementation belongs to the S14 owner; this reviewer changed no product files.

## Fresh evidence and Q16=A

Run from the isolated review worktree:

```powershell
python -B evidence/reviews/R-A/recheck-fix6/probe.py
python -B evidence/reviews/R-A/recheck-fix6/verify.py
```

- The probe was adapted from **the original reviewer** `recheck-fix5/probe.py` (SHA256 `c699a66c00af5c6f3298a4ac89b1fc3a6edfa9908ad597b75c4397f8b1fd04f9`), not the S14 worker's copied adaptation. [Adaptation diff](C:/Users/HP/Documents/Hackathon/2026-10-26%20-%20Meta%20Global%20AI%20Developer%20Hackathon/.worktrees/R-A-recheck4-orch102/evidence/reviews/R-A/recheck-fix6/adaptation.diff) records the expectation updates, fix6 packet reference, secret-read guard and independent extension.
- Prior probes: twenty exact cases, eighty surfaces, twelve forgery checks, eight F1-R3 gap cases with thirty-two surfaces, and seven actual helper trials that all safely fall back.
- New bounded extension: sixteen cases, sixty-four surfaces, six actual helper bypasses. Oracle corpus self-check **66/66**; AST import check confirms no `contracts.agent` dependency in the oracle. Agreement on that finite corpus is not closure of F1-R4.
- Focused agent/pipeline suite **59 tests OK**, plus production setup-validator suite **14 tests OK**: **73 total, zero failures/errors/skips**. Setup tests use synthetic safety fixtures, not calibrated recordings.
- Hashes of **433 protected files** under Build/contracts/tests/evidence/S14 match before/after probes and after tests. Python network connections are denied; live post is stubbed to fail; no S14 CLI or new frame extraction was run. No installs, Meta calls, spend or secret reads.
- Fresh `S14g_fix5_gate_a.run()` under the fix6 imports, with the exact scope-string transformation from the fix6 wrapper, matches the saved fix6 **summary**. Ten distinct recorded-scene fixtures pass numeric contracts **10/10**. Ten observed calls through the original production setup-validator binding all fail with absent authoritative bundles: **0/10**. Binding is restored; four synthetic threshold-only checks cover below-threshold specs, accepted amended threshold, missing turns and invented-number failure.
- Saved turns: **30/30 unchanged**, **0 fallback**, **0 oracle-flagged shown inventions**, thirty unique case IDs; tool-output hashes verified during replay. These are historical recorded model replies, with synthetic interview answers and synthetic-room trial tools, not physical/calibrated/user-interview evidence.
- Packet status is **MET_AMENDED_Q16**, never plain MET for this packet; verbatim label **"scale unverified, not setup-validated"**, with setup **0/10** alongside. Owner Q16=A (`DECISIONS_LOG.md:3–11`) is honored. Correct packet reporting is accepted; final amended Gate A clearance is **withheld** because F1-R4 remains.

Machine evidence: [results.json](C:/Users/HP/Documents/Hackathon/2026-10-26%20-%20Meta%20Global%20AI%20Developer%20Hackathon/.worktrees/R-A-recheck4-orch102/evidence/reviews/R-A/recheck-fix6/results.json), [fresh replay](C:/Users/HP/Documents/Hackathon/2026-10-26%20-%20Meta%20Global%20AI%20Developer%20Hackathon/.worktrees/R-A-recheck4-orch102/evidence/reviews/R-A/recheck-fix6/fix6-replay.json), `probe-stdout.txt`, `tests.txt`, `tests-summary.json`, and the assertion-bearing scripts beside them.

Skipped new live/model/UI/physical tests and product fixes. Remaining risk: P1 explicit-one measurement bypass; saved-packet success is not numeric-language clearance.
