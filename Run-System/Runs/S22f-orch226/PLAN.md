# S22f-orch226 PLAN

- Objective: judge Gate D rehearsal evidence (S22b-e, S15ay) and prioritise defects; read-only (no product code, deploy, accounts).
- Owns: evidence/qa/claude/S22f-GATE-D-JUDGEMENT.md; Run-System/Runs/S22f-orch226/{PLAN.md,TIMEBOX.json,REPORT.md}.
- Model: anthropic/claude-opus-5-5/high (CLAUDE lane); OpenCodex-managed, not polled.
- Window: issued 2026-10-31T16:11:14Z, cutoff 16:36:14Z, deadline 16:41:14Z.
- Checks: (1) every Gate D criterion (GATE_D_PROTOCOL 2.x/3.x) gets MET/NOT MET/PARTIAL with an exact evidence line cross-checked against RUN.md + source; (2) P2-1 decision with smallest honest change; (3) prioritised P1/P2/P3 list with lane + fix row; worker_timebox check PASS.
