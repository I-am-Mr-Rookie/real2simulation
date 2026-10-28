"""Offline input validation only: passing is NOT scene/stability execution approval."""

import argparse
import json
import importlib.util
import math
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


SCHEMA_PATH = Path(__file__).with_name("experiment.schema.json")
VALIDATOR = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
_SCENE_MODULE = importlib.util.spec_from_file_location(
    "scene_bundle_validator", SCHEMA_PATH.parent.parent / "scene" / "validate_scene.py")
_SCENE_VALIDATOR = importlib.util.module_from_spec(_SCENE_MODULE)
_SCENE_MODULE.loader.exec_module(_SCENE_VALIDATOR)


class ExperimentValidationError(ValueError):
    """Readable input errors, each prefixed with a JSON-style field path."""

    def __init__(self, issues):
        self.issues = tuple(issues)
        super().__init__("; ".join(self.issues))


def parse_json(text):
    """Strict JSON: no duplicate keys, NaN/Infinity tokens or overflow numbers."""
    def constant(token):
        raise ExperimentValidationError([f"$: non-JSON numeric constant {token}"])

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ExperimentValidationError([f"$: duplicate JSON key {key!r}"])
            result[key] = value
        return result

    try:
        result = json.loads(text, parse_constant=constant, object_pairs_hook=unique)
    except (json.JSONDecodeError, RecursionError, ValueError) as error:
        if isinstance(error, ExperimentValidationError):
            raise
        raise ExperimentValidationError([f"$: invalid JSON: {error}"]) from error
    _finite(result)
    return result


def load_json(path):
    return parse_json(Path(path).read_text(encoding="utf-8"))


def _path(parts):
    return "$" + "".join(f"[{part}]" if isinstance(part, int) else f".{part}" for part in parts)


