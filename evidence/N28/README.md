# N28 evidence: lab agent acts like an assistant; panel layout; F3 contributor card

Local only: next start :3028 (worktree build) + local uvicorn :8128 (R2S_DATA_DIR=.n28-data, throwaway local workspace token).
Harness: panel.mjs, headed Playwright Chromium, public /lab?editor=1 with the real AgentPanel; its /api/workspace/agent/* calls
are forwarded to the local uvicorn. A ramp is added in the editor first, then three prompts.

| File | What |
|---|---|
| run1-turns.json | LIVE run 1 (owner n28-live), muse-spark-1.3: 3/3 acted with no question. T1 lab_add_object {diameter_m 0.05, height_m 1.2} + lab_run, reply "Assuming your 5 cm is diameter...", SIMULATED g 9.81 +/- 0.014 m/s^2. T2 lab_update_object {id ball, dx_m -0.3, diameter_m 0.1} (first call missing id, retried). T3 lab_remove_object {id ramp} ok. |
| run1-panel-*.png, run1-*-375.png | Panel after run 1. Layout bug visible: suggestion chips hidden (class clash with stage .le-chips). |
| run2-turns.json | LIVE run 2 (owner n28-live2): T1, T2 acted with stated assumptions; T3 sent {kind: ramp}, rejected by the schema (missing id), agent asked for the id. Fixed after: tools take id or kind (unit test), not re-run live (6-turn cap used). |
| replay-*.png, replay-turns.json | Final layout: run-2 replies REPLAYED from run2-turns.json (no model call, marked replayed), desktop + 375. Log scrolls, last answer in view (scroll gap 0 px after each turn), chips above the bottom bar with input and Ask, 375 has no horizontal overflow. 3D view in replay does not show agent edits (no tool ran). |

F3: N27 account A did show the card (evidence/N27/a1-01-contributor.png, taken right after the heading wait). Its FAIL was the
next wait on .lv-chip, which lives in the closed Agent & tools drawer: a harness false negative. The real slow-session gap found:
one failed /health probe (401/5xx in a fresh session's first seconds) hid the whole live centre and its card for the page's life.
Now probeUntilLive retries 1 s, 2 s, 4 s (tests/shell-workspace/private-workspace.test.mjs). Not re-checked on DEV (no deploy).
