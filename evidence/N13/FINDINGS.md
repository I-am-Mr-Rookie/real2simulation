# N13 end-to-end QA on DEV (read-only on code)

DEV: https://web-dev-cd80.up.railway.app (web fca5a968, api 20fa6b1f). Run window 2026-11-01 13:50 to 14:08 UTC. Headed Playwright Chromium, fresh +clerk_test accounts (A1, A2, A3 in parallel, plus one 4th account for pass 2 and one 5th for the isolation probe). Licensed clips only (Pexels, clips.csv): ST03 trimmed to 4 s (720x1366, 410 KB), RM02 trimmed to 6 s (292 KB), RM02 re-encoded to a 26,214,400 byte file for the size test. No owner clips. Scripts: qa.mjs (3 accounts), qa2.mjs (agent chat, voice, 375 px), probe.mjs (isolation). Raw data: acc1..3.json, pass2.json, probe.json. Screenshots: a<N>-*.png (desktop), a<N>-m-*.png (375 px, resized from desktop so layout can be stale), p2-m_*.png (375 px fresh loads, trustworthy).

## Findings

### P1
**F1. Mode B without a known size shows no value, no chart, no fit band (3/3 accounts).** Steps: upload ST03, Measure this experiment, click the apple, no size, Start measuring. Expected (PLAN N22, N23 report): pixel track and fit with 1 sigma band, labelled scale unverified (N23 saw 2348 +/- 106 px/s^2 from the API). Actual: card says "No value reported." with tags scale unverified, playback clock, and the line "Guess the Gravity needs a known size". Chart parts count 0 (no band, no curve, no dots). Done in 19 to 49 s. Screens a1-06-b1-result.png, a2-..., a3-.... Not checked: the raw API payload (the 6 Mode B job cap was used up), so I cannot say whether the API omitted the fit or the UI dropped it.
**F2. The SAMPLE project is not visible in the UI (3/3, plus the probe account).** Expected: every new account shows a SAMPLE project. Actual: Projects card says "Start a new project..." only. The API does create it lazily on the first list call: /projects returns "SAMPLE (RECORDED): classroom room and falling apple", /experiments returns a seeded row (file_id "sample", status done, result null). That row shows in Processing as a bare 32-char hash with done and Open, so a new user sees a mystery job instead of a sample. Screens a1-fail-contributor_screen.png (hash row), a2-02-workspace-first.png (none yet), a3-02-workspace-first.png, probe-fresh-account.png. Also noted by N23.

### P2
**F3. The contributor choice is skipped right after sign-up (3/3).** Steps: sign up, land on /workspace. Expected: "Choose how the agent runs" with pros and cons (PLAN decision). Actual: not shown within 30 s, workspace loads as Standard. On the 4th account, a fresh goto('/workspace') after sign-up showed the card at once (p2-01-mode-settings.png) and the chip menu always works. Looks like a race on first load after sign-up (mode read before the session is ready, falls back to Standard). Standard is a safe default, so no privacy harm, but the owner decision is not met on the first load.
**F4. A good Mode B result looks overconfident (3/3, identical numbers).** B2 (typed name apple, known size "apple width 8 cm"): 2.70 +/- 0.30 m/s^2 tagged MEASURED, 19 tracked frames over 0.70 s. True g is 9.81, so the value is off by 3.6x while the band claims 11%. The size is a user assumption and the clip is probable slow motion (UI does say "capture clock unverified"). Expected: uncertainty or tag that carries the assumed scale (scale assumed, not measured). Screens a1-08-b2-result.png.
**F5. Agent refuses a valid request nondeterministically (1/3).** "Drop a 5 cm ball from 1.2 m and measure g" in the lab editor: A1 and A2 ran lab_add_object + lab_run (SIMULATED g 9.81 +/- 0.014). A3 got "I drafted a question with numbers that did not come from a tool output, so I am not showing it." with no tool calls (usage 1838 in / 794 out). The guard is right to block numbers, but the user gets a dead end for a normal prompt. Screens a3-16-agent-drop.png.
**F6. A4 scale accepts any two clicks and labels the result MEASURED (3/3).** RM02 has no A4 sheet; two arbitrary clicks gave "Scale MEASURED: 3.742 +/- 0.178 m per unit". Wiring works (the task asked for it), but no plausibility check (A4 is 210 mm; ratio or px distance). Screens a3-16-agent-drop.png, a1-14-a4.png.

### P3
**F7.** Stale copy in the /lab footer: "Uploads are limited to approved licensed clips in the signed-in workspace." The owner decision says own videos, no approved-list gate.
**F8.** The 21st upload is refused correctly but the message is only "tiny-19.mp4: Upload failed (429)." (20 uploads were accepted on A3: ST03, RM02, 18 tiny). No reason or reset time (API quota carries uploads_reset_at 18:00Z). Deleting a file frees storage but not the daily count (17 of 20 left after upload, delete).
**F9.** A1 saw two failed experiment polls during the run: GET experiments/<B1 id> 404 and GET experiments/<B2 id> 500. The UI still finished both jobs, so likely one transient poll each; cause not investigated.
**F10.** GPU dot (global, sampled every 2 s): red "GPU sleeping Queue empty", then "Checking GPU", then green "GPU running" with "Your job: 2 of 2 in queue" / "1 of 2" / "Queue empty" while three accounts ran jobs. Yellow (starting) was never sampled; Mode B jobs on hosted SAM also turn the dot green. The dot goes back to "Queue empty" but stays green after the queue empties (idle timer, not checked to 15 min).