def _finite(value, path=()):
    # Run before jsonschema: NaN/Infinity can otherwise pass 'number' or upset integer checks.
    if isinstance(value, (float, int)) and not isinstance(value, bool):
        try:
            valid = math.isfinite(value)
        except OverflowError:
            valid = False
        if not valid:
            raise ExperimentValidationError([f"{_path(path)}: number must be finite and representable as binary64"])
    elif isinstance(value, dict):
        for key, child in value.items():
            _finite(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _finite(child, (*path, index))


def _schema_issues(error, template):
    if error.context:
        contexts = error.context
        if error.validator == "oneOf" and isinstance(error.instance, dict) and "template" in error.instance:
            # Only explain the selected variant, not the three irrelevant alternatives.
            selected = next((i for i, branch in enumerate(error.validator_value)
                             if branch.get("properties", {}).get("template", {}).get("const") == template), None)
            if selected is not None:
                contexts = [child for child in contexts if child.schema_path[0] == selected]
        for child in contexts:
            yield from _schema_issues(child, template)
    else:
        yield f"{_path(error.absolute_path)}: {error.message}"


def validate(spec):
    """Return the unchanged spec or raise; checks numeric inputs, NOT actual scene fit.

    Unknown quantities are valid drafts in the schema but rejected by this numeric
    stage. This function never fills defaults, converts units or authenticates sources.
    """
    _finite(spec)
    template = spec.get("template") if isinstance(spec, dict) else None
    issues = [issue for error in VALIDATOR.iter_errors(spec)
              for issue in _schema_issues(error, template)]
    if issues:
        raise ExperimentValidationError(sorted(set(issues)))

    def require(condition, path, reason):
        if not condition:
            issues.append(f"{path}: {reason}")

    def quantity(item, path):
        if isinstance(item, dict):
            if {"value", "unit", "source", "uncertainty"} <= item.keys():
                require(item["value"] is not None, path + ".value", "known numeric input required (unknown draft)")
                uncertainty = item["uncertainty"]
                require(uncertainty is None or uncertainty >= 0, path + ".uncertainty", "must be nonnegative or null")
            for key, child in item.items():
                quantity(child, path + "." + key)
        elif isinstance(item, list):
            for i, child in enumerate(item):
                quantity(child, path + f"[{i}]")

    quantity(spec, "$")
    require(spec["placement"]["origin"]["value"] is not None,
            "$.placement.origin.value", "known world position required (unknown draft)")
    if issues:
        raise ExperimentValidationError(issues)

    def range_check(section, field, predicate, reason):
        value = spec[section][field]["value"]
        require(predicate(value), f"$.{section}.{field}.value", reason)

    for section, field in (("environment", "gravity"), ("body", "mass"), ("body", "radius"),
                           ("simulation", "duration"), ("simulation", "time_step")):
        range_check(section, field, lambda v: v > 0, "must be > 0")
    constraints = spec["scene"]["constraints"]
    require(constraints["clearance"]["value"] >= 0, "$.scene.constraints.clearance.value", "must be >= 0")
    for axis, (lo, hi) in enumerate(zip(constraints["bounds_m"]["min"], constraints["bounds_m"]["max"])):
        require(lo <= hi, f"$.scene.constraints.bounds_m.min[{axis}]", "must be <= corresponding maximum")
    require(spec["simulation"]["time_step"]["value"] <= spec["simulation"]["duration"]["value"],
            "$.simulation.time_step.value", "must be <= simulation.duration.value")

    if template in ("free_fall", "projectile"):
        height = "drop_height" if template == "free_fall" else "launch_height"
        range_check("parameters", height, lambda v: v > 0, "must be > 0 (centre travel to stop plane)")
    if template == "projectile":
        range_check("parameters", "horizontal_speed", lambda v: v >= 0, "must be >= 0 (+X launch)")
    if template in ("ramp", "pendulum"):
        range_check("parameters", "length", lambda v: v > 0, "must be > 0")
    if template == "ramp":
        range_check("parameters", "incline_angle", lambda v: 0 < v < math.pi / 2, "must be in (0, pi/2) rad")
        for field in ("friction_coefficient", "initial_speed"):
            range_check("parameters", field, lambda v: v >= 0, "must be >= 0")
    if template == "pendulum":
        range_check("parameters", "release_angle", lambda v: -math.pi <= v <= math.pi, "must be in [-pi, pi] rad")

    if issues:
        raise ExperimentValidationError(issues)
    return spec


def validate_setup(spec, scene, scene_root):
    """Numeric + authoritative bundle + conservative geometry/stability preflight.

    Not an integrator accuracy proof or rights/owner-approval check. No mutation.
    Contact-mounted setups fail closed until contact geometry is implemented.
    """
    validate(spec)

    def require(condition, path, reason):
        if not condition:
            raise ExperimentValidationError([f"{path}: {reason}"])

    try:
        _finite(scene)
        _SCENE_VALIDATOR.validate(scene, scene_root)
    except (ValueError, OSError, OverflowError) as error:
        raise ExperimentValidationError([f"$.scene: invalid authoritative bundle: {error}"]) from error

    reference = spec['scene']
    constraints = reference['constraints']
    require(reference['scene_id'] == scene['id'], '$.scene.scene_id', 'does not match authoritative scene')
    require(reference['schema_version'] == scene['schema_version'], '$.scene.schema_version', 'version mismatch')
    require(scene['scale']['status'] != 'unknown' and reference['scale_status'] == scene['scale']['status'],
            '$.scene.scale_status', 'known matching scene scale required')
    require(constraints['bounds_m'] == scene['bounds_m'], '$.scene.constraints.bounds_m', 'snapshot mismatch')
    surfaces = {surface['id']: surface for surface in scene['surfaces']}
    obstacles = {collider['id'] for collider in scene['colliders']}
    require(set(constraints['allowed_surface_ids']) <= surfaces.keys(),
            '$.scene.constraints.allowed_surface_ids', 'unresolved surface')
    require(set(constraints['collision_obstacle_ids']) <= obstacles,
            '$.scene.constraints.collision_obstacle_ids', 'unresolved obstacle')
    support = spec['placement']['surface_id']
    require(support is None or support in constraints['allowed_surface_ids'],
            '$.placement.surface_id', 'surface is not allowed')
    gravity = scene['gravity']
    g = spec['environment']['gravity']['value']
    require(gravity['status'] != 'unknown' and gravity['direction'] == [0, -1, 0]
            and gravity['magnitude_m_s2'] == g, '$.environment.gravity', 'known matching -Y scene gravity required')
    require(g >= sys.float_info.min, '$.environment.gravity', 'numerical subnormal gravity is unsupported')

    dt = spec['simulation']['time_step']['value']
    duration = spec['simulation']['duration']['value']
    steps = duration / dt
    require(math.isfinite(steps) and steps <= 100_000, '$.simulation', 'maximum 100000 steps exceeded')
    require(dt <= 1 / 60, '$.simulation.time_step', 'time_step must be <= 1/60 s')
    origin = spec['placement']['origin']['value']
    radius = spec['body']['radius']['value']
    margin = radius + constraints['clearance']['value']
    p = {key: item['value'] for key, item in spec['parameters'].items()}
    low, high = list(origin), list(origin)
    kind = spec['template']
    try:
        if kind in ('free_fall', 'projectile'):
            height_field = 'drop_height' if kind == 'free_fall' else 'launch_height'
            height = p[height_field]
            require(origin[1] - height < origin[1], f'$.parameters.{height_field}',
                    'stop-plane displacement is not representable at the world origin')
            vy = p['initial_vertical_velocity'] if kind == 'free_fall' else 0
            speed_y = math.sqrt(vy * vy + 2 * g * height)
            # Stable positive root even for strongly negative initial velocity.
            flight = ((vy + speed_y) / g if vy >= 0 else 2 * height / (speed_y - vy))
            low[1] -= height
            high[1] += max(vy, 0) ** 2 / (2 * g)
            vx = p.get('horizontal_speed', 0)
            high[0] += vx * flight
            speed = math.hypot(vx, speed_y)
            acceleration = g
        elif kind == 'ramp':
            length = p['length']
            high[0] += length * math.cos(p['incline_angle'])
            low[1] -= length * math.sin(p['incline_angle'])
            acceleration = g * (1 + p['friction_coefficient'])
            speed = math.sqrt(p['initial_speed'] ** 2 + 2 * acceleration * length)
        else:
            length = p['length']
            # Full rotation envelope, not a guessed small-angle excursion.
            for axis in (0, 1):
                low[axis] -= length
                high[axis] += length
            speed = math.sqrt((length * p['initial_angular_velocity']) ** 2 + 4 * g * length)
            acceleration = g + speed * speed / length
            require(dt * math.sqrt(g / length) <= 0.05, '$.simulation.time_step',
                    'time_step under-resolves pendulum frequency')
        energy = 0.5 * spec['body']['mass']['value'] * speed * speed
        require(math.isfinite(energy) and energy > 0, '$.body.mass', 'energy is not representable')
        require(all(math.isfinite(v) for v in [margin, speed, acceleration, *low, *high]),
                '$.parameters', 'numerical overflow in safety envelope')
        require(speed > 0 and acceleration > 0, '$.parameters', 'numerical underflow in safety envelope')
    except (OverflowError, ZeroDivisionError) as error:
        raise ExperimentValidationError(['$.parameters: numerical overflow/underflow in safety envelope']) from error

    bounds = scene['bounds_m']
    swept_min = [v - margin for v in low]
    swept_max = [v + margin for v in high]
    require(all(a <= b and a <= lo <= hi <= b for a, b, lo, hi in
                zip(bounds['min'], bounds['max'], swept_min, swept_max)),
            '$.placement.origin', 'body/trajectory with clearance outside scene bounds')
    require(all(radius >= 32 * math.ulp(v) for v in [*low, *high]),
            '$.body.radius', 'numerical coordinate precision insufficient for body radius')
    require(speed * dt + 0.5 * acceleration * dt * dt <= radius / 2,
            '$.simulation.time_step', 'time_step permits excessive displacement; reduce it')

    # Conservative enclosing world AABB for every oriented box, regardless of the
    # client obstacle list. False positives reject rather than permit penetration.
    for collider in scene['colliders']:
        q = collider['pose']['rotation_xyzw']
        norm = math.hypot(*q)
        x, y, z, w = [v / norm for v in q]
        rotation = ((1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)),
                    (2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)),
                    (2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)))
        half = [sum(abs(v) * extent for v, extent in zip(row, collider['half_extents_m']))
                for row in rotation]
        center = collider['pose']['position_m']
        separated = any(hi < c-h or lo > c+h for lo, hi, c, h in zip(swept_min, swept_max, center, half))
        require(separated, '$.placement', f"swept envelope intersects collider {collider['id']}")
    require(support is None, '$.placement.surface_id', 'contact surface placement not yet supported; no collider exemptions')
    return spec


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()
    try:
        validate(load_json(args.spec))
    except (ValueError, OSError) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: numeric/unit inputs only; scene-fit and stability NOT evaluated; NOT execution approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
