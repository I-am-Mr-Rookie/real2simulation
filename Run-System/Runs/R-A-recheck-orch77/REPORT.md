# R-A-recheck-orch77 — DONE; verdict CHANGES_REQUIRED

Review artifact: `evidence/reviews/R-A/RECHECK-fix3.md`. Parent S14/Gate A is **not cleared**. This DONE denotes completion of the assigned read-only review, not product acceptance.

## Findings

- **P1 F1-R:** original one/double/couple/split probes now blocked, but `The elapsed time is a second.`, `The period is a minute.`, `The angle is a radian.` pass display and actual trial gate with no oracle finding. New oracle is implementation-independent but shares conceptual unit-coverage gaps. Return to S14 owner; extend independent expected-bad corpus and display regressions.
- **P1 F3-R:** ten distinct approved recorded clips now have valid acquisition/source/manifest custody; ten numeric-contract specs are not nine successful production bundle-bound specs. The evidence monkeypatches `interview.validate_setup` to numeric `validate()`, inherits synthetic test environment/estimated-scale fields, and uses labelled synthetic answers. Scope stays provisional; unconditional `gate_a=MET` is not justified by the normal setup path.
- **F2 closed** for the original joined-render defect; 52 fresh tests pass.
- **F4 closed at saved-display provenance scope:** ten accepted texts/specs and thirty exact tool-output/response records support local revalidation/render audit, including fourteen Mystery turns. No physical/provider attestation inferred.
- Factual corrections: saved RM02 frames are PTS, not seek; RM05/PJ03 are seek; PD02 has two selected frames. Offline Spark replies are scripted, not saved-live reply replay. Offline/live matching gate totals do not mean identical runs (24 vs 30 shown model replies; 6 vs 0 fallbacks; 66 vs 30 attempts). Fresh Mystery simulation is not byte-deterministic.

## Contract, scope and timing

- Assigned CLAUDE cross-vendor review lane, `gpt-6.1-sol/high`; no routing/model/effort/provider changes. OpenCodex-managed; not polled. Tokens unknown; new provider spend $0.
- Parent project explicitly supplied: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; controller `01a1882d-3481-7ce3-8f88-45c942e341cd`. No new chat was created or association independently queried.
- Plain Git isolated worktree `.worktrees/R-A-recheck-orch77`, branch `run/R-A-recheck-orch77`, from main `eddead8528135e25e36431cbdc100354b3bcde71`. Canonical controls untouched; no merge/push. Controller integrates after inspecting findings.
- Issued 2026-10-30T05:40:07+00:00; cutoff 06:05:07Z; deadline 06:10:07Z (12:10:07 Dhaka). First observed clock 05:41:42Z. Actual completion/report times are in TIMEBOX.json; early DONE is permitted only after assigned review checks finish.
- Owns only `evidence/reviews/R-A/RECHECK-fix3.md`, `evidence/reviews/R-A/recheck-fix3/`, `Run-System/Runs/R-A-recheck-orch77/`.

## Checks and runnable evidence

From this worktree, with `PYTHONDONTWRITEBYTECODE=1`:

1. `python -B evidence/reviews/R-A/recheck-fix3/probe.py` — **PASS**: four original attack closures, three new trial-path misses, ten source-byte/manifest/context bindings, recorded Wonder replay, numeric/production-validator distinction, two offline runs, exact saved thirty-turn rendering/hash audit (fourteen Mystery), seven JSON/JSONL files with zero credential-shaped key paths, S14 input hashes unchanged. Receipts `results.json`, `probe-stdout.txt`. Fresh full offline turn arrays are not deterministic; specs and summaries match the saved offline packet.
2. `python -B evidence/reviews/R-A/recheck-fix3/custody.py` — PASS, ten acquisition/manifest bindings, forty saved ledger calls with matching attempt labels and HTTP 200, independent oracle imports, exact timing metadata and offline/live differences. Receipts `custody.json`, `custody-stdout.txt`.
3. `python -B -m unittest tests.agent.test_visible_text tests.agent.test_contracts tests.agent.test_reply tests.agent.test_trial tests.agent.test_retry tests.agent.test_interview tests.agent.test_muse` — **52 OK**, 12.484s. Receipt `agent-tests.txt`.
4. `python -B Run-System/worker_timebox.py check Run-System/Runs/R-A-recheck-orch77/TIMEBOX.json` — receipt `timebox-check.txt`.

The first probe run incorrectly asserted complete equality of live and offline summaries; this exposed their scripted/live operational differences. Corrected the review assertion to compare saved offline with fresh offline and compare only stated gate/count metrics with live, while recording all differing metrics separately. No source evidence was changed to make a test pass.

Final runner-only scratch-directory routing and bounded frame-transcode memoization were separately startup-asserted (`startup-check.txt`, PASS); the full replay logic had already passed before those non-semantic changes. No expensive third full replay was needed. A final results inspection confirms all ten specs inherit fixture environment/scale and synthetic answers and all ten restored production calls refuse missing bundles.

## Ponytail full / communication / limits

Read installed Ponytail 5.3.3 SKILL.md and applied full mode. Reused actual validators/renderers, existing offline gate function (never its output-writing CLI), saved accepted responses/tools, production simulator bridge, approved manifests and existing targeted tests. Added two stdlib-only scoped probes rather than changing product code or adding dependencies. Frame transcoding is memoized for repeat replay; fixture scratch directories are routed under owned evidence in the final runner. Initial runs used existing bridge's temporary self-cleaning system scratch before that redirect; cached clip inputs were read-only. No persistent writes outside Owns or canonical edits.

Skipped live Meta/GPU/provider calls, browser/UI/physical integration, installs, mutations of product/tests/S14, full build and pipeline/UI reruns; those are unnecessary for this read-only regression judgment. Existing twenty-nine-case oracle corpus was rechecked, not treated as universal language coverage.

Risk: key-name-only hygiene cannot prove absence of a secret hidden in innocent-looking free text; no secret values were searched or printed. Cached frame manifests/bytes were available locally but are not a published portable video-input archive. Recorded labels/ledger are local evidence, not independent provider billing or physical calibration proof. No owner decision or extra authority is inferred.

Communication: mandatory brief start/skill/finding notices were higher-priority exceptions to silent mode; no optional greetings or duplicated chat report. One authorized completion pointer to controller; no other outbound messages. Remaining action: original S14 owner fixes F1-R and resolves provisional spec scope before gate acceptance.
