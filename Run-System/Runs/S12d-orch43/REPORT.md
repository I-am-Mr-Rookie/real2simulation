# S12d-orch43 REPORT — DONE

Lane CODEX-1, step S12; assigned anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Worker only, branch run/S12d-orch43
from main 55aa2a7, worktree .worktrees/S12d-orch43. UTC start 2026-10-29T21:34:35Z (issued 21:34:01), work stopped 2026-10-29T21:39:24+00:00.
Tokens/cost: unknown (not observable); no GPU/Modal/Meta/API calls, $0.

## Changes (Owns only)
- **Build/real2sim/predict.py** `pendulum(boundary, sealed, frequency)`: small-angle continuation of the tracked 1-D image coordinate,
  `y = c + a cos(wt) + b sin(wt)` = the linearized solution already in Build/templates/pendulum.analytic_pendulum
  (theta0 cos + omega0/w sin) projected onto one image coordinate. w from a validated params `angular_frequency` record; (c,a,b) by
  linear least squares on the prefix only, 1-sigma OLS band (w fixed). Reuses S12c `_identities`/`_seal` (prefix-only, hashed trace).
- **Build/real2sim/params.py**: `angular_frequency` (rad/s, PTS clock, uncalibrated) added to UNITS; `transfer()` now iterates an explicit
  `TRANSFER` tuple (g, speed, friction, restitution) so the simulator transfer set is unchanged (adding to UNITS alone broke 3 S12b tests — fixed at root).
- **contracts/overlay/** (new): `validate.py` (stdlib; `overlay/1.0.0`), `CONTRACT.md`, `__init__.py`. `validate(doc, clip_id, source_sha256, frame_map)`
  rejects unknown/missing fields, other version, gate_m != NOT_MET, non-scale-free units, other clip / source sha, frame-map hash mismatch,
  any row whose frame is absent or PTS off by > 1e-6 s, non-increasing frames, and any trace whose sha no longer matches `[kind, model, trace]`
  (same hash as boundary._sha). Returns a tuple of immutable `Trace` named tuples (tuple rows) — the renderer's read-only input. No UI built.
- **Build/real2sim/overlay.py**: `build(boundary, predictions, frame_map, provenance, sources)` (refuses predictions not made from that boundary;
  validates its own JSON round-trip), `st03_frame_map`, `synthetic_pendulum` fixture, `main`.
- **evidence/S12/overlay-ST03.json** (image-derived, real): S12c projectile prediction sha c81e0f94c110eb229502b37d03c29ec36b11621ed8ca97015f9e671508c9d1b0
  (regenerated and asserted equal to committed prediction-ST03.json), 466 rows frames 77–542, timebase = presentation-map PTS
  (frame_map_sha256 ad73b98a...; sources: ST03 errata frame_map b49858b0..., presentation-map 420aef7f...). Suffix still untracked (S12e).
- **evidence/S12/overlay-pendulum-SYNTHETIC.json**: SYNTHETIC fixture (clip SYNTHETIC-pendulum-v1, source sha = hash of fixture definition
  cdbd413b...), prefix frames 0–23, 66 predicted rows, trace sha 50af6864b2078a42b7ffa7697c03a58825280662be47f0c922025563ddeb8389.
  Pendulum is synthetic because no approved pendulum clip (PD01–PD06 in clips.csv) has tracking: rg for PD0x in evidence/S07 result/track files found none.
- **tests/prediction/test_overlay.py**: 8 tests. evidence/S12/tests-prediction-S12d.txt.

## Acceptance
1. Predictions and actual frames aligned by clip/timebase: validator ties every row to (clip_id, source_sha256, frame_index, source PTS);
   tests reject other clip, other source, half-frame PTS-shifted map, map-hash-matching-but-rows-on-old-PTS, dropped frame, retimed row.
   Committed ST03 overlay validates against the frame map regenerated from sources, and its (frame, PTS) rows equal the sealed suffix identities.
2. Renderer consumes immutable traces: `validate` returns tuple-of-tuple `Trace`s (item/attr assignment raises; tested); mutated value (+1e-6) rejected by sha.
3. Pendulum prediction from prefix only: changing held-out values (+50 px) leaves trace sha identical; SYNTHETIC noise-free max error < 1e-9 (fixture self-consistency, not accuracy).
4. Gate M NOT_MET in every output (overlay, trace); gate_m=MET, other version, unit "m" rejected.

## Fresh checks (Python 3.14.5, this worktree)
- `python -m unittest discover -s tests/prediction -v` -> 26 OK (18 prior + 8 S12d).
- `python -m Build.real2sim.overlay` twice -> both evidence files byte-identical (SHA256 73D16F87... ST03, 45C5D9E8... pendulum).
- Env: gitignored junction Build/simulator/node_modules -> canonical (needed by S12b simulate tests; not committed; delete with worktree).
- Not run: Node simulator suite (no simulator file touched; the 4 pre-existing pendulum/ramp extended-templates failures on main remain, not fixed — outside Owns).

## Ponytail (full)
- Reused: S12c `_identities`/`_seal`/`check`/`as_json`/`st03_record`; S12a `split`/`_sha`/GATE_M/LIMITS; S12b `parameter`; linearized pendulum
  solution form from Build/templates/pendulum.py; installed numpy lstsq (no new dependency); ST03 errata/presentation map as timebase.
- Smallest complete: one predictor function, one stdlib validator, one builder module, one test file; frame map stored as hash + source pointers,
  not copied; immutability via named tuples instead of a viewer API.
- Skipped: calling analytic_pendulum directly (needs metric scene/spec + validate_setup, contradicting scale-free Q15=A); fitting w from the prefix
  (w supplied as a sourced record); damping/large-angle; 2-D (x,y) traces (S12a boundary is 1-D); renderer/UI; scoring (S12e); JSON Schema file.

## Risks
- Pendulum is SYNTHETIC only; on real clips w must come from a sourced record and the 1-D slot is named y_px even when it carries x (naming debt, like S12c F2).
- PTS tolerance 1e-6 s assumes exact presentation-map PTS; a re-muxed source with jittered PTS will be rejected (intended fail-closed).
- No cross-vendor review of S12 path yet; Gate M/RS not run.

Communication: one completion line to controller (authorized). No canonical controls edited; no merge (controller accepts).
