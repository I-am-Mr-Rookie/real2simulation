# Experiment input contract v1.0.0

`experiment.schema.json` is JSON Schema 2020-12. It describes **inputs, not results**.
It is local/offline: all references resolve inside the document. Python >=3.11,
with the existing jsonschema 4.23.0 dependency; no install performed in S08a.

```powershell
python -m unittest discover -s tests/spec -p 'test_*.py' -v
```

## Consumer boundary (mandatory)

1. Parse strict JSON (reject duplicate keys and non-JSON NaN/Infinity tokens).
2. Validate against this exact version; reject unknown versions/extra fields.
3. Apply the S08b numeric/range/dimensional validator, then S08c scene-fit and
   stability checks against the actual validated scene bundle.
4. Only then execute a template. S08b provides the numeric validator below;
   S08c provides `validate_setup(spec, scene, scene_root)` for preflight.
   No simulator exists here yet; preflight is not integrator accuracy evidence.

**Structural validity is not execution approval.** S08a deliberately permits
unknown draft quantities and represents scene constraints without evaluating them.
Numeric finiteness, physical ranges, nonnegative uncertainty and clearance, and
ordered bounds are checked by S08b. Shape containment, collisions,
energy/stability limits and agreement with the actual scene remain S08c checks.
Do not use jsonschema alone to enable apparatus placement or simulation.

## Numeric validator (S08b)

```powershell
python contracts/experiment/validate_experiment.py path/to/experiment.json
python -m unittest discover -s tests/spec -p 'test_*.py' -v
```

Python API in `validate_experiment.py`: `parse_json(text)`, `load_json(path)` and
`validate(spec)`. Call `validate(load_json(path))` for files. `validate` returns the
same unmodified input or raises `ExperimentValidationError` (a `ValueError`) with
an `issues` tuple of readable field-path messages. CLI exit 0 means **numeric/unit
checks only**, never permission to run; exit 1 reports invalid inputs/read errors.
Callers must not silently continue after failure. No defaults or unit conversions.

Strict parsing rejects duplicate keys, NaN/Infinity literals, numeric exponent
overflow and malformed JSON. The Python-object entry point independently rejects
nonfinite numbers everywhere before schema validation, including vectors and seed.
Numbers too large for finite binary64 are rejected; this is not a stability or
precision guarantee. Typed schema quantities enforce the dimensional table below
and distinguish radians from plain dimensionless values. Unknown/null draft
quantities and unknown positions cannot pass the numeric stage; null uncertainty
is allowed and remains unquantified rather than becoming zero.

| Input | Numeric domain |
|---|---|
| Gravity magnitude, mass, body radius, duration, step | strictly positive |
| Step relative to duration | step <= duration; not an integration-accuracy check |
| All scalar uncertainty, scene clearance | nonnegative (uncertainty may be null) |
| Scene bounds | each minimum <= corresponding maximum; containment not checked |
| Fall drop height / projectile launch height | strictly positive centre travel |
| Projectile horizontal speed / ramp initial speed | nonnegative; fixed forward direction |
| Ramp length / pendulum length | strictly positive |
| Ramp angle | strictly between 0 and pi/2 radians (downhill, not horizontal/vertical) |
| Ramp kinetic friction | nonnegative, **not** artificially capped at 1 |
| Pendulum release angle | principal signed interval [-pi, pi] radians |
| Fall vertical / pendulum angular velocity | any finite signed value |

No empirical magnitude ceilings or terrestrial-g defaults are invented. The S08c
preflight below adds scene and numerical safety policy; actual integration
accuracy and each oracle's approximation domain remain later gates. Passing a
numeric check with synthetic metadata does not make it real measured evidence.

## Scene and stability preflight (S08c)

Python API: `validate_setup(spec, scene, scene_root)` in the same module. Pass the
actual parsed scene and its local bundle directory, **not client-supplied scene
metadata**. It returns the same unmodified spec or raises `ExperimentValidationError`.
It first runs numeric validation and the existing scene validator, including local
asset byte lengths, SHA256 and point-cloud integrity. Missing/modified assets fail.
The numeric-only `validate` and CLI remain numeric-only for draft callers.

- Require matching scene ID/version, known matching scale (estimated is allowed
  but never promoted to calibrated), exact authoritative bounds snapshot, resolved
  allowed surfaces/obstacles, known matching gravity magnitude and world -Y direction.
  Unknown gravity is not silently replaced with an Earth default.
- Check the **whole planned motion**, even if duration is shorter: fall/projectile
  through the stop plane, upward apex and projectile range; full ramp segment;
  conservative full pendulum rotation disk in XY. Expand by body radius plus
  requested clearance. The expanded envelope must stay inside scene bounds.
