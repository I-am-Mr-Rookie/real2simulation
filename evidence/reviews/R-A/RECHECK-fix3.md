# R-A fix3 recheck — CHANGES_REQUIRED

Baseline main `eddead8528135e25e36431cbdc100354b3bcde71`; reviewer assigned `gpt-6.1-sol/high`, cross-vendor review of Opus S14 work. Read-only product review; no paid calls. Review completion does not mean Gate A completion.

## Closure decisions

| Original finding | Recheck |
|---|---|
| F1 P1: one/double/couple; same detector used by gate | **Original examples fixed; invariant still OPEN (P1 F1-R below).** New oracle is implementation-independent, not an independent guarantee of numeric-language coverage. |
| F2 P1: split text assembles a number | **CLOSED for reported defect.** Joined visible-run validation blocks the original split example. Fresh 52-test suite covers reply text, prompts, chips, rationales and the trial path. |
| F3 P1: ten repeats of one synthetic scene | **Clip diversity/custody CLOSED; valid-spec gate remains PROVISIONAL (P1 F3-R).** Ten distinct source hashes and accepted Wonder responses are real recorded-clip cases, but their specs bypass the production setup validator. |
| F4 P2: saved artifacts cannot re-audit historical numeric provenance | **CLOSED at saved-response/display scope.** Ten accepted texts/specs retained; all thirty accepted turn responses carry exact hashed tool outputs, including fourteen Mystery turns. No raw-provider or physical-result attestation is inferred. |

## F1-R — [P1] Common implicit time/angle claims still pass display and gate oracle

Runnable probe: `python -B evidence/reviews/R-A/recheck-fix3/probe.py` from this worktree.

These uncited model text claims pass `safe_reply` AND the actual `check_trial -> safe_reply -> oracle` gate path:

- `The elapsed time is a second.`
- `The period is a minute.`
- `The angle is a radian.`

Each plainly asserts a unit-valued quantity without a trusted quantity reference. Every end-to-end probe shows the model reply, takes one attempt, records no blocked issue, and returns no invented-number finding; an unrelated legitimate gravity reference does not source these assertions. The original `one metre`, `double`, `couple`, and split `nine point eight` attacks are now blocked. Ordinary pronoun `one` and `double-check` remain allowed.

Owning code: `contracts/agent/validate.py:34–47` handles `a/an` for selected spatial/mass units but time/angle units only after `one`; `evidence/S14/S14g_fix_oracle.py:19–21,43` similarly excludes `a/an` + TIME, and radians are absent from its unit sets. Independent tokenizer/imports remove the original shared-function error, but the same conceptual coverage gap remains. Corpus self-check passes all 29 cases and does not contain these misses.

Required: close these explicit unit-valued claims at the production display boundary, extend the independent expected-bad corpus/regressions, and rerun Gate A. Prefer a constrained narrative/tool-only fallback if open prose cannot meet the stated invariant. Do not turn this review into a blacklist-based universal guarantee.

## F3-R — [P1] Numeric draft validation is not production setup validity

Written Gate A (`QUEUE.md:439–440`; final plan S14) requires nine valid specs from ten recorded scene fixtures and no untraced number across thirty test turns. The production interview calls `contracts.experiment.validate_setup`, which checks authoritative scene identity, scale, constraints, geometry and numerical stability. S08c explicitly requires out-of-scene/unstable setups to be rejected.

Fix3 instead starts with `tests/spec/test_experiment_schema.py` authored synthetic fixtures and temporarily replaces `interview.validate_setup` with `validate()` (`S14g_fix3_gate_a.py:107–117`). All ten saved specs pass that numeric contract, but all retain the test fixture's environment and estimated scene-scale status while their recorded scene contexts say unverified scale. Restoring the real interview validator and calling with the same absent bundles refuses all ten; no successful bundle-bound production specs are demonstrated. The numeric validator's CLI itself warns that scene-fit/stability are not evaluated and it is not execution approval.

Therefore **10/10 numeric-contract fixtures is a useful provisional result, not unconditional Gate A MET**. The scope string and honest worker limits do not change what `summary.gate_a = MET` communicates. Keep that status provisional/not met until nine cases pass the normal setup path, or an explicit owner-approved gate amendment defines a narrower acceptance. This review makes no such amendment and asks for no unnecessary paid rerun.

Synthetic interview answers are transparently labelled and acceptable for a fixture test, but are not user-interview evidence. Synthetic-room tool outputs are also acceptable for testing thirty-turn numeric enforcement: Gate A does not itself demand thirty measured-video trials. Neither fact alone is a new physical-success requirement. The decisive gap is bypassing the normal spec validator while claiming valid recorded-scene specs.

## Custody, replay and factual corrections

- Ten IDs exactly match the scoped S02 approval: RM02, RM04, RM05, PD02, PD03, PD04, PD06, PJ03, ST03, BN01. All ten on-disk source-byte hashes match S02c acquisition, saved source hashes and keyframe-manifest source hashes. Saved manifest/context hashes and selected frame metadata match. Licence/source-URL fields match acquisition. This verifies local custody, not public-media-use approval or calibrated scale.
- **The report's RM02 seek claim is incorrect for the saved packet.** RM02 records PTS-sourced frames; RM05 and PJ03 record `ffmpeg-seek(container duration)`. PD02 has two selected frames, not three. See `recheck-fix3/custody.json`. Seek timestamps are container-time evidence, not calibrated physical capture timing. Correct the worker report; do not silently relabel existing evidence.
- The existing offline function replays the ten recorded Wonder texts, but its thirty Spark replies are **scripted**, not replayed saved live replies (`S14g_fix3_gate_a.py:139`). Saved offline and live gate/count totals agree; operational totals do not: offline has 24 model replies/6 fallbacks/66 attempts versus live 30/0/30. Equal MET summaries do not imply identical end-to-end runs.
- The review separately validates and renders every **saved live** accepted turn against its **saved exact** tool outputs. All tool hashes and rendered texts match; independent tool-quantity-format removal leaves no detector-flagged numeric text. This closes the historical fourteen-Mystery-display provenance gap without substituting fresh random simulator values.
- Re-running the full offline simulator is not byte-deterministic: Mystery-g uses a fresh `secrets.randbits(32)` seed (`Build/lab/session-bridge.py`). Stable specs/summary and exact saved-response rendering are narrower claims than deterministic fresh simulation.
- Large JSON/JSONL hygiene is **key-name-only**, including embedded accepted JSON: no credential-shaped key paths found. This is not proof that no credential could appear under an innocuous key or free text; secret-value searching/printing was deliberately not performed.

## Evidence and handback

`recheck-fix3/probe.py`, `results.json`, `probe-stdout.txt`: original/new attacks, source custody, numeric/production distinction, offline replay, exact live render/hash replay, key-name hygiene and input immutability. `custody.py`, `custody.json`, `custody-stdout.txt`: independent acquisition-manifest bindings, frame timing, all forty saved ledger labels/HTTP statuses, oracle import independence, offline/live differences. `agent-tests.txt`: 52 tests pass.

Return F1-R/F3-R to S14 owner; correct frame/replay wording. Do not close S14g/S14h from this packet. No Build/tests/S14/control changes were made; no live API calls, spend, dependency installs, secrets access or publication.
