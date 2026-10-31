# S15aa-orch185 PLAN
Model: anthropic/claude-opus-5-5, medium (controller correction; launch text said sonnet). Issued 2026-10-31T02:48:29Z, deadline 03:18:29Z, cutoff 03:13:29Z.

Objective: owner clips in product show stored frozen-v1 g ± u + S07m v3 verdict (PASS/FAIL, chi2/dof, p) copied programmatically from evidence/S07/S07m/results.json, or an explicit abstain with reason (OWN06 invalid, OWN10/OWN11 v1 abstain, OWN12 excluded per S07h).

Owns: Build/api/workspace/; Build/web/src/workspace/; tests/api-workspace/; tests/workspace/; evidence/S15aa/; Run-System/Runs/S15aa-orch185/.

Steps: evidence/S15aa/sync_owner_measurements.py writes owner_clips.json measurement/abstain; jobs.owner_measurement builds one generic caveat; test re-derives every stored number from the evidence JSON; api tests + 4 web node globs; rebase; Railway DEV api redeploy (web unchanged unless needed).
