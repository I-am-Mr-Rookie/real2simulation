# R15-combined-gate PLAN

- Role: native Claude cross-vendor gate review (CLAUDE lane, Opus 5.5 medium, existing route; not Claude Code). Review only.
- Window: issued 2026-10-29T07:38:01Z, cutoff 08:03:01Z, deadline 08:08:01Z (14:08:01 Dhaka). Owner stop 10:00Z not crossed.
- Objective: independent P0-P3 review of Build source deltas 1325ae9..b37f7b8 (candidate checkout swarm12-covariance-fix): S10p replay, S10q transport, S11l fitter residual scale, S10o numerics.
- Owns: Run-System/Runs/R15-combined-gate/ only. No Build/test edits, no fanout, no install/network/GPU/deploy.
- Checks: read diffs; small targeted scripts (legacy covariance equivalence, AIC identity, subnormal RMSE, RK4 bit/overflow, replay compat); run frozen+recovery numerics test once.

