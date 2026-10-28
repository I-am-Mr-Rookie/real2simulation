# Worker health (S04e skeleton; real loop/dependency integration pending)

Reserve GET `/health/live`: 200 for a responsive worker health process; GET
`/health/ready`: 200 only while worker loop/heartbeat is current and required
Redis/bucket connections are available; 503 if stale, missing or unavailable.
Use the API health response shape with service `worker`; report required
dependencies only. Define heartbeat timeout with the real worker, not an invented
healthy constant. Bounded probes; never execute reconstruction or paid inference.

Public responses contain sanitized status and deployed revision only, never
queue contents/user IDs/credentials. A responding sidecar alone cannot establish
worker readiness. S04e adds the HTTP process, not a job loop. Readiness remains503
while heartbeat is unavailable. S04f probes Redis/bucket independently and returns
their real missing/failed/successful status, never an invented loop heartbeat.
