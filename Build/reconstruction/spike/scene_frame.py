"""S05d: floor plane, gravity orientation and known-object scale from MapAnything npz.

CPU only. Abstains instead of inventing: metric scale needs a source-backed
reference (length + citation + pixel endpoints); gravity is ABSTAIN when the
clip source says the scene is not under gravity (e.g. ISS) or no floor is found.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

SEED = 0
CONF_QUANTILE = 0.5      # keep the more confident half of valid pixels
INLIER_M = 0.02          # model-unit (MapAnything metric) inlier band
PRIOR_MAX_DEG = 35.0     # floor normal must be within this of mean camera-down
ITERS = 400
BOOT = 50
PATCH_PX = 8            # hypothesis triplets are image-local, so low-inlier floors still get sampled
MIN_SUPPORT = 0.03      # floor = LOWEST plane with >=3% support (dominant plane is often a desk top)


def load_views(path):
    d = np.load(path)
    n = len({k.split("_")[0] for k in d.files if k.startswith("view")})
    views = []
    for i in range(n):
        p = f"view{i}_"
        views.append({"pts": d[p + "pts3d"][0].reshape(-1, 3),
                      "conf": d[p + "conf"][0].reshape(-1),
                      "mask": d[p + "mask"][0].reshape(-1) > 0.5,
                      "pose": d[p + "camera_poses"][0],
                      "msf": float(d[p + "metric_scaling_factor"].reshape(-1)[0]),
                      "pts_img": d[p + "pts3d"][0]})
    return views


def unit(v):
    return v / np.linalg.norm(v)


def refit(p):
    c = p.mean(0)
    return unit(np.linalg.svd(p - c, full_matrices=False)[2][-1]), c


def angle_deg(a, b):
    return float(np.degrees(np.arccos(np.clip(abs(np.dot(unit(a), unit(b))), 0, 1))))


def local_triplets(grids, rng):
    """Yield 3-point samples from image-adjacent pixels (P(all inliers) ~ inlier fraction, not its cube)."""
    while True:
        g, ok = grids[rng.integers(len(grids))]
        r, c = rng.integers(0, g.shape[0] - PATCH_PX), rng.integers(0, g.shape[1] - PATCH_PX)
        idx = ((r, c), (r + PATCH_PX, c), (r, c + PATCH_PX))
        if all(ok[i] for i in idx):
            yield np.stack([g[i] for i in idx])


def fit_floor(pts, down_prior, cam_centres, rng, samples):
    """RANSAC plane constrained near camera-down and below every camera."""
    best = None
    for _ in range(ITERS):
        s = next(samples)
        n = np.cross(s[1] - s[0], s[2] - s[0])
        if np.linalg.norm(n) < 1e-9:
            continue
        n = unit(n)
        if np.dot(n, down_prior) < 0:
            n = -n                                   # n points "down", toward floor
        if angle_deg(n, down_prior) > PRIOR_MAX_DEG:
            continue
        if np.any((cam_centres - s[0]) @ n > -INLIER_M):
            continue                                 # every camera must be above plane
        cnt = int((np.abs((pts - s[0]) @ n) < INLIER_M).sum())
        low = float(np.min((s[0] - cam_centres) @ n))   # height below the closest camera
        if cnt >= MIN_SUPPORT * len(pts) and (best is None or low > best[0] + INLIER_M
                                              or (abs(low - best[0]) <= INLIER_M and cnt > best[1])):
            best = (low, cnt, n, s[0])
    if best is None:
        return None
    _, _, n, o = best
    for _ in range(2):                               # least-squares polish on inliers
        inl = pts[np.abs((pts - o) @ n) < INLIER_M]
        n2, o = refit(inl)
        n = n2 if np.dot(n2, n) > 0 else -n2
    res = (inl - o) @ n
    boot = [angle_deg(refit(inl[rng.integers(0, len(inl), len(inl))])[0], n) for _ in range(BOOT)]
    return {"normal_down": n, "origin": o, "inliers": int(len(inl)),
            "inlier_fraction": float(len(inl) / len(pts)),
            "rms_residual": float(np.sqrt(np.mean(res ** 2))),
            "p95_abs_residual": float(np.percentile(np.abs(res), 95)),
            "normal_bootstrap_std_deg": float(np.std(boot)),
            "normal_bootstrap_max_deg": float(np.max(boot))}


def known_object_scale(views, ref):
    """ref: {view, p0:[row,col], p1:[row,col], length_m, length_sd_m, source[, pixel_sd_rel]}.

    Returns metres per model unit with propagated 1-sigma uncertainty."""
    if not ref.get("source") or not ref.get("length_m"):
        raise ValueError("known-object reference needs length_m and a source")
    img = _view_img(views, ref)
    a, b = (_pixel_point(img, ref[k]) for k in ("p0", "p1"))
    if tuple(ref["p0"]) == tuple(ref["p1"]):
        raise ValueError("reference endpoints must be distinct")
    model_len = float(np.linalg.norm(a - b))
    s = ref["length_m"] / model_len
    rel = np.hypot(ref.get("length_sd_m", 0.0) / ref["length_m"], ref.get("pixel_sd_rel", 0.0))
    return {"metres_per_model_unit": s, "sd": float(s * rel),
            "model_length": model_len, "source": ref["source"], "view": ref["view"],
            "p0": list(ref["p0"]), "p1": list(ref["p1"]), "length_m": ref["length_m"],
            "length_sd_m": ref.get("length_sd_m"), "raw_rel_error": abs(model_len - ref["length_m"]) / ref["length_m"]}


def _view_img(views, ref):
    if not isinstance(ref.get("view"), int) or not 0 <= ref["view"] < len(views):
        raise ValueError(f"reference view out of range: {ref.get('view')!r}")
    return views[ref["view"]]["pts_img"]


def _pixel_point(img, rc):
    r, c = rc
    if not (isinstance(r, int) and isinstance(c, int) and 0 <= r < img.shape[0] and 0 <= c < img.shape[1]):
        raise ValueError(f"pixel {rc!r} outside {img.shape[:2]}")
    p = img[r, c]
    if not np.isfinite(p).all():
        raise ValueError(f"pixel {rc!r} has no finite 3D sample")
    return p


def a4_plane(views, ref):
    """ref: {view, corners:[[row,col]x4], source}. Plane normal from 3D samples inside the annotated corners.

    shortcut: uses the corners' bounding box, not the exact quadrilateral; upgrade if the sheet is strongly oblique."""
    if not ref.get("source"):
        raise ValueError("A4 reference needs a source/identity citation")
    img = _view_img(views, ref)
    for rc in ref["corners"]:
        _pixel_point(img, rc)
    rs, cs = zip(*ref["corners"])
    patch = img[min(rs):max(rs) + 1, min(cs):max(cs) + 1].reshape(-1, 3)
    patch = patch[np.isfinite(patch).all(1)]
    if len(patch) < 3:
        raise ValueError("A4 region has <3 valid 3D samples")
    n, c = refit(patch)
    return n, {"samples": int(len(patch)), "rms_residual": float(np.sqrt(np.mean(((patch - c) @ n) ** 2))),
               "corners": [list(x) for x in ref["corners"]], "view": ref["view"], "source": ref["source"]}


