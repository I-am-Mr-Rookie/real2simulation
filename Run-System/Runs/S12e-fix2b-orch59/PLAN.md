# S12e-fix2b-orch59 PLAN

Issued 2026-10-30T03:46:18Z; deadline 04:16:18Z (Dhaka 10:16:18); minute-25 cutoff 04:11:18Z.
Model anthropic/claude-opus-5-5/high (CODEX-1 lane); OpenCodex-managed, not polled.
Branch run/S12e-fix2b-orch59 from run/S12e-fix2-orch56 (3591656 WIP), rebased on main 93b679d.

Objective: close R-RS RECHECK F1-R (v2 commitment binding kind/model/trace/clip/source sha/training/suffix
seal+count; v1 legacy-audit only) and F2-R (gate eligibility from independent clips.csv + APPROVAL.md +
S02c registry receipt; fail closed), with regressions; regenerate gate-rs.json unchanged NOT_MET.

Owns: Build/real2sim/; contracts/overlay/; tests/prediction/; evidence/S12/; Run-System/Runs/S12e-fix2b-orch59/.

Acceptance: (1) tests/prediction green incl. metadata-relabel (clip, training) and three nonpublic
synthetic image-derived fixtures -> shortfall; (2) reviewer reproduce.py replayed read-only -> refusals;
(3) gate-rs.json regenerated, measured fields unchanged, NOT_MET, Gate M NOT_MET.
