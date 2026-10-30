"""S07i: MEASURED g on OWN01 from the REAL SAM 3.1 track (evidence/S07/S07g/track-own01.json).
Every rule below (frames, split, error allowances) is fixed BEFORE the fit; nothing is tuned toward 9.79.
Run from repo root (worktree or canonical): python evidence/S07/S07i/measure_own01.py [--self-check]"""
import hashlib, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from Build.measurement.free_fall import evaluate_held_out  # noqa: E402
from Build.measurement.uncertainty import propagate_uncertainty  # noqa: E402

CANONICAL = Path("C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon")
TRACK = next(p for p in (ROOT / "evidence/S07/S07g/track-own01.json",
                         CANONICAL / "evidence/S07/S07g/track-own01.json") if p.exists())
EDGE_M, EDGE_U_M = 0.2028, 0.0005  # owner-declared cover edge; +/-0.5 mm ruler-reading ASSUMPTION
SCALE_FRAMES = range(40, 45)       # held pre-release frames, fixed in S07g run_sam_track.ps1 before tracking
BOX_EDGE_U_PX = 2.0                # SAM box edge allowance (blur/antialias), declared
DETECTION_STD_PX = 2.0             # per-frame centroid error under motion blur, declared (not residual-derived)
PTS_STD_S = 1e-4                   # raw-phone PTS jitter (S07g: dt 33.23-33.43 ms)
CLOCK_U = 1e-3                     # phone clock rate, NOT externally verified; 0.1% declared
START_PX = 8.0                     # release = first frame > held median + 8 px (S07g rule)
G_LOCAL = 9.79                     # owner value; comparison only


