"""Offline structural, cross-reference and bundle integrity checks; no model calls."""
import argparse
import hashlib
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA = Path(__file__).with_name("scene.schema.json")


def load_json(path):
    def invalid(value):
        raise ValueError(f"non-JSON numeric constant: {value}")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      parse_constant=invalid, object_pairs_hook=unique)


def validate(scene, root):
    """Raise ValueError for unsupported/unsafe bundles; return parsed scene."""
    schema = load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(scene), key=lambda e: str(e.path))
    if errors:
        raise ValueError("; ".join(f"{list(e.path)}: {e.message}" for e in errors))

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    def finite(value):
        if isinstance(value, float):
            require(math.isfinite(value), "non-finite number")
        elif isinstance(value, dict):
            for child in value.values():
                finite(child)
        elif isinstance(value, list):
            for child in value:
                finite(child)

    def unit(values):
        require(abs(sum(v*v for v in values) - 1) <= 1e-5, "non-unit direction/quaternion")

    def point_cloud(path, expected_count=None):
        with path.open(encoding="ascii") as stream:
            require(stream.readline().strip() == "ply", "invalid PLY magic")
            require(stream.readline().strip() == "format ascii 1.0", "unsupported PLY encoding")
            header = []
            for _ in range(64):
                line = stream.readline().strip()
                if line == "end_header":
                    break
                if not line.startswith("comment "):
                    header.append(line)
            else:
                raise ValueError("PLY header too large")
            require(len(header) == 7 and header[0].startswith("element vertex "), "invalid PLY header")
            count = int(header[0].split()[-1])
            require(count > 0 and (expected_count is None or count == expected_count), "PLY point count mismatch")
            require(header[1:] == [f"property float {axis}" for axis in "xyz"] +
                    [f"property uchar {color}" for color in ("red", "green", "blue")], "invalid PLY properties")
            actual = 0
            for line in stream:
                values = line.split()
                require(len(values) == 6, "invalid PLY vertex")
                xyz = [float(value) for value in values[:3]]
                rgb = [int(value) for value in values[3:]]
                require(all(math.isfinite(v) for v in xyz), "non-finite PLY point")
                require(all(0 <= v <= 255 for v in rgb), "invalid PLY RGB")
                require(all(lo <= v <= hi for lo, v, hi in zip(scene["bounds_m"]["min"], xyz, scene["bounds_m"]["max"])), "PLY point outside bounds")
                actual += 1
            require(actual == count, "PLY vertex count mismatch")
            return count

    def indexed(items):
        ids = [item["id"] for item in items]
        require(len(set(ids)) == len(ids), "duplicate IDs")
        return {item["id"]: item for item in items}

    finite(scene)
    require(all(lo <= hi for lo, hi in zip(scene["bounds_m"]["min"], scene["bounds_m"]["max"])), "inverted bounds")
    provenance = scene["provenance"]
    require(scene["synthetic"] == (provenance["method"] == "synthetic"), "synthetic provenance mismatch")
    if scene["synthetic"]:
        require(not provenance["sources"] and not provenance["models"], "synthetic bundle must not claim footage/model inference")
    else:
        require(bool(provenance["sources"]), "real scene requires licensed source and owner approval evidence")
    if provenance["method"] == "mapanything-apache":
        require(bool(provenance["models"]), "missing reconstruction model")
        require(all(m["id"] == "facebook/map-anything-apache" and m["license"] == "Apache-2.0"
                    for m in provenance["models"]), "unapproved MapAnything checkpoint/license")

    assets = indexed(scene["assets"])
    surfaces = indexed(scene["surfaces"])
    indexed(scene["colliders"])
    indexed(scene["labels"])
    for surface in surfaces.values():
        unit(surface["normal"])
    for collider in scene["colliders"]:
        require(collider["surface_id"] is None or collider["surface_id"] in surfaces, "missing collider surface")
        unit(collider["pose"]["rotation_xyzw"])
    times = [camera["time_s"] for camera in scene["camera_path"]]
    require(all(a < b for a, b in zip(times, times[1:])), "camera times must strictly increase")
    for camera in scene["camera_path"]:
        unit(camera["pose"]["rotation_xyzw"])
    if scene["gravity"]["direction"] is not None:
        unit(scene["gravity"]["direction"])

    root = Path(root).resolve()
    paths = set()
    for asset in assets.values():
        path = (root / asset["path"]).resolve()
        require(path.is_relative_to(root), "asset escapes bundle root")
        require(path not in paths, "duplicate asset path")
        paths.add(path)
        require(path.is_file(), "missing asset")
        require(path.stat().st_size == asset["bytes"], "asset byte length mismatch")
        # Stream rather than allocating an entire reconstruction asset in memory.
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        require(digest == asset["sha256"], "asset SHA256 mismatch")
        suffix = {"ply-ascii-xyzrgb": ".ply", "glb": ".glb", "splat": ".splat"}[asset["format"]]
        require(path.suffix == suffix, "asset extension/format mismatch")
    render = scene["render"]
    expected = {"points": "ply-ascii-xyzrgb", "mesh": "glb", "splats": "splat"}[render["kind"]]
    for key in ("asset_id", "mobile_asset_id"):
        require(render[key] in assets, "missing render asset")
        require(assets[render[key]]["format"] == expected, "render kind/asset format mismatch")
    if render["kind"] == "points":
        require(render["point_count"] > 0, "empty point cloud")
        counts = {}
        for key in ("asset_id", "mobile_asset_id"):
            asset_id = render[key]
            if asset_id not in counts:
                counts[asset_id] = point_cloud(root / assets[asset_id]["path"],
                                              render["point_count"] if key == "asset_id" else None)
        require(counts[render["mobile_asset_id"]] <= render["point_count"], "mobile LOD exceeds main")
    elif render["kind"] == "mesh":
        require(render["point_count"] == 0, "mesh must not declare point count")
    else:
        require(render["point_count"] > 0, "empty splat cloud")
        require(assets[render["asset_id"]]["bytes"] == 32 * render["point_count"], "splat count/size mismatch")
        require(assets[render["mobile_asset_id"]]["bytes"] % 32 == 0, "invalid mobile splat length")
    return scene


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene", type=Path)
    args = parser.parse_args()
    try:
        scene = validate(load_json(args.scene), args.scene.parent)
    except (ValueError, OSError) as error:
        parser.exit(1, f"INVALID: {error}\n")
    print(f"PASS {scene['id']} schema={scene['schema_version']} synthetic={scene['synthetic']} (not Gate R evidence)")


if __name__ == "__main__":
    main()
