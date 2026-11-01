"""N14: click an object in a room view -> hosted SAM 3.1 image point prompt -> box -> MapAnything points of that
object -> gravity-aligned box proxy with measured size -> lab-scene-v1 "block" (closest primitive), MODEL-ESTIMATED.

SAM 3D Objects stays off (Build/gpu/sam3d_option.gate: no owner licence receipt, A10G 23 GB < 32 GB), so no mesh.
The click view is the room job's own MapAnything view image (model grid pixels), so SAM pixels = point-map pixels.
Masks are not decoded (same as hosted_sam): object points = SAM box x depth band around the clicked surface.
Paid call: one sam-3.1 image call, reserved/settled on Build/guardrails/daily_cap.py ($2.50 per 1k images).
N31: those object pixels also form the RGBA cut-out for Stable Fast 3D (Build/gpu/sf3d.py); its unit-scale mesh is
turned to face the camera (quarter turns), fitted into the measured box and stored as the object's shape (physics too).
"""
import base64
import io
import json
import threading

import numpy as np

from Build.measurement import hosted_sam
from Build.reconstruction import live_room

USD_PER_IMAGE = 2.50 / 1000
WINDOW = 2  # click depth = median of the valid points in a (2*WINDOW+1)^2 pixel window
_LOCK = threading.Lock()
# Typical values per category (fixed, kg, friction): MODEL-ESTIMATED, not measured. Static room furniture -> trimesh.
CATEGORIES = {"desk": (True, 30.0, 0.5), "table": (True, 25.0, 0.5), "chair": (True, 6.0, 0.5), "sofa": (True, 40.0, 0.8),
              "shelf": (True, 20.0, 0.5), "cabinet": (True, 30.0, 0.5), "bed": (True, 50.0, 0.8),
              "box": (False, 1.0, 0.5), "ball": (False, 0.4, 0.6), "book": (False, 0.5, 0.4), "bottle": (False, 0.5, 0.3),
              "other": (False, 1.0, 0.5)}
MAX_TRIANGLES = 6000  # SF3D remesh targets about 2k; scene JSON stays well under 512 KiB


def view_png(npz, view):
    """The view's own RGB (img_no_norm, model grid) as PNG bytes, plus (width, height)."""
    from PIL import Image
    views = live_room.load_views(npz)
    if not (isinstance(view, int) and 0 <= view < len(views)):
        raise ValueError(f"view must be an integer 0..{len(views) - 1}")
    h, w = views[view]["pts_img"].shape[:2]
    buf = io.BytesIO()
    Image.fromarray(np.clip(views[view]["rgb"].reshape(h, w, 3) * 255 + 0.5, 0, 255).astype(np.uint8)).save(buf, "PNG")
    return buf.getvalue(), w, h


def sam_box(png, point, width, height, cap_path=None, timeout=300):
    """One hosted sam-3.1 image call with a positive point [row, col]. Returns (box x1,y1,x2,y2, raw response)."""
    from Build.guardrails import daily_cap
    row, col = point
    prompt = hosted_sam.point_prompt(1, [(col, row, True)], width, height)
    body = {"model": "sam-3.1", "metadata": {"mask_encoding": "one_bit"}, "input": [{"type": "message", "role": "user",
            "content": [{"type": "input_text", "text": prompt}, {"type": "input_image",
                         "image_url": "data:image/png;base64," + base64.b64encode(png).decode()}]}]}
    rid = daily_cap.reserve("Meta Model API", USD_PER_IMAGE, "N14 sam-3.1 image point prompt", path=cap_path)
    try:  # billed or failed, one image is counted (a failed call's cost is unknown, so count it)
        resp = hosted_sam._post("/responses", json.dumps(body).encode(), "application/json", timeout)
    finally:
        daily_cap.settle(rid, USD_PER_IMAGE, path=cap_path)
    return pick_box(hosted_sam.output_text(resp), point), resp


def pick_box(text, point):
    """Box of the object containing the click (smallest if several); image replies may omit the <0f> tag."""
    frames, _ = hosted_sam.parse(text if hosted_sam._FRAME.search(text) else "<0f>" + text)
    row, col = point
    boxes = [b for f in frames.values() for b in f.values() if b[0] <= col <= b[2] and b[1] <= row <= b[3]]
    if not boxes:
        raise ValueError("sam-3.1 returned no object at the click")
    return min(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))


