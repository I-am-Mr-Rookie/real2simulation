"""Owner-scoped previews: frame pixels overlay their video; relative trajectories are separate labelled plots."""
import json
import math


def track_preview(result):
    track = (result or {}).get("track") or {}
    w, h, frames = track.get("width"), track.get("height"), track.get("frames")
    finite = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
    points = []
    kind, label = "frame", track.get("label") or "MEASURED: tracked frame-pixel path"
    if finite(w) and finite(h) and w > 0 and h > 0 and isinstance(frames, list):
        points = [[f[2], f[3]] for f in frames if isinstance(f, list) and len(f) >= 4
                  and finite(f[2]) and finite(f[3]) and 0 <= f[2] < w and 0 <= f[3] < h]
    if len(points) < 2:
        trajectory = (result or {}).get("trajectory") or {}
        x, y = trajectory.get("x"), trajectory.get("y")
        if not (isinstance(x, list) and isinstance(y, list) and len(x) == len(y)):
            return None
        points = [[a, b] for a, b in zip(x, y) if finite(a) and finite(b)]
        if len(points) < 2:
            return None
        lo_x, hi_x = min(p[0] for p in points), max(p[0] for p in points)
        lo_y, hi_y = min(p[1] for p in points), max(p[1] for p in points)
        w, h = max(hi_x - lo_x, 1), max(hi_y - lo_y, 1)
        points = [[a - lo_x, hi_y - b] for a, b in points]
        kind, label = "plot", "MEASURED: relative tracked path (" + str(trajectory.get("unit") or "units unverified") + "), not aligned to video"
    step = max(1, math.ceil(len(points) / 160))
    return {"kind": kind, "width": w, "height": h, "points": points[::step], "label": label}


def project_previews(store, owner):
    with store.lock:
        if not store.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='experiments'").fetchone():
            return {}
        rows = store.db.execute("SELECT project_id, file_id, result FROM experiments WHERE user=? AND status='done' ORDER BY updated DESC, id DESC", (owner,)).fetchall()
    previews = {}
    for row in rows:
        if row["project_id"] not in previews:
            preview = track_preview(json.loads(row["result"]) if row["result"] else None)
            previews[row["project_id"]] = {**preview, "file_id": row["file_id"]} if preview else None
    return previews
