# S14g-fix7-orch105 PLAN

Objective: close R-A F1-R4 (RECHECK-fix6.md) with ONE clause-level rule: a clause (split at . ! ? ;) holding a unit word may hold no amount word; "in <units>" binds only when directly followed (optional ":"/"=") by a CITE or clause end. Identical, independent in runtime validator and oracle. Refusal -> existing tool-only fallback.

Owns: contracts/agent/validate.py; evidence/S14/S14g_fix_oracle.py; tests/agent/fixtures/adversarial-visible-text.json; evidence/S14/S14g_fix7_gate_a.py + fix7 outputs + fix7-reviewer-probe/; Run-System/Runs/S14g-fix7-orch105/.
Checks: 8-module suite; oracle self-check; prompt scan vs main; reviewer probe copy; fix7 offline replay (30 saved turns).
Lane CODEX-1, assigned anthropic/claude-opus-5-5/high; OpenCodex-managed, not polled. Offline, $0.
