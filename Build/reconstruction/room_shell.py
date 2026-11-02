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
OUTSIDE_MAX = 0.1  # N44: a wall bounds the room: at most this share of its side's points beyond it (doors, windows)
MERGE_OVERLAP = 0.3  # N42: footprints overlapping this much (of the smaller) are parts of one item
PARTS = ("table", "shelf")  # N42: merge groups that form one item when they overlap (desk + hutch, desk + cabinet)
MAX_TABLE = 1.1  # N42: a "table"/"desk" top above this (m above the floor) is front-view clutter (N39 1.26 m "table")


def keyframes(n, k=KEYFRAMES):
    m = min(k, n)
    return sorted({int(round(i * (n - 1) / max(1, m - 1))) for i in range(m)})


def top_surface(h, w=0.02, flat=None):
    """Top of the densest horizontal layer of an object's points (the table top under a laptop): p95 of the points
    within 3 bins of the histogram peak. Returns (surface height, bin width); points above surface + w are clutter.
    flat (N42): mask of points on horizontal surfaces below the camera; the peak is taken among them when there are
    enough, so a front view (desk face, book stacks, hutch) still finds the desk top instead of a 1.26 m "table"."""
    h = np.asarray(h, float)
    peak = h[flat] if flat is not None and np.count_nonzero(flat) >= 30 else h
    counts, edges = np.histogram(peak, bins=np.arange(peak.min(), peak.max() + 2 * w, w))
    c = edges[int(np.argmax(counts))] + w / 2
    return float(np.percentile(h[np.abs(h - c) <= 3 * w], 95)), w


def _heights(npz, view, mask, room, camera_y=np.inf):
    """Room-frame heights of the masked points + which lie on horizontal surfaces seen from above (N42: grid normals
    within about 25 deg of vertical, below the camera)."""
    v = live_room.load_views(npz)[view]
    rot, origin = object_lift._room_frame(npz)
    p = (v["pts_img"] - origin) @ rot.T * room["scale"]["metres_per_model_unit"]
    n = np.cross(*np.gradient(p, axis=(0, 1)))
    m = mask.reshape(p.shape[:2])
    h = p[m][:, 1]
    flat = np.abs(n[m][:, 1]) > 0.9 * np.linalg.norm(n[m], axis=1)
    return h, flat & (h < camera_y - 0.05)


def _footprint_overlap(a, b):
    """Fraction of the smaller footprint covered by the other, and the union rectangle in a's local x/z (lo, hi).
    b's footprint is taken as its bounding rectangle in a's axes (yaw boxes)."""
    ya, yb = (2 * np.arctan2(p["rotation"][1], p["rotation"][3]) for p in (a, b))
    d = np.subtract(b["position"], a["position"])[[0, 2]]
    corners = []
    for su in (-0.5, 0.5):
        for sw in (-0.5, 0.5):
            u, w = su * b["size"][0], sw * b["size"][2]
            x, z = d[0] + u * np.cos(yb) + w * np.sin(yb), d[1] - u * np.sin(yb) + w * np.cos(yb)
            corners.append([x * np.cos(ya) - z * np.sin(ya), x * np.sin(ya) + z * np.cos(ya)])
    blo, bhi = np.min(corners, 0), np.max(corners, 0)
    ahi = np.array([a["size"][0], a["size"][2]]) / 2
    inter = np.prod(np.clip(np.minimum(ahi, bhi) - np.maximum(-ahi, blo), 0, None))
    small = min(np.prod(2 * ahi), b["size"][0] * b["size"][2])
    return float(inter / small) if small > 0 else 0.0, np.minimum(-ahi, blo), np.maximum(ahi, bhi)


