# S15d-orch19 plan
Objective: interview chips + free-text panel; Q/A transitions against validated fixtures. Lane CLAUDE, anthropic/claude-sonnet-5-5/high.
Owns: Build/web/src/workspace/; tests/workspace/; evidence/S15/; Run-System/Runs/S15d-orch19/. Branch run/S15d-orch19.
Design (smallest complete): pure `interview.mjs` (parse validated agent-response questions, own reducer, view model, h-injected markup); optional `interview` prop hook in view.mjs/react.mjs; CSS; fixtures generated from S14a validators by an evidence script (no model calls).
Acceptance: Q->A transitions (chips, free_text, chips_and_free_text, back, multi-round) pass against fixtures validated by contracts/agent/validate.py; Node tests + React SSR check green.
