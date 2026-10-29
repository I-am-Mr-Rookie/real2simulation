# R15-numerics — DONE (owned numerical recovery only)

**Three R14 root causes repaired and freshly verified; no full Gate P/product pass claimed.** The unchanged frozen suite remains **15 pass / 2 fail** solely because its two small-angle controls require the incompatible nonlinear energy invariant. This intentional model correction is independently justified below; neither frozen tests nor `0.005` were edited. Parent integration/review remains separate.

## Contract, interruption and timing

- CODEX-1, assigned existing managed `gpt-6.1-sol/high`; runtime identity/effort not independently exposed. **OpenCodex-managed; not polled. Tokens/cost unknown.** No paid operation or model/provider/policy change.
- Actual new issue **2026-10-29T07:23:40.000Z**, cutoff **07:48:40Z**, deadline **07:53:40Z / 13:53:40 Dhaka**; original new window exactly **1800 seconds**. Owner extension stop **10:00:00Z / 16:00 Dhaka** is later. Actual product work stop/report times are in [TIMEBOX.json](TIMEBOX.json); no R14 clock reused or backdated. Verified completion of this bounded scope permits early DONE.
- Worktree `C:/Users/HP/.codex/worktrees/swarm14-simulator-audit/2026-10-26 - Meta Global AI Developer Hackathon`; base `5ac5f2557422b15d161723aa23c2d0ab74fa95f8`; new branch `run/R15-numerics`, switched from `run/R14-simulator-fix` without reset. No main/shared-control edit, merge or rebase.
- Intake preserved all inherited edits: modified `extended-templates.mjs`, `rk4.mjs`, `extended-templates.test.mjs`; untracked `NUMERICS.md`, `r14-recovery.test.mjs` and `numerical-recovery/`. The initial patch/hashes/status are saved under the new evidence directory. Existing R14 evidence files remain intact at their original paths.
- Original R14-fix PLAN/TIMEBOX exist but have **no terminal report or actual work-stop receipt**. Its logs do not prove DONE or a truthful interruption time. The controller reports an actual usage-limit interruption and old handle `not_found`; these are inherited facts, not independently queried worker/runtime evidence. This run records only its own new observations; old timestamps/receipts were not altered.
- Canonical AGENTS/STATE/QUEUE/timebox policy, R14 audit/recovery plan and relevant R10/R11 reports read. Meta AI Hackathon project `91e441f8-e40c-4ec4-bea2-de7fa1582d97` inherited; child UI binding not independently verified. Canonical root remains `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`.

## Smallest complete changes — Ponytail full applied

Read the requested full installed skill. Grepped RK4 callers and inspected the accepted S08 sources, browser consumer and tests before extending inherited work. Reused existing APIs, metadata selector, stage validation, authoritative exporter, Node tests and Python standard library; no dependency, wrapper, copied validator or new model option.

1. **Pendulum:** inherited repair makes the existing `small-angle-linearized` selector solve `theta''=-(g/L)*theta`, matching accepted S08. Larger-amplitude `nonlinear-only` retains sine restoring force. No new horizon/amplitude restriction, fixture adjustment or threshold change.
2. **Ramp:** inherited repair computes `g*(sin(angle)-mu*cos(angle))` in S08's order. The valid tiny-positive case runs; represented zero/negative acceleration is still rejected. No invented epsilon or unsupported coasting regime.
3. **RK4:** inherited repair normalizes the final weighted mean before summing slopes, preserves tiny timesteps, and falls back when `dt*largestSlope` overflows but the weighted increment is finite. All actual intermediate states, derivatives and final results remain validated.
4. **Additional same-root arithmetic edge:** a fresh pure two-state dynamics test exposed `dt*k/2` overflowing before a representable half-stage (`dt=3`, slope +/-1e308). Added the smallest midpoint fallback `dt*(k/2)` only when the unhalved product overflows; do not halve subnormal slopes normally. New test was red before this edit, green after it, and verifies all four observed stage states.
5. Preserved the inherited overflow-test correction: place the ramp endpoint beyond the tested step so that it tests **actual position overflow**, not the now-repaired accidental slope-sum overflow. Added only two recovery tests and explicit numerical-model documentation beyond inherited recovery work.

## Independent energy justification — not a weakened oracle

Accepted `Build/templates/pendulum.py` and `Build/templates/README.md:119-133` explicitly specify linear angular dynamics and linearized energy. For that ODE, `E_lin=L^2*omega^2/2+g*L*theta^2/2` has derivative zero. The dimensionless invariant is `theta^2+(omega/sqrt(g/L))^2`.

The old diagnostic uses `E_nonlin=L^2*omega^2/2+g*L*(1-cos(theta))`. Along the **linear** ODE its derivative is `g*L*omega*(sin(theta)-theta)`, generally nonzero. Starting at angle A with zero velocity, exact quarter-period motion predicts `E_nonlin(quarter)/E_nonlin(initial)=A^2/(4*sin(A/2)^2)`, not 1. A new test checks this independently derived magnitude for signed amplitudes and two gravity/length pairs, while checking the linear invariant at every sample. It also preserves the existing nonlinear-only energy test. No diagnostic tolerance is relaxed; frozen nonlinear assertions remain unchanged and visibly fail.

