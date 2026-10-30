# S18f → S18g guest interface

Unwired, local-only delivery. No deployment, publication, UI or health-app edits.

## Server integration

Import `create_app` from `Build.library.guest`; instantiate it with the trusted
checkout/bundle root (default: module's repository root). Either serve the factory
or mount its ASGI app at `/` so these paths remain unchanged. Root `/api/library`
routes contain no authentication dependency, cookies, provider or paid calls.
Required installed dependencies are the existing FastAPI/jsonschema stack and
the offline custody validator's existing imports. No dependency installs.

Bundle the accepted five catalogues + their content-addressed objects and audit
evidence required by `validate_file` (clips/approval/registry, report/ledger/source
references, S12f fallback and Gate RS receipt). Missing/revoked/corrupt custody
returns a generic 503, never a path or partially validated catalogue.

## HTTP contract

| Request | Response |
|---|---|
| `GET /api/library/manifest` | 200 JSON `schema_version: guest-1.0.0`, `audience: anonymous-guest`, `scope`, `defaults`, `demos[]`; no-store |
| `GET /api/library/artifacts/<64 lowercase hex>` | 200 verified JSON bytes, immutable public one-year cache, quoted SHA ETag, Content-Length, nosniff |
| Invalid ID | 400 JSON `{"error":"invalid_artifact_id"}`, no-store |
| Valid but unexposed/unknown hash | 404 JSON `{"error":"artifact_not_found"}`, no-store |
| Invalid/missing/revoked catalogue/custody | 503 JSON `{"error":"library_unavailable"}`, no-store |
| Artifact response hash/size mismatch | 503 JSON `{"error":"artifact_unavailable"}`, no-store |
| Non-GET | Framework 405; no mutation occurs |

Demo fields: `id`, `title`, `source` (existing attribution/licence where applicable),
`label` (`SIMULATED` or `SCALE_UNVERIFIED`), `scale_label: SCALE_UNVERIFIED`,
`scale_verified: false`, `display_only: true`, `availability: metadata-only`,
`gates`, `limitations`, `defaults`, `artifact`, optional `challenge`.
The manifest's selected default is the simulated answer-free Mystery-g setup.
Defaults contain `demo_id`, `autoplay: false`, `physics_enabled: false`,
`real_scene_prediction: WITHHELD`, `parameters: []`.

Unavailable entries are `apollo`, `bounce`, `rm05-scene`; each has title,
`label: UNAVAILABLE`, `availability: unavailable`, reason and `artifact: null`.
Do not fetch or launch an unavailable entry.

Artifact fields: `kind`, `media_type: application/json`, `sha256`, `bytes`, `href`.
Fetch the **exact href** and verify SHA/byte bound before use. Do not construct a
route from source SHA, local object path, provenance report or audit references.
Only guest-manifest object hashes are HTTP-addressable; disk object enumeration
and arbitrary-hash retrieval are intentionally absent.

- `scene-descriptor`: original scene-v1 descriptor. It can describe absent assets;
  **not** a viewer-ready bundle. No referenced PLY/raw frames are exposed here.
- `simulation-setup`: a new content-addressed setup-only JSON projection with
  `source: simulated`, template, source-backed duration/time-step,
  `display_only: true`, `availability: metadata-only`. Not an experiment spec or
  replay. Original acceptance hash/metrics/gravity are never guest artifacts.
- `challenge-record`: original validated answer-free setup bytes. Preserve its
  `answer_visibility: withheld-until-fit`; use the existing `/lab` challenge/fit
  contract for any reveal, **not** the guest endpoints.

Never infer calibrated scale, playable availability, physical success or Gate D
from HTTP success. No `Build/web` integration was necessary for this scoped task;
S18g must respect its own Owns and use the existing viewer interface, not edit
CLAUDE-owned modules. Deployment or raw-media exposure requires separate scope.

## Custody / caching tradeoff

Every valid request revalidates current catalogue authority and evidence. This
avoids a stale startup snapshot serving revoked sources, at the cost of repeated
offline schema/hash checks. A future cache must invalidate on authority/evidence
changes. Previously cached public immutable descriptor bytes cannot be revoked
from clients by this server; no confidential/raw media is included in them.
