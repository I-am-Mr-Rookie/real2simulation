# R-A — Gate A cross-vendor review

**Verdict: CHANGES_REQUIRED.** Review complete; Gate A must not be accepted as clear. Return defects to the original S14 owner; this run changes no product source or canonical controls.

Baseline: main `ca34cbff8a3aaae6b3a4b07c4dda83d73e6b9821`; contract R-A-orch50; assigned gpt-6.1-sol/high reviewing S14 Opus work. Evidence is local/synthetic, not calibrated physical evidence. No live Meta calls.

## Findings

### F1 — [P1] Shared number-word blind spots let invented claims pass both runtime and the claimed independent scan

- Owning source: `contracts/agent/validate.py:30–37,48–54`; gate checker `evidence/S14/S14g_gate_a.py:27,42–47,59–68`.
- `numeric_issue` deliberately allows standalone **one** and **double**. `invented` imports that exact predicate, so it is independent only of the validator's *verdict*, not of its number-detection failure modes.
- Reproduced with actual local simulator/fitter outputs: `Gravity is one metre per second squared.` and `Gravity is double the fitted value.`, each with an otherwise-valid fitter ref. Both go through `trial.check_trial` and `safe_reply`, show the invented claim, and return `invented: null`, `model_number_attempts: 0`, one attempt, no blocked issues. Neither the asserted unit-valued one nor the multiplier is backed by a number segment. `Distance is a couple of metres.` also passes both checks.
- Evidence: `probe-results.json` → `probes[0:3]`, `end_to_end_gate_turns[0:2]`; reproduction: `python evidence/reviews/R-A/probe.py`. These assertions expect the observed defects, not a product pass.
- Required owner action: close the numeric-claim holes at the display boundary, add these cases to product regressions, and use a genuinely independent oracle/adversarial corpus for gate counting. Preserve ordinary pronoun/use cases without allowing `one` + a unit or a doubled quantity. If unrestricted prose cannot meet the invariant, constrain the narrative/fallback rather than claiming a universal guarantee from this blacklist.

### F2 — [P1] Per-segment checking permits an invented number assembled during rendering

- Owning source: `contracts/agent/validate.py:109–115`; `Build/agent/tools.py:40–52,76–86`.
- Three individually allowed text segments, `Gravity is ni` + `ne point ei` + `ght metres per second squared.`, render as **Gravity is nine point eight metres per second squared.** No text segment itself matches the regex; `safe_reply` returns `blocked=[]` and displays the whole invented claim.
- Reproduced through `gate.turn` too. Unlike F1, the post-render gate scan catches this particular joined claim, but that scan does not protect runtime display and the existing thirty-turn suite omits this attack.
- Evidence: `probe-results.json` → last `probes` item and `end_to_end_gate_turns[2]` (one attempt; model reply shown; `invented` non-null).
- Required owner action: validate the eventual visible text/contiguous text runs, including question prompts, chip labels and candidate rationales, before display; add split-token regressions. Keep resolving number segments only against trusted tool outputs.

### F3 — [P1] Ten completions on one synthetic scene are not the required ten recorded-scene fixture cases

- Owning source: `evidence/S14/S14g_gate_a.py:35,79–90,127–140,179–189,192–202`; acceptance `QUEUE.md:439–440` and final plan Gate A.
- `spec_case` always receives the same `CONTEXT`, selects only the first candidate, then uses hand-written `SYNTHETIC_ANSWERS` and an existing test base spec. Offline rotates four recorded replies for the same `synthetic-room-v1`; live repeats the same scene ten times. All saved live specs choose `free_fall`.
- The **10/10 arithmetic is honest for those ten synthetic completions**, and S14g's report candidly states the limitation. It does not establish the specified “9 of 10 recorded scene fixtures” acceptance. `summary` nevertheless promotes it to `gate_a: MET` with no coverage check. The real-scene integration prerequisite does not become evidence merely because it is marked ready.
- Required owner action: exercise the actual required recorded-scene fixture set with explicit case identities, or have the controller explicitly retain a constrained/provisional synthetic result instead of claiming the unmodified gate has passed. Do not manufacture fixture diversity by repeating one case.

### F4 — [P2] Historical live provenance cannot be fully re-audited from the saved packet

