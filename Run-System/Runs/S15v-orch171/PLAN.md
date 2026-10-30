# S15v-orch171 PLAN
Lane CLAUDE, anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Issued 2026-10-30T23:40:23Z, deadline 2026-10-31T00:10:23Z, cutoff 00:05:23Z.
Objective: product accepts registered 30 fps owner phone clips, asks for an object of known size (user-declared scale, labelled), and shows the stored S07i g ± u as a labelled RECORDED replay or an explicit abstain instead of failing. Redeploy api+web DEV.
Owns: Build/api/workspace/; Build/web/src/workspace/; tests/api-workspace/; tests/workspace/; evidence/S15v/; Run-System/Runs/S15v-orch171/ (other contract Owns untouched).
Checks: python -B -m unittest discover -s tests/api-workspace; node --test workspace/shell-workspace/web-private/web-workspace-api; npm run build; DEV health/version revision.
