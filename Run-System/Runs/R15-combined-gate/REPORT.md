# R15-combined-gate REPORT — DONE (review only)

**Verdict: no P0/P1/P2 in the reviewed scope.** Pin `b37f7b8` (candidate `C:/Users/HP/.codex/worktrees/swarm12-covariance-fix/...`, clean, HEAD=b37f7b8) vs accepted base `1325ae9`. Build delta = 9 files: fitter api/core/README, lab/session-service, simulator replay(.mjs/.md), rk4, extended-templates, NUMERICS.md. Hash consistency is not authentication.

- Lane/model: CLAUDE, Opus 5.5 medium, existing desktop route (not Claude Code). Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable).
- UTC: issued 07:38:01Z; work start 07:38:10Z; stopped/reported 2026-10-29T07:44:08Z; deadline 08:08:01Z. Early finish = verified DONE for all 4 slices.
- Branch `run/R15-combined-gate` from 4452f92 (requirements report preserved). Owns only `Run-System/Runs/R15-combined-gate/`. No Build/test edits.

## Slice judgments

1. **S11l fitter (0e6227b)** — PASS. `_aic` = n(2 log scale + 2 log‖e/scale‖ − log n)+2k ≡ n log(RSS/n)+2k (300 random fits, deg 1/2, agree <1e-8 rel). Legacy `iid_fixed_clock_scale` path now `position_sigmas=(max σ,)*n` → sandwich floored by RSS/dof: 300/300 same validity as old `sigma=max(σ,√(RSS/dof))`, max rel variance diff 5.1e-16 ⇒ no noise inflation/coverage/tolerance/criterion change. Underflow case (residuals 5e-320): rss=0, rmse=2.39e-320>0, AIC finite, residual_variance_floor→None, `rss_status: underflow` ⇒ no false exact zero. `noise_model` label change is internal (not in API JSON).
2. **S10p replay (3897542)** — PASS. One detached frozen snapshot before first await; metadata validated before runner; getter-swap record rejected (`accessor property`). Base vs current `createReplayRecord` hashes identical for an ordinary JSON input; replay of JSON round-tripped record OK.
3. **S10q transport (c9fd7e1)** — PASS. StringDecoder handles split UTF-8; cap counts raw bytes; data after stop ignored; slot retained until `close`; sticky `stopped` unchanged. Latent P3 agreed (fixed producer ensure_ascii=True), not exaggerated.
4. **S10o numerics (b37f7b8)** — PASS with judgment below.
   - Pendulum: accepted S08 `Build/templates/pendulum.py:53` solves θ''+(g/L)θ=0 for amplitude ≤0.1. Making the RK4 dynamics follow the existing `small-angle-linearized` selector is the correct model; linear invariant L²ω²/2+gLθ²/2 is right. Checked derivation: E_nl(0)=2gL sin²(A/2), E_nl(T/4)=gLA²/2 ⇒ ratio A²/(4 sin²(A/2)) ≠1, so frozen nonlinear-energy ≤1e-7 assertion is incompatible with the linear model, not a hidden regression. Gate P oracle/0.005/fixtures untouched; no horizon restriction. Fresh run: `node --test r14-invariants + r14-recovery` → 42 tests, 40 pass, 2 fail = exactly `control-pendulum-frequency-step-boundary`, `control-pendulum-negative-phase` (claim honest; not a passing-frozen-suite claim).
   - Ramp: `g*(sin−μcos)` = same op order as `Build/templates/ramp.py:12` ⇒ preflight sign agrees with S08 reference; zero/negative still rejected, no epsilon.
   - RK4: overflow case `[0,1e308], dt .5, k=1e308` → new finite [5e307,1.5e308] (old [∞,∞]); subnormal step unchanged.

## P3 (non-blocking)

- **RK4 bit drift:** division by non-power-of-2 `scale` changes ordinary results: 4780/8000 steps differ from base formula, max rel 1.1e-11 (accuracy-neutral). Explains derived browser/server snapshot churn and invalidates any previously stored replay hashes of RK4 traces. Smaller-churn option: keep old expression when finite, fall back to normalized form only on overflow (or scale by power of two). Parent's call; regenerate only derived snapshots as stated.
- **Pendulum transparency:** output has no explicit integrated-dynamics field (selector doubles as comparison label); 0.1 rad threshold gives a small dynamics discontinuity (documented in NUMERICS.md). Controller should record the 2 frozen nonlinear-energy controls as superseded-by-decision rather than leave a permanently red suite without receipt.
- **Replay strictness:** `createReplayRecord({...,version: undefined})` and non-JSON extra keys now reject (base accepted). No in-repo caller affected (`Build/lab/replay-check.mjs`, internal replay call).
- Transport latent P3 as above.

## Ponytail (full/default) — applied
Verified installed `C:/Users/HP/.codex/.tmp/marketplaces/ponytail/skills/ponytail/SKILL.md` (52 lines, SHA256 F1800847…BCF32); read fully, not installed/altered. Applied: reuse — called existing `jacobian_covariance`, `_aic`, `rk4Step`, `createReplayRecord`, frozen test files and base module via `git show` instead of new harnesses; smallest complete check — 3 tiny scripts targeting each changed branch (legacy equivalence, underflow, overflow, getter, compat) + one targeted node test run; judged each fix for smallest root-cause change (ramp/pendulum one-line model alignment ok; RK4 flagged as larger-than-needed churn). Skipped: full builds/test suites already run by parent, browser consumer, Rapier, lab bridge end-to-end, README prose review, Mystery auth audit (out of scope). Risk: RK4 snapshot/hash churn; linear model is not finite-angle physics.

## Evidence (this dir)
`fitter_check.py` (output above), `rk4_bitcheck.mjs`, `replay_compat.mjs` + `base_replay_1325ae9.mjs` (git show of base). No physical Gate M/S12/deploy/GPU/network claims. Communication: silent; single final line.

