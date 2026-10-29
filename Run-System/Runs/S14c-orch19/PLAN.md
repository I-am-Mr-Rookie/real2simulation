# S14c-orch19 PLAN

Objective: one-to-three-question interview; chips and free text map into validated S08 spec inputs.
Lane/model: anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Offline only: NO Meta/Muse calls.
Owns: Build/agent/, contracts/agent/, tests/agent/, evidence/S14/, Run-System/Runs/S14c-orch19/.

Design (smallest complete): code-owned per-template questions (agent-response question format, validated
number-free via S14a validate_response); answers {chip|text} -> sourced quantities (label assumed,
evidence user-input:<qid>) patched onto a caller base spec of the same template, then S08c validate_setup.
Template comes from a validated Muse candidate (S14b) or explicit choice; no model-authored numbers.
Checks: unittest tests/agent; mutation spot checks.