def analyse(path, gravity_applicable=True, refs=(), a4_refs=()):
    rng = np.random.default_rng(SEED)
    views = load_views(path)
    keep = []
    grids = []
    for v in views:
        ok = v["mask"] & np.isfinite(v["pts"]).all(1)
        thr = np.quantile(v["conf"][ok], CONF_QUANTILE)
        keep.append(v["pts"][ok & (v["conf"] >= thr)])
        grids.append((v["pts_img"], (ok & (v["conf"] >= thr)).reshape(v["pts_img"].shape[:2])))
    pts = np.concatenate(keep)
    pts = pts[rng.choice(len(pts), min(len(pts), 60000), replace=False)]
    cams = np.stack([v["pose"][:3, 3] for v in views])
    # OpenCV camera convention: +y is image-down; pose is cam-to-world.
    down = unit(np.mean([v["pose"][:3, 1] for v in views], 0))
    floor = fit_floor(pts, down, cams, rng, local_triplets(grids, rng))
    out = {"npz_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
           "views": len(views), "points_used": int(len(pts)),
           "params": {"seed": SEED, "conf_quantile": CONF_QUANTILE, "inlier_band_model_units": INLIER_M,
                      "prior_max_deg": PRIOR_MAX_DEG, "ransac_iters": ITERS, "bootstrap": BOOT,
                      "patch_px": PATCH_PX},
           "mapanything_metric_scaling_factor": [round(v["msf"], 6) for v in views],
           "camera_down_prior": down.round(6).tolist()}
    if floor is None:
        out["floor"] = {"status": "ABSTAIN", "reason": "no plane below all cameras within prior"}
    else:
        n = floor["normal_down"]
        out["floor"] = {"status": "FIT", "normal_down": n.round(6).tolist(),
                        "angle_to_camera_down_prior_deg": round(angle_deg(n, down), 3),
                        "camera_heights_model_units": [round(float((floor["origin"] - c) @ n), 4) for c in cams],
                        **{k: floor[k] for k in ("inliers", "inlier_fraction", "rms_residual",
                                                 "p95_abs_residual", "normal_bootstrap_std_deg",
                                                 "normal_bootstrap_max_deg")}}
    if floor is None or not gravity_applicable:
        out["gravity"] = {"status": "ABSTAIN", "direction": None, "magnitude_m_s2": None,
                          "reason": "no floor fit" if floor is None else "clip source: not under gravity"}
    else:
        out["gravity"] = {"status": "estimated", "direction": n.round(6).tolist(), "magnitude_m_s2": None,
                          "uncertainty_deg_1sd": floor["normal_bootstrap_std_deg"],
                          "basis": "floor normal assumed horizontal; magnitude never assumed"}
    # No detector: an annotated, source-backed horizontal A4 sheet region is required; gravity must be estimated.
    if a4_refs and out["gravity"]["status"] == "estimated":
        fits = [a4_plane(views, r) for r in a4_refs]
        angles = [angle_deg(fn, n) for fn, _ in fits]
        out["a4_plane_normal"] = {"status": "MEASURED", "angle_to_gravity_deg": max(angles),
                                  "per_reference": [{**m, "angle_deg": a} for (_, m), a in zip(fits, angles)]}
    else:
        out["a4_plane_normal"] = {"status": "ABSTAIN", "reason": "no accepted A4 sheet annotation for this clip"
                                  if not a4_refs else "gravity not estimated"}
    if refs:
        ests = [known_object_scale(views, r) for r in refs]
        w = np.array([1 / max(e["sd"], 1e-12) ** 2 for e in ests])
        out["metric_scale"] = {"status": "calibrated",
                               "metres_per_model_unit": float(w @ [e["metres_per_model_unit"] for e in ests] / w.sum()),
                               "sd": float(1 / np.sqrt(w.sum())), "references": ests}
    else:
        out["metric_scale"] = {"status": "ABSTAIN", "metres_per_model_unit": None,
                               "reason": "no source-backed known-size object reference"}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", help="JSON list of {clip_id,npz,npz_label,gravity_applicable,refs,missing_reference}")
    ap.add_argument("out")
    a = ap.parse_args()
    res = {}
    for c in json.loads(Path(a.manifest).read_text()):
        r = analyse(c["npz"], c.get("gravity_applicable", True), c.get("refs", []), c.get("a4_refs", []))
        if r["metric_scale"]["status"] == "ABSTAIN":
            r["metric_scale"]["missing_reference"] = c["missing_reference"]
        r["npz"] = c["npz_label"]
        res[c["clip_id"]] = r
    Path(a.out).write_text(json.dumps(res, indent=2) + "\n")


if __name__ == "__main__":
    main()
