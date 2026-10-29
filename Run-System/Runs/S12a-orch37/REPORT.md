# S12a-orch37 REPORT — DONE (worker 01a18968)

Lane CODEX-1 · anthropic/claude-opus-5-5/high · coding quota OpenCodex-managed; not polled · tokens/cost unknown; no GPU/Modal/Meta/paid calls.
UTC issue 2026-10-29T20:44:39Z · work started 20:44:59Z · stopped see TIMEBOX.json · base main d131047, rebased onto current main before final commit.

## Duplicate dispatch / write race (controller action)
Controller dispatched S12a-orch37 twice: worker 01a18967 (issued 20:43:22Z) and this worker (20:44:39Z), same worktree + branch.
Both wrote Build/real2sim/boundary.py and tests/prediction/test_boundary.py ~20:47-20:49Z. Commit f74b383 (01a18967, REPORT=DONE) captured
MY boundary.py with ITS test file and ITS evidence (S12a-boundary.json, S12a-tests.txt) -> inconsistent HEAD (its tests target an API that is
not in git; its module source was overwritten in the working tree and never committed). Nonterminal blocker sent to controller 20:51Z; no
reply by 21:00Z, so this commit makes the branch consistent with ONE implementation (this one): its two evidence files are removed and its
PLAN/REPORT/TIMEBOX replaced (all recoverable from f74b383). No other worker files changed after 20:49Z.

## Result
Gate M: **NOT_MET** in every output (source evidence/S07/S07f/actual-gate-m.json status NOT_MET_INPUT_READINESS, hashed in the record).
No calibrated g, metric scale or physical-accuracy claim. Units: image-height fraction (scale-free).

Files:
- Build/real2sim/boundary.py — split(record, suffix_identities=None) -> (Boundary, sealed_suffix); verify(boundary, sealed); fit_prefix(boundary)
  (wraps fitter select_model); record_json; main() writes the real ST03 record.
- tests/prediction/test_boundary.py — 7 tests (6 on fixtures labelled SYNTHETIC + 1 check of the committed ST03 record).
- evidence/S12/boundary-ST03.json — real boundary; evidence/S12/tests-prediction.txt — test log.

Acceptance:
1. Immutable prefix/suffix: Boundary is a frozen dataclass of tuples; SHA-256 of training rows, suffix identities (index, PTS) and, when tracked,
   suffix observations taken at split time; verify() rejects dropped/re-indexed/changed suffix frames and a forged prefix (test).
2. No leakage: Boundary stores only suffix hashes/count; fit_prefix only accepts a Boundary. Spy on select_model proves the fitter receives exactly
   the 6 prefix samples and no suffix time/position; arbitrary suffix values leave the fit identical (test). split() rejects suffix overlap by index
   OR PTS, non-increasing data, <3 prefix frames, empty suffix, non-int split (test).
3. Gate M result required: record carries gate_m NOT_MET plus source path/sha/status; test asserts it and absence of any g field.

## Real clip (ST03, approved scene_tracking scope, evidence/owner/S02/APPROVAL.md)
- Prefix = accepted S07b orch14 SAM3.1 track f58-76 (19 frames); last_training_frame 76; suffix identities = remaining source frames, sealed (465).
- **Finding (S07 custody):** orch14 frame_map labels frame 76 with PTS 2.569233 s, but the hash-verified source (fresh local ffprobe on
  test-data/public/ST03.mp4, sha 7239da80..., and recovery3 presentation-map) gives 2.535867 s; 2.569233 s is frame 77. Frames 58-75 match.
  Boundary quarantines frame 77 from the suffix and fit_run=false (real prefix fit withheld) until S07 owner/controller corrects the
  frame_map. No S07 evidence edited (outside Owns).
- Suffix observations are NOT tracked; S12c must track exactly the sealed identities and call verify() before scoring.

## Fresh checks (Python 3.14.5, this worktree)
- python -m unittest discover -s tests/prediction -v -> 7 OK (evidence/S12/tests-prediction.txt).
- python -m Build.real2sim.boundary -> "evidence/S12/boundary-ST03.json gate_m=NOT_MET conflicts=1 quarantined=[77] suffix=465".
- Regression: tests/measurement OK (1 pre-existing skip); tests/fitter OK.
- python Run-System/worker_timebox.py check Run-System/Runs/S12a-orch37/TIMEBOX.json -> TIMING PASS (run after commit-ready).

## Ponytail (full)
- Reused fitter select_model (no new fit code) and accepted S07b track / PTS map / Gate M files; stdlib hashlib/json/dataclasses; no deps, no __init__.
- Smallest complete: custody by type (Boundary has no suffix values) + hashes, not a custody service. One shortcut comment: fitter labels "m"
  but values are image-height fractions.
- Skipped: normalized-error scoring (S12c/S12e), parameter transfer (S12b), x-axis (vertical motion only), external sealed storage.

## Risks
- Process-local custody: caller holds the sealed suffix; verify() detects but cannot prevent substitution of both data and boundary.
- Time axis is presentation PTS (capture clock unverified): fine for scale-free extrapolation, not physics.
- Cross-vendor review of the S12 gate path still required. Controller must decide how to record the duplicate run (01a18967 also reported DONE).

Communication: one nonterminal blocker message + one completion line to controller (both authorized). No canonical controls edited.