- Check every scene collider, even when omitted from the client obstacle list.
  Normalize validated quaternions and conservatively enclose oriented boxes in
  world AABBs; reject touching/overlapping swept envelopes. This can reject some
  collision-free paths (false positives), never claims an exact continuous solver.
- **Contact-mounted placements (`surface_id != null`) fail closed for now.** No
  selected support collider is exempted; contact frames/thickness are not defined
  by this preflight. Free-standing ramp start/link envelopes are supported, not
  arbitrary apparatus mounting. Later placement work must add tested contact rules.
- Policy limits: at most 100,000 steps and dt <= 1/60 s. Conservative speed and
  acceleration bounds must permit travel <= radius/2 per step. Pendulum additionally
  requires dt*sqrt(g/length) <= 0.05. These are initial conservative policy limits,
  not experimentally established accuracy thresholds or a stability proof for any
  arbitrary future integrator; S09/S10 and Gate P must validate the actual engine.
- Require finite positive representable energy bounds, finite envelopes, normal
  (not subnormal) gravity, and radius >= 32 binary64 ULPs at envelope coordinates.
  Arithmetic overflow/underflow fails readably; no clipping or implicit rescaling.

Tests include `tests/spec/fixtures/unsafe_setups.json` (14 synthetic invalid cases).
All fixtures are authored test inputs, not fitter/simulator output or real trials.
Asset revalidation deliberately prioritizes freshness over caching; a future UI
must not repeatedly hash large bundles on each pointer move. Any cache must bind
to immutable validated scene content, not just a scene ID.

## Versioning and source labels

- `schema_version=1.0.0`, `$id=urn:real2simulation:experiment:1.0.0`.
  Breaking shape/units/meaning changes require a new version and explicit migration.
- Every physical scalar is `{value, unit, source, uncertainty}`. Source is
  `{label, evidence}`; evidence is a nonblank, plain-text tool/trial/decision/fixture
  reference. It is metadata, not authenticated proof, a URL to fetch, or HTML.
- Labels: `measured` (fitter/measurement evidence), `simulated` (simulator evidence),
  `assumed` (explicit human/config choice), `synthetic` (test-only authored value),
  `unknown` (unavailable). Unknown requires null value and uncertainty. Other
  labels require a number; uncertainty may be null when not quantified, never
  implicitly zero. Uncertainty means one standard deviation in the same unit.
- Never label a model-generated number measured/simulated. Real result numbers
  must come from the fitter/simulator, which S08a does not implement. Synthetic
  test data is neither product output nor gate evidence.
- Dimensionless replay `seed` is uint32, not a physical measurement. Bounds and
  reference IDs are a snapshot of scene metadata, not new measurements.

## Units and scene frame

| Quantity | Canonical unit | Dimension (length, mass, time) |
|---|---|---|
| Length, radius, clearance, world position | `m` | (1,0,0) |
| Duration, fixed time step | `s` | (0,0,1) |
| Mass | `kg` | (0,1,0) |
| Linear speed / signed vertical velocity | `m/s` | (1,0,-1) |
| Positive gravity magnitude | `m/s^2` | (1,0,-2) |
| Angle | `rad` | (0,0,0), angle semantic tag |
| Angular velocity | `rad/s` | (0,0,-1), angle semantic tag |
| Friction coefficient | `1` | (0,0,0) |

No implicit conversion from cm, degrees, frames or pixels. Convert at the adapter
boundary with recorded evidence before constructing the spec. Angle tags remain
distinct from plain dimensionless values, despite equal physical dimensions.

Scene v1.0.0 uses right-handed world axes, +Y up, metres and seconds (see
`contracts/scene/README.md`). Scene JSON stores coordinate fields individually;
the experiment's `coordinate_system` literal is a summary of that same frame,
not a literal field copied from the scene manifest. No second scale multiplier.
These four baseline templates use uniform gravity along world -Y and neglect air
resistance; tilted-gravity scenes need an explicit future adapter/version, not a
silent rotation. `scale_status=unknown` is representable for drafts, never runnable.

`scene_id` and `schema_version` identify the actual scene bundle. `bounds_m` is an
inclusive world AABB; allowed surfaces and obstacle IDs refer to scene collection
IDs. Consumers must resolve them and verify the snapshot against the scene,
including obstacles (an omitted ID must not bypass collisions). `clearance` is
the requested minimum separation from non-contact obstacles. A surface contact
is permitted only through the selected allowed `placement.surface_id`; null
means no support attachment. Scene provenance/rights approval stays external.

## Four structural variants (not runnable template generators)

`placement.origin` is a metre vec3 with a source label (or null for unknown).
It is the body-centre start for free fall/projectile, body-centre start at the
top of the ramp, and the suspension pivot for the pendulum. Coordinates refer
to the world frame, never camera pixels. Finite body radius affects scene fit;
the baseline analytic motion treats the moving body as a point mass.

