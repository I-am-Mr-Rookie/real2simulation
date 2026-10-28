# Railway dev handoff (S04f/S04g)

## Verifier regression (S04g1)

`python -m unittest discover -s infra/railway/dev -p test_verify.py -v`
runs synthetic offline responses through the real verifier CLI; no network or
credentials. `python infra/railway/dev/verify.py` performs read-only live dev GETs.
API/worker responses must match their exact service and pinned source revision.
Health status must be `ok`, except worker readiness: HTTP503, `unavailable`,
Redis/bucket `ok`, heartbeat `unavailable`. API readiness requires all three
dependencies `ok`. `/api/version` has service/revision, not a required status.
The worker503 acceptance attests only to the expected unavailable sidecar state,
not consumer readiness. Web checks and unavailable auth/private boundaries stay
unchanged. Neither offline success nor live HTTP success proves event gates.

S04g deployed source300cd2096f9e32bcdf3433520b36b67f709df0d5. Exact service,
deployment IDs and URLs: deployments.json. Live HTTP evidence and context hashes:
Run-System/Runs/S04g/. Provider reports SUCCESS for all three apps. Web production
Next build succeeded on Railway; / and /library200. Sign-in is an explicit
unavailable fallback (no Clerk configuration), private workspace404. Not auth E2E.

API /health/live200 and /health/ready200: live Postgres SELECT1, Redis PING and
bucket HeadBucket succeeded. Worker /health/live200, /health/ready503 with Redis
and bucket ok but heartbeat unavailable. No job consumer exists. /api/version on
API/worker matches source revision. This proves read-only dependency connectivity,
not model inference, job completion, browser rendering, event gates or judging.

## Reproduce the isolated build context

From the committed checkout, run `python infra/railway/dev/stage.py api <new-dir>`
(also worker/web). It reads only tracked committed allowlisted event sources,
never .env/archive/research/uploads; writes a SHA256 context manifest and selected
Dockerfile. Upload ONLY that fresh directory using `railway up --detach --project
<projectId> --environment <devId> --service <serviceId>` with IDs from deployments.json.
All processes bind8080/default PORT. Railway healthcheck API/worker=/health/live,
web=/. Root image module paths retain the shared dependency probe. Build/runtime
credentials are supplied by existing Railway references, never the uploaded context.
No web secret was fetched/copied/configured. Run `python infra/railway/dev/verify.py`
for this pinned deployment's read-only ten-endpoint acceptance checks.

Staging safety validations run in normal AND optimized Python: invalid service,
missing committed sources/Dockerfile, forbidden source paths and existing output
directories fail before writes. The destination is claimed exclusively after
validation, so a competing creator is not overwritten. Partial output after a
later Git/storage failure is retained for inspection; choose another fresh path,
never merge it into an existing context. `python -m unittest discover -s
infra/railway/dev -p test_stage.py -v` uses only synthetic Git blobs/temporary paths.

## S04f historical provisioning record

Private project Real2Simulation, only environment dev. IDs, provider statuses and
names-only variable receipts: resources.json. Reference expressions only:
variable-references.json. No credential values/exports stored here.

Created under existing dev-deployment approval: no account, upgrade, purchase,
terms acceptance, production/judging environment or changes to unrelated projects.
Official Postgres18/Redis8.2 templates generate credentials inside Railway;
singletons, one persistent volume each (default maximum capacity50,000MB each,
not measured stored usage). Both deployments reported SUCCESS. Normal ongoing
Railway usage accrues; actual charges/balance unknown, not zero. Private bucket
region sin. No file uploaded; no public domain created.

api/worker/web are source-less service placeholders for S04g. API/worker reference
variables set with skipDeploys=true; provider names-only read confirmed expected
fields and withheld all values (valuesRedacted=true). Web gets no DB/Redis/bucket
credentials. No Clerk credentials copied/provisioned. Provider deployment SUCCESS
and variable names are NOT proof of resolved references or app connectivity.

## S04g verification

1. Use exact project/environment IDs; dev only. Deploy event-work-only build
   context, never the entire event folder/private archive.
2. API/worker images use repository-root module resolution/shared probe module
   and their own requirements. Process health check is /health/live, NOT the
   worker readiness endpoint. Web production build remains separate.
3. Confirm deployed revision, API live200/ready200 with all dependencies ok.
   Worker live200/ready503 until a real consumer heartbeat exists. Dependency
   failures remain503. Debug sanitized states/references, never credential values.
4. Verify bucket reference resolution, virtual-hosted URL and live HeadBucket.
   No uploads/application writes inferred. Auth, E4/jobs and event gates NOT RUN.

## Official sources consulted

- [Railway private buckets, URL style, variable names](https://docs.railway.com/storage-buckets)
- [Psycopg connections](https://www.psycopg.org/psycopg3/docs/api/connections.html)
- [redis-py connections](https://redis.io/docs/latest/develop/clients/redis-py/connect/)
- [Boto3 HeadBucket](https://docs.aws.amazon.com/boto3/latest/reference/services/s3/client/head_bucket.html)

No S04g app deployment, public exposure, publication or submission in this run.
