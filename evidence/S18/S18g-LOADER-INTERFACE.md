# S18g guest-entry loading / viewer boundary

Local, unwired ESM: `Build/library/loader.mjs`. No app/viewer module changed.

## One-call /library hookup (later app owner)

From `Build/web/src/app/(public)/library/`, the exact relative import is:

```js
import { loadLibraryEntry } from '../../../../../library/loader.mjs';

const loaded = await loadLibraryEntry(entry, { signal: controller.signal });
```

`entry` is a selected `guest-1.0.0` manifest `demos[]` object, not a local
catalogue object. Default transport is browser `fetch` to the exact same-origin
artifact href. Tests/other transports may inject `fetch`. Requests omit credentials,
reject redirects, forward cancellation, and never resolve source/audit paths.
Catch `ViewerError` (`INVALID_ARTIFACT`, `UNSUPPORTED`, `LOAD_FAILED`) and display
its authored message as plain text. Abort errors mean the selection was cancelled.
Render title, banner, reason, attribution and limitations using React text or
`textContent`, never `innerHTML`. Clear old content on selection change; do not
leave a previously rendered scene visible beneath a new metadata/unavailable label.

Returned fields:

- `id`, `title`, `label`, `availability`, `banner`, `reason`, `canMount`,
  `viewerRequest`, `metadata`.
- Available metadata additionally retains `scaleLabel: SCALE_UNVERIFIED`,
  `displayOnly: true`, cloned safe `defaults`, `source` attribution, `gates`,
  and `limitations`. Result is recursively frozen without freezing the input.
- `UNAVAILABLE`: no fetch, `metadata`/`viewerRequest` null. Apollo retains
  **Moon result not measured**. Bounce and RM05 remain unavailable too.

## Kind mapping and honest limitations

| Guest kind | Validated result | Viewer boundary |
|---|---|---|
| `simulation-setup` (free-fall, projectile, pendulum) | Exact answer-free setup keys, positive finite source duration/time-step, known template; SIMULATED | `viewerRequest: null`; no scene/trajectory exists in this artifact |
| `scene-descriptor` (RM02/RM04) | `checkManifest` with `DEFAULT_LIMITS`; reconstructed, scale unverified, display-only | Exact `checkViewerRequest`-validated guest/inspect request, scene ID/version from descriptor; **not** a bundle |
| `challenge-record` | Exact answer-free keys, `withheld-until-fit`, `/lab` target; SIMULATED | `viewerRequest: null`; use existing /lab toggle + server fit, never viewer mystery mode |
| unavailable | Reason only, no artifact | Never mount/fetch |

**Every current entry has `canMount: false`.** This is an upstream fact, not a
loading success promoted to readiness: S18f exposes no PLY bytes or simulation
trajectories; current `createThreeViewer().mount()` needs `{manifest, assets}`
from `loadScene`, and explicitly rejects mystery mode. A setup JSON object is
not scene-v1. Do not pass it to `decodePlyXyzRgb`, invent point geometry, route
local provenance paths, or substitute `synthetic-room-v1` for a selected demo.

For a future separately approved **actual scene bundle mount**, the unchanged
viewer interface is exactly:

```js
// Only after canMount is established by a future asset-availability integration:
const handle = await createThreeViewer().mount(host, loaded.viewerRequest, {
  loadScene: createArtifactLoader({ bundleUrl: approvedBundleUrl }),
  signal: controller.signal, onState, onError,
});
// handle.dispose() on unmount; the existing viewer rechecks bytes/SHA and decodes PLY.
```

`approvedBundleUrl` is a trusted scene-ref-to-directory resolver, not a descriptor
source URL; no such public mount is provided or inferred here. Consequently this
snippet is the exact later boundary, **not** current runnable playable wiring.
The loader itself never imports Three.js, mounts a renderer, invokes physics,
enables autoplay, fits, calls models/GPU, or changes any gate.

Real descriptors use the existing `SCALE_UNVERIFIED_BANNER`. Simulated metadata
gets an explicit SIMULATED/setup-only banner, **not** `SYNTHETIC_BANNER`, whose
wording denotes authored fixture geometry that these entries do not contain.
If actual synthetic geometry is later rendered, the existing viewer owns that
fixture banner and `decodePlyXyzRgb`/render limits; no duplicate decoder exists.

## Deferred playable follow-up: exact missing inputs by kind

Controller receipt in this worker chat approves DONE for metadata loading +
validated viewer-request boundary; playable asset/replay wiring moves to a new
controller row. The missing inputs are:

