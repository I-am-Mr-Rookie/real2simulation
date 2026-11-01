N35-orch277 DONE. GPU queue lease + heartbeat.
Changed: Build/api/gpu/__init__.py (queue code lives here; Build/gpu/ondemand.py unchanged, 900 s scale-to-zero kept).
- Every unfinished job has heartbeat_at. start() spawns a daemon heartbeat thread (every 20 s, stopped by finish()); waiting jobs beat on each start() poll.
- No beat for 90 s: job failed with "GPU job stopped responding", next job starts (start() and status() both reap). Reaped job cannot start/beat again (JobStopped), finish() raises.
- Cap: enqueue(..., reservation=rid, cap_db=path) stores the daily_cap id. Reaped started job: settled once at its reserved amount (may have run, no free run). Never started: settled 0 (released). Runner-settled first or late runner settle: ValueError, no double charge.
- Old gpu_jobs DBs get the 4 new columns automatically; pre-lease unfinished rows count as expired.
Checks: pytest tests/gpu tests/guardrails/test_daily_cap.py tests/n21 tests/reconstruction/test_live_room.py = 43 passed (evidence/N35/pytest.txt). New tests/gpu/test_lease.py (8); test_ondemand T0 now real time.
Paid calls: none. No deploy.
Risks: (1) Build/reconstruction/live_room.py (not in Owns) must pass reservation=rid, cap_db=cap_db to gpu_jobs.enqueue for cap settlement on a crash; until then queue recovery works but the reservation stays open (counts at full estimate, conservative). (2) A hung but alive process keeps beating (Modal timeout=300 bounds the remote call). (3) Uses private daily_cap._connect/UNIT to read the reserved amount. (4) Heartbeat is per process; multi-process sharing one SQLite is fine.
