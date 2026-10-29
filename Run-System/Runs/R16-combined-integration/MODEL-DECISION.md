# Accepted model / frozen-diagnostic decision

Controller accepts the existing S08 declared small-angle linear ODE, not a different finite-angle physics model. Native reviewer R15-combined-gate independently agrees on pinb37f7b8 with noP0-P2.

The two frozen R14 controls `control-pendulum-frequency-step-boundary` and `control-pendulum-negative-phase` impose the nonlinear-energy invariant on this linear ODE. Their nonlinear-energy assertions are superseded as acceptance requirements **only for the declared small-angle-linearized domain**. Their original inputs, tests, output and failures are retained unchanged: frozen15/17 is not called green. This is an explicit model-compatibility judgment, not a tolerance change or deletion of unfavorable evidence.

Independent derivation, accepted S08 source, unchanged analytic oracle and0.005 threshold, linear-invariant checks and nonlinear-only checks remain binding. Along theta''=-(g/L)theta, the nonlinear energy derivative is gL*omega*(sin(theta)-theta), generally nonzero; the quarter-period ratio is A²/(4sin²(A/2)). New recovery checks validate this derived mismatch as well as the correct linear invariant. No shortened horizon, forced covariance validity, physical accuracy claim, or gate relaxation follows.

RK4 normalized arithmetic legitimately changes some binary64 traces. Prior stored replay records are not silently rewritten or reauthenticated. Only derived browser server-trace fixtures may be regenerated from immutable inputs after independent analytic checks. Hash consistency remains distinct from authentication. This decision does not establish a real-surface builder or physical Gate M/S12.
