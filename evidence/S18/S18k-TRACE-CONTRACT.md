# Guest trace contract (S18k -> S09k)

`loadLibraryEntry(entry)` returns `canMount: true` only for a verified
`simulation-trace` artifact. Its `trace` property is the viewer DTO:

```js
{ kind, source: 'simulated', inputProvenance: 'synthetic', dt_s,
  samples: [{ step, time_s, position_m: [x, y, z] }],
  sha256, label: 'SIMULATED' }
```

- `kind`: `free-fall`, `projectile`, or `pendulum`; right-handed +Y-up,
  synthetic metres/seconds only. No real-scene scale/physics/gate claim.
- Finite positive `dt_s`; 2..4096 dense samples; sequential integer `step`
  starting at zero; `time_s === step * dt_s`; finite dense XYZ vectors.
- JSON body maximum 262144 bytes. Artifact kind `simulation-trace`, JSON
  media type, exact byte length and lowercase SHA-256 are in the guest entry.
  Href is `/api/library/artifacts/<sha256>`. Loader verifies length/hash before
  parsing/validating, then adds `sha256` to `trace`. **SHA hashes exact fetched
  body bytes, which do not contain their own SHA field.** All other DTO fields
  are in the body. Result/trace are deeply frozen.
- `availability: playable`, `label: SIMULATED`, `displayOnly: true`;
  defaults remain no autoplay/no physics/no editable parameters, real prediction
  WITHHELD, SCALE_UNVERIFIED. `viewerRequest` stays null: this is not scene-v1.
  The parallel viewer owns rendering, not the library. No fabricated geometry.
- `UNAVAILABLE` is no-fetch/canMount false with a reason. Mystery-g remains
  answer-free metadata via `/lab`; no `s10-replay-v1` or challenge trace is public.

Custody/generation and missing-input inventory will be recorded alongside this
contract. Generation must use existing accepted simulator implementations and
JSON pointers into existing accepted setup records, reproducing the catalogue
record's inputs. Retain historical and newly produced full-sample hashes
separately; current simulator model changes must not inherit historical accuracy claims.

## Current availability / source distinction

`simulated-projectile-baseline-short` and `simulated-pendulum-short-small-angle`
are guest-playable. Projectile's stored DTO SHA is
`13e00f7fe86c695598ae84773031473ff1385e78fca1531c995d66cdaa951608`;
16858 bytes, 201 samples. These are actual generated artifact results, not
physical measurements. `playable.json` holds exact source pointers/hashes.

Free-fall baseline reproduces its accepted trace but is **not guest-routed**:
the Mystery-g catalogue points at that same accepted record (`/cases/0`).
Times/positions mathematically reveal its answer even without parameter fields.
Pendulum uses preserved accepted initial-condition pointers and the accepted
short horizon. Accepted fix `b37f7b8` changed its small-angle model to linearized
dynamics, so current regeneration differs from the historical acceptance trace;
both hashes are recorded and the guest limitation disclaims historical accuracy.
Other cases have incomplete preserved setup pointers.
RM02/RM04 are UNAVAILABLE because accepted descriptor-declared PLY bytes are
absent locally. Metadata-only legacy handling remains supported by the loader
but these unavailable entries never fetch or mount. No synthetic room substitutes.
