# S12f-orch97 REPORT — DONE

- Lane/model: CODEX-1, anthropic/claude-opus-5-5 high. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable); $0, offline, no GPU, no installs.
- UTC start 2026-10-30T06:49:37+00:00 (issued); work stopped 2026-10-30T06:53:22+00:00. Base main 83143a8; branch run/S12f-orch97.
- Inputs: S12e Gate RS NOT_MET (evidence/S12/gate-rs/gate-rs.json), R-RS RECHECK4 CLEAR (incl. P3 H1 trusted-registry limitation), Gate M NOT_MET, owner Q15=A scale-free normalized error.

## Result
- Code-owned decision [Build/real2sim/fallback.py](../../../Build/real2sim/fallback.py): re-runs `score.gate` on stored clip scores (raises if it disagrees with stored result), then `decide(median)`: <=0.05 SHOWN; (0.05,0.10] SHOWN_WITH_ERROR; >0.10 or unmeasured (null/NaN/neg/non-number) VIRTUAL_LAB_ONLY + WITHHELD.
- Current: **VIRTUAL_LAB_ONLY, real-scene prediction WITHHELD, error unmeasured** (Gate RS NOT_MET, median null; ST03 7/466 diagnostic only).
- Labels per output in [evidence/S12/S12f-fallback.json](../../../evidence/S12/S12f-fallback.json): ST03 overlay = "REAL CLIP - PREDICTION WITHHELD", trace simulated, observations measured (image-derived), error unmeasured, SCALE_UNVERIFIED, limits verbatim; synthetic pendulum = SYNTHETIC / VIRTUAL_LAB / SCALE_UNVERIFIED.
- Review packet: [evidence/S12/S12f-REVIEW-PACKET.md](../../../evidence/S12/S12f-REVIEW-PACKET.md).

## Files
Build/real2sim/fallback.py (new); tests/prediction/test_fallback.py (new, 6 tests); evidence/S12/S12f-fallback.json; evidence/S12/S12f-REVIEW-PACKET.md; Run-System/Runs/S12f-orch97/{PLAN.md,TIMEBOX.json,REPORT.md}.

## Checks (fresh)
- `python -B -m Build.real2sim.fallback` -> `S12f decision=VIRTUAL_LAB_ONLY real_scene=WITHHELD gate_rs=NOT_MET median=None gate_m=NOT_MET`.
- `python -B -m unittest tests.prediction.test_fallback` -> 6 OK (thresholds incl. exact 0.05/0.10 edges, >10, null/NaN/inf/neg/bool/str, insufficient coverage via score.gate, labels, live evidence).
- `python -B -m unittest discover -s tests/prediction` -> 50 run, 48 pass, 1 fail + 1 error: both test_params simulator tests; worktree lacks node_modules/@dimforge/rapier3d-compat (Test-Path False). Same pre-existing prerequisite recorded by R-RS recheck4 / S12e-orch45; not installed per contract.

## Ponytail (full) applied
- Reused score.gate/THRESHOLD/CATEGORIES (no duplicate eligibility logic), boundary GATE_M/LIMITS verbatim, existing SCALE_UNVERIFIED label convention (Build/library), existing overlay outputs. One small module + one test file; stdlib only.
- Smallest complete: sidecar labels keyed by output path+sha256 instead of editing reviewed overlay/prediction evidence or contracts/overlay (not owned).
- Skipped: UI wiring (no Build/web consumer of ST03 overlay exists today — rg found none), per-category gating, overlay contract change.

## Risks / limits
- Labels are not embedded in overlay documents; a future UI consumer must read S12f-fallback.json (flagged in packet).
- Inherited R-RS H1 (P3): trusted registry writers can forge admission; fallback adds no new boundary.
- Simulator-dependent prediction tests unverified in this worktree (missing rapier).
- Communication: silent; one completion line to controller as authorized.

Next: cross-vendor review of the packet; controller integration.
