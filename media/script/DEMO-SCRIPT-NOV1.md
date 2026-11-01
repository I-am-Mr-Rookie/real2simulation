# Real2Simulation: 3-minute demo script, Nov 1 pivot (N17)

Status: DRAFT for Koushik's voice-over. Matches DEV (https://web-dev-cd80.up.railway.app) as tested in N13 (2026-11-01 13:50 to 14:08 UTC). Spoken total about 2:22 (limit 2:50); the rest is screen time. Read lines: [READ-SHEET-NOV1.md](../narration/READ-SHEET-NOV1.md).
Rules: numbers only from the cited files. [PENDING N24/N25/N26] = not yet shown on DEV; do not record that screen or take until it is fixed, or use the fallback shown. No em dashes. Honesty labels stay visible on screen.
Evidence short names: N13 = evidence/N13/FINDINGS.md; N22 = Run-System/Runs/N22-orch265/REPORT.md; N23 = Run-System/Runs/N23-orch266/REPORT.md; PLAN = Run-System/PLAN-NOV1.md.

| Time | Take | On-screen action | Line (full text in read sheet) | Evidence |
|---|---|---|---|---|
| 0:00-0:08 | V01 | Cut: ST03 apple clip falls, freeze on the apple, then the result card with the uncertainty band | "Anyone can film a falling apple. Almost nobody can say what it proves. This turns your video into a measurement." | N13 B2 result (screen a1-08-b2-result.png). Band must show: [PENDING N24/N25/N26] (N13 F1) |
| 0:08-0:20 | V02 | Sign up (test account), then the card "Choose how the agent runs" with pros and cons; pick Standard | "I sign in and choose how the agent runs..." | PLAN decision; card seen at p2-01-mode-settings.png. Not shown right after sign-up: [PENDING N24/N25/N26] (N13 F3). Fallback: open the mode chip menu |
| 0:20-0:26 | V03 | New project, agent card "What are you uploading?" (Room video / My experiment) | "The agent asks one question first..." | N13 step new_project_question_card PASS; a1-03-question-card.png |
| 0:26-0:34 | V04 | Pick My experiment, drop the apple clip (4 s, 720x1366). Files panel shows quota text | "I drop in a phone clip..." | N13: upload 2.5 s; "26 MB of 1.0 GB used. 17 of 20 uploads left today." (limits 20/day, 1 GB: PLAN) |
| 0:34-0:42 | V05 | Measure this experiment, first frame, click the apple. Marker appears | "I click the apple on the first frame..." | N22 click flow; a1-04-b1-click.png |
| 0:42-0:50 | V06 | Type "apple", size "apple width 8 cm". Show the scale-assumed tag | "I tell it the apple is eight centimetres wide. That is my assumption..." | N13 B2. "scale assumed" tag [PENDING N24/N25/N26] (N13 F4). Fallback: tag reads "capture clock unverified" |
| 0:50-1:02 | - | Progress card; GPU dot goes green. Speed up in edit, no voice | (none) | N13: B2 took 28.5 to 41.8 s; GPU dot F10 |
| 1:02-1:14 | V07 | Result card: 2.70 +/- 0.30 m/s^2, MEASURED, band and fitted curve | "It comes back in under a minute: 2.7, plus or minus 0.3 metres per second squared..." | N13 F4: 2.70 +/- 0.30 m/s^2, 19 tracked frames, 0.70 s; a1-08-b2-result.png. Numbers must be re-read from the live card at recording |
| 1:14-1:24 | V08 | Hold on the card. Highlight "capture clock unverified" tag | "That is far from 9.8. We show it instead of hiding it..." | N13 F4 (true g 9.81; value off about 3.6x; probable slow motion) |
| 1:24-1:32 | V09 | Click "3D replay, redo with changes"; lab opens with measured track and SIMULATED ball | "One click opens a 3D replay..." | N13 redo_in_3d PASS 5.9 to 10.4 s; a1-11-redo-lab.png |
| 1:32-1:40 | V10 | Share as Guess the Gravity, copy link, open it logged out: no answer shown. Revoke | "I can share it as Guess the Gravity..." | N13 share checks (opens logged out, no answer before guess, revoke works); a1-09-guess-public.png |
| 1:40-1:48 | V11 | New project, Room video, upload RM02 room clip, Build my lab. GPU dot red then yellow then green | "Now a room..." | N13 modeA_build_lab; yellow never sampled (F10): [PENDING N24/N25/N26] for the yellow state; do not claim it |
| 1:48-2:00 | V12 | Open my lab: 3D room point cloud. Scale label "unverified". Mark the A4 sheet with two clicks, label turns MEASURED | "In about a minute I get a 3D room..." | N13: build 30.9 to 48.8 s, 20000-point room, scale unverified, gravity MODEL-ESTIMATED. Use a clip that really shows an A4 sheet; RM02 has none, N13 F6 (any two clicks give MEASURED). [PENDING N24/N25/N26] |
| 2:00-2:06 | V13 | Click a real object in a view, a block appears in the lab with MODEL-ESTIMATED tag | "I click a real object..." | N13: room-object-1 box proxy MODEL-ESTIMATED; a3-m-a-lab.png |
| 2:06-2:20 | V14 | Open Agent & tools. Type "Drop a 5 cm ball from 1.2 m and measure g". Tool calls run, SIMULATED g shown | "Then I ask the agent..." | N13 F5: SIMULATED g 9.81 +/- 0.014. Agent refused 1 of 3 runs, so retake until it runs; do not edit a refusal into a success |
| 2:20-2:26 | V15 | Mic button, speak, text appears | "I can also talk to it..." | N13 pass2: muse-voice-transcribe-1.0 returned the sentence (15.5 s with fake mic) |
| 2:26-2:38 | V16 | Cut across labels on screen: RECORDED, SIMULATED, MEASURED, MODEL-ESTIMATED, scale unverified | "Every number carries a label..." | Honesty rules (AGENTS.md); labels seen in N13 screens |
| 2:38-2:50 | V17 | Slow title cards: hosted SAM 3.1, Muse Spark 1.3, Muse voice transcribe, MapAnything on Modal | "Under the hood..." | PLAN lines 31, 50 to 58; N23 (hosted sam-3.1 and muse-spark-1.3 live on DEV via the Modal proxy; Mode A on Modal A10G) |
| 2:50-2:54 | V18 | OPTIONAL: lab report with Muse Image illustration | "The report can include a Muse Image picture." | [PENDING N24/N25/N26] not shown on DEV. Cut this take if absent |
| 2:54-3:00 | V19 | Logo and tagline, DEV URL not shown (judging deploy needs S23a) | "Real2Simulation. Film it, measure it, and see how sure we are." | - |

## Open points for the editor and owner
- Do not show the "No value reported" card (Mode B without a size, N13 F1) as a success. If N24 to N26 do not fix it, V06 must always give a size.
- Stale /lab footer says uploads need approved clips (N13 F7). Crop it out.
- No real emails on screen. Use +clerk_test accounts and licensed clips (Pexels) only; no owner clips.
- No cost or latency claim beyond: "under a minute" (B2 28.5 to 41.8 s, N13) and "about a minute" (Mode A 30.9 to 48.8 s, N13).
