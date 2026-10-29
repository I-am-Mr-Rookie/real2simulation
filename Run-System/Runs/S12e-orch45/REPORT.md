# S12e-orch45 REPORT — DONE (Gate RS NOT_MET: measured shortfall)

Lane CODEX-1, step S12; assigned anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Worker only, branch run/S12e-orch45
from main 1e052d4, worktree .worktrees/S12e-orch45. Issued 21:40:47Z, UTC start 21:41:13Z, work stopped 21:50:34Z (deadline 22:10:47Z).
Tokens: unknown (not observable). Modal: 2 jobs, retries 0, billed $0.0528 total (read-only, may still accrue). No Meta/AWS/other spend.

## Result (scale-free, Gate M NOT_MET; no calibrated/physical claim)
evidence/S12/gate-rs/gate-rs.json: **Gate RS NOT_MET, median undefined (2 of 3 categories unscored)**.
| category | clip | scored / sealed | normalized RMS (|dy|/H) | first-5 diag | status |
|---|---|---|---|---|---|
| projectile | ST03 | 7 / 466 (1.5%) | **19.8%** (max 33.3%) | 13.3% | shortfall (> 5% and coverage < 80%) |
| bounce | BN01 approved | 0 | — | — | shortfall: not tracked |
| pendulum | PD02/03/04/06 approved | 0 | — | — | shortfall: not tracked |

Projectile cause (measured): apple is on the ground from f77 (obs y 0.817 -> 0.800, small rebound) while the committed ballistic
prefix fit has no floor (pred 0.828 at f77 -> 1.133 at f83, leaves image at f81). ST03's sealed suffix holds essentially NO free
flight: f77 is the impact frame, so this clip cannot pass a ballistic Gate RS regardless of tracking coverage (input for S12f/R-RS).

## Metric + integrity (PLAN.md, committed 81996b0 21:44:10Z, before the scored job2 launched 21:46:40Z; job1 launched 21:43:19Z, returned no observations)
- Per clip RMS over sealed suffix frames of |y_pred - y_obs| in image-height fractions; frames without observation excluded and
  reported; coverage < 80% => shortfall; gate = median over 3 categories, any unscored category => NOT_MET. No synthetic substitution.
- Build/real2sim/score.py `score()`: boundary.verify(prefix, sealed identities) + predict.check + sha == committed sha +
  suffix_identity match, THEN calls the observation loader (tests prove the loader never runs on tampered seal/sha/trace).
  Per-row PTS must equal sealed PTS within 1e-6 s.
- Prediction scored = S12c committed sha c81e0f94... (git 8cf86ab 21:32:56Z, before any tracking); regenerated from the errata
  record and required to match.
- Observations: Build/pipeline validate_segment (OK) on obj 2 of job2, PTS from presentation-map. Prefix re-track agrees with orch14
  within 0.00045 H (identity check).

## Modal jobs (ledger evidence/S12/gate-rs/gpu-ledger.jsonl; standing auth GPU-AUTHORIZATION.md; ST03 approved)
1. ap-cKH0R4xXlsZqus6i4Sk7wY ST03 f58-542 "apple" obj 2 --masks: add_prompt found 3 objects, then **CUDA OOM** on A10G (24 GB) in
   propagation; 0 stream frames. Billed $0.02947895 (ST03-f58-542-cost.json). result.json kept (error only, no masks).
2. ap-2Sbu8Pen5jJhHlNxAhuva6 ST03 f58-83 (26 frames; orch14 19 frames peaked 17.1 GB): tracked, peak VRAM 19.09 GB, remote 48 s.
   Billed $0.02330591 (ST03-f58-83-cost.json). result.json 157 KB (COCO RLE masks; no media).
Containers: [] before job1 (containers-before.json); after job1 only another worker's app ap-I8ur... (stopped 21:46:11Z, not this run);
before job2 another worker's s06d-scene-job pending (not this run); after job2 [] (containers-after-job2.json). billing-post.json = read-only report.
Not used: 2 of 4 jobs, ~$1.45 of $1.50 — further ST03 segments cannot change the outcome (coverage and error only grow);
bounce/pendulum strict path (prefix job -> committed prediction -> suffix job) needs 2 jobs each plus sourced restitution/floor and
angular-frequency records that do not exist, and ~26 contiguous frames/job (0.11 s at 240 fps BN01; 0.9 s at 30 fps PD) is far
below one bounce arc / pendulum period. Spending to "attempt" would be appearance work.

## Changes (Owns only)
- Build/real2sim/score.py (new): score, gate, st03_observations, main -> evidence/S12/gate-rs/gate-rs.json (byte-stable on rerun).
- tests/prediction/test_score.py (new): 4 tests (loader-after-checks, tamper/uncommitted never reads suffix, PTS mismatch/coverage/RMS, gate needs all categories).
- evidence/S12/gate-rs/*: results, logs, ledger, cost, containers, billing; evidence/S12/tests-prediction-S12e.txt.

## Fresh checks (Python 3.14.5, this worktree)
- `python -m unittest discover -s tests/prediction -v` -> 30 OK (26 prior + 4). Needs gitignored junction Build/simulator/node_modules
  -> canonical (same as S12d; not committed; first run without it: 2 pre-existing simulator tests failed on missing node deps).
- `python -m unittest tests.pipeline.test_gpu_stages` -> 6 OK (called, not edited).
- `python -m Build.real2sim.score` twice -> identical gate-rs.json (SHA256 F4037BB0...).

## Finding outside Owns (not fixed)
Build/pipeline/gpu_stages.validate_segment assumes stream/mask indices equal record source frame indices; modal_track emits
segment-relative 0..n-1, so any segment with --first > 0 is rejected. score.py maps relative k -> frame_map[k] before calling it.
Owner: pipeline lane.

## Ponytail (full)
- Reused: S12a split/verify, S12c projectile/check/st03_record (errata PTS), committed prediction JSON, Build/pipeline validate_segment,
  modal_track.py unchanged CLI, Build/gpu/cost_log.py reconcile, presentation-map PTS; stdlib statistics/json only.
- Smallest complete: one module + one test file; loader callback is the whole "read-after-verify" mechanism.
- Skipped: extra ST03 segments/re-association, BN01/PD tracking, pendulum w fitting, overlay rendering, JSON Schema.

## Risks / next
- Gate RS has 1 measured data point; S12f must show >10% honestly (limits demo prediction to virtual lab per QUEUE) unless a clip
  with free flight in its suffix and a memory-chunked tracker exist. R-RS should review score.py ordering + the 80% coverage rule.
- Billing may still accrue; latest read wins.
Communication: one completion line to controller (authorized). No canonical controls edited; no merge.