def _grow(p, lo, hi):
    """Box proxy p grown to the local x/z rectangle (lo, hi); height kept (support top of the best view)."""
    yaw = 2 * np.arctan2(p["rotation"][1], p["rotation"][3])
    cu, cw = (lo + hi) / 2
    p["position"][0] = round(float(p["position"][0] + cu * np.cos(yaw) + cw * np.sin(yaw)), 4)
    p["position"][2] = round(float(p["position"][2] - cu * np.sin(yaw) + cw * np.cos(yaw)), 4)
    p["size"][0], p["size"][2] = round(float(hi[0] - lo[0]), 4), round(float(hi[1] - lo[1]), 4)


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
            h, flat = _heights(npz, view, p["mask"], room, p["camera"][1])
            surface, w = top_surface(h, flat=flat)
            m = p["mask"].reshape(-1).copy()
            m[np.flatnonzero(m)[h > surface + w]] = False
            p["mask"], p["clutter_px"] = m.reshape(p["mask"].shape), int((h > surface + w).sum())
            top = min(top, surface)
            if noun in ("table", "desk") and top > MAX_TABLE:
                drop(f"table top above {MAX_TABLE} m (front-view clutter, not a table)")
                continue
        if top < MIN_TOP or max(p["size"][0], p["size"][2]) < MIN_SPAN:
            drop("too small for main furniture")
            continue
        p["position"][1], p["size"][1] = round(top / 2, 4), round(top, 4)  # measured box reaches the floor
        items.append({"noun": noun, "view": view, "box": [int(x) for x in box], "proxy": p, "views": [view]})
    kept = []
    for it in sorted(items, key=lambda x: -x["proxy"]["points"]):
        p = it["proxy"]
        same = lambda k: FURNITURE[k["noun"]] == FURNITURE[it["noun"]]  # noqa: E731
        # parts of one item: overlap with the kept item's first (ungrown) footprint, so merges do not snowball
        part = lambda k: ((same(k) or {FURNITURE[k["noun"]], FURNITURE[it["noun"]]} <= set(PARTS))  # noqa: E731
                          and _footprint_overlap(k["box0"], p)[0] > MERGE_OVERLAP)
        twin = next((k for k in kept if np.hypot(
            p["position"][0] - k["proxy"]["position"][0], p["position"][2] - k["proxy"]["position"][2])
            < (0.5 if same(k) else 0.3) * max(p["size"][0], p["size"][2], k["proxy"]["size"][0], k["proxy"]["size"][2])
            or part(k)), None)
        if twin:
            # N42: parts of one item (desk + hutch, other views) become one box over the union footprint
            if part(twin):  # a centre-distance twin with little overlap is a misaligned view: no growth
                _, lo, hi = _footprint_overlap(twin["proxy"], p)
                _grow(twin["proxy"], lo, hi)
            twin["views"].append(it["view"])
            twin.setdefault("merged", []).append(it["noun"])
            drop("same item seen in another view (merged)" if same(twin) else "part of a larger detected item (merged)")
        else:
            it["box0"] = {k: list(p[k]) for k in ("position", "size", "rotation")}
            kept.append(it)
    return kept, dropped


def _axes(a):
    return np.array([np.cos(a), -np.sin(a)]), np.array([np.sin(a), np.cos(a)])  # local x, local z in (x, z)


def walls(aligned, inside=(), cell=0.05):
    """Room-frame points (metres, floor y = 0) -> (yaw, [wall]) with wall = {axis 0|1, side -1|1, plane, support,
    p95_residual, span [lo, hi], height}; sides without enough support are reported as not observed.
    N44: the plane is the densest cell among those with at most OUTSIDE_MAX of the side's points beyond it (the plain
    peak per half picked desk rows next to the median: RM02 and N06 "walls" 0.05 to 0.2 apart). inside = room-frame
    (x, z) of the cameras and kept furniture centres; a wall with one of them beyond it is not observed (partial view of
    a large room: RM02's nearest desk row looked like a wall in front of the camera)."""
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
            if len(half) < 30:  # nothing on this side of the room (N42: exact synthetic floors left it empty)
                out.append({"axis": axis, "side": side, "plane": None, "support": 0.0, "status": "not observed"})
                continue
            counts, edges = np.histogram(half, bins=max(1, int(np.ptp(half) / cell)))
            beyond = np.cumsum(counts[::-1])[::-1] - counts if side > 0 else np.cumsum(counts) - counts
            k = int(np.argmax(np.where(beyond <= OUTSIDE_MAX * len(half), counts, -1)))
            centre = (edges[k] + edges[k + 1]) / 2
            near = np.abs(c - centre) <= cell
            plane = float(np.median(c[near]))
            near = np.abs(c - plane) <= cell
            w = {"axis": axis, "side": side, "plane": round(plane, 4), "support": round(float(near.mean()), 4)}
            if w["support"] < MIN_SUPPORT:
                out.append({**w, "status": "not observed"})
                continue
            outside = [p for p in inside if side * (np.dot(p, ex if axis == 0 else ez) - plane) > cell]
            if outside:
                out.append({**w, "status": "not observed", "reason": f"{len(outside)} camera or furniture position(s) beyond it"})
                continue
            o = uv[near, 1 - axis]
            out.append({**w, "status": "FIT", "p95_residual": round(float(np.percentile(np.abs(c[near] - plane), 95)), 4),
                        "span": [round(float(np.percentile(o, 2)), 4), round(float(np.percentile(o, 98)), 4)],
                        "height": round(float(top), 4)})
    fit = [w for w in out if w["status"] == "FIT"]
    for w in fit:  # stretch each wall to the planes of the FIT walls across its ends (N44: also when only one is FIT)
        ends = [x["plane"] for x in fit if x["axis"] != w["axis"]]
        w["span"] = sorted(ends) if len(ends) == 2 else [min([w["span"][0], *ends]), max([w["span"][1], *ends])]
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
    o = {"wall": i, "noun": noun, "view": view, "along": [round(float(np.percentile(a, 5)), 4),
         round(float(np.percentile(a, 95)), 4)], "y": [round(lo, 4), round(float(np.percentile(y, 95)), 4)]}
    return o if on_wall(o, fit[i]) else None


