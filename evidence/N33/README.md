# N33 evidence: lab kit, Add menu, Delete and Undo/Redo, live agent turns

Local only: `next start` :3033 (worktree build) + local uvicorn :8133 (R2S_DATA_DIR=.n33-data, throwaway local token, owner n33-live). No deploy.

| File | What |
|---|---|
| shoot.mjs, screenshots.json | Headed Playwright Chromium, public /lab?editor=1. Add menu has 20 items (Basics, Apparatus, Mass set, Probes). Adds 7 kit objects; Delete key removes the selected photogate; Ctrl+Z restores it, Ctrl+Shift+Z removes it again, the Undo button restores it. Play 0.96 s then Pause. 375 px: scrollWidth 360, menu inside the viewport. |
| add-menu-desktop.png, add-menu-375.png | Compact Add menu with icons. |
| kit-play-desktop.png, kit-play-375.png | Atwood, flywheel, cart and track, launcher, collision balls, 200 g mass, photogate during Play (SIMULATED). |
| agent.mjs, turns.json | LIVE, muse-spark-1.3, 2 turns, both acted with no question. T1 "Set up an Atwood machine with 200 g and 150 g and measure the acceleration": lab_add_object atwood {mass1_kg 0.2, mass2_kg 0.15} + lab_run, SIMULATED a 1.40143 +/- 0.003 m/s^2 (theory g (m1-m2)/(m1+m2) = 1.401). T2 "Add a flywheel and find its moment of inertia": defaults, SIMULATED I 0.01124977 +/- 3.9e-05 kg m^2 (scene disc 0.01125). |
| editor-desktop.png, panel-desktop.png, panel-375.png, viewport-375.png | Editor and agent panel after the live turns; Undo is enabled after agent edits. |
