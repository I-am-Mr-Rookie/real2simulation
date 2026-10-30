# S21a-orch126 REPORT — DONE

- Lane/model: CODEX-2 (army: Claude), anthropic/claude-opus-5-5/high. Coding quota: OpenCodex-managed; not polled.
- UTC issued 2026-10-30T10:53:45Z; work started ~10:55:26Z; stopped 2026-10-30T10:59:24+00:00. Branch run/S21a-orch126 from main 67e299a.
- Tokens/cost: unobservable (unknown). No GPU/API/network calls. No dependency installs. No secrets read.

## Delivered
- [Build/benchmark/manifest.json](Build/benchmark/manifest.json): 11 sha256-pinned accepted evidence files (S05d, S06e/f/h,
  S07b orch14, S11, S12), clips ST03/BN01/PD02-06/RM02/RM04/RM05, ST03 split refs, 21 metrics labelled
  measured/simulated/unavailable. Zero literal numbers in gates/clips/split/metrics (enforced).
- [Build/benchmark/manifest.py](Build/benchmark/manifest.py): stdlib validator (sha pin, RFC 6901 pointers, authored-number
  rejection, class rules) + `leakage()` (overlap, ordering, boundary agreement across 3 files, seal counts, scored ⊆ held-out,
  training/prediction sha consistency, suffix_observations_read=false).
- [Build/benchmark/test_manifest.py](Build/benchmark/test_manifest.py): 6 unittest cases (pass + 5 tamper negatives).
- [BENCHMARK.md](BENCHMARK.md) method section; [evidence/S21/check.json](evidence/S21/check.json) resolved freeze output.

## Fresh checks
- `python Build/benchmark/manifest.py check` -> exit 0, ok=true; gates gate_m=NOT_MET_INPUT_READINESS, gate_rs=NOT_MET;
  split train 19 (58-76), held-out 466 (77-542), scored 7; no leak.
- `python -m unittest Build/benchmark/test_manifest.py` -> Ran 6, OK.

## Honest result
Gate M and Gate RS NOT_MET. ST03 normalized RMS is measured but diagnostic (7/466 coverage, scored=false). Gravity in m/s^2,
metric scale (RM02/04/05), Gate RS median, bounce and pendulum RMS = UNAVAILABLE with evidence reasons.

## Ponytail
Reuse: existing S12 seals/prediction commitments are the split source of truth (no new split authored); pointers instead of
copied numbers; stdlib json/hashlib only, no jsonschema dep. Smallest: one module + one JSON + one test. Skipped: freeze/write
helper (hashes filled once by a one-off hashlib command), Build/web/src/about/ (S21e), S11 per-case extraction, S07 chunktrack
PD/BN results (not accepted into S12 split). Risks: evidence edits break sha pins (intended: refreeze); `sample_count: "1 run"`
strings are descriptive labels; S05d npz bytes are gitignored (only their recorded sha is pinned).

## Communication
Silent; one completion message to controller chat as authorized.
