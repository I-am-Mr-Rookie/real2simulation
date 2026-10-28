# Swarm extension — Oct29 00:00 to00:30 Dhaka

Owner explicitly extended maximum-speed swarm work to2026-10-28T18:30Z.
First extension clock18:00:51Z; baseline d5af52b,68/205. Same inline exception
and simulation-only S10/S11 scope; no expanded physical, spend or deployment gate.

## Result

**Four additional canonical leaves DONE: S10c,d,e,f;68 ->72/205.** Since the
original58 baseline this is14 new completed leaves, not a count of commits/tests.

- Pinned Apache-2.0 Rapier0.21.0 in a dedicated local simulator package/lock;
  native WASM executes real narrow-phase contacts against the exact RK4 state.
  Explicit timestep/geometry/physics; immutable common time-series stops at first
  contact. No independent-world timestamps, hidden gravity defaults or fabricated
  contact labels. This is a sampled detector, not post-contact rebound dynamics.
  It currently handles an axis-aligned synthetic floor and sphere, not arbitrary
  scene collider reconstruction; coarse-step tunneling is not ruled out.
- Free-fall and projectile both run through the real common contact adapter.
- Ramp and nonlinear pendulum reuse RK4 and actual S08 validated setup export.
  Ramp stops before the first endpoint-crossing bracket and rejects unsupported
  static/stalling regimes; derived geometry is checked finite.
- Browser-capable WebCrypto replay canonicalizes JSON, rejects unsafe data,
  clones before freezing and verifies trace/replay hashes. All four actual engines
  pass repeated trace/hash tests. Seed binds identity; noiseless physics does not
  change just to manufacture apparent randomness.
- Mystery-g public DTO uses allowlisted observations, hides private setup/seed/g,
  and reveals an observation-bound sanitized actual S11 quantity with simulated
  provenance/uncertainty. The handoff factory is a trusted tool-producer boundary,
  not authentication; shape validation alone cannot prove scientific provenance.
- Offline CLI now connects actual S08 factory/validation -> Node simulator ->
  light-gate/ruler observations -> actual S11 fitter. Invalid setup never enters
  the simulator; cross-process vectors/time/source and successful quantities are
  checked. Honest fitter errors remain data; instrument uncertainty is not
  propagated by the conditional iid fixed-clock/scale fitter.

## Verification

Exact commands/logs and machine-readable four-template results: verification/.
Fresh main: lab5/5, combined Node68/68, fitter19/19, instruments10/10 PASS.
Last narrow replay-version rejection + both real ballistic contact runs7/7 PASS.
The0.5% analytic threshold is unchanged; max relative position error is pendulum
0.0002664499123 (0.026645%), at justified small-angle amplitude0.05rad. Other three
authored cases are near floating-point precision. Actual S08 oracle results,
declared characteristic normalization and trace/replay SHA256s are retained.
One authored case per template is not exhaustive domain or full Gate P acceptance.

Initial DONE claims were rejected and corrected: disconnected Rapier clock/state,
gravity default, missing contact boundary checks, ramp overshoot/stall semantics,
fabricated fitter-shape/measured label, weak public blacklist, mutation/getters,
unsupported replay versions, and broken inline Python test. Fresh evidence, not
self-reported DONE, drove acceptance. Review is local Sol, not other-vendor R-P.

## Incomplete / boundaries

**S10g remains PARTIAL**: the redacted contract works, but actual viewer/toggle is
still unwired. S10h/i/j and required R-P are not marked DONE from numeric sidecar
evidence. Whole S10 and real-scene integration remain unfinished. Physical Gate M
NOT_MET_INPUT_READINESS, physics NOT_RUN, S12 locked; S05b/S07b still PARTIAL.
Plain Python health missingpsycopg from the previous window remains unverified;
no dependency installation just to conceal that error. No browser/hardware E2E,
actual calibrated-g, production/deployment/publication/model invocation or spend.
Previous Claude-route ECONNREFUSED is not bypassed or silently reclassified.
Historical2.85/30 reservations unchanged; exact charge unknown, no new reservation.

## Method / communication

Applied Ponytail full: reuse validator/RK4/oracles/instruments/fitter, one pinned
physics package rather than a new collision implementation, stdlib CLI and small
actual integration tests. Disjoint managed worktrees; parent alone serializes
controls/lock/FF integration. No unrelated owner PDF/private file changed/staged.
OpenCodex-managed; not polled. Exact backend usage/cost unknown. Worker clocks
remain full1800s; approved owner-stop receipt is explicit, no backdating accepted.
An early reviewer PARTIAL with invalid future timing was returned for correction,
not accepted as completed review. Silent work except mandatory initial extension
update and concrete coordination. No implementation started after18:25UTC.

Final verification/control/cleanup continues to the18:30UTC owner boundary, with
no dispatcher, schedule or automatic continuation. Further work needs owner scope.

Final local review FF5cdd684: reported findings re-reviewed/closed within the
synthetic scope; all four actual timeboxes PASS and all reports tracked on main.
No open P1/P2 reported by that reviewer; it does not certify R-P/vendor or UI.
Three managed extension worktrees were archived recoverably; native archive
refused the primary review checkout, retained without deletion/bypass. Source
manifest covers19 changed Build/contracts/tests files; C0-control audit is clean.
