# Shell integration contract v1.0.0 (S04a)

S04a defines contracts; S04b adds the local Next.js shell, empty public library
and deny-all private route. Clerk, scene playback, API/worker endpoints, queue,
uploads and deployment are not connected. Schema acceptance is NOT access
control, scene safety, physics readiness or Gate evidence.

## Ownership and dependency direction

| Owner | Paths | Boundary |
|---|---|---|
| CODEX-2 S04 | `src/app`, `src/shell`, `src/auth`, web package manifest; API/worker health; dev infra | Route composition, identity, transport, slots and loading/error states |
| CLAUDE S09 | `src/viewer`, `tests/viewer`, `evidence/S09` | Viewer adapter, geometry, render loop and GPU lifecycle |
| CLAUDE S15 | `src/workspace`, `tests/workspace`, `evidence/S15` | Workspace/editor UI; consumes shell and viewer interfaces |
| CODEX-1 S05 | `contracts/scene`, reconstruction, synthetic scene bundle | Scene-v1 producer/validation |
| CODEX-1 later pipeline | Queue-assigned API/pipeline paths | Job producer, artifact storage and authorization |

`src/*` paths above are relative to `Build/web`; tests, evidence and contracts are
repository-root paths.
QUEUE remains the exact write authority. Consumers import/read contracts; never
edit another lane's module. Shared package/lock changes are serialized through
CODEX-2; S09 requests dependencies rather than writing the manifest. This run adds
no package manifest or lockfile. No React/Next/Three version is prematurely pinned.

Dependency direction: app composition -> shell/auth + injected viewer/workspace.
Shell never imports viewer internals. Viewer never imports app routes or Clerk.
Avoid duplicate scene JSON, fixture copies and revalidation on every render frame.

## Routes and mount points (S04b composition; integrations reserved)

| Route/slot | Audience | Input and behavior |
|---|---|---|
| `/` | public | Product entry; link to guest library even without Clerk config |
| `/library` | public | Explicit allowlisted library entries, no private catalog |
| `/library/[entryId]` / `viewer` slot | public | Resolve entry server-side; public scene reference -> viewer |
| `/workspace/[sceneId]` / `workspace`, `viewer`, `job-status` slots | signed in | Verify ownership before resolving any scene, job or assets |
| `/sign-in`, `/sign-up` | public | Clerk UI boundary, added S04c; no custom Google client |

App owns page/layout and responsive slot containers; viewer owns its canvas and
controls within the supplied element. Loading, unavailable, invalid-artifact and
failed-job states must be explicit; no fake completion or silent fixture fallback.
Fixture mounting is opt-in dev/library content, never an upload-processing fallback.
The test mount is repository-local; never expose the repository root or .env as a
static directory. `reserved_route` is a future route, not evidence it responds.

## Viewer adapter (S09 implements; no implementation here)

Public API shape, independent of React/framework:

```typescript
type ViewerHandle = { dispose(): void };
type ViewerAdapter = {
  mount(host: HTMLElement, request: ViewerRequest, services: {
    loadScene(scene: SceneReference, signal: AbortSignal): Promise<ValidatedSceneBundle>;
    signal: AbortSignal;
    onState(state: 'loading' | 'ready' | 'unavailable' | 'error'): void;
    onError(error: { code: string; message: string }): void;
  }): Promise<ViewerHandle>;
};
```

`ViewerRequest` and `SceneReference` are JSON shapes from `integration.schema.json`;
`ValidatedSceneBundle` is the existing scene-v1 manifest plus resolved asset bytes
validated against `contracts/scene`, not a new coordinate format. No transport URL,
JWT, secret or owner ID enters the viewer DTO. Transport stays injected and must
authorize every request; reference `access` and `audience` fields are descriptive,
never proof of identity. Reject schema/scene version mismatches explicitly.

Shell aborts previous mount before replacing scene/route and ignores callbacks from
superseded mounts. Adapter must reject an aborted mount, clean partial resources
on failure, and return an idempotent disposer on success. Dispose removes listeners,
animation loops and GPU resources; no callbacks after disposal. Unmount never
cancels a server processing job. S09 owns lifecycle and browser tests.

Scene-v1 uses right-handed +Y-up metres and seconds, world coordinates, xyzw
quaternions and local -Z camera forward. Scale has already been applied. Preserve
unknown gravity and synthetic labels; loading a scene cannot enable physics.
Render all labels/errors as plain text. Mystery-g cannot rely on merely hiding a
number in the UI: S10 must provide a redacted consumer payload before mystery mode
loads any data containing hidden gravity. No such secret-safe payload exists yet;
keep mystery mode disabled until that contract is implemented.

## Jobs and library DTOs

`integration.schema.json` is authoritative for JSON structure; closed versioned
viewer/job/library variants. Examples are explicitly synthetic integration inputs,
not running jobs or reconstructed scenes. Consumers use Draft 2020-12 validation;
the existing Python jsonschema dependency suffices for offline checks.

Job states: queued -> running -> ready/failed/cancelled, or queued -> failed/cancelled.
Terminal states never transition; retry creates a new job ID. Producer increments
`revision` for each update, consumer ignores equal/older revisions. Only ready has
a scene result; only failed has a sanitized error. Ready means an artifact is
available, NOT measured accuracy, simulation success or a passed gate. Authorization
failure is an HTTP error, not a job snapshot disclosing someone else's job ID.
No fabricated percentages, durations, physical numbers or spend values. Future
poll/SSE transport must preserve this shape; transport/auth implementation belongs
to later pipeline runs. No polling loop is added now.

Library entries only reference the server allowlist of public artifacts approved
for release. The synthetic fixture needs no footage rights; sourced media must
retain clips.csv credits and Koushik's approval before inclusion. Public DTOs
contain no owner data/private storage paths. Reconstructed is provenance, not a
quality claim. Guest library playback stays available when uploads/spend are paused.

## Offline checks

From repository root:

```powershell
python -m unittest discover -s Build/web/src/shell -p test_contract.py -v
python contracts/scene/validate_scene.py test-data/synthetic/scene/room-v1/scene.json
```

These verify DTO structure and an existing synthetic bundle only. Auth/E2E,
renderer lifecycle, public route responses, jobs and Railway health remain later
S04/S09/pipeline acceptance. Breaking contract changes require a new version and
coordinated migration; do not silently reinterpret v1.

## Local shell (S04b)

From Build/web, Node >=20.9:

```powershell
$env:NEXT_TELEMETRY_DISABLED='1'
npm install --package-lock=false --ignore-scripts --no-fund
npm run build
npm run smoke
npm run start -- --hostname 127.0.0.1
```

Smoke starts and stops its own production server on an available loopback port,
checks public pages, private denial and unknown-route 404s, and checks source
ownership isolation. It does not use credentials or call any backend. Run smoke
again after building changes: it tests the compiled production output.

Exact direct dependency pins come from the registry; no root lockfile is written
because it is outside this run's Owns. Transitive resolution is not locked yet.
Webpack build is selected using Next's documented flag; no root config/TypeScript
files are generated. Three is installed for the S09b renderer request, but the
shell does not import it or the viewer/workspace implementation.

Reference: [official Next.js installation](https://nextjs.org/docs/app/getting-started/installation).
No remote fonts/assets. The camera illustration is authored SVG, explicitly not
scene evidence. Library remains empty; no synthetic fixture is published.