def window(frames):
    """Fixed rule: start at release (S07g threshold); end at the last frame of the CONTIGUOUS tracked run."""
    base = sorted(f["y_px"] for f in frames if f["frame_index"] in SCALE_FRAMES)[2]
    start = next(i for i, f in enumerate(frames) if f["y_px"] > base + START_PX)
    end = start
    while end + 1 < len(frames) and frames[end + 1]["frame_index"] == frames[end]["frame_index"] + 1:
        end += 1
    seg = frames[start:end + 1]
    return seg, seg[len(seg) * 2 // 3 - 1]["frame_index"]  # train = first floor(2n/3) frames


def record(track, point):
    rec, boxes = track["record"], {track["frame_map"][i][0]: b for i, _, b in track["stream"] if b}
    W, H = rec["width_px"], rec["height_px"]
    frames = [dict(f) for f in rec["frames"]]
    if point == "box_centre":  # normalized xywh -> centre px (sensitivity to the centroid choice)
        for f in frames:
            x, y, w, h = boxes[f["frame_index"]][0]
            f["x_px"], f["y_px"] = (x + w / 2) * W, (y + h / 2) * H
    widths = [boxes[i][0][2] * W for i in SCALE_FRAMES]
    mean = sum(widths) / len(widths)
    sd = math.sqrt(sum((w - mean) ** 2 for w in widths) / (len(widths) - 1))
    u_w = math.hypot(sd / math.sqrt(len(widths)), BOX_EDGE_U_PX)
    mpp = EDGE_M / mean
    seg, split = window(frames)
    data = {**{k: rec[k] for k in ("clip_id", "source_sha256", "licence", "provenance", "width_px", "height_px")},
            "approval": {"scope": "metric_measurement", "evidence": "evidence/S07/S07g/OWNER-APPROVAL.md"},
            "motion": "earth_free_fall",
            "continuous_segment_evidence": f"SAM 3.1 contiguous tracked frames {seg[0]['frame_index']}-{seg[-1]['frame_index']}",
            "scale": {"method": "independent_reference", "m_per_px": mpp,
                      "uncertainty_m_per_px": mpp * math.hypot(u_w / mean, EDGE_U_M / EDGE_M),
                      "plane_verified": True,
                      "evidence": "USER-DECLARED: owner book edge 0.2028 m / SAM box width f40-44; plane = release depth, NOT verified"},
            "timebase": {"capture_seconds_per_pts_second": 1.0, "uncertainty_factor": CLOCK_U, "verified": True,
                         "evidence": "phone PTS, NOT externally verified (declared)"},
            "last_training_frame": split, "frames": seg}
    return data, {"widths_px": widths, "mean_px": mean, "sd_px": sd, "u_width_px": u_w}


def assume(n):
    return {"independent_frame_errors": True, "calibration_independent_of_frames": True,
            "small_error_linearization": True, "remaining_systematics_negligible": True,
            "detection_std_px": [DETECTION_STD_PX] * n, "timestamp_std_pts_s": [PTS_STD_S] * n,
            "scale_clock_correlation": 0.0,
            "evidence": "declared S07i constants; systematics reported separately as the model component"}


def run():
    raw = TRACK.read_bytes()
    track = json.loads(raw)
    out = {"label": "MEASURED (owner clip OWN01, user-declared scale 0.2028 m, phone clock not externally verified)",
           "track": "evidence/S07/S07g/track-own01.json", "track_sha256": hashlib.sha256(raw).hexdigest(),
           "missing_frames": track["record"]["tracking"]["missing_frames"]}
    for point in ("mask_centroid", "box_centre"):
        data, scale = record(track, point)
        n = sum(f["frame_index"] <= data["last_training_frame"] for f in data["frames"])
        u = propagate_uncertainty(data, assume(n))
        held = evaluate_held_out(u.fit, data)
        out[point] = {"g": u.fit.g_m_s2, "u_fit": u.detection_standard_m_s2,
                      "u_timing": math.hypot(u.timestamp_standard_m_s2, u.clock_sensitivity * CLOCK_U),
                      "u_scale": abs(u.scale_sensitivity) * data["scale"]["uncertainty_m_per_px"],
                      "u_conditional_total": u.standard_uncertainty_m_s2, "scale": scale,
                      "m_per_px": data["scale"]["m_per_px"],
                      "fall_frames": [data["frames"][0]["frame_index"], data["frames"][-1]["frame_index"]],
                      "last_training_frame": data["last_training_frame"],
                      "fall_duration_s": data["frames"][-1]["pts_s"] - data["frames"][0]["pts_s"],
                      "train_rms_px": u.fit.training.rmse_m / u.fit.m_per_px,
                      "held_out": {"frames": held.frame_indices,
                                   "residuals_px": [r / u.fit.m_per_px for r in held.residuals_m],
                                   "rmse_px": held.rmse_m / u.fit.m_per_px}}
    c, b = out["mask_centroid"], out["box_centre"]
    model = abs(c["g"] - b["g"])
    total = math.hypot(c["u_conditional_total"], model)
    out["result"] = {"point": "mask_centroid (area-weighted; box centre follows extreme corners under rotation)",
                     "g": c["g"], "u_model_centroid_vs_box": model, "u_total": total,
                     "delta_vs_local": c["g"] - G_LOCAL, "z_vs_local": (c["g"] - G_LOCAL) / total,
                     "local_g": G_LOCAL, "s07g_diagnostic": [10.73, 0.41]}
    return out


def self_check():
    seg, split = window([{"frame_index": i, "y_px": 100.0 + (0 if i < 46 else 5 * (i - 45) ** 2)} for i in range(40, 55)]
                        + [{"frame_index": 60, "y_px": 999.0}])
    assert (seg[0]["frame_index"], seg[-1]["frame_index"], split) == (47, 54, 51), (seg[0], seg[-1], split)
    r = run()
    assert r["mask_centroid"]["fall_frames"][1] < 55 and 5 < r["result"]["g"] < 15
    print("self-check OK")


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        self_check()
    else:
        res = run()
        dest = Path(__file__).with_name("result-own01.json")
        dest.write_text(json.dumps(res, indent=1), encoding="utf-8")
        print(json.dumps(res["result"], indent=1))
