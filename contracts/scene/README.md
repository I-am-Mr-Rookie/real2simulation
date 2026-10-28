# Scene artifact contract — frozen v1.0.0

Scope: a **bundle**, `scene.json` plus its relative assets. First consumer: S09 viewer;
S05b reconstruction adapters produce it; S06 persists it in the bucket. No backend,
viewer, renderer, inference or physics implementation is supplied here.

Canonical shape: [scene.schema.json](scene.schema.json). Apply both JSON Schema
2020-12 **and** `validate_scene.py` semantics before loading. Python >=3.11 and
`jsonschema` are needed; this is a lane-local dependency, not a web manifest change.

```powershell
python -m pip install -r contracts/scene/requirements.txt
python contracts/scene/validate_scene.py test-data/synthetic/scene/room-v1/scene.json
python -m unittest discover -s contracts/scene -p 'test_*.py' -v
```

## Units and transforms

- Right-handed, +Y up, metres, seconds; camera looks along local -Z with +Y up.
- All positions, points, surfaces and colliders are in the same world frame.
  Quaternions are normalized `[x,y,z,w]`, active local-to-world rotations.
- Upstream adapters must transform camera convention, handedness, axes and scale
  once; do not feed raw computer-vision +Z-forward poses into the viewer.
- `scale.metres_per_source_unit` records the applied conversion, **not a further
  multiplier** for the viewer. `estimated` means nominal metric prediction, not
  calibrated truth. `unknown` uses null; nominal geometry is display-only until
  calibration. Never silently turn unknown scale into calibrated 1 m/unit.
- `bounds_m` is a world AABB, inclusive min/max. Collider half-extents are local
  positive half sizes, never full sizes. Surface normals are unit vectors.
- Surface `extent_m` is full width/depth around `origin_m`. To remove tangent
  ambiguity: project world +X onto the plane and normalize for U; if its length
  is <1e-6, project +Z instead. V = normal cross U. Width is along U, depth V.
- `gravity.direction` is a unit downward direction, not an acceleration vector.
  Magnitude is separate, may be null even when direction is known; `unknown`
  requires both null. `assumed` is not measured. Never enable physics with unknown
  scale, unknown direction or null magnitude. Mystery-g hiding belongs to S10;
  a scene manifest itself is **not** a secrecy boundary for client-side values.

## Geometry and consumers

- Required `render` selects main and mobile asset IDs. Both may reference the same
  tiny fixture; production reduced LOD/performance is not established here.
- `points`: PLY ASCII 1.0, vertex-only, properties exactly float x/y/z followed by
  uchar red/green/blue; RGB 0..255. `point_count` describes the main asset.
- `mesh`: GLB 2.0, world coordinates, metre units; `point_count` must be 0.
- `splats`: 32-byte little-endian records: position float32[3], scale float32[3],
  RGBA uint8[4], quaternion uint8[4] in wxyz order decoded as `(byte-128)/128`.
  `point_count` is record count. No splat/GLB adapter is implemented or validated
  by this run; renderers must validate these payloads themselves before decoding.
- Every asset has a relative ASCII allowlisted path, SHA256 and byte length;
  no remote URL, absolute path, query string, backslash or traversal. Transport
  resolves the authenticated bundle root; do not put bucket secrets in manifests.
  The validator never fetches URLs. Integrity is not proof of safe rendering.
- Optional content is represented by empty arrays, not invented surfaces or
  colliders. Camera path is at least one pose, with strictly increasing times.
  `labels` are plain text, never HTML. IDs are unique within each collection.
- Adapters may output boxes/points when complex reconstruction is unavailable.
  A static fixture is never reconstruction evidence or a Gate R pass.

## Provenance and fail-closed behavior

`synthetic=true` requires `method=synthetic`, no sources and no models. All fixture
geometry below was authored for offline integration, not produced by a fitter,
simulator or model. **Never show fixture values as measured/simulated results.**
Real scenes require clip IDs resolving to owner-approved `clips.csv` rows, source
URLs, exact licences, attribution and approval-evidence pointers. The validator
checks fields, not authenticity, domains or permission: S02 approval remains an
external mandatory gate. Preserve SA requirements; do not blanket relicense scenes.
Model entries record immutable code/weight revisions and their distinct licences.
For `mapanything-apache`, the validator rejects the default NC model identity.
SAM 3D use remains blocked by the licence decision, even though the schema can
represent its eventual output; schema validity is not authorization.

Unknown schema versions/extra fields, invalid axes, non-finite numbers, duplicate
keys/IDs, missing references/assets, non-unit normals/quaternions, invalid ordering,
and tampered assets fail. Consumers must enforce resource limits before parsing
untrusted uploads; this offline validator is not an upload security gate.

v1 is now frozen for fixture integration. Breaking layout/units/codec changes
require a new version and producer/consumer migration; do not silently reinterpret
v1. No job API/auth contracts or cross-lane files are modified.
