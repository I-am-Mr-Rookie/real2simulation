# R-A fix5 recheck — CHANGES_REQUIRED

Reviewed main `0a18072251360c971ca80b8e0c67fa27ce918fa1` (fix5), assigned `gpt-6.1-sol/high`, CLAUDE cross-vendor lane. Offline, read-only product review; incremental spend $0. Review completion is **not** Gate A clearance.

## Closure decisions

| Check | Decision |
|---|---|
| Six exact F1-R2 regressions from RECHECK-fix4 | **CLOSED for the exact strings.** Runtime and independent oracle both refuse all six. |
| `one g` / `one N` detector asymmetry | **CLOSED.** Both detectors refuse both strings. |
| Model-forged CITE | **CLOSED for tested paths.** Private-use model text is rejected at every visible surface, including escaped JSON through the trial loop. |
| Benign pronoun / double-check | **PASS.** `This one fits the scene.` and `Please double-check the fit.` still display. |
| Fail-closed retries | **PASS when validation rejects.** Four bad attempts yield the existing code-owned tool-only reply, without the rejected prose. |
| Q16=A reporting / saved thirty turns | **PASS for the saved packet.** Exact amended label, 10/10 numeric-contract, 0/10 setup, 30/30 unchanged, zero oracle flags. |
| Worker-disclosed label-adjacency residual | **OPEN — P1 F1-R3 below.** It is an ordinary amount-claim bypass, not only a unit-dimension mismatch. |

## F1-R3 — [P1] A label-adjacent citation launders an explicit invented amount

The documented residual is reproducible without obfuscation: append `:` and an actual number reference to the same modified-unit claim that fix5 otherwise refuses. The real production path `validate_response -> check_trial -> safe_reply` accepts it without retry, and the independent oracle returns `None`:

```text
The period is one whole minute: 9.81 ± 7.4e-05 m/s^2 (simulated)
```

The displayed numeric rendering above is from the saved fitter tool output, not a model-authored test value. The preceding **one whole minute** is a separate model-authored duration unsupported by that gravity quantity. `S14g_fix_gate_a.turn()` independently reproduces it with **attempts=1, model_reply_shown=true, invented=null**. The new simulator run's gravity rendering can differ slightly; the evidence records its actual output.

This is more than the worker's stated lack of unit-dimension matching. Even citing a legitimate duration leaves the independent invented amount unvalidated:

```text
The elapsed time is a full second: 0.2 ± 1e-06 s (simulated)
```

Here the reference's actual saved duration is approximately 0.2 seconds, yet **a full second** still passes both detectors. Dimension compatibility alone cannot close this finding.

Bounded probes also reproduce `one full radian = <gravity q>` and `one full metre: <gravity q>`. All five accepted variants pass segments, question prompts, chip labels and candidate rationales. Period/comma-separated claims and `one more minute` are refused, confirming that label adjacency—not a general detector failure—is the differentiator.

**Root cause:** `contracts/agent/validate.py:57` masks a unit chain ending in `:`/`=` plus CITE; `numeric_issue` at lines 76–82 does not recognize the preceding modified quantifier once the unit has been masked. `_segments` lines 138–159 supplies CITE based on reference presence, not the claimed amount. The independent oracle's `_bound` at `evidence/S14/S14g_fix_oracle.py:61–71` likewise treats punctuation-plus-CITE as sufficient binding. Its implementation is separate, but the same conceptual gap remains.

**Required, bounded:** prevent explicit amount prose from becoming valid merely because a unit is label-adjacent to a citation. Cover the disclosed example and the same-dimension counterexample at the visible surfaces and oracle. Reuse the existing tool-only/constrained code-owned narrative where prose cannot be checked safely. No universal English blacklist, new physical criterion or elaborate dimension system is required. Return implementation to the S14 owner; reviewer changed no product files.

**Why P1:** this is the same central no-invented-numbers trust boundary, bypassed with ordinary punctuation on the previously reported claims; neither runtime nor the gate-counting oracle notices. It is not a spelling corner case or merely confusing units. The saved thirty turns themselves show no newly discovered invention; that finite sample does not close the reproducible enforcement defect. Q16 explicitly retains numeric-language review, so amended Gate A acceptance is **not cleared** by this review.

## Fresh verification

Run from the isolated review worktree:

```powershell
python -B evidence/reviews/R-A/recheck-fix5/probe.py
```

- Twenty **exact** prior-review strings, extracted from its AST: sixteen bad claims refused by both detectors; four benign claims preserved. This includes `a full second`, `one whole minute`, `one full radian`, `one full metre`, `a one-second delay`, `a single-second interval`, `one g` and `one N` in their original sentences.
- Eighty visible-surface checks; twelve private-use forgery checks (U+E000, U+F8FF, U+F0000). Three escaped-JSON forgery trial checks each exhaust four attempts and fall back safely.
- Eight bounded gap probes and thirty-two associated surface checks; seven actual gate-helper trials (six original misses safely fall back, one disclosed label miss is displayed).
- Independent oracle imports no `contracts.agent`; its existing corpus agrees on **56/56**. This does not negate F1-R3.
- Agent plus pipeline suite: **59 tests OK**. Setup-validator suite: **14 tests OK**, synthetic safety fixtures only.
- Hashes of **418 protected files** under Build/contracts/tests/S14 match before and after; network denied; no new extraction or S14 CLI writes.

Evidence is beside [the reproducible probe](C:/Users/HP/Documents/Hackathon/2026-10-26%20-%20Meta%20Global%20AI%20Developer%20Hackathon/.worktrees/R-A-recheck3-orch96/evidence/reviews/R-A/recheck-fix5/probe.py): `results.json`, `fix5-replay.json`, `probe-stdout.txt`, `agent-tests.txt`, `setup-tests.txt`.

## Q16=A and packet provenance — reporting defect stays closed

Fresh `S14g_fix5_gate_a.run()` exactly matches the saved fix5 **summary**:

- `gate_a = MET_AMENDED_Q16`, **not plain MET**.
- Verbatim `gate_a_label = "scale unverified, not setup-validated"`.
- Ten distinct recorded scenes; numeric-contract **10/10**, production setup-validator **0/10**, shown alongside.
- Saved live turns **30/30 shown unchanged**, **0 fallback**, **0 oracle-flagged invented shown numbers**; thirty unique case IDs. Tool-output hashes are checked during replay.
- Ten actual calls through the original production setup validator were observed with absent bundles (`scene=None`), with its binding restored afterward. No fake setup success. Four additional clearly synthetic summary-logic checks verify the numeric threshold, missing-turn failure and flagged-invention failure.

Owner Q16=A is recorded in `DECISIONS_LOG.md:3–10` and `STATE.md:3–5`; it amends the spec-validity arm only. The fixture interview answers and synthetic-room trial outputs are not physical, calibrated or user-interview evidence. Historical plain-MET packets are not relabelled or overwritten by this review.

Skipped new model calls, spend, installs, physical/UI integration and product fixes. Remaining risk: the label-adjacency amount bypass blocks numeric-language clearance despite correct Q16 labels and a clean saved sample.
