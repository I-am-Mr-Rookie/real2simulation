# N43 DEV end-to-end QA

**QA complete. Acceptance has failures: 1 P1, 3 P2, 1 P3. No application code changes or deploy.**

DEV: https://web-dev-cd80.up.railway.app. Active deployments independently read from Railway: web `5ef6d2eb-185a-4e2b-bd26-115d465f0ce6`, API `60195792-fc94-4473-875b-6e63d5d26fbd`, both SUCCESS. Browser: headed Playwright Chromium, never Chrome. Test account `n43-mvym1kik+clerk_test@example.com`, Clerk test code `424242`. All screenshots contain only Pexels RM02/ST03 or simulated scenes, never owner clips or real email addresses.

Reused the N13 `qa.mjs`, `qa2.mjs`, and `probe.mjs` patterns: isolated Clerk test account, response receipts, screenshots, upload/measure/build selectors, quota test, and fresh-load mobile width checks. N43 `qa.mjs` is the shared interactive recorder. `verify.mjs` checks saved receipts offline. No isolation probe was rerun because N43 did not request it.

## Acceptance matrix

| Requested check | Result | Evidence |
|---|---|---|
| 1. Sign-up tier/contributor choice, default Standard | PASS | Fresh signup showed Standard, Contributor pros/cons, Spark, Muse Open. `01-signup-tier-choice.png/.txt`. |
| 1. Sample project visible | PASS | Classroom room and apple, SAMPLE and RECORDED, both open actions present. `02-workspace-first.png`, `03-sample-project-visible.png`. |
| 2. Live Mode A RM02, shell builds automatically | PASS for execution, FAIL for usable geometry | Room `82f05b85de1748b3bd91003122b8e70d`, created 01:59:52Z, done 02:07:34Z. L4 capacity timeout then A10G succeeded. Auto shell: 4 FIT walls, 24 reported openings, 7 kept furniture, 97 dropped; no manual Build shell click. F2 below. `room-result-before.json`, `rooms-final.json`, `room-20-auto-shell.png`. |
| 2. SF3D objects and required labels/credit | PASS desktop, mobile legibility issue | Three A10G meshes, four documented box fallbacks from the three-object limit. Mesh captions show MODEL-GENERATED shape and Powered by Stability AI. `room-20-auto-shell.png`, `32-mobile-room.png`. F5 below. |
| 2. Drop ball on a table and it rests | FAIL | Two actual DEV Play runs roll off the first detected SF3D table and reach the floor. F1 below. |
| 2. A4 rescale preserves shell | PASS wiring only | Rejected out-of-range 2.934x reference retained the shell. A second reference applied 1.491359x; all 13 server scene object IDs and shell remained. `room-24-a4-result.png`, `room-25-a4-applied-shell-kept.png`, before/after JSON. Arbitrary QA reference clicks, NOT a physical calibration or proof of A4 dimensions. |
| 2. GPU red/yellow/green and queue position | PARTIAL observation | Red sleeping and yellow starting, including “Your job: 1 of 1 in queue”, recorded in `results.json`. Green was not sampled during the short A10G execution. `05-room-starting.png`, `07-room-current.png`, `28-mobile-workspace.png`. No product failure inferred from missed green coverage. |
| 3. Every kit item, Play | PASS | All 20 menu entries added: five basics, five apparatus, seven masses, three probes. Scene has 20 objects; Play advanced with SIMULATED label. `kit-add.json`, `kit-scene.json`, `08-lab-kit-menu.png`, `09-kit-all-added.png`, `10-kit-play.png`. Not a per-apparatus physics accuracy benchmark. |
| 3. Agent drop and measure g; Atwood and measure a | PASS | API tool outputs: SIMULATED g 9.810018 +/- 0.0074 m/s²; Atwood a 1.961998 +/- 0.0044 m/s². Repeated g for screenshot: 9.809989 +/- 0.015. These are fitter outputs, not physical measurements. `lab-results.json`, `15-agent-atwood.png`, `33-agent-g-result.png`. |
| 3. Delete, Ctrl+Z, Ctrl+Shift+Z | PASS | Scene object count 21 -> Delete 20 -> Undo 21 -> Redo 20. `history-confirmed.json`, `11-delete-undo-redo.png`. The initial immediate read was stale; confirmed after React settled. |
| 4. Spark and Muse Open answer, Sol not selectable, off-topic refusal | PASS in workspace; FAIL tier consistency in lab | Both actual provider model IDs returned successful answers; off-topic poem/restaurant request refused. No Sol option; direct `tier: sol` rejected 422 before inference. `14-agent-tier-options.png`, `17-spark-answer.png`, `18-muse-open-answer.png`, `19-off-topic-refusal.png`, `sol-rejected.json`. F3 below. No forced fallback/provider failure injection. |
| 5. Mode B size input, fit chart and uncertainty | PASS | ST03 4 s; 8 cm apple-width QA assumption entered. Hosted SAM processed 120 frames; result in 10 s. 18 plotted points, fitted curve, one-sigma band. 2.71 +/- 0.42 m/s² explicitly labelled vertical acceleration, assumed size, playback clock/capture clock unverified. NOT a calibrated gravity accuracy claim. `13-mode-b-known-size-input.png`, `16-mode-b-fit-band.png/.txt`, `mode-b-result.json`. |
| 6. Files upload, preview, delete; quotas | PASS daily count, storage enforcement not exhausted | RM02 preview decoded 1280x720, 6 s. Twenty uploads accepted, upload input disabled at 20, direct 21st upload rejected 429 with reason and midnight-Dhaka reset. Deleting one own tiny file reduced bytes, did not restore daily uploads. 1 GB cap displayed but not filled. `12-file-preview.png`, `26-quota-at20.png`, `27-file-deleted.png`, `quota-21.json`, `files-final.json`. |
| 7. 375 px /workspace and /lab overflow | PASS | Fresh loads: document scrollWidth == clientWidth == 360 CSS px at 375 px viewport (vertical scrollbar). Room-loaded lab also 360/360. `mobile.json`, `28-mobile-workspace.png`, `29-mobile-lab.png`, `32-mobile-room.png`. |
| 8. Footer credit and no visible em dashes | PASS sampled states | Lab and room footers show Powered by Stability AI. Workspace is a full-screen shell without a site footer. No U+2014 found in observed signup/workspace/agent/lab/room text. `visible-copy.json`, `29-mobile-lab.png`, `32-mobile-room.png`. Not an exhaustive crawl or guarantee about future model replies. |

