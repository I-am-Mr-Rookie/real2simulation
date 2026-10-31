# S15af-orch192 REPORT — DONE
Lane CLAUDE; anthropic/claude-sonnet-5-5 medium; OpenCodex-managed, not polled. UTC 2026-10-31T07:52Z-07:59Z. Tokens/cost unknown. No Meta/GPU, secrets, Chrome, publication.

## Changes (railReduce rules/timers untouched)
1. Temporary pane top: 3.9rem (below header row): toggle no longer covered; still absolute, centre not pushed.
2. Removed "Keep open" button (workspace-shell.mjs, .r2s-pin CSS); test asserts none. Pin by icon click, Escape, pointer-leave unchanged.
3. --sh-left 14rem->16rem, temporary pane 12.75rem, overflow-wrap:anywhere on nav links: no clipped labels at 1280.
4. Current icon: inset 3px left indicator added to filled tile + 1px ink border (#1c1a16 on #fffcf5, >3:1).

## Checks
- node --test workspace/shell-workspace/web-private/web-workspace-api: 150/150 pass. npm run build OK (node_modules junction removed).
- evidence/S15af/ static SSR + Edge headless probes: 1280 open, collapsed, preview all toggleTop=toggle (elementFromPoint at toggle centre = toggle), clipped=false, no h-scroll, preview centreLeft 52 (not pushed). 375: headless Edge min window 492px (not true 375); drawer covers header under scrim by design (unchanged); no h-scroll.
- Deploy: rebased on main (HEAD b641fe05ab9a31ff5156db57f712634fd855b25b), stage.py web (113 files) + railway up. Deployment 55ba928c-fd5b-4642-9211-45a17ef1449c SUCCESS; previous fbb52f25 REMOVING. GET / 200.

deployments.json web lines for controller (file NOT edited):
"deploymentId": "55ba928c-fd5b-4642-9211-45a17ef1449c", "previousDeploymentId": "fbb52f25-e1e1-448e-92fd-d8165b5f762e", "sourceRevision": "b641fe05ab9a31ff5156db57f712634fd855b25b", "redeployNote": "S15af-orch192: stage.py web + railway up (rail polish)", "providerStatus": "SUCCESS"

## Ponytail
Reused renderShell and S15ae static_render.mjs; deleted dead pin button+CSS; four small CSS tweaks. Skipped: reducer pin action kept (tests use it); narrow-drawer toggle (scrim by design).
## Risks / unverified
Signed-in DEV walk is controller's; true 375 render unverified; header height assumed 3.9rem (very long wrapped titles could be taller).
Communication: silent; one completion line.
