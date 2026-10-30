"""S07g DIAGNOSTIC ONLY (not the pipeline result): colour-threshold track of the yellow book on OWN01.
SAM 3.1/Modal was refused by the S20 GPU admission guardrail (no operator receipt.json); see REPORT.
Rules below were fixed before any fit was computed; nothing is tuned toward 9.79.
Run from repo root: python evidence/S07/S07g/diagnostic_colour.py"""
import json, subprocess
from pathlib import Path
import numpy as np

CLIP = Path("C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/"
            "Videos for Meta AI Hackathon/01_demo_hero__035735.mp4")
W, H, FIRST, LAST = 1080, 1920, 36, 64
EDGE_M = 0.2028  # owner-declared book cover horizontal edge


def frames():
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(CLIP), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def pts():
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "frame=pts_time", "-of", "csv=p=0", str(CLIP)], text=True)
    return np.array([float(x) for x in out.replace(",", " ").split()])


def yellow(rgb):
    r, g, b = (rgb[..., i].astype(int) for i in range(3))
    return (r > 140) & (g > 130) & (b < 0.6 * g) & (abs(r - g) < 70)


def measure(rgb):
    m = yellow(rgb)
    ys, xs = np.nonzero(m)
    if len(ys) < 500:
        return None
    lo, hi = np.percentile(xs, [2, 98])
    return {"cx": float(xs.mean()), "cy": float(ys.mean()), "n": int(len(ys)), "width_px": float(hi - lo)}


def fit(t, y):
    """Quadratic y = a + b t + c t^2 (pixels, seconds); g_px = 2c; covariance from residuals."""
    A = np.vstack([np.ones_like(t), t, t * t]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    res = y - A @ coef
    dof = max(len(t) - 3, 1)
    cov = np.linalg.inv(A.T @ A) * float(res @ res) / dof
    return coef, res, cov


def main():
    video, times = frames(), pts()
    obs = {i: measure(video[i]) for i in range(FIRST, LAST + 1)}
    held = [o for i, o in obs.items() if i <= 44 and o]  # pre-release frames (contact sheet: release ~f48)
    cy0 = np.median([o["cy"] for o in held])
    # Fixed rules: fall = first frame whose centroid is >8 px below held median, through the frame
    # before the centroid stops increasing (landing). Training = first 2/3 of fall frames, held-out = rest.
    fall = [i for i, o in obs.items() if o and o["cy"] > cy0 + 8]
    start, end = fall[0], fall[0]
    while end + 1 in obs and obs[end + 1] and obs[end + 1]["cy"] > obs[end]["cy"] + 1:
        end += 1
    idx = list(range(start, end + 1))
    k = max(3, (2 * len(idx)) // 3)
    train, test = idx[:k], idx[k:]
    widths = np.array([o["width_px"] for o in held])
    px_per_m = widths.mean() / EDGE_M
    t = times[idx] - times[start]
    y = np.array([obs[i]["cy"] for i in idx])
    coef, res, cov = fit(t[:k], y[:k])
    g = 2 * coef[2] / px_per_m
    u_fit = 2 * np.sqrt(cov[2, 2]) / px_per_m
    u_scale = g * (widths.std(ddof=1) / np.sqrt(len(widths)) + 3.0) / widths.mean()  # +3 px edge/blur allowance
    u_time = g * 2 * (1e-3 / max(t[k - 1], 1e-9))  # assumed 1 ms PTS jitter over training span
    pred = np.vstack([np.ones(len(test)), t[k:], t[k:] ** 2]).T @ coef if test else np.array([])
    out = {"label": "DIAGNOSTIC (colour threshold; NOT SAM 3.1 pipeline; NOT MEASURED product evidence)",
           "clip": "OWN01", "frames_fall": [start, end], "train": train, "held_out": test,
           "held_px_width_mean": float(widths.mean()), "held_px_width_sd": float(widths.std(ddof=1)),
           "px_per_m": float(px_per_m), "g_mps2": float(g),
           "u_components_mps2": {"fit": float(u_fit), "scale": float(u_scale), "timing": float(u_time)},
           "u_combined_mps2": float(np.sqrt(u_fit ** 2 + u_scale ** 2 + u_time ** 2)),
           "train_rms_px": float(np.sqrt(np.mean(res ** 2))),
           "held_out_residual_px": [float(v) for v in (y[k:] - pred)],
           "reference_local_g": 9.79,
           "per_frame": {i: o for i, o in obs.items()}}
    Path(__file__).with_name("diagnostic-own01.json").write_text(json.dumps(out, indent=1), "utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "per_frame"}, indent=1))


def self_check():
    t = np.arange(10) / 30.0
    coef, res, _ = fit(t, 5 + 2 * t + 0.5 * 9000.0 * t * t)
    assert abs(2 * coef[2] - 9000.0) < 1e-6 and float(abs(res).max()) < 1e-6
    assert yellow(np.array([[[220, 210, 60]], [[240, 240, 240]]], np.uint8)).ravel().tolist() == [True, False]
    print("self-check ok")


if __name__ == "__main__":
    import sys
    self_check() if "--self-check" in sys.argv else main()

