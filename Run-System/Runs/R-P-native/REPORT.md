# R-P-native REPORT — PARTIAL-REVIEW-COMPLETE (Gate P not passed)

- Lane/model: CLAUDE lane; native Codex `anthropic/claude-opus-5-5` medium as issued (route not independently re-verified in-session). Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable).
- UTC: issued 2026-10-28T18:58:07Z, start 18:58:37Z (first clock read). Branch run/R-P-native from main f409018.
- Owns touched: evidence/reviews/R-P-native/ (FINDINGS.md, 3 repro scripts + outputs), Run-System/Runs/R-P-native/ (PLAN, REPORT, TIMEBOX). No implementation/control/config/peer file edited.

## Result
Full findings: [FINDINGS.md](../../../evidence/reviews/R-P-native/FINDINGS.md).
- P2-1 contacts.mjs:36-38,73-75 — speculative-manifold contact: reported contact 14.5 mm above floor, -2.4 ms early, non-convergent with dt; contactDist<=0 filter also non-convergent (+6.6..+17.6 ms). Gate-p b5d674a "zero spread / no jitter" is this bias, not stability.
- P2-2 contacts.mjs / contact-runs.mjs:7 — no per-step displacement guard: dt 0.1 tunnels to y=-17.62 m with no contact and no fallback.
- P2-3 lab-service 11f3159 session-bridge.py:31-36,68 — Mystery-g private g fixed 9.81/seed 42 for every session; DTO itself does not leak.
- P3: shape-only "actual S11" wording (mystery-g.mjs:12); unavailable-branch False defaults (gate-p acceptance.py:359-363); shared abort/no tree kill (session-service.mjs:16,35); pendulum 3 ms half-period margin (session-bridge.py:58); zip truncation (regression.py:74).
- Sound: RK4/integer horizon/sample time; 4-template regression at unchanged 0.005 (max rel 2.66e-4 pendulum); small-angle honesty; ramp positive-acceleration-only; WebCrypto canonical replay on real engines; route prod-deny/loopback/same-origin/body cap/TTL/capacity; UI strict reveal + stale guard; simulated labels.

## Fresh checks (run, this checkout)
- `npm ci --no-audit --no-fund` in Build/simulator (existing lock, no manifest change).
- `node --test` tests/simulator/*.mjs tests/lab/*.mjs → 28/28 pass. (Directory form `node --test tests/simulator/` fails on Windows; not a code failure.)
- `python -m unittest tests.lab.test_pipeline tests.lab.test_regression tests.simulator.test_s10_adapter` → 7 OK (pytest absent).
- `python -m Build.lab.regression` → passed true.
- 3 repro scripts run; outputs saved beside them. Peer files read only (not run): lab-service, lab-ui, gate-p acceptance.

## Ponytail (full) applied
Reuse: repros import existing trajectories/contacts modules and the pinned Rapier; no new deps, no source copies. Smallest change: review-only, fixes recommended as narrow edits (geometric same-sample bracket; displacement guard; seeded private g or honest label). Skipped: browser/UI run, Python service end-to-end start/fit, gate-p acceptance rerun, Rapier internals of why contactDist lags. Risk: contact timing claims stay unsupported until P2-1/P2-2 fixed and re-reviewed.

## Communication
Silent; no other-chat messages; single final pointer line. Parent integrates; final re-review at main 1650652 plus canonical uncommitted controller diff: see FINDINGS Addendum. P2-1/2/3 remain open; no Gate P pass claimed.


## Final (19:20Z)
All three P2s are resolved in the parent's uncommitted canonical fixes, verified by fresh runs; see the FINDINGS Addendum 2. The P3 about acceptance 'jitter' semantics and the stale acceptance.json remain. The fixes are not yet committed to main; no Gate P pass is claimed by this review.
