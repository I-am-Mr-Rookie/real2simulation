# R14-simulator-audit — DONE (bounded audit, NOT product pass)

**Three concrete defects frozen. No product edits.** New focused suite: **11 pass, 6 fail**, the six failures representing three root causes. The unchanged analytic threshold remains **0.005**. Controller-owned fixes/review remain necessary; this report does not reopen physical Gate M, S12 or real-scene work.

## Contract and provenance

- CODEX-1, assigned managed `gpt-6.1-sol/high`; runtime model identifier/effort not independently exposed. No model/routing/configuration change. Coding quota: **OpenCodex-managed; not polled**. Tokens/cost unknown; no paid operation.
- Worktree: `C:/Users/HP/.codex/worktrees/swarm14-simulator-audit/2026-10-26 - Meta Global AI Developer Hackathon`; branch `run/R14-simulator-audit`, reviewed base `74c886f9b2cc1322dde152f5be5813f813904bc6`. Initially clean; parent main untouched; no merge/rebase.
- Original issue **2026-10-28T21:29:07.000Z**, actual intake **21:29:21.4015305Z**; original cutoff **21:54:07Z**, deadline **21:59:07Z / Oct29 03:59:07 Dhaka**. Actual work stop/report times: [TIMEBOX.json](TIMEBOX.json). Verified bounded DONE may finish early; no unfinished owned implementation is being relabelled.
- Parent project `91e441f8-e40c-4ec4-bea2-de7fa1582d97`, Meta AI Hackathon, canonical event root inherited from the handout. One-time inline exception applied; child UI binding not independently verified.
- Current canonical AGENTS/STATE/QUEUE/timebox policy and R10-S10-audit, R10-S10-fix, R11-browser-gate reports informed scope. The known contact fixes and existing 15-case acceptance suite were inspected, not ceremonially rerun.
- Controller refinement applied: RK4/analytic/domain/step-size audit only. Replay source had already been read before refinement; no independent replay audit/test/change followed. Dedicated replay worker retains that objective.

## Findings

### P2-1 — valid amplitude-boundary pendulum exceeds the analytic gate over four seconds

**Source:** `Build/simulator/extended-templates.mjs:84,87-88`; the dynamics use `sin(theta)` but advertise `small-angle-linearized` whenever amplitude <=0.1, without a horizon restriction. S08's accepted oracle is linear (`Build/templates/pendulum.py:16,80-84`).

**Exact input:** length=1 m, gravity=9.81 m/s², initial angle=0.1 rad, angular velocity=0, dt=0.001 s, duration=4 s, origin=[0,2,0]; actual S08 export, 4,001 samples. Complete spec/scene and Python oracle are frozen under `pendulum-amplitude-boundary` in [validated-cases.json](../../../../evidence/S10/numerical-invariants/validated-cases.json).

- At t=3.531 s, observed position **[0.005691139062496376,1.000016194663048,0]**, independent linear-oracle position **[0.006379860466847602,1.0000203515168802,0]**. Python's actual oracle at that exact time is frozen and matched independently by the test.
- Maximum error / (length × amplitude) = **0.006887339488113734 = 0.6887339488%**, exceeding unchanged **0.5%**. Expected: <=0.005 throughout the accepted comparison horizon.
- Halving dt to 0.0005 gives **0.006887339479846007**; common-time angular traces differ by <1e-10. Smaller RK4 steps do not remove the discrepancy.
- Independent energy-integral quadrature (Simpson, 8,192 panels; not RK4) gives nonlinear period **2.00732119117531 s**, versus the linear oracle's **2.006066680710647 s**. This supports accumulated model/phase mismatch, not an integrator step-size defect.

**Controller action:** reconcile accepted pendulum dynamics/reference semantics without loosening 0.005 or adjusting the frozen oracle to current output. This audit does not select or implement a new model policy.

### P2-2 — valid positive-acceleration ramp is rejected as stalled after cancellation

**Source:** `Build/simulator/extended-templates.mjs:70-73` distributes gravity across the two opposing terms before subtraction; the S08 oracle uses `g*(sin(angle)-mu*cos(angle))` at `Build/templates/ramp.py:11-12`.

**Exact input:** gravity=1.62, length=1, angle=0.7, friction=0.8422883804630792, initial speed=0, dt=0.001, duration=0.2, origin=[0,0,0]. Actual `validate_setup` export **and** `analytic_ramp` accept it.

- S08 positive acceleration: **1.7985612998927537e-16 m/s²**; last oracle distance **3.597122599785508e-18 m**.
- Simulator computes exactly **0**, then throws `INVALID_EXTENDED_TEMPLATE: ramp acceleration must be positive...` before producing the valid trace.
- Independent 100-digit Decimal Taylor sin/cos using the **exact binary64 input values** gives **2.26640735539990863771410435558…e-16 m/s²**, strictly positive. This is a genuine supported downhill input, not a truly stalled ramp accidentally admitted by S08.
- Expected: preserve the accepted positive domain / do not misclassify it as a stall. The frozen regression asserts successful positive motion, not a fabricated minimum acceleration.

**Controller action:** repair cancellation/domain consistency at the shared ramp boundary. S08's tiny positive value is itself ill-conditioned; this audit does **not** certify its relative acceleration accuracy or permit threshold relaxation.

### P3-3 — unscaled RK4 slope sum overflows although every stage and final answer are finite

