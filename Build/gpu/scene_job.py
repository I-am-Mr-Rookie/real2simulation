"""S06d Modal scene job: approved licensed scene id -> MapAnything (S06b runtime) -> contracts/scene bundle.

Offline (no Modal/GPU, existing MapAnything npz):
    python Build/gpu/scene_job.py RM02 <out_dir> --npz <RM02-mapanything.npz>
One A10G job (frames from a S05 input manifest, already-approved licensed frames only):
    modal run Build/gpu/scene_job.py --scene RM02 --out <out_dir> --manifest <S05 input.json>
    -> <out_dir>/<scene>-scene-log.json: cold start, GPU seconds, estimated cost; billed via Build/gpu/cost_log.py.
SAM 3D stays off (sam3d_option default); colliders/surfaces stay empty: no object bounds exist yet.
"""
import argparse
import csv
import hashlib
import io
import json
import sys
import time
from pathlib import Path

CONTAINER_START = time.time()  # inside Modal: module import = container start (S06e cold-start split)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "contracts/scene"))
import image_spec as s

APPROVAL = "evidence/owner/S02/APPROVAL.md"
SCENE_IDS = {"RM02", "RM04", "RM05"}  # room-scene IDs in APPROVAL.md; other approved IDs are tracking clips
LICENCES = {"Pexels": "Pexels", "Pixabay": "Pixabay", "PD-USGov-NASA": "Public-Domain", "CC0": "CC0-1.0"}
MAX_POINTS, MOBILE_POINTS = 20000, 5000
CPU, MEM_MIB, SCALEDOWN_S = 2, 16384, 2  # scene_job resources; also feed the S06e cost estimate
F = (1.0, -1.0, -1.0)  # OpenCV (x right, y down, z fwd) -> contract (+Y up, camera looks -Z)


def clip_row(scene_id, clips=ROOT / "clips.csv"):
    if scene_id not in SCENE_IDS:
        raise ValueError(f"{scene_id}: not an owner-approved scene id ({APPROVAL})")
    with Path(clips).open(encoding="utf-8") as fh:
        row = next((r for r in csv.DictReader(fh) if r["clip_id"] == scene_id), None)
    if row is not None:
        if row["licence"] not in LICENCES:
            raise ValueError(f"{scene_id}: licence {row['licence']!r} not allowlisted")
        return row
    raise ValueError(f"{scene_id}: missing from clips.csv")


def quat_xyzw(r):
    """Rotation matrix -> unit quaternion [x,y,z,w]."""
    import numpy as np
    w = np.sqrt(max(0.0, 1 + r[0, 0] + r[1, 1] + r[2, 2])) / 2
    x = np.copysign(np.sqrt(max(0.0, 1 + r[0, 0] - r[1, 1] - r[2, 2])) / 2, r[2, 1] - r[1, 2])
    y = np.copysign(np.sqrt(max(0.0, 1 - r[0, 0] + r[1, 1] - r[2, 2])) / 2, r[0, 2] - r[2, 0])
    z = np.copysign(np.sqrt(max(0.0, 1 - r[0, 0] - r[1, 1] + r[2, 2])) / 2, r[1, 0] - r[0, 1])
    q = np.array([x, y, z, w])
    return [float(v) for v in q / np.linalg.norm(q)]


def write_ply(path, pts, rgb):
    head = ["ply", "format ascii 1.0", "comment Real2Simulation S06d MapAnything points (nominal scale)",
            f"element vertex {len(pts)}", "property float x", "property float y", "property float z",
            "property uchar red", "property uchar green", "property uchar blue", "end_header"]
    body = [f"{x:.5f} {y:.5f} {z:.5f} {r} {g} {b}" for (x, y, z), (r, g, b) in zip(pts.tolist(), rgb.tolist())]
    path.write_bytes(("\n".join(head + body) + "\n").encode("ascii"))


