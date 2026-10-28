# API health (S04e skeleton; S04f dependency integration)

Reserve GET `/health/live`: 200 iff the API process can respond; no downstream calls.
Reserve GET `/health/ready`: 200 only if required configured Postgres, Redis and
bucket checks succeed within bounded time; otherwise 503. Missing configuration
is unavailable, not a successful dependency. No paid inference/GPU readiness probe.

Body: `{ "service": "api", "status": "ok|unavailable", "revision": "<commit SHA or unknown>",
"dependencies": { "postgres": "ok|unavailable|not-configured", "redis": "...", "bucket": "..." } }`.
Liveness omits dependencies. Strings with `|` above describe alternatives, not literal
response values. Never expose env values, raw exceptions, internal hosts or keys.
Expose deploy revision separately at GET `/api/version` for later frozen-SHA proof.
S04f implements dev-only read-only adapters with a3s response deadline and bounded
pool. Missing required fields: not-configured; invalid/failed/disabled: unavailable.
API200 requires successful SELECT1/PING/HeadBucket, never config presence.
Health is not E2E/job readiness. Provider resources exist; app deployment/live
dependency success remain S04g work. See README.md for exact limits.