### Checked and fine
- Isolation: a fresh account sees only its own SAMPLE rows; GET of the six experiment/room ids from A1 to A3 returns 404 (probe.json).
- Share link: opens logged out, shows no answer before a guess, Revoke works and the public page then says the challenge does not exist or was withdrawn.
- 25 MB upload through the proxy: 26,214,400 bytes accepted in 15 s (N22 risk fixed). Quota text: "26 MB of 1.0 GB used. 17 of 20 uploads left today."
- Agent: physics question answered (physics-only, 5 s); off-topic poem plus pizza request refused ("Sorry I cannot help with that, but I can help with lab videos, tracking, ..."); drop-ball measure g ran in the lab (A1, A2). Voice with a fake mic (SAPI speech WAV): muse-voice-transcribe-1.0 returned the sentence (looped twice because the 6 s recording repeats the 3 s WAV, a harness effect).
- Files: preview plays (1280x720, 6.0 s), download returns the exact bytes (292,379), delete frees storage.
- 375 px fresh loads: /workspace, /lab?editor=1, /library, / have scrollWidth 360 = clientWidth 360 (no horizontal overflow). Full-page screenshots taken after resizing from 1280 (a*-m-*.png) can show stale desktop layout; use p2-m_*.png.
- Mode A: Build my lab 31 to 49 s, lab opens (20000-point room, 0 objects, scale unverified, gravity MODEL-ESTIMATED), A4 click and add real object work (room-object-1 box proxy MODEL-ESTIMATED).

## Harness limits (not product bugs)
In qa.mjs the agent chat steps (physics, off-topic, voice) failed on A1 to A3 because the chat lives in the closed "Agent & tools" drawer; qa2.mjs reran them on a 4th account (all pass). The "fit band" and "contributor screen" FAILs are product results (F1, F3). Step table cell "agent_editor_drop_ball_measure_g PASS" for A3 is a pass of the step but a refusal (F5).

## Pass/fail per step x account (seconds per step)
| Step | A1 | A2 | A3 |
|---|---|---|---|
| signup | PASS 9.3s | PASS 9.4s | PASS 10s |
| contributor_screen | FAIL 32.3s | FAIL 31.7s | FAIL 31.3s |
| sample_project_visible | FAIL 1.8s | FAIL 1.7s | FAIL 1.7s |
| gpu_dot_present | PASS 0s | PASS 0s | PASS 0s |
| new_project_question_card | PASS 0.9s | PASS 1.1s | PASS 1.4s |
| upload_st03 | PASS 2.5s | PASS 2.4s | PASS 2.9s |
| modeB1_click_no_size | PASS 53.1s | PASS 22.7s | PASS 40.3s |
| modeB1_fit_band_and_labels | FAIL 0.1s | FAIL 0.1s | FAIL 0.1s |
| modeB2_typed_name_known_size | PASS 28.5s | PASS 41.8s | PASS 32.2s |
| share_link | PASS 0.4s | PASS 0.9s | PASS 0.4s |
| share_logged_out_open | PASS 1.7s | PASS 1.6s | PASS 2.2s |
| share_revoke | PASS 4.2s | PASS 4.4s | PASS 5.2s |
| redo_in_3d | PASS 10.3s | PASS 5.9s | PASS 10.4s |
| modeA_new_project_upload | PASS 4.5s | PASS 3.3s | PASS 3.3s |
| modeA_build_lab | PASS 48.8s | PASS 30.9s | PASS 36.9s |
| modeA_open_editor | PASS 4.5s | PASS 4.5s | PASS 4.5s |
| A4_click_wiring | PASS 3.9s | PASS 3.8s | PASS 4.6s |
| add_real_object | PASS 5.4s | PASS 5.9s | PASS 6s |
| agent_editor_drop_ball_measure_g | PASS 19.4s | PASS 16s | PASS 4.2s |
| agent_physics_question | FAIL 30.1s | FAIL 30.1s | FAIL 30.1s |
| agent_offtopic_refuses | FAIL 30.4s | FAIL 30.1s | FAIL 30.1s |
| agent_voice_input | FAIL 30.1s | FAIL 30.1s | FAIL 30.1s |
| files_preview | PASS 1.9s | PASS 1.6s | PASS 1.5s |
| files_download | PASS 3.5s | PASS 2.4s | PASS 1.7s |
| upload_25mb | PASS 14.8s | not run | not run |
| files_delete | PASS 1s | PASS 1.5s | PASS 1.5s |
| mobile_375_workspace_top | PASS 3.8s | PASS 3.6s | PASS 4.1s |
| over_quota_21st_upload | not run | not run | PASS 19.7s |

| Step (fresh 4th account, pass 2) | Result |
|---|---|
| mode_chip_and_settings | PASS 2.3s |
| close_mode_settings | PASS 0s |
| agent_physics_question | PASS 5.3s |
| agent_offtopic_refuses | PASS 3.4s |
| agent_voice_input | PASS 15.5s |
| mobile_375_overflow | PASS 12.8s |

## Paid calls (estimate)
6 Mode B jobs (hosted sam-3.1, about 120 frames each, N23 rate $0.03 per 150 frames, about $0.14 total), 3 Mode A jobs (Modal A10G, about $0.34 each from N23, about $1.0 total), 5 muse-spark-1.3 turns (API returned usage only for 3: 1838/794, 1830/1110, 1906/563 tokens, each well under $0.01) and 1 muse-voice-transcribe call. Total about $1.2, inside the $10/day cap. Job costs are not in the POST responses, so these are estimates, not billed numbers.
