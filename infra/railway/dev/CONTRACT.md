# Dev integration handoff (apps deployed by S04g)

Current deployment IDs/URLs/revision: deployments.json. Web production build
runs on Railway; API ready200 proves read-only dependency operations. Worker
ready503 intentionally refuses to claim a consumer heartbeat. Sign-in fallback
remains unavailable pending secure Clerk configuration and owner S01b tests.
No source/config secret values fetched. Historical S04f contract follows.

S04f configures isolated dev-only web/API/worker/Postgres/Redis/object storage;
S04g deploys after local acceptance. Railway dev is approved; no judging,
candidate or production changes, resource purchase or legal acceptance implied.

Builds run on Railway. Web uses public library independently of private auth or
paid-job availability. API and worker expose separate live/ready checks per their
health contracts; route authorization cannot be delegated to a health endpoint.
Map external ingress paths to the service paths explicitly in S04g and retain
deployed SHA evidence; no hostname, URL or resource availability is asserted now.

Private environment variables belong in service configuration, not source,
fixtures, logs or client bundles. Inspect names only until authorized config work.
S04f uses provider-side references only (no credential values). IDs and names-only
receipts in resources.json; actual live adapter checks await S04g application deploy.
No bucket keys/Clerk secret is public; public Clerk publishable config must be
explicitly allowlisted. Missing services produce unavailable readiness, never fake
health. Keep the synthetic fixture visibly labelled; it is not Gate R/E4 evidence.
