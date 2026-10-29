# S12d-orch43 PLAN

Objective: pendulum continuation prediction (prefix-only, scale-free image units) + versioned overlay
contract tying immutable predicted traces to clip id, source sha and PTS frame timebase; validator rejects
misaligned clip/timebase or mutated trace. Gate M NOT_MET everywhere; no UI, no GPU/Modal/Meta.

Owns: Build/real2sim/; tests/prediction/; evidence/S12/; contracts/overlay/ (new); Run-System/Runs/S12d-orch43/.

Steps: (1) predict.pendulum reusing S12c _identities/_seal and the linearized solution of
Build/templates/pendulum.py; (2) contracts/overlay validate.py + CONTRACT.md; (3) Build/real2sim/overlay.py
builder + main (ST03 real projectile overlay with errata/presentation-map timebase; SYNTHETIC pendulum);
(4) tests/prediction/test_overlay.py; (5) evidence + REPORT + TIMEBOX.

Acceptance: predictions and frames aligned by clip/timebase (validator); renderer consumes immutable traces.
