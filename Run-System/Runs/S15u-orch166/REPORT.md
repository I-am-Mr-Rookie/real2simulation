# S15u-orch166 REPORT — DONE
Lane CLAUDE, anthropic/claude-sonnet-5-5/medium (OpenCodex-managed; not polled). UTC 2026-10-30T22:31:23Z to 22:42Z. Branch run/S15u-orch166 on main 8d77f36f (no rebase needed). Tokens/cost unknown; no Meta/GPU call, no secrets.

## Changes (Ponytail: smallest complete)
- fit-view.mjs: (d) pm drops the 15-decimal cap; when uncertainty needs >8 decimals it prints 10 sig figs + exponent uncertainty (-9.81 ± 2.0e-15 m/s²); exact text stays in the cell title (existing caption promise). (b) fitView(state, input, whatIf) uses the what-if label as the gravity row source when set; react.mjs passes the existing whatIf prop (no new plumbing); synthetic-lab path unchanged. (c) residual table = first 10 rows (row renderer reused as a local helper) + native details/summary with the remaining rows.
- workspace.css: (a) 375px table cells overflow-wrap: anywhere (break-word keeps long numbers' min-content and widened the card), .ws-fit > * {min-width:0}, summary style.
## Checks
- tests/workspace/fit.test.mjs +4 tests (sig figs/title, what-if source, head+details, CSS structure). node --test workspace+shell-workspace+web-private+web-workspace-api: 117/117 pass. npm run build: exit 0 (junction to canonical node_modules, removed via rmdir; target intact).
## Deploy (Railway DEV, web only)
- stage.py web -> 111 files, source_revision 35805e6af742e4355e12f073dc494794572c68df; railway up --detach (project b07b0d66, env c5823a28, service 49f2938d). web deployment bec439d2-582a-4c87-bb3b-4e34ccd5c177 SUCCESS (previous b1805418-6caa-44db-8f15-133918341eff REMOVED); https://web-dev-cd80.up.railway.app/ -> 200.
- For controller (deployments.json not edited): web {deploymentId bec439d2-582a-4c87-bb3b-4e34ccd5c177, previousDeploymentId b1805418-6caa-44db-8f15-133918341eff, sourceRevision 35805e6af742e4355e12f073dc494794572c68df}. API unchanged. Revision is the code commit; the PLAN/REPORT commit follows it.
## Not verified / risks
- Actual 375px scrollWidth not measured in a browser (controller walk); CSS fix is by cause analysis + structure test. If 395 persists, suspect another element (run/instrument panels), not the fit tables.
- Gravity uncertainty rule is display-only; the d>8 threshold is my choice.
- Communication: silent; one completion line.