## Ranked findings

### F1 [P1] A centre drop rolls off the generated table instead of resting

1. Sign in, upload N13's Pexels `RM02-trim.mp4` (6 s, 292,379 bytes), choose Room video, Build my lab, wait for automatic shell completion.
2. Open the generated room. Add Ball. Through the supported Scene JSON editor, set diameter 0.05, restitution 0, zero initial velocity, sensor on, position `[0.0839, 1.21735, -1.7662]`. This is directly above `room-object-1`, the first generated table, with its unscaled top at 0.41735.
3. Play for at least four simulated seconds; pause and Export traces. Full reproducible scene: `drop-scene.json`.
4. Expected rest centre y = 0.44235. Actual repeat at t=4.216666667: `[0.9114863873, 0.0249097068, -1.3030406237]`, on the floor. First run likewise ends on the floor at t=14.441666667. The trace shows initial table contact near 0.42 s, then lateral motion and roll-off, not simply missed collision. Two of two observed runs failed.

Evidence: `table-drop-traces.json`, `table-drop-repeat-traces.json`, `table-drop-summary.json`, `drop-scene.json`. The second replay restored the original unscaled saved scene after the A4 wiring check, so its stage scale chip and the server room tool scale differ by design; do not report that QA-induced mismatch as a product bug.

![Ball has rolled off after the centre drop](<C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/N43-orch288/evidence/N43/room-31-table-drop-3s.png>)

### F2 [P2] Reported walls/openings do not enclose or cut the reconstructed room

1. Complete the same new RM02 room job; do not press Build lab shell manually.
2. Inspect the default shell and `room-result-before.json`.
3. The four FIT wall planes enclose only 0.2074 x 0.9647 nominal room units, height 0.4413. All seven retained furniture centres lie outside that wall envelope in the fitted yaw frame. None of the 24 reported opening rectangles intersects its assigned wall rectangle. Example: wall index 2 span `[1.8817,2.0891]`, opening `[2.2396,2.4816]`.
4. The UI nevertheless reports “4 walls, 24 openings”. Furniture meshes also visibly look severely distorted. Scale is unverified, but this is an internal geometry/count inconsistency, not a demand for calibrated metres.