- Owning source: `evidence/S14/S14g_gate_a.py:71–76,79–106`; `S14g-live.json`.
- The recorder retains raw replies only in a local `seen` list. Persisted spec rows contain attempts/rejections/template/valid booleans, but no accepted response, resulting spec or scene identity. Turn rows save `shown` and verdicts, not the tool outputs/observations/random seed that back their values.
- Fresh independent review reproduced the deterministic tool quantities for **16** non-mystery saved turns. **14** mystery turns use `secrets.randbits` in `Build/lab/session-bridge.py:36–37`; their historical tool values cannot be regenerated from the packet. Their format-only residual scan is explicitly *not* provenance proof. No evidence of fabricated historical values was found; the evidence is simply insufficient to independently prove them all.
- Evidence: `probe-results.json` → `live_independent_residual_scan[*].provenance`. The initial attempted deterministic re-audit failed on mystery turn 2; the review correctly narrowed its claim instead of substituting a fresh random run as historical proof.
- Required owner action: retain sanitized accepted responses, scene/case IDs, validated specs and exact trusted tool outputs (or replayable input/seed plus hashes) with future gate evidence. Never retain keys/private files. The controller decides whether existing evidence needs a rerun; this review authorizes no paid call.

## Verified sound behavior

- Existing agent suite: **49/49 pass** (`agent-tests.txt`). Existing understand-pipeline suite: **7/7 pass** (`pipeline-tests.txt`). Existing interview UI suite: **8/8 pass** (`interview-ui-tests.txt`). These passing tests do not invalidate the new counterexamples.
- The new `kind` normalization preserves chips/prompts and does not mutate caller input. All six kind/empty-vs-nonempty-chip combinations were checked; direct number words in both prompts and chips are rejected in all combinations. No new normalization-specific weakening found. F1/F2 are inherited text-check weaknesses, not dropped-field normalization bugs.
- Unknown tool IDs cause whole-reply fallback; fallback includes each trusted fitter/simulator quantity with value/uncertainty/unit/label. No-tool fallback has no numbers. Invalid tool outputs raise instead of being relabeled or silently accepted. Existing tests also cover unknown quantities, foreign refs, duplicate IDs and malformed quantities.
- Ordinary number words, spelled ranges, digit ranges, units with digits, Arabic-Indic digits, Roman numeral characters, CJK numerals, fractions, **twice** and **half** are blocked in the exercised cases. This is finite coverage, not an unbypassable-language guarantee.
- Offline Gate A rerun via imported `offline()` (never its overwriting CLI): **10/10, 30 turns, 0 detected invented claims, 24 shown / 6 tool-only fallbacks, 36 caught number attempts, 13 replayed Wonder / 66 scripted Spark attempts**. All original `evidence/S14/*` hashes remained unchanged. The original suite still reports MET because the new counterexamples are outside its corpus.

## Counting and spend audit

- Saved live summary recomputes exactly: **10/10**, **30** turns, **0** detector-positive shown claims, **30** model replies / **0** fallbacks; **12 Wonder + 30 Spark = 42** attempts. The two extra Wonder calls correspond to rejected unknown-ID replies; they are not silently omitted from the ledger.
- Ledger labels/multiplicities reconcile exactly with per-case attempts; all 42 records report HTTP 200 and token usage. Per-row token-price arithmetic reconciles; total **estimated $1.132782**, rounded **$1.1328**, below the run's **$3** estimate cap. No row's estimate exceeds its recorded reservation.
- This is internally complete for the **recorded** S14g attempts, not an independently queried provider invoice or account-wide ledger. Billed amounts remain null. Spark is estimated with the reused Wonder-rate margin; actual Spark price/billing remains unverified, as the source report says. S14b has a separate historical ledger; this total is not all project spending.
- **0/30 is honest as a count of this detector's outcomes**, not proof of no possible invented numbers: F1 produces false negatives. No claim of dishonest operator behavior is made.
- This review made **0 provider calls and $0 API/GPU spend**; coding subscription tokens/cost unobservable, OpenCodex-managed; not polled.

## Scope and handback

Read S14a–f reports, S14g-orch47 report and stored packet; reviewed Build/agent, contracts/agent/schema, related tests, pipeline validation and interview rendering consumers. Fresh checks and probes are recorded only in this run's Owns.

Return F1–F4 to the original S14 owner. S14h/parent completion remains held pending controller acceptance of remediation or an explicit constrained fallback. Review task itself is DONE; it does not merge, clear, patch or reroute Gate A.

Skipped: live calls, source-mutating historical mutation scripts, product fixes, full web build/browser/E2E, physical/calibration validation, and provider billing access. Risks: invented numeric claims can reach users and evade the shared detector; saved live evidence does not fully establish historical provenance or required fixture coverage.
