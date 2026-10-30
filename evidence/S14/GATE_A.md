# Gate A checkpoint — MET_AMENDED_Q16

**Verdict: MET_AMENDED_Q16 — "scale unverified, not setup-validated".** Never plain MET. Machine record: [GATE_A.json](GATE_A.json).

- Owner amendment Q16=A (Oct30): numeric-contract validation on recorded scenes accepted, labelled verbatim.
- Numeric-contract specs **10/10** (need 9); production setup-validator **0/10** shown alongside (no authoritative bundles).
- fix7 offline replay: **30/30** shown unchanged, **0** fallback, **0** oracle-flagged inventions; oracle corpus **84/84**; agent suite 59 OK ([S14g-fix7-offline.json](S14g-fix7-offline.json)).
- S14h re-run after micro/nanosecond unit addition: same counts ([S14h-replay.json](S14h-replay.json)); suite 60 OK ([S14h-unittest.txt](S14h-unittest.txt)).
- Cross-vendor review: R-A recheck5 **CLEAR** ([RECHECK-fix7.md](../reviews/R-A/RECHECK-fix7.md)).
- Fallback: any validation failure -> code-owned tool-only card (`safe_reply` -> `tool_backed`), issues returned for logging; proven model-invariant by `test_fallback_card_is_code_owned_and_model_invariant`.

Known limits (carried): P2 unitless "one", count nouns ("single oscillation"), unlisted units beyond micro/nanosecond; P3 conservative refusals, live fallback rate unmeasured.
Inputs: recorded-scene fixtures, synthetic answers, synthetic-room tools. No calibrated scale, setup validation or physical evidence claimed. $0, offline.