Evidence: `geometry-summary.json`, derived by `verify.mjs` from the actual pre-rescale output; `room-result-before.json`.

![Generated shell does not form the classroom](<C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/N43-orch288/evidence/N43/room-20-auto-shell.png>)

### F3 [P2] Muse Open selection is ignored by the lab's agent

1. In /workspace, open Agent & tools, edit the mode, choose Standard > Muse Open, Save.
2. Ask a physics question there. Network response model is `meta-models/muse-spark-open-1026` and UI says Standard: Muse Open.
3. Open /lab?editor=1 in the same signed-in browser. Ask “Explain how a pulley changes the direction of a force. No calculations needed.”
4. Actual lab response model is `muse-spark-1.3`, despite the saved per-workspace mode being `open`. The lab has no tier selector or model disclosure. The current `AgentPanel.jsx` sends text/history without tier/contributor; this matches the observed response. Does not invalidate the two workspace tier answers.

Evidence: `lab-tier-check.json`, `results.json`, `lab-results.json` (02:11:48Z response).

![Workspace Muse Open selection and answer](<C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/N43-orch288/evidence/N43/18-muse-open-answer.png>)
![Lab answer silently uses Spark; model identity is in the response receipt](<C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/N43-orch288/evidence/N43/30-lab-tier-ignored.png>)

### F4 [P2] New Room project stays empty while its upload/job land outside it

1. Fresh account: New project > Room video > Continue.
2. Upload RM02 and Build my lab through that flow.
3. Refresh projects after completion. `Room 2026-11-02 01:59` remains “No rooms or experiments yet”; the actual room is under “Not in a project”.
4. API project `f578dc3ba08f46c68bb9f1d6ef6cc6ac` exists, but both the uploaded RM02 file and room job have `project_id: null`. Mode B separately auto-created an Experiment project correctly.

Evidence: `projects-final.json`, `rooms-final.json`, `files-final.json`, initial project/upload POST receipts in `results.json`.

![Room project is empty and finished room is unassigned](<C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/N43-orch288/evidence/N43/34-project-attachment.png>)

### F5 [P3] Required model-generated captions are illegible at 375 px

1. Open the generated room at 375x812 without zooming or orbiting.
2. The canvas' two-line MODEL-GENERATED shape / Powered by Stability AI sprite captions shrink to unreadable text; one is partly clipped at the right edge. The footer credit remains readable. No document horizontal overflow occurs.
3. Desktop labels do render; the issue is default mobile legibility, not absence of a credit.

![Default mobile room and tiny shape captions](<C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/N43-orch288/evidence/N43/32-mobile-room.png>)

## Paid calls and limits

`paid-ledger.json`: **estimated $1.05580886 total, below $2.00**. One room reconstruction with failed L4 + successful A10G attempts $0.66533785; 72 SAM image calls $0.18; three SF3D jobs $0.10045726; one 120-frame hosted tracking job $0.024; seven agent turns $0.08601375 (five Spark, two Muse Open, token aggregates). No Sol inference, purchases, deployment, or extra GPU jobs for status colour coverage.

The ledger records UTC receipt times or enclosing intervals, model, units, estimate. Shell sub-call exact UTC timestamps were not exposed by the UI. Runtime code already reserves/settles these jobs; do not insert this summary as additional charges. A read-only Railway SSH ledger audit failed with exit 255, so no server SQLite reconciliation or provider invoice verification is claimed.

Skipped: physical calibration/ground-truth g, one-gigabyte exhaustion, forced Sol fallback, cross-account isolation, continuous green-GPU capture, 15-minute idle shutdown, and independent physics accuracy tests for every kit item. Two recorder timeouts required reopening the same test account; successful receipts and saved state were recovered, no second room or tracking job was started. No application tests/build because application code was unchanged.

Screenshots are retained in this worktree, intentionally not committed under WORKER_CONTRACT's no-media-binaries rule. Text receipts and their screenshot SHA256 manifest are committed. Captured plain text has trailing spaces normalized; JSON formatting may be minified without dropping values. Response bodies marked `body_is_excerpt` are limited recorder excerpts; full room results are saved separately. Source Pexels clips and temporary authenticated browser state are not committed.
