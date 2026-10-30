# S14j-orch159 PLAN

Issued 2026-10-30T20:22:53Z; deadline 20:52:53Z; cutoff 20:47:53Z. Model anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled).

Objective: POST /internal/workspace/scenes/{id}/spec applies owner Q16=A for recorded scenes whose ONLY failure is
"$.scene: invalid authoritative bundle" -> numeric spec contract (Gate A spec_only = contracts.experiment validate())
-> 200 {ok, spec, validated_setup, label:'scale unverified, not setup-validated', setup_validated:false}. Others unchanged.
Then redeploy API to Railway DEV (stage.py api + railway up) and run verify.py.

Owns: Build/api/workspace/analysis.py; tests/api-workspace/; evidence/S14j/; Run-System/Runs/S14j-orch159/.
