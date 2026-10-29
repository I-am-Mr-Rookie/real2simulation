"""S06c optional SAM 3D Objects path: DISABLED by default; every failure falls back to primitive boxes.

Gate order (licence first, then VRAM): env flag -> owner access receipt -> GPU VRAM -> runner.
No SAM 3D code, weights or environment is packaged here (custom SAM License, manually gated HF repo;
upstream needs >=32 GB VRAM and its own torch 2.5.1/cu121 + pytorch3d env, incompatible with the S06a lock).
Offline receipt:  python Build/gpu/sam3d_option.py [out.json]   (no Modal, no network)
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FLAG = "R2S_ENABLE_SAM3D"  # must be exactly "1"; anything else keeps it off
# Owner-only receipt (agents must never create it): HF access granted + SAM License accepted by Koushik.
ACCESS_RECEIPT = ROOT / "evidence/owner/S06/SAM3D-ACCESS.md"
MODEL_ID = "facebook/sam-3d-objects"
CODE_REV = "f91db411c50efee93d8db7aeb323885650f6f722"
WEIGHT_REV = "2e73555018d2741ccd486e56c24fac41155a1dc6"
LICENCE = "SAM License (custom, 2025-11-19); HF license:other, gated=manual"
MIN_VRAM_MIB = 32 * 1024  # upstream doc/setup.md @ CODE_REV: "at least 32 Gb of VRAM"
MEASURED_A10G_MIB = 23028  # evidence/S06/S06b/smoke-remote.json (current image_spec.GPU)


def gate(vram_mib, env=None, receipt=ACCESS_RECEIPT):
    """Return reasons SAM 3D must NOT run; empty list means all gates pass."""
    env = os.environ if env is None else env
    reasons = []
    if env.get(ENV_FLAG) != "1":
        reasons.append(f"disabled: {ENV_FLAG} != 1 (default off)")
    if not Path(receipt).is_file():
        reasons.append(f"licence/access: no owner receipt {Path(receipt).name} (custom SAM License, gated manual)")
    if vram_mib is None or vram_mib < MIN_VRAM_MIB:
        reasons.append(f"vram: {vram_mib} MiB < {MIN_VRAM_MIB} MiB required")
    return reasons


def primitive_boxes(objects):
    """Scene-schema box colliders from per-object axis-aligned bounds {id, min, max} (metres, world frame)."""
    boxes = []
    for o in objects:
        lo, hi = o["min"], o["max"]
        half = [(b - a) / 2 for a, b in zip(lo, hi)]
        if len(half) != 3 or min(half) <= 0:
            raise ValueError(f"object {o['id']}: degenerate bounds")
        boxes.append({"id": o["id"], "shape": "box",
                      "pose": {"position_m": [(a + b) / 2 for a, b in zip(lo, hi)],
                               "rotation_xyzw": [0.0, 0.0, 0.0, 1.0]},
                      "half_extents_m": half, "surface_id": o.get("surface_id")})
    return boxes


def object_meshes(objects, vram_mib, runner=None, env=None, receipt=ACCESS_RECEIPT):
    """Primitive boxes unless every gate passes AND runner succeeds; never raises because of SAM 3D."""
    reasons = gate(vram_mib, env, receipt)
    if not reasons and runner is None:
        reasons.append("runtime: no SAM 3D runner packaged (S06c stub)")
    if not reasons:
        try:
            return {"backend": "sam3d", "reasons": [], "meshes": runner(objects)}
        except Exception as e:  # any SAM 3D failure (OOM, import, auth) keeps the primitive path
            reasons.append(f"runner failed: {type(e).__name__}: {e}")
    return {"backend": "primitive", "reasons": reasons, "colliders": primitive_boxes(objects)}


if __name__ == "__main__":
    demo = [{"id": "synthetic-box", "min": [-0.1, 0.0, -0.1], "max": [0.1, 0.2, 0.1], "surface_id": None}]
    result = {"contract": "S06c-sam3d-option/v1", "synthetic_input": True, "model_id": MODEL_ID,
              "code_revision": CODE_REV, "weight_revision": WEIGHT_REV, "licence": LICENCE,
              "min_vram_mib": MIN_VRAM_MIB, "vram_mib_checked": MEASURED_A10G_MIB,
              **object_meshes(demo, MEASURED_A10G_MIB)}
    text = json.dumps(result, indent=1)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).parent.mkdir(parents=True, exist_ok=True)
        Path(sys.argv[1]).write_text(text + "\n")
    print(text)
