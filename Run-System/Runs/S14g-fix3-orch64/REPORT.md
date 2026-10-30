# S14g-fix3-orch64 REPORT — DONE (Gate A MET at spec-contract scope; see limits)
Lane CODEX-1; anthropic/claude-opus-5-5/high; coding quota OpenCodex-managed; not polled. Tokens unknown.
UTC: worker start 04:57:38; controller-reissued window 04:58:49–05:28:49; live run 05:05:53–05:11:42; work stopped/report see TIMEBOX.json.
Branch run/S14g-fix3-orch64 from main 34886b9. Historical S14g/S14g-fix evidence untouched.

## Result (evidence/S14/S14g-fix3-live.json, measured)
- 10 distinct recorded cases, case_id = approved clip id (RM02 RM04 RM05 PD02 PD03 PD04 PD06 PJ03 ST03 BN01), each with source sha256 checked against evidence/clips/S02c-acquisition.json before use, keyframe-manifest sha, scene-context sha, frame indices/times, licence/source URL.
- Wonder: 10 calls, 10/10 contract-valid first attempt, 0 retries. Templates chosen: pendulum for all 4 PD clips, free_fall RM04/ST03/BN01, projectile RM02/RM05/PJ03 (RM02 empty classroom -> hypothetical projectile; plausible-but-weak).
- Valid specs 10/10 (>=9 required); invented numbers 0 by independent oracle (S14g_fix_oracle) over every visible string of specs and the 30 shown turn texts; 30/30 Spark turns, 30 model replies shown, 0 fallbacks.
- summary.gate_a = MET; coverage check strict (distinct_recorded_scenes 10/10; stub replies force NOT_MET).
- Offline replay of saved recorded responses (S14g-fix3-offline.json, spec_sources all "recorded"): same MET, 10/10.

## F4 persistence
- S14g-fix3-recorded.json: sanitized accepted Wonder output text per clip (no headers/keys). live.json keeps per spec: accepted_text, accepted_response, template, answers, validated spec, hashes; per turn: accepted_response, exact tool_outputs (incl. 14 mystery turns) + sha256, shown text.
- Fresh re-audit: 30/30 turn tool_outputs sha match; 10/10 saved accepted_text re-validate to the saved accepted_response. rg for bearer/api_key/authorization in new files: 0.

## Spend (Meta, evidence/S14/S14g-fix3-ledger.jsonl)
- 40 calls (10 Wonder keyframe + 30 Spark), est $1.186 (cap $2.50); billed unknown; $120 hard stop/$30 reserve untouched (live_post meta check over all S14*ledger files).
- Note: Wonder input_tokens ~811-816 per 3-image call -> provider usage may not count images; est may undercount. Reservation was chars/2 worst case.

## Limits (controller/R-A must judge)
- Spec validity = contracts.experiment validate() (numeric spec contract) after interview answers. Authoritative-bundle validate_setup is UNAVAILABLE for real clips (no scene bundle with known scale; S05d abstained); the evidence script swaps interview.validate_setup for validate() during the call only (restored in finally). Recorded per case as bundle_bound. If Gate A requires bundle-bound specs, this is PROVISIONAL.
- Interview answers are the hand-written SYNTHETIC S14c answers per template, not user answers.
- Turns run on synthetic-room-v1 simulator/fitter outputs (as before), not on clip measurements.
- RM02 (897 s) fails upload duration policy -> 3 ffmpeg-seek frames at 10/50/90% (time_source labelled); others use S13c keyframes sampled to 3. Frames kept in %TEMP%/S14g-fix3-kf, not committed.

## Ponytail
- Reuse: S14g_fix_gate_a (oracle, visible_strings, turn, summary, live_post+ledger+caps via module globals), S13c keyframes.extract/provenance, S13e understand.clip_context/sample/build/frame_jpeg, interview.answers_to_spec, tsv.fixture. New: one evidence script (~150 lines); no product code, contract or record_muse.py change (S20 interface untouched).
- Skipped: dedicated unit test for the evidence script (its offline mode is the self-check: stub -> NOT_MET, recorded -> replay); mutation runs; UI/pipeline suites.

## Checks (fresh)
- python evidence/S14/S14g_fix3_gate_a.py offline (stub: plumbing, gate NOT_MET as required) -> live -> offline replay (MET).
- python -m unittest tests.agent.test_visible_text tests.agent.test_contracts tests.agent.test_reply tests.agent.test_trial tests.agent.test_retry tests.agent.test_interview tests.agent.test_muse -> 52 OK.
- python evidence/S14/S14g_fix_oracle.py -> corpus 29, oracle_agrees true.

Next: R-A re-review of F3/F4 at this scope; decide whether bundle-bound validation is required for Gate A.
Communication: silent; one completion line to controller.
