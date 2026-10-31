# S24l-orch181 REPORT
Lane/model: CLAUDE, anthropic/claude-sonnet-5-5/medium; OpenCodex-managed; not polled. Issued 2026-10-31T00:47:01Z. Branch run/S24l-orch181.

## Changed (only media/script/DEMO_SCRIPT_DRAFT.md, now v4)
- SWAP BLOCK rewritten from S07h/S07k/S07m: hero OWN01 10.96 ± 0.77 FAILS v3 (p 0.0065) and v2 abstains -> "not validated"; OWN05 v1 8.62 ± 1.28, OWN05 v2 9.62 ± 0.74, OWN07 v2 9.51 ± 0.93, OWN08 v2 8.82 ± 0.27 (~3.6 u below 9.79; passing ≠ accurate), OWN02 v2 7.27 ± 3.07 (low power): all "conditional". All values copied from the S07m table.
- Caveats in block: v2/v3 are second/third analyses after v1 failed (forking paths), same scene/operator/phone; 6 px rule miscalibrated (S07l); v1 held-out 0/9, 11 clips = 9 measured + 2 abstain, OWN12 excluded; repeat drops 8.62/8.72/8.82 ~1 m/s² low; scale user-declared, clock unverified, rolling shutter assumed.
- Beat 5b VO/caption/status rewritten (hero fails own check; passing repeat windows ~7–9.6 each with u; user declares scale; app reports uncertainty). Word "validated/accurate" banned; only "conditional".
- Kept: stopwatch placeholder (Q22 open), "public use pending Koushik's go-ahead" on OWN shots, beat 5b still 20 s; timing line unchanged = 180 s (3:00).

## Ponytail use
Edited one existing file in place via line splice, no new tooling; reused S07m table verbatim; skipped other beats and no video.

## Checks
- git diff: 1 file, 18+/14-. worker_timebox.py check run (see below). Timing line untouched (sum 180 s).
- Not done: VO read-aloud timing (~55 words for 20 s is tight; cut list unchanged: drop the "You declare the scale" sentence first if over). Canonical QUEUE row read verbatim; STATE/controls not edited.
- Communication compliance: silent; one completion line to controller.
