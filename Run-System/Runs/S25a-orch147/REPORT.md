# S25a-orch147 REPORT — DONE

- Lane/model: CODEX-2 (army: Claude), anthropic/claude-opus-5-5/medium. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable); no provider/GPU/API calls.
- UTC: start 2026-10-30T11:46:17Z, stopped 2026-10-30T11:52:03+00:00. Base main 8aa3e7f3, branch run/S25a-orch147.

## Files
- README.md (replaced workspace index with project README; dev-controls links kept in last section).
- ATTRIBUTION.md (new): 9 footage credits = BENCHMARK clips (ST03, BN01, PD02/03/04/06, RM02/04/05) incl. both non-simulated S18h credits (RM02, RM04); SIMULATED library entries noted; SAM 3.1 + Apache upstream licence copies; direct third-party libraries with versions from package.json/requirements.
- evidence/release/check_links.py (new): relative-link resolver for README/ATTRIBUTION with regex self-check.

## Content sources (no hand-made numbers)
- Results/gates copied as labels from BENCHMARK.md summary; numbers left in BENCHMARK.md.
- Meta usage: muse-wonder-1.0 (Build/agent/muse.py MODEL; evidence/S14/S14g-fix3-ledger.jsonl), Baseten meta-models/muse-spark-open-1026 one call 1,176 tokens (S16e/S16h checkpoint), facebook/sam3.1 (evidence/S13/S13h/live/segment/raw-result.json). Open-weight bonus NOT claimed. Meta dollar cost UNAVAILABLE.
- Judging URL, frozen revision, demo video: PENDING S23. Railway dev hosts listed as dev only (from STATE.md).

## Checks (fresh)
- python evidence/release/check_links.py -> "all relative links resolve", exit 0.
- python Build/benchmark/manifest.py check -> exit 0.
- python -m unittest Build/benchmark/test_manifest.py Build/benchmark/test_about.py -> 9 tests OK.
- python -m unittest Build.api.health.test_health -> 6 tests OK.
- rg scan README/ATTRIBUTION for key patterns, user paths, archive/AttemptLens -> no matches.
- python Run-System/worker_timebox.py check -> see TIMEBOX.

## Ponytail
- Reused BENCHMARK.md summary, existing health READMEs' exact commands, S18h credits JSON and clips.csv rows instead of re-deriving; no new tooling beyond one ~20-line stdlib checker.
- Skipped: per-transitive-dependency licence inventory; web `npm run build`/dev run; Build.api.health.test_dependencies (needs test requirements; not re-run); live URL checks of Railway dev hosts and footage URLs.

## Risks / next
- clips.csv owner_approved = NO for all used rows (approval receipts live elsewhere); flagged in ATTRIBUTION for S25b reconciliation.
- No project LICENSE file; marked PENDING owner decision.
- Library licence column is from upstream knowledge, not verified against installed package metadata.
- Next: S23 fills judging URL/frozen revision; S25b public-package checklist.

Communication: silent; one completion line to controller only.
