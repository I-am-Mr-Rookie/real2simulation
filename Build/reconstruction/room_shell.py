"""N39: room job -> simple lab shell (owner decision Nov 2: simple shell + main furniture, no clutter).

Floor = live_room's RANSAC plane (y = 0). Walls = Manhattan planes fitted to the MapAnything points (yaw search on the
horizontal point histogram); hosted SAM 3.1 "window"/"door" boxes become openings cut into the wall they sit on.
Furniture = hosted SAM 3.1 noun prompts on a few keyframes -> N14 box proxy per detection -> merged across views ->
box extended down to the floor -> small items on top surfaces masked out -> SF3D shape via the N31 path (box fallback
with reason). Everything else is dropped and counted. Geometry MODEL-ESTIMATED; scale from room.json.
"""
import numpy as np

from Build.reconstruction import live_room, object_lift

# prompt noun -> merge group (a desk seen as "table" in another view is the same item)
FURNITURE = {"table": "table", "desk": "table", "chair": "chair", "sofa": "sofa", "bed": "bed", "shelf": "shelf",
             "cabinet": "shelf"}
FEATURES = ("window", "door")
TOP_SURFACE = ("table", "desk", "shelf", "cabinet")  # clutter on these is masked out before SF3D
KEYFRAMES = 8  # all sampled room frames (8): with 3, the N06 window and door were never in view
MIN_TOP = 0.05  # model metres; N06's coffee table top is about 0.1 above the fitted floor (scale unverified)
MIN_SPAN = 0.25
MAX_SF3D = 3  # SF3D GPU calls per shell (largest items first); the rest keep their measured box, with the reason
WALL_T = 0.08
MIN_SUPPORT = 0.04  # fraction of wall-band points within one cell of the plane


def keyframes(n, k=KEYFRAMES):
    m = min(k, n)
    return sorted({int(round(i * (n - 1) / max(1, m - 1))) for i in range(m)})


def top_surface(h, w=0.02):
    """Top of the densest horizontal layer of an object's points (the table top under a laptop): p95 of the points
    within 3 bins of the histogram peak. Returns (surface height, bin width); points above surface + w are clutter."""
    h = np.asarray(h, float)
    counts, edges = np.histogram(h, bins=np.arange(h.min(), h.max() + 2 * w, w))
    c = edges[int(np.argmax(counts))] + w / 2
    return float(np.percentile(h[np.abs(h - c) <= 3 * w], 95)), w


def _heights(npz, view, mask, room):
    v = live_room.load_views(npz)[view]
    rot, origin = object_lift._room_frame(npz)
    return ((v["pts_img"].reshape(-1, 3)[mask.reshape(-1)] - origin) @ rot.T * room["scale"]["metres_per_model_unit"])[:, 1]


def furniture(npz, room, detections):
    """detections: [(view, noun, box)] -> (kept [{noun, view, box, proxy, views}], dropped {reason: count})."""
    items, dropped = [], {}

    def drop(reason):
        dropped[reason] = dropped.get(reason, 0) + 1
    for view, noun, box in detections:
        point = [(box[1] + box[3]) / 2, (box[0] + box[2]) / 2]
        try:
            p = object_lift.lift(npz, view, point, box, room)
        except ValueError:
            drop("no reconstructed points")
            continue
        top = p["position"][1] + p["size"][1] / 2
        if noun in TOP_SURFACE and p["mask"].any():  # items on the top surface: out of the cut-out and the box
            h = _heights(npz, view, p["mask"], room)
            surface, w = top_surface(h)
            m = p["mask"].reshape(-1).copy()
            m[np.flatnonzero(m)[h > surface + w]] = False
            p["mask"], p["clutter_px"] = m.reshape(p["mask"].shape), int((h > surface + w).sum())
            top = min(top, surface)
        if top < MIN_TOP or max(p["size"][0], p["size"][2]) < MIN_SPAN:
            drop("too small for main furniture")
            continue
        p["position"][1], p["size"][1] = round(top / 2, 4), round(top, 4)  # measured box reaches the floor
        items.append({"noun": noun, "view": view, "box": [int(x) for x in box], "proxy": p, "views": [view]})
    kept = []
    for it in sorted(items, key=lambda x: -x["proxy"]["points"]):
        p = it["proxy"]
        same = lambda k: FURNITURE[k["noun"]] == FURNITURE[it["noun"]]  # noqa: E731
        twin = next((k for k in kept if np.hypot(
            p["position"][0] - k["proxy"]["position"][0], p["position"][2] - k["proxy"]["position"][2])
            < (0.5 if same(k) else 0.3) * max(p["size"][0], p["size"][2], k["proxy"]["size"][0], k["proxy"]["size"][2])), None)
        if twin:
            twin["views"].append(it["view"])
            drop("same item seen in another view" if same(twin) else "overlaps a larger detected item")
        else:
            kept.append(it)
    return kept, dropped


def _axes(a):
    return np.array([np.cos(a), -np.sin(a)]), np.array([np.sin(a), np.cos(a)])  # local x, local z in (x, z)