def on_wall(o, wall, min_len=0.05):
    """N44: an opening counts only when its rectangle overlaps its wall's (N43 RM02: 0 of 24 did)."""
    return (min(o["along"][1], wall["span"][1]) - max(o["along"][0], wall["span"][0]) >= min_len
            and o["y"][0] < wall["height"] and o["y"][1] > 0)


def merge_openings(holes):
    """N44: the same window seen in several views is one opening (N43: 24 reported for a few windows): overlapping
    rectangles on one wall merge into their union, nouns and views kept."""
    out = []
    for h in sorted(holes, key=lambda h: (h["wall"], h["along"][0])):
        m = out[-1] if out and out[-1]["wall"] == h["wall"] else None
        if m and h["along"][0] <= m["along"][1] and h["y"][0] <= m["y"][1] and h["y"][1] >= m["y"][0]:
            m["along"][1], m["y"] = max(m["along"][1], h["along"][1]), [min(m["y"][0], h["y"][0]), max(m["y"][1], h["y"][1])]
            m["views"] = sorted({*m["views"], h["view"]})
            m["noun"] = "door" if "door" in (m["noun"], h["noun"]) else m["noun"]
        else:
            out.append({**h, "along": list(h["along"]), "y": list(h["y"]), "views": [h["view"]]})
    return out


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
    kept, dropped = furniture(npz, room, found["furniture"])
    inside = [(c[0], c[2]) for c in room.get("camera_positions_m", [])] + [
        (it["proxy"]["position"][0], it["proxy"]["position"][2]) for it in kept]
    yaw, all_walls = walls(aligned, inside)
    fit = [w for w in all_walls if w["status"] == "FIT"]
    cand = [opening(npz, v, b, room, yaw, fit, n) for v, n, b in found["features"]]
    holes = merge_openings([o for o in cand if o])
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
            turns, verts, idx, support = object_lift.fit_mesh(gen["vertices"], gen["faces"], p, noun in TOP_SURFACE)
            glbs[obj["id"]] = gen["glb"]
            obj["shape"] = object_lift.mesh_shape(noun, glb_url(obj["id"]) if glb_url else "", turns, verts, idx, support)
        except Exception as e:  # noqa: BLE001  shape is optional: the box is the documented fallback
            obj["shape"] = {"type": "box", "fallback_reason": f"SF3D: {type(e).__name__}: {e}"[:300]}
        kept_list.append({"id": obj["id"], "category": noun, "views": it["views"], "merged": it.get("merged", []), "points": p["points"],
                          "size_m": obj["size"], "size_sd_m": p["size_sd"], "clutter_px_masked": p.get("clutter_px", 0),
                          "shape": obj["shape"]["type"], "fallback_reason": obj["shape"].get("fallback_reason"),
                          "sf3d": {k: gen.get(k) for k in ("gpu", "wall_s", "inference_s", "estimated_usd")} if gen else None,
                          "reason": f"main furniture ({noun}), {len(it['views'])} view(s), box reaches the floor"})
    shell = {"schema": "n39-shell/1", "keyframes": frames, "sam_calls": calls, "sam_cost_usd": round(calls * object_lift.USD_PER_IMAGE, 4),
             "floor": room["floor"]["status"], "yaw_deg": round(float(np.degrees(yaw)), 2), "walls": all_walls,
             "openings": holes, "opening_detections_off_wall": sum(o is None for o in cand),
             "kept": kept_list, "dropped": sum(dropped.values()), "dropped_reasons": dropped,
             "detections": {"furniture": len(found["furniture"]), "features": len(found["features"])},
             "labels": {"geometry": "MODEL-ESTIMATED", "scale": room["scale"]["status"],
                        "shape": "MODEL-GENERATED shape, Powered by Stability AI (mesh items only)",
                        "note": "only floor, walls and main furniture; clutter dropped; dense collision boxes off by default"}}
    return out, shell, glbs
