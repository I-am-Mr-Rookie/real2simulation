# N30-orch275
Status: PARTIAL. Code, tests and Modal deployment complete; one RM02 smoke could not run before cutoff because L4 capacity was unavailable.
Branch: run/N30-orch275. Owns extension: live_room.py and its tests approved by controller.
Change: image_spec.GPU=L4; scene_job returns measured hardware name/type and per-call peak allocated bytes.
Fallback: existing deployed reconstruct Function, dynamic with_options(gpu="A10G"), one retry for OOM/no capacity only.
Capacity: named ROOM_START_BUDGET_S=120; spawn/get timeout cancels its input before A10G dispatch; fallback also has a bounded get.
Spend review hunks: Build/reconstruction/live_room.py GPU constants/import, modal_reconstruct(), retry_on_a10g(), run_job() per-attempt reserve/settle and summed result cost.
Spend review hunks: Build/gpu/image_spec.py GPU default; Build/gpu/cost_log.py pricing-source comment (existing numeric L4/A10G/CPU/memory rates unchanged).
Cap: separate GPU-specific reservation/settlement per attempt, including each pool's 900s idle; unknown failures conservatively charged, retry denied if cap is exhausted.
Checks: uv, Python 3.12, repo FastAPI 0.124.4, numpy 2.2.6, httpx 0.28.1, jsonschema 4.23.0; tests/gpu + tests/reconstruction/test_live_room.py + 3 legacy GPU files: 50 passed, one dependency deprecation warning.
Initial unpinned FastAPI run: 31 passed, unrelated health-route test failed against newer FastAPI; reran successfully with project pin. git diff --check passed.
Deploy: existing r2s-ondemand, modal 1.6.3, success in 9.155s; evidence/N30/deployment.json. No changes to ondemand.py or Build/api/gpu, no Railway deploy.
Paid job: UTC 2026-11-01T20:32:41Z, MapAnything Apache, ONE RM02/Pexels room job, 8 sampled frames; no second paid smoke or A10G invocation.
Cost: daily_cap reserved AND settled USD 0.40855680, full 240s startup + 300s execution + 900s idle envelope, below USD 0.50; not a provider bill. Final receipt: evidence/N30/run.json.
Live: own client stopped at cutoff; at 20:49:16 UTC reconstruct backlog=1, runners=0, running_inputs=0; wall wait 995.528s, no GPU/memory result. Original smoke used blocking remote before the start-budget fix.
Cancellation limitation: FunctionCallList returned UnimplementedError; did not stop/redeploy the app or cancel any other worker's call.
Skipped/unverified: real GPU peak, hardware identity, inference wall time, live A10G retry, combined provider billing. Local daily_cap ledger is not global provider aggregation.
Risk: a queued remote input can execute later. Controller must watch backlog; cost/spend diff needs Claude acceptance review before merge.