| `template` | Required parameters | Convention |
|---|---|---|
| `free_fall` | drop_height; initial_vertical_velocity | Height is positive centre travel to the stop plane; velocity is signed +Y. Plane Y = origin Y - height. |
| `projectile` | launch_height; horizontal_speed | Horizontal launch along +X, initial vertical speed zero; centre stop plane Y = origin Y - height. |
| `ramp` | length; incline_angle; friction_coefficient; initial_speed | Straight sliding ramp in XY; downhill is +X/-Y; angle below horizontal, kinetic Coulomb friction, no rolling. |
| `pendulum` | length; release_angle; initial_angular_velocity | Ideal massless rigid link to point mass, XY plane; angle from downward vertical toward +X, positive angular velocity increases angle. |

Every variant forbids parameter mixing and unknown keys. S08b applies the baseline
numeric domains above; S08d-g implement actual templates/oracles and document any
further approximation domains. No analytic answer,
Gate P accuracy, reconstruction or real-world measurement is established here.
Mystery-g UI hiding belongs to S10: this input document contains gravity and is
**not** a client confidentiality boundary.

## Implemented template tools

S08d adds `Build/templates/free_fall.py`: explicit-input factory plus deterministic
closed-form free-fall oracle; both require `validate_setup` against the bundle.
See `Build/templates/README.md` for arguments, stop-plane conventions, sourced
output format and time/uncertainty limits. This does not establish Gate P accuracy.

S08e adds `Build/templates/projectile.py`: `make_projectile` and
`analytic_projectile` implement the schema's horizontal +X launch (initial
vertical velocity zero), not an arbitrary-angle projectile. Both revalidate the
authoritative scene/setup. The oracle exposes full ideal stop-plane impact time,
horizontal range, position and velocity plus explicitly requested pre-impact
samples. See the template README for sourced inputs/outputs, formulas, duration
semantics and limitations. No schema changes or Gate P success claim.

S08f adds `Build/templates/ramp.py`: `make_ramp` and `analytic_ramp` provide
straight downhill kinetic-Coulomb sliding with finite positive acceleration
only. Both retain authoritative setup validation. Coasting/stalling/static
friction are unsupported (readable rejection); no rolling, support attachment,
post-end dynamics or integrator is implied. Full ramp-end time/speed/position/
velocity and bounded samples carry simulated labels and source provenance.
See the template README for formulas and approximation limits. Baseline schema
unchanged; Gate P NOT RUN.

S08g adds `Build.templates.pendulum.make_pendulum` / `analytic_pendulum`,
with pivot-origin XY geometry and sourced inputs. General v1 pendulum specs
remain unchanged; this oracle additionally requires small-angle amplitude
`hypot(release_angle,initial_angular_velocity/sqrt(g/L))<=0.1 rad`.
Period `2*pi*sqrt(L/g)` is a linearized analytic reference, not exact nonlinear
or measured evidence. Factory and oracle revalidate the authoritative bundle;
period and duration-bounded samples are simulated, uncertainty unpropagated.
See template README for conventions and API. Gate P NOT RUN.

## S08 acceptance regression (S08h)

```powershell
python -m unittest discover -s tests/spec -p test_s08_acceptance.py -v
python -m unittest discover -s tests/spec -p 'test_*.py' -q
```

`tests/spec/fixtures/ten_bad_specs.json` names exactly ten single-field mutations:
unsupported version/template, unexpected result field, wrong gravity unit, zero
mass, negative projectile speed, zero ramp length, negative pendulum length,
forged scene identity and unsafe timestep. Each starts from a factory-created
valid baseline against the authored synthetic bundle, then must fail with a
readable reason at both `validate_setup` and its corresponding oracle boundary.
The verbose command exposes ten individual rejection results rather than hiding
the acceptance count inside a single table test. Other negative suites remain.

The same regression calls all four factories/oracles, checks independent analytic
values, repeated-call equality, simulated output labels, unpropagated uncertainty,
source preservation and nonmutation. These are synthetic offline contract and
closed-form reference checks, **not** measured accuracy, a working integrator,
real-scene suitability or Gate P acceptance. Oracle-specific approximation
domains still apply; schema validity alone is never execution approval.

## Numeric representability (S08i)

Free-fall drop height and projectile launch height must produce a stop-plane Y
strictly below the world-space origin. Positive heights that round back to the
origin are rejected with a parameter-specific error; no arbitrary minimum height
is imposed. This is a numeric representation guard, not a calibration threshold.
Free-fall sample times reject out-of-range signed large integers before float
conversion, matching sibling oracles' readable `ValueError` boundary.
