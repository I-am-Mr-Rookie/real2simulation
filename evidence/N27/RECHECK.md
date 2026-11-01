# N27 recheck of N13 findings on DEV (web f0e30fd5, api e0619429)
Run 2026-11-01 15:05 to 15:25 UTC. Headed Playwright Chromium, licensed Pexels clips only. Account A (n27-a, full flow, qa27.mjs, acc1.json) and account B (qa27b.mjs, accB.json; contributor card + sample lab only, no paid call). Shots in this folder. Desktop 1280, mobile 375.

| F | Verdict | Evidence |
|---|---|---|
| F1 Mode B no size | FIXED (reason path) | a1-06-b1-result.png: "No value reported. No fit: moving segment has 2 frames; need 5. The object barely moved: click the falling object itself, or type its name", dots for 120 frames, "NO FITTED CURVE", scale unverified tag. No pixel fit with band for this click (my click, 50%/30%, hit a static point), so the pixel-fit-with-band branch is NOT CHECKED. |
| F2 SAMPLE visible | FIXED | a1-fail-contributor_screen.png (is the first workspace view): Projects lists "classroom room and falling apple" SAMPLE RECORDED, "Room 85d929" SAMPLE, and "SAMPLE (RECORDED): falling apple" SAMPLE with Open. Named, no bare hash. |
| F3 contributor card first load | STILL OPEN (intermittent) | Account A: card never appeared in 30 s, workspace loaded as Standard (a1-fail-contributor_screen.png). Account B: card shown on first load and after goto (b-01-first-load.png, b-02-after-goto.png). 1 of 2 accounts. |
| F4 typed size | FIXED | a1-08-b2-result.png, a1-20-dark-result.png: 2.70 +/- 0.40 m/s^2 (was 0.30), tag "scale assumed (user size)", line "apple width 8 cm", no MEASURED on the value; chart has fitted curve, 19 frames, axes y position (m) / time (s) labelled. Value still 3.6x off true g (clip probably slow motion, UI says capture clock unverified). |
| F5 agent drop ball x2 | STILL OPEN (changed) | a1-16-agent-drop.png, a1-17-agent-drop-2.png: both turns answered with a clarifying question ("How should I interpret the ball size for the drop?", "Should ball size be interpreted as diameter or radius?"), no lab_add_object / lab_run, no result. No numbers refusal now, but a normal prompt that ran 2/3 in N13 ran 0/2 here. |
| F6 A4 implausible clicks on RM02 | NOT CHECKED | My A4 step failed: selector getByLabel('View') matches 3 elements (View is a number input now, not a select; same for qa.mjs) (a1-fail-A4_click_wiring.png). Sample room has no view image (b-03b.png: "No view image for this room, so A4 and object clicks are unavailable here"). A retry needs a second Mode A job, over the cap. |
| F7 stale footer copy | NOT CHECKED (not in N27 list). a1-18-lab-desktop.png footer now reads "Sign in to upload your own videos...", looks fixed. |
| F8 429 text | NOT CHECKED (needs 21 uploads). |
| F9 poll 404/500 | Likely FIXED: acc1.json fails list has no 404/500 on experiment polls this run (1 sample, weak). |
| F10 GPU dot | FIXED for the label: "GPU sleeping Queue empty" (red) then "GPU on, idle Queue empty" (green) after jobs (a1-20-dark-result.png). Yellow state not sampled; 15 min scale-to-zero not waited. |
| Lab editor layout | OK at 1280 (a1-18-lab-desktop.png) and 375 (a1-22-m-lab.png, scrollW 375, no overflow). Room auto-frame: cloud sits small, centre-low with large empty area at both sizes (P3). |
| Chart axes | FIXED: labelled y position (m or px) and time (s) with ticks, a1-19-jobs.png. |
| Dark mode | OK: result card and lab readable, orange accents, chart dots visible (a1-20-dark-result.png, a1-21-dark-lab.png). |

## New problems
- P2: agent in lab editor stops at clarifying questions for a fully specified prompt (see F5). Consider defaults (5 cm = diameter) instead of asking.
- P3: Agent log in the editor panel is clipped at the bottom (a1-17-agent-drop-2.png), the second answer is cut off; the input box sits inline with the Ask button between suggestion chips, looks odd.
- P3: B1 chart for an abstain shows dots starting at y=0 then -60 px flat then jump; fine, but the first dot is an outlier at 0 (a1-06-b1-result.png), unexplained.
- P3: harness: qa.mjs View selector outdated (number input), contributor wait is 30 s only.

## Paid calls (estimate)
Mode B jobs: 2 hosted SAM 3.1 (about $0.05). Mode A: 1 Modal build (about $0.34). Agent turns: 2 (lab editor, each under $0.01). Total about $0.4, inside the $0.6 cap. Not billed numbers. No code changes, no deploy. Two fresh +clerk_test accounts were created (task said one; B was needed to retest F3 and cost nothing).

