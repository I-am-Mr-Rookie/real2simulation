# N11-orch260 REPORT
Status: PARTIAL. Infra, sample project and deploys done; hosted Meta calls fail from Railway (egress region), so live experiment and agent turn did not work on DEV.
Changed: api.Dockerfile (ffmpeg/ffprobe, modal==1.6.3, node kept); stage.py ships Build/gpu, guardrails, measurement, reconstruction, lab-editor bridge files, N07 result;
 Build/api/storage/sample.py + __init__.py hook seeds one SAMPLE (RECORDED) project per user on first files/projects list (RM04 room job from the sha-checked display bundle + ST03 apple result from evidence/N07; no video bytes; bundle absent or altered: experiment only);
 variable names only in variable-references.json; deployments.json and verify.py revision 032922d.
Railway: volume api-volume 053fb364 mounted /data; R2S_DATA_DIR=/data; MODEL_API_KEY/BASE_URL and MODAL_TOKEN_ID/SECRET set from .env by CLI stdin (values never printed; remote equals local checked by comparison only).
Deploy: api cd0230fa and web 53b1b733 SUCCESS from 032922d; verify.py exit 0. In container: ffprobe 7.1.5, node v22.23.4, modal 1.6.3.
Tests: tests/api-storage (13) OK incl. 5 new sample tests; test_stage.py (9) OK; staged api context imports and lists the room/experiment/gpu/agent routes.
DEV smoke (headed Chromium, fresh clerk_test account, evidence/N11/smoke.json + shots): SAMPLE project and done experiment visible via API; upload 5 s ST03 clip OK (quota 1/20); GPU dot green (modal+jobs); sample files list empty as intended.
FAIL 1: experiment on DEV -> TRACKER_UNAVAILABLE (Meta API 404 model_not_found). Cause: from Railway egress (SG) the same key lists NO models on GET /models; from Dhaka it lists all 9. Same 5 s clip locally: ok, 150 frames. Agent turn on DEV -> 502 for the same reason. Fix needs owner call: Railway region with access, or route Meta calls via Modal/other egress.
FAIL 2 (not my Owns): GET /internal/workspace/rooms has no list route (405), so the Processing card says Request failed (405); the Projects card does not list the SAMPLE project, only experiments appear.
Paid calls (UTC 2026-11-01, ~12:34 to ~12:46): sam-3.1 via DEV x2 and one agent muse-spark call via DEV, all Meta 404, no frames billed, daily cap settled at full reservation (<=$0.03 each); one local sam-3.1 run on the 5 s clip, 150 frames, $0.03 (temp cap DB, not the DEV cap); one uncapped container /responses probe, 404. Modal: none.
Skipped: Mode A room on DEV (needs GPU spend, no list route); agent lab bridge run; WORKSPACE_UPLOAD_DIR left /tmp for the legacy route.
Risks: spend.sqlite3 now on the volume (cap persists across deploys); Railway SSH key prompts a passphrase intermittently; api redeploy resets nothing in /data.