def asset(path, asset_id):
    data = path.read_bytes()
    return {"id": asset_id, "path": path.name, "format": "ply-ascii-xyzrgb",
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def build_bundle(scene_id, npz, out_dir, provenance_note):
    """MapAnything npz (S05 view<i>_* keys) -> scene bundle in out_dir, validated by contracts/scene."""
    import numpy as np
    from validate_scene import validate
    row = clip_row(scene_id)
    d = np.load(npz)
    n = len({k.split("_")[0] for k in d.files if k.startswith("view")})
    if n < 2:
        raise ValueError("need >=2 views")
    f = np.array(F)
    pts, rgb, cams = [], [], []
    for i in range(n):
        p = d[f"view{i}_pts3d"][0].reshape(-1, 3).astype(np.float64)
        keep = (d[f"view{i}_mask"][0].reshape(-1) > 0.5) & np.isfinite(p).all(1)
        conf = d[f"view{i}_conf"][0].reshape(-1)
        keep &= conf >= np.median(conf[keep])  # more confident half, as S05d
        pts.append(np.round(p[keep] * f, 5))  # rounded = exactly what the PLY text stores
        rgb.append(np.clip(d[f"view{i}_img_no_norm"][0].reshape(-1, 3)[keep] * 255 + 0.5, 0, 255))
        pose = d[f"view{i}_camera_poses"][0].astype(np.float64)  # cam->world, OpenCV
        cams.append((np.diag(f) @ pose[:3, :3] @ np.diag(f), pose[:3, 3] * f))
    pts, rgb = np.concatenate(pts), np.concatenate(rgb).astype(np.uint8)
    if len(pts) == 0:
        raise ValueError("no valid points")
    idx = np.random.default_rng(0).permutation(len(pts))[:MAX_POINTS]
    pts, rgb = pts[idx], rgb[idx]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    write_ply(out / "points.ply", pts, rgb)
    write_ply(out / "points-mobile.ply", pts[:MOBILE_POINTS], rgb[:MOBILE_POINTS])
    scene = {
        "schema_version": "1.0.0", "id": f"{scene_id.lower()}-mapanything-s06d",
        "label": f"{scene_id} MapAnything reconstruction - nominal scale, NOT calibrated, NOT Gate R evidence",
        "synthetic": False,
        "coordinates": {"handedness": "right", "up": "+Y", "length_unit": "m", "camera_forward": "-Z",
                        "quaternion_order": "xyzw"},
        "provenance": {
            "method": "mapanything-apache",
            "sources": [{"clip_id": scene_id.lower(), "source_url": row["source_url"], "license": LICENCES[row["licence"]],
                         "attribution": row["attribution"], "approval_evidence": APPROVAL}],
            "models": [{"id": s.MODEL_ID, "revision": s.WEIGHT_REV, "code_revision": s.CODE_REV,
                        "license": "Apache-2.0"}],
            "evidence": provenance_note},
        "scale": {"status": "estimated", "metres_per_source_unit": 1,
                  "evidence": "MapAnything nominal metric output; no source-backed scale reference (S05d abstained)"},
        "gravity": {"status": "unknown", "direction": None, "magnitude_m_s2": None,
                    "evidence": "Not estimated by S06d; physics must remain disabled"},
        "bounds_m": {"min": (pts.min(0) - 1e-4).tolist(), "max": (pts.max(0) + 1e-4).tolist()},
        "assets": [asset(out / "points.ply", "points"), asset(out / "points-mobile.ply", "points-mobile")],
        "render": {"kind": "points", "asset_id": "points", "mobile_asset_id": "points-mobile",
                   "point_count": int(len(pts))},
        "surfaces": [], "colliders": [],
        "camera_path": [{"time_s": float(i), "pose": {"position_m": t.tolist(), "rotation_xyzw": quat_xyzw(r)},
                         "vertical_fov_deg": 50} for i, (r, t) in enumerate(cams)],
        "labels": [],
    }
    (out / "scene.json").write_text(json.dumps(scene, indent=1) + "\n", encoding="utf-8")
    return validate(json.loads((out / "scene.json").read_text(encoding="utf-8")), out)


def load_frames(manifest, scene_id):
    """Hash-verified frames of one approved scene from a S05 input manifest (frames stay gitignored)."""
    clip_row(scene_id)
    m = json.loads(Path(manifest).read_text(encoding="utf-8"))
    for sc in m.get("scenes", [m]):
        if sc.get("clip_id") == scene_id:
            frames = []
            for fr in sc.get("frames") or sc["sample"]["frames"]:  # S05c list form / S05b single-scene form
                data = (Path(manifest).parent / fr["path"]).read_bytes()
                if len(data) != fr["bytes"] or hashlib.sha256(data).hexdigest() != fr["sha256"]:
                    raise ValueError("frame size/SHA256 mismatch")
                frames.append(data)
            if len(frames) < 2:
                raise ValueError("need >=2 frames")
            return frames
    raise ValueError(f"{scene_id} not in {manifest}")


try:
    import modal
except ImportError:  # offline converter needs no Modal client
    modal = None

if modal is not None:
    from runtime import RUNTIME_IMAGE, load_model
    app = modal.App("s06d-scene-job")

    @app.function(image=RUNTIME_IMAGE.add_local_python_source("runtime"), gpu=s.GPU, cpu=CPU, memory=MEM_MIB,
                  timeout=300, startup_timeout=240, retries=0, min_containers=0, max_containers=1,
                  buffer_containers=0, scaledown_window=SCALEDOWN_S, single_use_containers=True)
    def scene_job(frames):
        import numpy as np
        import torch
        from mapanything.utils.image import load_images
        t0 = time.time()
        paths = []
        for i, data in enumerate(frames):
            paths.append(f"/tmp/frame-{i:02}.png")
            Path(paths[-1]).write_bytes(data)
        model = load_model()
        t1 = time.time()
        with torch.inference_mode():
            preds = model.infer(load_images(paths), memory_efficient_inference=True, minibatch_size=1,
                                use_amp=True, amp_dtype="bf16", apply_mask=True, mask_edges=True,
                                apply_confidence_mask=False, use_multiview_confidence=False)
        t2 = time.time()
        keys = ("pts3d", "conf", "mask", "img_no_norm", "camera_poses")
        arrays = {f"view{i}_{k}": p[k].float().cpu().numpy() for i, p in enumerate(preds) for k in keys}
        buf = io.BytesIO()
        np.savez_compressed(buf, **arrays)
        t3 = time.time()
        return {"npz": buf.getvalue(), "function_elapsed_s": t3 - t0,
                "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
                "container_start_epoch": CONTAINER_START, "function_start_epoch": t0, "function_end_epoch": t3,
                "model_load_s": t1 - t0, "inference_s": t2 - t1}

    @app.local_entrypoint()
    def main(scene: str, out: str, manifest: str):
        from cost_log import scene_log
        frames = load_frames(manifest, scene)  # preflight before any GPU allocation
        call = time.time()
        r = scene_job.remote(frames)
        ret = time.time()
        out_dir = Path(out)
        out_dir.mkdir(parents=True, exist_ok=True)
        log = scene_log(app.app_id, call, ret, r, s.GPU, CPU, MEM_MIB / 1024, SCALEDOWN_S)
        log["peak_allocated_bytes"] = r["peak_allocated_bytes"]
        (out_dir / f"{scene}-scene-log.json").write_text(json.dumps(log, indent=1) + "\n", encoding="utf-8")
        (out_dir / f"{scene}-mapanything.npz").write_bytes(r["npz"])
        sc = build_bundle(scene, out_dir / f"{scene}-mapanything.npz", out_dir,
                          "S06d/S06e Modal A10G scene_job on S06b runtime image")
        print(json.dumps({"scene": sc["id"], "points": sc["render"]["point_count"],
                          "timing_s": log["timing_s"], "gpu_seconds": log["gpu_seconds"],
                          "estimated_usd": log["cost"]["estimated"]["total_usd"]}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="offline: existing MapAnything npz -> validated scene bundle")
    ap.add_argument("scene")
    ap.add_argument("out")
    ap.add_argument("--npz", required=True)
    a = ap.parse_args()
    sc = build_bundle(a.scene, a.npz, a.out, f"S06d offline conversion of existing MapAnything output {Path(a.npz).name}")
    print(f"PASS {sc['id']} points={sc['render']['point_count']} synthetic={sc['synthetic']} (not Gate R evidence)")
