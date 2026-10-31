# S13j-orch213 PLAN

- Objective: re-capture RM04 geometry bytes (points.ply, points-mobile.ply, scene.json) via existing gpu_stages/e2e path into private DEV storage so the DEV workspace viewer stops showing LOAD_FAILED.
- Lane CODEX-1, model anthropic/claude-opus-5-5/high. Issued 2026-10-31T13:53:31Z, deadline 14:23:31Z, cutoff 14:18:31Z.
- Owns: evidence/S13j/; Build/pipeline/recorded/ (new manifest only); Run-System/Runs/S13j-orch213/.
- Steps: (1) gpu_stages.reserve (reserve_gpu -> require_reconstruction, canonical journal) with RECONSTRUCT_RESERVE_USD $0.50 (< $3 target) BEFORE any dispatch; (2) reconstruct RM04 from the hash-matching S05c manifest; (3) sha-record bytes, private storage only; (4) manifest under Build/pipeline/recorded/; (5) DEV viewer check in iab or exact wiring step.
- Stop rule: any guardrail refusal is final for this run (no bypass, no journal edits).