def walls(aligned, cell=0.05):
    """Room-frame points (metres, floor y = 0) -> (yaw, [wall]) with wall = {axis 0|1, side -1|1, plane, support,
    p95_residual, span [lo, hi], height}; sides without enough support are reported as not observed."""
    y = aligned[:, 1]
    top = np.percentile(y, 98)
    band = aligned[(y > 0.15 * top) & (y < 0.85 * top)]
    xz = band[:, [0, 2]]

    def score(a):
        ex, ez = _axes(a)
        return sum(float((np.histogram(xz @ e, bins=max(1, int(np.ptp(xz @ e) / cell)))[0].astype(float) ** 2).sum())
                   for e in (ex, ez))
    yaw = max(np.radians(np.arange(0, 90, 1.0)), key=score)
    ex, ez = _axes(yaw)
    uv = np.column_stack([xz @ ex, xz @ ez])
    out = []
    for axis in (0, 1):
        c = uv[:, axis]
        med = np.median(c)
        for side in (-1, 1):
            half = c[(c - med) * side > 0]
            counts, edges = np.histogram(half, bins=max(1, int(np.ptp(half) / cell)))
            centre = (edges[np.argmax(counts)] + edges[np.argmax(counts) + 1]) / 2
            near = np.abs(c - centre) <= cell
            plane = float(np.median(c[near]))
            near = np.abs(c - plane) <= cell
            w = {"axis": axis, "side": side, "plane": round(plane, 4), "support": round(float(near.mean()), 4)}
            if w["support"] < MIN_SUPPORT:
                out.append({**w, "status": "not observed"})
                continue
            o = uv[near, 1 - axis]
            out.append({**w, "status": "FIT", "p95_residual": round(float(np.percentile(np.abs(c[near] - plane), 95)), 4),
                        "span": [round(float(np.percentile(o, 2)), 4), round(float(np.percentile(o, 98)), 4)],
                        "height": round(float(top), 4)})
    fit = [w for w in out if w["status"] == "FIT"]
    for w in fit:  # stretch each wall to the planes of the walls across its ends
        ends = [x["plane"] for x in fit if x["axis"] != w["axis"]]
        if len(ends) == 2:
            w["span"] = sorted(ends)
    return float(yaw), out


def opening(npz, view, box, room, yaw, fit, noun, tol=0.2):
    """SAM window/door box -> {wall index, along [lo, hi], y [lo, hi]} on the FIT wall holding most of its points."""
    v = live_room.load_views(npz)[view]
    h, w = v["pts_img"].shape[:2]
    rr, cc = np.divmod(np.arange(h * w), w)
    sel = v["mask"] & (cc >= box[0]) & (cc <= box[2]) & (rr >= box[1]) & (rr <= box[3])
    rot, origin = object_lift._room_frame(npz)
    q = (v["pts_img"].reshape(-1, 3)[sel] - origin) @ rot.T * room["scale"]["metres_per_model_unit"]
    q = q[np.isfinite(q).all(1)]
    ex, ez = _axes(yaw)
    uv = np.column_stack([q[:, [0, 2]] @ ex, q[:, [0, 2]] @ ez])
    best = max(((i, np.abs(uv[:, wl["axis"]] - wl["plane"]) <= tol) for i, wl in enumerate(fit)),
               key=lambda t: t[1].sum(), default=(None, None))
    if best[0] is None or best[1].sum() < 30:
        return None
    i, near = best
    a, y = uv[near, 1 - fit[i]["axis"]], q[near, 1]
    lo = 0.0 if noun == "door" else max(0.0, float(np.percentile(y, 5)))
    return {"wall": i, "noun": noun, "view": view, "along": [round(float(np.percentile(a, 5)), 4),
            round(float(np.percentile(a, 95)), 4)], "y": [round(lo, 4), round(float(np.percentile(y, 95)), 4)]}


def pieces(span, height, holes):
    """Wall [span] x [0, height] minus rectangular holes (along, y) -> boxes [(a0, a1, y0, y1)]."""
    merged = []
    for a, y in sorted((h["along"], h["y"]) for h in holes):
        a = [max(span[0], a[0]), min(span[1], a[1])]
        if a[1] - a[0] < 0.05:
            continue
        if merged and a[0] <= merged[-1][0][1]:
            m = merged[-1]
            merged[-1] = ([m[0][0], max(m[0][1], a[1])], [min(m[1][0], y[0]), max(m[1][1], y[1])])
        else:
            merged.append((a, list(y)))
    out, cur = [], span[0]
    for a, y in merged:
        if a[0] - cur > 0.01:
            out.append((cur, a[0], 0.0, height))
        if y[0] > 0.02:
            out.append((a[0], a[1], 0.0, y[0]))
        if height - y[1] > 0.02:
            out.append((a[0], a[1], y[1], height))
        cur = a[1]
    if span[1] - cur > 0.01:
        out.append((cur, span[1], 0.0, height))
    return out


