# S05f-fix-orch32 PLAN

Objective: fix R-R recheck D1/D2 (evidence/reviews/R-R/RECHECK.md) in Build/reconstruction/spike/gate_r.py with regressions; thresholds unchanged; real Gate R must stay FAIL with identical metrics.
Owns: Build/reconstruction/spike/; evidence/S05/S05f/; Run-System/Runs/S05f-fix-orch32/. Never evidence/reviews/ or canonical controls.
Model: anthropic/claude-opus-5-5 medium (OpenCodex-managed; not polled). CPU only, $0.
Checks: test_gate_r (new D1/D2 regressions + failing controls); reproduce_remaining.py now fails its defect assertions; real CLI rerun == committed GATE_R.json.
