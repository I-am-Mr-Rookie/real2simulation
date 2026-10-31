# S15ax-orch217 PLAN

- Objective: owner-clip result chart becomes the centre-stage hero at report.owner (no scene); side card keeps g, verdict, caveats as text only.
- Owns: Build/web/src/workspace/ (result-chart.mjs, view.mjs, workspace.css), tests/workspace/, evidence/S15ax/, Run-System/Runs/S15ax-orch217/.
- Lane CLAUDE, anthropic/claude-opus-5-5 high. Issued 2026-10-31T14:27:20Z, deadline 14:57:20Z, cutoff 14:52:20Z.
- Smallest change: reuse resultChart() geometry (add axis gutters + ticks taken from series points), move the existing figure from renderMeasurement into the viewport section, CSS only for hero size/legend swatches/375 px.
- Checks: node --test tests/workspace tests/web-workspace-api tests/web-private; npm run build (Build/web); static renders into evidence/S15ax and look at them.