def _room_frame(npz):
    """(rot, origin) of N08's gravity-aligned lab frame: rerun live_room.analyse (seeded) and read _frame's output."""
    got, real = {}, live_room._frame

    def spy(*a):
        got["rot"], got["origin"] = out = real(*a)
        return out
    # shortcut: patches a module function under a lock and reruns the CPU analysis (seconds); upgrade: N08 saves rot/origin
    with _LOCK:
        live_room._frame = spy
        try:
            live_room.analyse(npz)
        finally:
            live_room._frame = real
    return got["rot"], got["origin"]


def lift(npz, view, point, box, room):
    """Object points -> gravity-aligned box proxy in the room frame. room = room.json (scale k and its sd)."""
    views = live_room.load_views(npz)
    if not (isinstance(view, int) and 0 <= view < len(views)):
        raise ValueError(f"view must be an integer 0..{len(views) - 1}")
    v = views[view]
    h, w = v["pts_img"].shape[:2]
    row, col = (int(round(x)) for x in point)
    if not (0 <= row < h and 0 <= col < w):
        raise ValueError(f"point must be [row, col] inside {h}x{w}")
    pts = v["pts_img"].reshape(-1, 3)
    cam = (pts - v["pose"][:3, 3]) @ v["pose"][:3, :3]  # world -> camera (OpenCV, z forward)
    ok = v["mask"] & np.isfinite(cam).all(1) & (cam[:, 2] > 0)
    rr, cc = np.divmod(np.arange(h * w), w)
    fx = np.polyfit(cam[ok, 0] / cam[ok, 2], cc[ok], 1)[0]  # focal (px) from the point map: col = f x/z + cx
    near = ok & (abs(rr - row) <= WINDOW) & (abs(cc - col) <= WINDOW)
    if not near.any():
        raise ValueError("no reconstructed depth at the click")
    z0 = float(np.median(cam[near, 2]))
    x1, y1, x2, y2 = box
    # depth band: +-half the largest visible side (object about as deep as wide), so the wall behind drops out
    extent = z0 * max(x2 - x1 + 1, y2 - y1 + 1) / abs(fx)
    sel = ok & (cc >= x1) & (cc <= x2) & (rr >= y1) & (rr <= y2) & (abs(cam[:, 2] - z0) <= extent / 2)
    rot, origin = _room_frame(npz)
    k = room["scale"]["metres_per_model_unit"]
    q = (pts[sel] - origin) @ rot.T * k
    if room["floor"]["status"] == "FIT":  # drop floor points inside the box: within 2x the floor fit's p95 residual
        q = q[q[:, 1] > 2 * room["floor"]["p95_abs_residual"] * k]
    if len(q) < 30:
        raise ValueError(f"only {len(q)} reconstructed points on the object")
    m = q[:, [0, 2]].mean(0)
    _, _, vt = np.linalg.svd(q[:, [0, 2]] - m, full_matrices=False)  # main horizontal axes
    local = np.column_stack([(q[:, [0, 2]] - m) @ vt[0], q[:, 1], (q[:, [0, 2]] - m) @ vt[1]])
    lo, hi = np.percentile(local, 5, 0), np.percentile(local, 95, 0)
    size = hi - lo
    sd = np.abs((np.percentile(local, 98, 0) - np.percentile(local, 2, 0)) - size) / 2  # boundary sensitivity
    rel = room["scale"].get("sd")
    if rel and room["scale"]["status"] == "MEASURED":
        sd = np.hypot(sd, size * rel)
    c = m + vt[0] * (lo[0] + hi[0]) / 2 + vt[1] * (lo[2] + hi[2]) / 2
    yaw = float(np.arctan2(-vt[0, 1], vt[0, 0]))  # about +Y: local x -> (cos, 0, -sin) = main axis
    mask = np.zeros(h * w, bool)
    idx = np.flatnonzero(sel)
    if room["floor"]["status"] == "FIT":
        idx = idx[((pts[idx] - origin) @ rot.T * k)[:, 1] > 2 * room["floor"]["p95_abs_residual"] * k]
    mask[idx] = True
    return {"position": [round(float(x), 4) for x in (c[0], (lo[1] + hi[1]) / 2, c[1])],
            "size": [round(float(s), 4) for s in size], "size_sd": [round(float(s), 4) for s in sd],
            "rotation": [0, round(float(np.sin(yaw / 2)), 6), 0, round(float(np.cos(yaw / 2)), 6)],
            "points": len(q), "focal_px": round(float(fx), 2),
            "camera": [round(float(x), 4) for x in (v["pose"][:3, 3] - origin) @ rot.T * k],  # room frame
            "mask": mask.reshape(h, w)}  # object pixels (box x depth band, floor dropped): the SF3D cut-out


