# S14g-orch47 PLAN — Run Gate A fixture and thirty-turn suite

- Lane CODEX-1, assigned anthropic/claude-opus-5-5 high; base main 7fbf29f; branch run/S14g-orch47.
- Issued 2026-10-29T21:51:42Z; deadline 22:21:42Z; minute-25 cutoff 22:16:42Z.
- Objective: measure Gate A = >=9/10 valid specs and 0 invented numeric claims across 30 turns.
- Owns: Build/agent/; contracts/agent/; tests/agent/; evidence/S14/; Run-System/Runs/S14g-orch47/.
- Steps: (1) STATE follow-up: normalise question kind vs chips (no relaxation of number ban);
  (2) evidence/S14/S14g_gate_a.py: 10 understand->interview->spec cases + 30 Spark trial checks on actual
  S10 simulator/fitter outputs; independent invented-number scan of shown text; offline first;
  (3) live Meta run, per-call ledger evidence/S14/S14g-ledger.jsonl, hard cap $3.00 (estimated);
  (4) fresh agent tests + prior mutation scripts; REPORT.
- Budget: Meta <= $3.00; no GPU, no installs.