Across the 16 frozen exported cases, fresh recovery observations give maximum relative position error **8.33247948876989e-8** versus unchanged **0.005**, maximum linear-energy drift **6.942274310972607e-9**, and maximum nonlinear-energy drift **0.0008337501654114288**. Values come from actual test output in `numerical-summary.json`; these are synthetic numerical observations, not measured physical results.

## Fresh verification

Evidence root: [evidence/S10/numerical-recovery/R15](../../../evidence/S10/numerical-recovery/R15/). Node **v24.18.0**, Python **3.14.5**.

| Check | Actual result / evidence |
|---|---|
| Inherited recovery baseline | **23/23 PASS**, `recovery-inherited.tap`; independently rerun, not accepted from old logs. |
| New midpoint + model-invariant tests before midpoint fix | **1 pass / 1 fail**, `missing-edge-before.tap`; finite half-stage regression is genuinely red. |
| Recovery suite after repair | **25/25 PASS**, `recovery-final.tap`; 16 unchanged all-sample references, scale/sign/subnormal/invalid-stage/ramp-boundary controls, long-horizon linear dynamics and both model invariants. |
| `node --test --test-reporter=tap tests/simulator/simulator.test.mjs tests/simulator/trajectories.test.mjs tests/simulator/extended-templates.test.mjs tests/simulator/mystery-g.test.mjs tests/simulator/r14-recovery.test.mjs` | **45/45 PASS**, `impacted-final.tap`; includes the 25 above, not an additional 25. |
| Unchanged `tests/simulator/r14-invariants.test.mjs` | **Exit 1, 15 pass / 2 fail**, `frozen-final.tap`; only `control-pendulum-frequency-step-boundary` and `control-pendulum-negative-phase`, both at the old nonlinear-energy assertion. All six original defect regressions now pass. |
| `python evidence/S10/numerical-invariants/generate-cases.py --check` | **PASS**, all **16** authoritative exports/oracles exactly match frozen inputs; `fixture-verification.json`. |
| `python -m unittest discover -s tests/lab -p test_regression.py` | **1/1 PASS**, actual four-template Python export -> Node simulator -> independent Python analytic comparison/replay check; `analytic-regression.txt`. |
| S08 pendulum/ramp unit suites, with existing tests/spec import path | **11/11 and 12/12 PASS**, `s08-pendulum.txt`, `s08-ramp.txt`. |
| Contact-inclusive exploratory impacted invocation | **45 pass / 1 module-loader failure**, `targeted-final.tap`; missing existing `@dimforge/rapier3d-compat`. No installation/junction or contact-success claim. |
| `node --test --test-reporter=tap tests/lab/browser-simulator.test.mjs` | **8 pass / 2 fail**, `browser-consumer.tap`; ramp/pendulum reach the unchanged frozen **server-trace snapshot comparison at line 29** after exact current engine/server parity assertions pass. Old snapshots differ from corrected dynamics/arithmetic. Not called green. |
| Frozen hashes / tracked diff / whitespace | Initial/final SHA256 match for the frozen test and validated cases; whole frozen evidence tree has zero Git diff. Authored source/test/docs/run files pass `git diff --cached --check`. Whole-index checking reports trailing whitespace in raw TAP/diff evidence; raw logs are deliberately preserved, not rewritten to hide diagnostics. Final scoped index/timebox checks saved with this report. |

## Parent handoff / limits

- Parent must integrate its instrument quantizer work, obtain required native independent review and actual IAB375 verification, and serialize main FF/heavy build. **No parent gate leaf or queue status was changed here.**
- Before calling browser consumer tests green, parent needs to regenerate and review `evidence/S10/browser-simulation/{ramp,pendulum}.server-trace.json` against these corrected models. Existing local `generate_fixtures.py` is the reusable generator (writes all four artifacts/traces and generation receipt); it was inspected, **not executed**, because those files are outside Owns. Frozen `numerical-invariants` must remain unchanged.
- Numerical limits: binary64 rounding/cancellation, fixed-step phase error at permitted frequency bounds, and discontinuous model choice at the existing 0.1-radian selector remain model/representation limitations. No exhaustive parameter-domain or arbitrary-precision guarantee. Near-zero ramp acceleration is physically ill-conditioned. The corrected small-angle model is not exact finite-angle physics.
- Skipped: absent Rapier contacts, exhaustive combinations, new fixtures outside Owns, full build, native/browser UI interaction, fitter/transport/replay recovery, model/GPU jobs, physical Gate M/S12, real scenes, deployments/publication/accounts/terms/auth/secrets/config. These are not silently claimed complete.
- Communication compliance: mandatory initial/skill update and two actionable nonterminal findings only; no optional chatter, fanout, other-chat messages or quota checks. Final response is one report-pointer line. No owner decision needed for these scoped repairs.
