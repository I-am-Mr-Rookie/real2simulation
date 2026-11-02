# N53-orch298 REPORT
Status: DONE for backend latency target; new code tested on DEV host in isolated overlays, not deployed. Warm A10G-container job 254.655 s; cold job 271.561 s, versus N47 recorded 667 s.
Owner overrides: deadline extended to 15:00 Dhaka; worker ceiling $5/job, separate from the collective $10/day visitor pool; explicitly approved the second public RM02 warm test.
Changed: fused strict binary mask validation into decode; two-worker ordered frame sampling; persistent room/shell stage timings. No dependency or web-source change.
Controlled checks: 426 actual cached masks identical to original strict codec; cached shell 34.151 -> 23.129 s with byte-identical scene; sampling 18.575 -> 11.337 s with all 16 PNG hashes identical.
Fresh stages cold/warm: L4 90.376/90.341 s; A10G 35.040/26.462 s; hosted SAM spans 49.675/41.357 s; lift+analysis 3.959/3.967 s; SF3D timeout 90.235/90.239 s. Upload not measured; full detail in evidence/N53/FINDINGS.md.
Warm means reused container, not cached model: second call still loads weights in 18.278 s. Cold model load 20.598 s. Both jobs include failed L4 attempts.
SPEND REVIEW 1: live_room.py L4 get budget 240 -> 90 s; cancel-before-retry; unconfirmed cancellation prevents retry and counts full reservation. GPU order, fallback budget, estimates, rates, idle windows and cap code unchanged.
SPEND REVIEW 2: sf3d.py client get budget 600 -> 90 s; cancel client/function timeout; unconfirmed cancellation retains original full A10G estimate. No remote resource/function-limit change.
SPEND REVIEW 3: room_shell.py stops further optional SF3D calls after a timeout, retaining labelled boxes; existing single-container pool stays sequential.
SPEND REVIEW 4: paid_probe.py guards a separate worker ledger at $5/job. No visitor quota-setting change; shared GPU queue used. Isolated /tmp code only; deployed source hashes unchanged.
Paid: cold $1.12006113 + approved second job $1.11689456 = $2.23695569 estimated; 352 SAM images, 4 MapAnything attempts, 2 SF3D attempts; 358 settled rows, zero unsettled. UTC/model/units/cost in ledger.json and warm-ledger.json; not invoices.
Checks: required production-pinned uv pytest suite 117 passed, also checked with Modal 1.6.3; git diff --check PASS. Source/hash and ledger arithmetic assertions pass.
Extra QA finding: both actual scenes pass 5/5 isolated table drops but only 4/5 full-scene drops; room-object-5 is obstructed by generated scene geometry. SIMULATED only; not fixed or concealed.
Risks: SF3D cold initialization remains too slow; both timed out and all furniture stayed labelled boxes. New five-minute result is not equal mesh quality to N47's two successful meshes.
Evidence: evidence/N53/live.json, warm.json, summary.json, n47-baseline.json, physics-cold.json, physics-warm.json; scale unverified, geometry MODEL-ESTIMATED.
Skipped: no deploy/push, browser upload/BFF E2E, private owner room, invoice reconciliation or physical calibration. No web-source change, so Node suite/Next build not run.
Controller: cross-vendor spend review, merge/deploy DEV, then deployed browser E2E and separate geometry-quality follow-up. Worker charges stay separate from visitor quota.
Timebox: direct owner extension to 09:00 UTC is recorded; legacy checker only supports exact 30/60-minute windows and cannot validate this extended receipt without manual acceptance.