**Source:** `Build/simulator/rk4.mjs:14` adds weighted unscaled derivatives before multiplying by dt.

**Smallest counterexample:** `rk4Step([0], 2**-1030, () => [5e307])`. All derivative/stage values are finite; exact constant-derivative answer is **0.004345847379896878**. The sum has magnitude `6*5e307`, overflowing before the tiny multiplication, and the function throws `INVALID_RK4: state became non-finite`.

The same root cause is reproduced through three **actual validated artifacts with finite analytic answers**, not just a generic solver call:

- dt=`2**-1030` = **8.691694759794e-311**, duration=8×dt = **6.953355807835e-310**, gravity=**5e307**, origin=[0,0,0]. Exact binary eight-step horizon avoids conflating this with decimal/subnormal ratio rounding.
- Free fall: drop height=1e-308, initial vy=0; projectile: launch height=1e-308, vx=1. Both finite oracle endpoints have y=**-1.208728924759e-311**, vy=**-0.03476677903917502**.
- Ramp: length=1e-308, angle=1.4, friction=0, initial speed=0; finite oracle distance=**1.191141592533e-311**.
- All three are rejected at the first RK4 step. Expected: executable finite trajectory for accepted representable inputs, or a consistent preflight representability contract—not accidental unscaled intermediate overflow.

**Priority caveat:** extreme synthetic scales, not physically realistic current lab presets; fail-closed rather than silent wrong physics. Controller owns any arithmetic repair; retain stage/result validation.

## Bounded clean evidence

Ten **new** valid-domain controls pass, distinct from the existing 15-case matrix: fast downward fall, traversal through upward apex, minimum-normal gravity, high-horizontal-speed projectile, very-low-gravity projectile, shallow/near-vertical ramps, ramp friction >1, signed pendulum phase with initial angular velocity, and the pendulum frequency-step boundary. Checks include exact sample/time indexing, all-sample independent positional reference, ballistic velocity including subnormal arithmetic, pendulum fixed length/tangency, and stable nonlinear energy conservation.

Frequency preflight at length=0.01, gravity=9.81: dt immediately below **0.0015963771420352524** and exactly at it are accepted; immediately above is rejected with `time_step under-resolves pendulum frequency` (`contracts/experiment/validate_experiment.py:241-242`). Accepted boundary RK4 case passes the independent short-horizon checks. This is bounded evidence, not an exhaustive domain proof.

## Reproduce / evidence

Evidence root: [evidence/S10/numerical-invariants](../../../../evidence/S10/numerical-invariants/).

| Command | Fresh result / artifact |
|---|---|
| `python evidence/S10/numerical-invariants/generate-cases.py --check` | 16 actual authoritative exports/oracles exactly match frozen inputs; `fixture-verification.json`. |
| `python evidence/S10/numerical-invariants/generate-cases.py --precision` | Positive high-precision independent ramp acceleration; `precision-reference.json`. |
| `python evidence/S10/numerical-invariants/generate-cases.py --boundary-check` | Below/at accepted, next representable step rejected; `frequency-boundary.json`. |
| `node evidence/S10/numerical-invariants/observe.mjs` | Actual outputs/errors and nonlinear-period quadrature; `observed.json`. |
| `node --test --test-reporter=tap tests/simulator/r14-invariants.test.mjs` | **Exit 1: 17 tests, 11 pass, 6 fail, 0 skipped/todo.** Intentional red counterexamples, not a green product claim; `invariants-red.tap`. |
| `git diff --check`; owned-path/staged review; timebox checker | Final results saved in `FINAL-CHECK.txt`; no Build/contracts/product diff. |

Node v24.18.0, Python 3.14.5. A failed exploratory long-pendulum control initially exceeded the conservative scene envelope (pivot y=2, length=3); its pivot was moved to y=4 **before** freezing it as a valid control. An exploratory decimal subnormal duration/step ratio was rejected by the existing integer-horizon check; exact binary steps isolate the RK4 defect. Neither exploration changed an oracle or acceptance tolerance.

## Ponytail full/default applied; limits and handoff

- Read requested installed full skill. Reused actual `regression_case`, S08 exporter/oracles, existing RK4 consumers, Node test runner and Python/Node standard library. No dependency installation, Rapier junction, copied validator, product wrapper or new feature.
- Smallest complete audit change: one focused test file, exact synthetic fixtures and small reproducible evidence scripts. Scalar RK4 counterexample isolates the shared cause; three artifact tests prove consumer reach. No broad legacy-suite repetition or contact/UI/replay re-audit.
- Owns only the run directory, `evidence/S10/numerical-invariants/`, and `tests/simulator/r14-invariants.test.mjs`. Commit only these paths; no canonical controls, main merge, installs, environment/secrets, network/model/GPU jobs, deployment, publishing, accounts or terms.
- No owner question needed. Controller must triage/fix the three findings and obtain any required vendor review. **Do not call Gate P numerically clean from this audit.** Physical Gate M/S12 remain locked.
- Communication: mandatory developer initial update, skill announcement and material-finding update only; no fanout, other-chat messages or optional repeated summaries. One final report-pointer line.
- Skipped: exhaustive scales/horizons, contact response, browser/rendering, replay record validation (dedicated worker), fitter, whole-suite/build/deployment and real footage. Residual risks are the three unfixed defects plus untested domain combinations.
