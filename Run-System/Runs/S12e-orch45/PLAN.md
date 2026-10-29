# S12e-orch45 PLAN — Gate RS on public motion clips

Lane CODEX-1, step S12; anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Issued 2026-10-29T21:40:47Z,
deadline 22:10:47Z (Dhaka 04:10:47 Oct30), minute-25 cutoff 22:05:47Z. Branch run/S12e-orch45 from main 1e052d4.
Owns: Build/real2sim/; tests/prediction/; evidence/S12/; Run-System/Runs/S12e-orch45/.

Objective: score sealed, pre-committed held-out predictions against tracked suffix observations; Gate RS = median of
per-category normalized errors (projectile, bounce, pendulum) <= 5%, else measured shortfall. Gate M NOT_MET everywhere.

## Pre-registered metric (written ~21:45Z, BEFORE any suffix observation exists locally)
- Positions are image-height fractions y/H (S12a boundary units; scale-free, Owner Q15=A).
- Per-clip error e = RMS over every sealed suffix frame of |y_pred - y_obs| (already /H) = "normalized error".
- Frames where the tracker has no observation are excluded and reported; coverage < 80% of the seal => that clip is a shortfall.
- Gate RS value = median over the three categories; a category with no scored clip is a measured shortfall and the gate is NOT_MET
  (no synthetic substitution). Diagnostic only (not the gate): same RMS over the first 5 suffix frames.
- Order enforced in code: boundary.verify(prefix, sealed identities) and prediction check (sha == committed sha) BEFORE the
  tracked suffix values are read; prediction sha must equal the one committed in git before tracking.

## Inputs / jobs
- ST03 projectile: committed prediction evidence/S12/prediction-ST03.json sha c81e0f94... (git 8cf86ab, 21:32:56Z), sealed suffix f77-542.
  One Modal job (<= $0.50): modal_track.py --clip ST03 --first 58 --last 542 --prompt apple --object-id 2 --masks; parse with
  Build/pipeline validate_segment + errata-fixed PTS (_pts fixed after orch14). Prefix f58-76 re-tracked as identity check vs orch14.
- Bounce (BN01) and pendulum (PD02/03/04/06): no existing prefix tracking, no sourced restitution / angular-frequency record;
  strict prefix-job -> commit prediction -> suffix-job needs 2 jobs each (> 4-job cap with ST03) plus object-id discovery.
  Planned outcome: measured shortfall unless time allows.
Budget: total <= $1.50, each <= $0.50, max 4 jobs, retries 0, containers [] before/after, ledger evidence/S12/gate-rs/gpu-ledger.jsonl.