def crop_rgba(npz, view, box, mask, pad=8):
    """PNG of the view inside the SAM box (+pad), alpha = the object's pixels. Input for SF3D."""
    from PIL import Image
    v = live_room.load_views(npz)[view]
    h, w = mask.shape
    x1, y1, x2, y2 = (int(round(b)) for b in box)
    x1, y1, x2, y2 = max(0, x1 - pad), max(0, y1 - pad), min(w, x2 + pad + 1), min(h, y2 + pad + 1)
    rgb = np.clip(v["rgb"].reshape(h, w, 3) * 255 + 0.5, 0, 255).astype(np.uint8)
    rgba = np.dstack([rgb, mask.astype(np.uint8) * 255])[y1:y2, x1:x2]
    buf = io.BytesIO()
    Image.fromarray(rgba, "RGBA").save(buf, "PNG")
    return buf.getvalue()


def fit_mesh(vertices, faces, proxy):
    """SF3D mesh (unit scale, glTF +Y up, front +Z) -> unit-box shape in the object's local frame.

    Turns the mesh by quarter turns about +Y so its front faces the camera, then the client and physics scale the
    unit box [-0.5, 0.5]^3 to the measured size. Returns (quarter_turns, flat vertices, flat indices)."""
    v, f = np.asarray(vertices, float), np.asarray(faces, np.int64)
    if v.ndim != 2 or v.shape[1] != 3 or f.ndim != 2 or f.shape[1] != 3 or not len(f) or f.min() < 0 or f.max() >= len(v):
        raise ValueError("SF3D returned a malformed mesh")
    if len(f) > MAX_TRIANGLES:
        raise ValueError(f"SF3D mesh has {len(f)} triangles (> {MAX_TRIANGLES})")
    qy, qw = proxy["rotation"][1], proxy["rotation"][3]
    yaw = 2 * np.arctan2(qy, qw)
    d = np.subtract(proxy["camera"], proxy["position"])
    dx = d[0] * np.cos(yaw) - d[2] * np.sin(yaw)  # camera direction in the box's local x/z
    dz = d[0] * np.sin(yaw) + d[2] * np.cos(yaw)
    turns = int(np.round(np.arctan2(dx, dz) / (np.pi / 2))) % 4  # R_y(turns*90 deg) takes +Z toward the camera
    a = turns * np.pi / 2
    v = np.column_stack([v[:, 0] * np.cos(a) + v[:, 2] * np.sin(a), v[:, 1], -v[:, 0] * np.sin(a) + v[:, 2] * np.cos(a)])
    lo, hi = v.min(0), v.max(0)
    if np.any(hi - lo < 1e-6):
        raise ValueError("SF3D mesh is flat")
    unit = (v - (lo + hi) / 2) / (hi - lo)
    return turns, [round(float(x), 4) for x in unit.ravel()], [int(i) for i in f.ravel()]


def mesh_shape(category, glb_url, turns, vertices, indices):
    """lab-scene-v1 shape of an SF3D object (Build/web/src/lab-editor/scene.mjs validates the same fields).
    Collider (physics.mjs meshCollider): trimesh while the object is fixed, convex hull when movable."""
    return {"type": "mesh", "label": "MODEL-GENERATED shape", "credit": "Powered by Stability AI", "category": category,
            "glb": glb_url, "quarter_turns": turns,
            "vertices": vertices, "indices": indices}


def to_scene(scene, proxy, shape=None, category="other"):
    """Append the object as a lab-scene-v1 block; shape = SF3D mesh shape, or the box fallback with its reason.
    Returns (scene, object). Mass/friction from the category (MODEL-ESTIMATED); other metadata stays out of the scene."""
    used = {o.get("id") for o in scene.get("objects", [])}
    n = 1
    while f"room-object-{n}" in used:
        n += 1
    fixed, mass, friction = CATEGORIES[category]
    obj = {"id": f"room-object-{n}", "kind": "block", "position": proxy["position"], "size": proxy["size"],
           "rotation": proxy["rotation"], "fixed": fixed, "sensor": False,  # solid: lab objects collide with it
           "mass": mass, "friction": friction}
    if shape:
        obj["shape"] = shape
    return {**scene, "objects": [*scene.get("objects", []), obj]}, obj