def wall_objects(yaw, fit, holes):
    """FIT walls (with openings cut out) -> fixed lab-scene-v1 blocks just outside the fitted plane."""
    ex, ez = _axes(yaw)
    q = [0, round(float(np.sin(yaw / 2)), 6), 0, round(float(np.cos(yaw / 2)), 6)]
    objs = []
    for i, w in enumerate(fit):
        for j, (a0, a1, y0, y1) in enumerate(pieces(w["span"], w["height"], [h for h in holes if h["wall"] == i])):
            n, a = w["plane"] + w["side"] * WALL_T / 2, (a0 + a1) / 2
            u, v = (n, a) if w["axis"] == 0 else (a, n)
            x, z = u * ex + v * ez
            size = [WALL_T, y1 - y0, a1 - a0] if w["axis"] == 0 else [a1 - a0, y1 - y0, WALL_T]
            objs.append({"id": f"wall-{i + 1}-{j + 1}", "kind": "block", "position": [round(float(x), 4),
                         round((y0 + y1) / 2, 4), round(float(z), 4)], "size": [round(max(s, 0.005), 4) for s in size],
                         "rotation": q, "fixed": True, "sensor": False, "mass": 100.0, "friction": 0.5})
    return objs


def build(npz, room, scene, detect, generate=None, glb_url=None):
    """npz bytes + room.json + scene.json -> (scene with shell objects, shell summary, {object id: glb bytes}).
    detect(png, noun, w, h) -> [boxes] (one hosted SAM 3.1 image call); generate(rgba png) -> SF3D dict or None."""
    views = live_room.load_views(npz)
    frames = keyframes(len(views))
    found = {"furniture": [], "features": []}
    calls = 0
    for view in frames:
        png, w, h = object_lift.view_png(npz, view)
        for noun in [*FURNITURE, *FEATURES]:
            calls += 1
            for b in detect(png, noun, w, h):
                found["features" if noun in FEATURES else "furniture"].append((view, noun, b))
    aligned, _, _, _ = live_room.analyse(npz)
    yaw, all_walls = walls(aligned)
    fit = [w for w in all_walls if w["status"] == "FIT"]
    holes = [o for o in (opening(npz, v, b, room, yaw, fit, n) for v, n, b in found["features"]) if o]
    kept, dropped = furniture(npz, room, found["furniture"])
    out = {**scene, "objects": [o for o in scene.get("objects", []) if not str(o.get("id", "")).startswith("wall-")]}
    out["objects"] += wall_objects(yaw, fit, holes)
    glbs, kept_list = {}, []
    for n_item, it in enumerate(kept):
        p, noun = it["proxy"], it["noun"]
        out, obj = object_lift.to_scene(out, p, category=noun)
        gen = {}
        try:  # N31 path: SF3D shape fitted to the measured box; any failure keeps the box with the reason
            if generate is None:
                raise RuntimeError("SF3D not requested")
            if n_item >= MAX_SF3D:
                raise RuntimeError(f"SF3D limit ({MAX_SF3D} per room) reached")
            gen = generate(object_lift.crop_rgba(npz, it["view"], it["box"], p["mask"]))
            turns, verts, idx = object_lift.fit_mesh(gen["vertices"], gen["faces"], p)
            glbs[obj["id"]] = gen["glb"]
            obj["shape"] = object_lift.mesh_shape(noun, glb_url(obj["id"]) if glb_url else "", turns, verts, idx)
        except Exception as e:  # noqa: BLE001  shape is optional: the box is the documented fallback
            obj["shape"] = {"type": "box", "fallback_reason": f"SF3D: {type(e).__name__}: {e}"[:300]}
        kept_list.append({"id": obj["id"], "category": noun, "views": it["views"], "points": p["points"],
                          "size_m": obj["size"], "size_sd_m": p["size_sd"], "clutter_px_masked": p.get("clutter_px", 0),
                          "shape": obj["shape"]["type"], "fallback_reason": obj["shape"].get("fallback_reason"),
                          "sf3d": {k: gen.get(k) for k in ("gpu", "wall_s", "inference_s", "estimated_usd")} if gen else None,
                          "reason": f"main furniture ({noun}), {len(it['views'])} view(s), box reaches the floor"})
    shell = {"schema": "n39-shell/1", "keyframes": frames, "sam_calls": calls, "sam_cost_usd": round(calls * object_lift.USD_PER_IMAGE, 4),
             "floor": room["floor"]["status"], "yaw_deg": round(float(np.degrees(yaw)), 2), "walls": all_walls,
             "openings": holes, "kept": kept_list, "dropped": sum(dropped.values()), "dropped_reasons": dropped,
             "detections": {"furniture": len(found["furniture"]), "features": len(found["features"])},
             "labels": {"geometry": "MODEL-ESTIMATED", "scale": room["scale"]["status"],
                        "shape": "MODEL-GENERATED shape, Powered by Stability AI (mesh items only)",
                        "note": "only floor, walls and main furniture; clutter dropped; dense collision boxes off by default"}}
    return out, shell, glbs