1. **RM02/RM04 `scene-descriptor`**: unchanged `createThreeViewer().mount()` needs
   `loadScene(sceneRef, signal)` resolving `{ manifest: <scene-v1 object>,
   assets: { [manifest.render.asset_id]: Uint8Array } }`. Current descriptors
   specify `render.kind: points`, `point_count: 20000`, main `points`, mobile
   `points-mobile`. The transport must serve descriptor-as-`scene.json` plus the
   exact content-hashed bytes below, after accepted licensing/exposure checks.
   The current loader fetches only main; full bundle validation also needs the
   declared mobile asset (do not promise mobile availability without it).

   | Descriptor | Asset path | Declared bytes | SHA-256 |
   |---|---|---:|---|
   | RM02 | `points.ply` | 753214 | `e46814613ca923d069663a5d295d360b1b1ada989563d839308ca1d9639b1399` |
   | RM02 | `points-mobile.ply` | 188332 | `61090c838d261542cb6ca21bf03f09e050556c1a0516ba5f5061e955bb7aab20` |
   | RM04 | `points.ply` | 752219 | `9f0c0bd9dd308549bbedc5e1702c0bdf16046123439129959e657e51d0e82385` |
   | RM04 | `points-mobile.ply` | 188327 | `e4ce5b06f300e6a88e1f930aa10879b98b1f90922d7c288ebd92346fa2d5e432` |

   Values above are copied descriptor declarations, **not verified downloaded
   bytes**. PLY is ASCII 1.0, vertex-only, header properties in exact order:
   `float x`, `float y`, `float z`, `uchar red`, `uchar green`, `uchar blue`;
   rows are finite XYZ plus integer RGB in [0,255]. Main vertex count must equal
   descriptor point_count; decoder and SHA validation stay viewer-owned.

2. **Free-fall/projectile `simulation-setup`**: no render bytes, initial state,
   gravity, seed or trace are present. Existing simulator output in
   `Build/simulator/trajectories.mjs` has `kind` (`free-fall`/`projectile`),
   `source: simulated`, `inputProvenance: synthetic`, `integrator: rk4-fixed-step`,
   `dt_s`, `requestedSteps`, `samples`, `stopPlaneY`, `stop`. Each sample is
   `{ step, time_s, position_m: [x,y,z], velocity_m_s: [vx,vy,vz] }` with finite
   dense vectors and fixed step/time. The new row must supply an accepted,
   bounded, hashed simulator-produced trace and its source/validation custody;
   timing-only guest setup cannot regenerate it. **The viewer has no trajectory
   input parameter**: an authorized replay/render adapter is also needed, plus
   an actual accepted scene-v1 geometry bundle if using this 3D viewer. Do not
   invent geometry or claim that samples alone are a `ValidatedSceneBundle`.

3. **Pendulum `simulation-setup`**: same missing scene/render adapter and bounded
   trace. Existing `Build/simulator/extended-templates.mjs` output has
   `kind: pendulum`, simulated/synthetic labels, fixed-step integrator, `dt_s`,
   `requestedSteps`, `units`, `analyticComparison`, `samples`. Samples add
   `angle_rad` and `angular_velocity_rad_s` to the same step/time/position/velocity
   fields. Accepted length/initial angle/angular velocity/gravity/validated setup
   are absent from guest metadata; never infer them from duration/time-step.

4. **Mystery-g `challenge-record`**: no viewer-compatible bundle or trajectory is
   exposed, and current viewer mystery mode explicitly refuses. Reuse the existing
   `/lab` server-owned challenge/fit path, not an unredacted stored replay. A
   future separately owned rendering path must define/validate its redacted trace
   DTO while preserving `withheld-until-fit`; there is **no existing accepted
   viewer mystery-trajectory format to name or fabricate**. Simulator replay
   records (`s10-replay-v1`: seed, parameters, trace, traceHash, replayHash) contain
   answer-bearing setup and must not simply become public challenge artifacts.

5. **Apollo / bounce / RM05 unavailable**: no accepted playable input; remain
   no-fetch UNAVAILABLE. Apollo additionally lacks an approved trackable measured
   lunar result. Obtaining acceptable source/approval and actual processed bytes
   is separate from adapting a metadata entry; this run authorizes none of it.

## Integrity / resource boundary

Validate kind, safety labels/defaults, lowercase SHA, exact hash href and JSON
media declaration before fetch. Metadata is capped at the existing viewer
`DEFAULT_LIMITS.manifestBytes` (256 KiB), deliberately stricter than the server's
general 64 MiB artifact ceiling. Stream and declared Content-Length must fit
the advertised byte count; exact length + WebCrypto SHA-256 precede fatal UTF-8
and JSON parsing. Scene asset sizes/points/paths reuse `checkManifest` and its
unchanged limits; referenced assets are not fetched.

Hash integrity is not authenticity/rights approval. The guest server remains the
owner of current custody/licence/approval validation. No manifest cache, alternate
endpoint, retry, credentials, provider, package, schema or fixture was added.
Requires the existing modern browser/Node WebCrypto + fetch runtime (tested Node
24.18.0), not a new polyfill. No live browser, Next bundler, HTTP deployment or
actual reconstructed media was exercised in this run.

## Verification

`tests/library/test_loader.py` feeds fresh `guest.load_guest()` output to the
Node contract suite: all 18 current entries plus malformed transport/metadata,
overflow/cancellation, labels/defaults, source immutability and scene viewer
request validation. It is included in the standard Python library discovery.
Viewer tests are read-only and distinguish absent real media skips from passes.
