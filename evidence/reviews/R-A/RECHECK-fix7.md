# R-A fix7 recheck — CLEAR (bounded Gate A / Q16 scope)

Reviewed main base `8fa101a9ce1995a28b96cc7211b1af822a829cfc`, including fix7 `3b07b4eefe12b3f1543ce74f05512c738c39ee2b`. Independent Sol/high review of the Claude implementation; offline, product-read-only, incremental API/compute spend **$0**.

**F1-R4 is structurally closed within the supported unit/amount vocabulary. Prior F1-R/F1-R2/F1-R3 and CITE-forgery closures are preserved. Gate A is supported as MET_AMENDED_Q16, verbatim label "scale unverified, not setup-validated", numeric-contract 10/10, production setup-validator 0/10. Never plain MET for this packet.** Two nonblocking residual categories remain below; this is not a universal natural-language guarantee.

## Closure evidence

| Check | Fresh result |
|---|---|
| Six F1-R4 explicit-one/in-unit bypasses | All refused by runtime and independent oracle on all four visible surfaces (24 checks). Each actual Gate A helper injection exhausts four attempts, displays only the tool-backed fallback, and reports no shown invention. |
| Remaining fix6 extension | All 16 cases / 64 surface checks match updated expectations. Eleven numeric-claim helper injections, including the six above, all safely fall back; zero helper bypasses. Benign pronoun, double-check and direct unit labels remain accepted. |
| F1-R/F1-R2 | Exact original 20 cases / 80 surfaces preserved: 16 numeric claims refused, four benign strings retained. |
| F1-R3 | All eight original gap cases / 32 surfaces refused. Seven prior actual-helper regression injections also fall back. |
| CITE forgery | Twelve private-use-marker/surface refusals; three JSON-escaped trials exhaust four attempts and fall back. |
| New independent extension | **192** clause cases (16 amount tokens × six unit families/aliases × two word orders) refused by both detectors; **30** binding/benign/surface controls and **eight** normalization/segmentation checks pass. |
| Focused suites | **73 tests OK**, no failures, errors or skips: agent, pipeline-understand and production setup-validator safety suites. |
| Oracle | Shared corpus **84/84**; AST check finds no `contracts.agent` import. Separate implementation is not independent semantic ground truth. |
| Read-only safety | SHA256 of **451** protected files unchanged through probes and tests. Python network connections and .env reads denied; no live calls, installs or new extraction. |

The reviewer adapted the original `recheck-fix6/probe.py`, not the implementation worker's copied probe. Original SHA256 `056edb817c36e3c918093c9fec53e51acc0600aa7befd16bdd2b0e111f50ca52`; reviewer adaptation `15861b76ad7198a403bc06110cac1d86726b3dc60e4bb5454983d76b49029092`. The [adaptation diff](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/R-A-recheck5-orch109/evidence/reviews/R-A/recheck-fix7/adaptation.diff) includes stronger actual-helper assertions, not merely changed verdict text.

## Why this closes the reported structure

`contracts/agent/validate.py:77–95` checks each normalized raw/Cf-stripped clause for amount-plus-unit **before** masking bound units. Thus an amount cannot be laundered by placing it before or after an `in <units>` label anywhere in that clause. `_BOUND` at line 59 separately demands a direct cited quantity or clause end after the label; `in seconds is ...` and `in seconds, ...` do not bind. This generalizes over word separation/order instead of adding the six reported phrases.

The oracle's `_scan` (`evidence/S14/S14g_fix_oracle.py:48`) accumulates unit/amount state until `. ! ? ;`, while `_bound` at line 72 checks the raw suffix. It independently rejects the same bypass class. Both checks also run on final joined visible text; splitting words across text segments does not bypass them. Fullwidth/Cf variants were freshly refused.

## Q16=A replay, not physical validation

Fresh replay through the existing helper matches the saved fix7 **summary**, with the exact fix7 wrapper's scope-string replacement. Ten calls were observed through the original production setup-validator binding; all received absent authoritative bundles and failed (**0/10**). The original binding remains restored. Numeric-contract fixtures pass **10/10**.

The thirty historical model replies replay **30/30 unchanged**, **zero fallback**, **zero oracle-flagged shown inventions**, with thirty distinct case IDs and tool-output hashes checked. Synthetic summary-only controls reject eight specs, missing turns and an invented number, and accept the amended nine-spec threshold. No setup success is fabricated.

These are recorded-scene fixtures with synthetic interview answers and synthetic-room trial tools, not new interviews, live model runs, calibrated scale, physical fitting success or deployed UI evidence. The packet itself says **MET_AMENDED_Q16**, **"scale unverified, not setup-validated"**, and **setup-validator 0/10** alongside.

## Nonblocking residuals — honest bounds

### P2 — finite vocabulary / unitless semantic claims

The independent exploratory probes demonstrate accepted prose, not universal closure:

- `Elapsed time in seconds. It is one. Tool result: <duration q>`
- `The duration is one. Tool result: <duration q>`
- `The sphere completes a single oscillation. Tool result: <duration q>`
- `The elapsed time is one microsecond. Tool result: <duration q>`

Both detectors accept these synthetic responses; `safe_reply` displays them beside the unchanged cited **0.2 s** tool value. The last is an explicit unsupported-unit claim and can mislead prose; it is not silently counted as a refusal. Clause boundaries, unitless `one`, count nouns and unlisted microsecond units are outside the bounded rule.

**Priority judgment: P2, not a new P1 blocker in this fifth-round scope.** The first two omit the amount's unit / split its context across sentences; the oscillation statement asserts a count absent from these tools, not a replacement tool measurement; a microsecond duration is an unlikely substitution in the ordinary seconds-scale reviewed trial context. They demonstrate coverage gaps, but not another ordinary supported-unit amount/binding bypass like F1-R4. They do not mutate any displayed cited quantity, although their prose can still be wrong. This likelihood/context judgment is not a proof they can never occur, nor is synthetic origin alone a reason to downgrade a realistic defect. If observed in normal model replies, reassess priority; for a universal prose guarantee, use the existing code-owned/tool-only narrative rather than claiming a finite lexicon proves it.

### P3 — conservative refusal / availability

Legitimate prose such as `Elapsed time in seconds is <q>`, `in seconds, <q>`, or amount-word questions in a unit clause may now be refused. Fresh controls confirm the strict behavior; saved thirty-turn replay has zero fallbacks. Future live fallback/retry rate is unmeasured. This affects usefulness, not fabrication of a cited tool measurement.

## Reproduce and inspect

```powershell
python -B evidence/reviews/R-A/recheck-fix7/probe.py
python -B evidence/reviews/R-A/recheck-fix7/extension.py
python -B evidence/reviews/R-A/recheck-fix7/verify.py
```

Machine evidence: [baseline results](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/R-A-recheck5-orch109/evidence/reviews/R-A/recheck-fix7/results.json), [independent extension](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/R-A-recheck5-orch109/evidence/reviews/R-A/recheck-fix7/extension-results.json), [fresh replay](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/R-A-recheck5-orch109/evidence/reviews/R-A/recheck-fix7/fix7-replay.json), [test summary](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/R-A-recheck5-orch109/evidence/reviews/R-A/recheck-fix7/tests-summary.json), and logs/scripts beside them.

Skipped live/model/UI/physical tests and product fixes. Remaining risks: P2 prose coverage and P3 conservative fallback; no universal or physical-validation claim.
