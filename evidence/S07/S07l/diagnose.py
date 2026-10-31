"""S07l: DIAGNOSIS of why held-out prediction fails on every owner clip (v1 = S07h, v2 = S07k).
Inputs: the existing real SAM 3.1 track JSONs (paths from S07k measure_v2.TRACKS) + S07h/S07k results.json ONLY.
No tracking, video, frames, model, Modal/GPU/Meta call. Pixel-space y(t) fits on the SAME windows and floor(2n/3)
split as the pipelines (Build.measurement.free_fall fits y(pts) only), so held-out pixel RMSE is reproduced exactly
and is independent of the metric scale. Thresholds/assumptions below were fixed before the real run; nothing is
chosen by closeness to 9.79 (g-shifts are reported only as consequences).
Run from repo root (worktree or canonical): python -B evidence/S07/S07l/diagnose.py [--self-check]"""
import json, sys
from pathlib import Path

import numpy as np
from scipy.stats import chi2

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "S07k"))
import measure_v2 as v2  # noqa: E402  (-> S07h measure_heldout -> S07i measure_own01 + Build.measurement)
h, m = v2.h, v2.m

HELD_PX, DETECT_PX = h.HELD_PASS_PX, m.DETECTION_STD_PX   # 6 px pass threshold, 2 px declared detection error
IMPACT_RATIO = v2.DECEL       # velocity step < 0.5 x previous step = impact/catch (same as v2 rule)
SHAPE_TOL = 0.05              # box w or h change > 5 % vs scale mean inside the window = rotation/perspective
OFFSET_TOL_PX = HELD_PX / 2   # centroid-minus-box-centre y drift > 3 px across the window = material shape bias
VFR_TOL_S = 1e-3              # PTS step range > 1 ms = variable frame rate
RS_READOUT_S = 0.020          # ASSUMPTION: phone rolling-shutter readout time; Realme C53 value unknown
RHO, CD = 1.2, 1.2            # ASSUMPTION: air density kg/m^3, flat-plate drag coefficient
MASS_KG = (0.2, 1.0)          # ASSUMPTION: book mass range (not measured)
AREA_M2 = (0.2028 * 0.02, 0.2028 * 0.30)  # ASSUMPTION: edge-on (2 cm) .. face-on (30 cm) x declared 0.2028 m edge
V3_ALPHA = 0.05               # v3 candidate (HYPOTHESIS): chi-square predictive held-out test at 5 %


def load(clip):
    track = json.loads(h.locate(v2.TRACKS[clip]).read_bytes())
    rec = track["record"]
    W, H = rec["width_px"], rec["height_px"]
    boxes = {track["frame_map"][i][0]: b[0] for i, _, b in track["stream"] if b}
    fr = {}
    for f in sorted(rec["frames"], key=lambda f: f["frame_index"]):
        bx, by, bw, bh = boxes.get(f["frame_index"], (np.nan,) * 4)
        fr[f["frame_index"]] = {"t": f["pts_s"], "x": f["x_px"], "y": f["y_px"], "yb": (by + bh / 2) * H,
                                "w": bw * W, "h": bh * H}
    return fr, W, H


def held(t, y, deg):
    """Fit first floor(2n/3) frames (pipeline split), return (coeffs, held RMSE, train residuals)."""
    n, tt = len(t) * 2 // 3, t - t[0]
    p = np.polyfit(tt[:n], y[:n], deg)
    r = y[n:] - np.polyval(p, tt[n:])
    return p, float(np.sqrt(np.mean(r ** 2))), y[:n] - np.polyval(p, tt[:n])


def leverage(t, deg=2):
    """Held-out prediction-variance factor x'(X'X)^-1 x per held frame (floor(2n/3) split)."""
    n, tt = len(t) * 2 // 3, t - t[0]
    X, Xh = np.vander(tt[:n], deg + 1), np.vander(tt[n:], deg + 1)
    return np.einsum("ij,jk,ik->i", Xh, np.linalg.inv(X.T @ X), Xh)


def expected_held(t, sigma, deg=2):
    """Expected held-out RMSE if the quadratic model were exact and errors iid N(0, sigma): noise + extrapolation."""
    return float(sigma * np.sqrt(np.mean(1 + leverage(t, deg))))


def rs_effect(t, y, pos, size, T):
    """Refit after sampling the fitted trajectory at t + T*pos/size (rolling shutter along that image axis)."""
    p, _, _ = held(t, y, 2)
    tt, ys = t - t[0], np.polyval(p, t - t[0])
    for _ in range(8):  # fixed point: object row depends on its own sampled position
        ys = np.polyval(p, tt + T * (ys if pos is None else pos) / size)
    q, rm, _ = held(t, ys, 2)
    return rm, float(q[0] / p[0])


def analyse(fr, W, H, f0, f1, scale, mpp):
    fis = [i for i in range(f0, f1 + 1) if i in fr]
    t, y, yb, x = (np.array([fr[i][k] for i in fis]) for k in ("t", "y", "yb", "x"))
    n = len(t) * 2 // 3
    p2, rm2, tr = held(t, y, 2)
    hr2 = y[n:] - np.polyval(p2, t[n:] - t[0])
    d = np.diff(y)
    ratios = d[1:] / d[:-1]
    post = (fr[f1 + 1]["y"] - fr[f1]["y"]) / (fr[f1]["y"] - fr[f1 - 1]["y"]) if f1 + 1 in fr and f1 - 1 in fr else None
    dd = np.diff(y, 2)  # px/frame^2, centred on fis[1:-1]
    w0 = np.mean([fr[i]["w"] for i in scale]) if scale else fr[f0]["w"]
    h0 = np.mean([fr[i]["h"] for i in scale]) if scale else fr[f0]["h"]
    wr, hr = np.array([fr[i]["w"] for i in fis]) / w0 - 1, np.array([fr[i]["h"] for i in fis]) / h0 - 1
    off = y - yb
    _, rmb, _ = held(t, yb, 2)
    p3, rm3, _ = held(t, y, 3)
    k = float(-3 * p3[0] / p3[1])  # linear drag: y''' = -k y''  =>  6 c3 = -k (2 c2)
    v = float(np.mean(np.polyval(np.polyder(p2), t - t[0]))) * mpp  # mean fall speed m/s
    allt = np.array([fr[i]["t"] for i in sorted(fr)])
    steps = np.diff(allt)[np.diff(sorted(fr)) == 1]
    stat = [fr[i]["y"] for i in scale]
    ts = [fr[i]["t"] for i in scale]
    static_sd = float(np.std(np.array(stat) - np.polyval(np.polyfit(ts, stat, 1), ts), ddof=2)) if len(stat) >= 3 else None
    train_sd = float(np.sqrt(np.sum(tr ** 2) / max(n - 3, 1)))
    sig = max(train_sd, DETECT_PX)
    x2 = float(np.sum(hr2 ** 2 / (sig ** 2 * (1 + leverage(t)))))
    speed = np.abs(np.gradient(y, t))
    dh = np.array([fr[i]["h"] for i in fis]) - h0
    with np.errstate(invalid="ignore"):  # constant synthetic heights -> r undefined
        blur_s, blur_r = float(np.polyfit(speed, dh, 1)[0]), float(np.corrcoef(speed, dh)[0, 1])
    rs_y = rs_effect(t, y, None, H, RS_READOUT_S)
    rs_x = rs_effect(t, y, x, W, RS_READOUT_S)
    wsc = [fr[i]["w"] for i in scale]
    return {
        "frames": [fis[0], fis[-1]], "n": len(fis), "n_train": n, "held_rmse_px": rm2,
        "a_impact": {"min_step_ratio": float(ratios.min()), "at_frame": fis[int(ratios.argmin()) + 2],
                     "post_window_step_ratio": post, "impact_in_window": bool(ratios.min() < IMPACT_RATIO),
                     "accel_px_per_frame2_train_vs_held": [float(dd[:n - 1].mean()), float(dd[n - 1:].mean())]},
        "b_shape": {"max_abs_width_change": float(np.abs(wr).max()), "max_abs_height_change": float(np.abs(hr).max()),
                    "held_width_change": float(np.abs(wr[n:]).max()), "held_height_change": float(np.abs(hr[n:]).max()),
                    "aspect_h_over_w_first_last": [float(fr[fis[0]]["h"] / fr[fis[0]]["w"]),
                                                   float(fr[fis[-1]]["h"] / fr[fis[-1]]["w"])],
                    "x_drift_px": float(x[-1] - x[0]),
                    "height_growth_vs_speed_slope_s": blur_s, "height_growth_vs_speed_r": blur_r,
                    "present": bool(max(np.abs(wr).max(), np.abs(hr).max()) > SHAPE_TOL)},
        "c_centroid": {"offset_range_px": float(off.max() - off.min()), "held_rmse_box_centre_px": rmb,
                       "material": bool(off.max() - off.min() > OFFSET_TOL_PX)},
        "d_drag": {"held_rmse_cubic_px": rm3, "cubic_better": bool(rm3 < rm2), "k_linear_drag_per_s": k,
                   "mean_speed_m_s": v, "required_drag_m_s2": k * v,
                   "plausible_quadratic_drag_m_s2": [RHO * CD * AREA_M2[0] * v * v / (2 * MASS_KG[1]),
                                                     RHO * CD * AREA_M2[1] * v * v / (2 * MASS_KG[0])]},
        "e_timing": {"pts_step_ms_min_max": [float(steps.min() * 1e3), float(steps.max() * 1e3)],
                     "vfr": bool(steps.max() - steps.min() > VFR_TOL_S),
                     "rs_readout_along_y": {"held_rmse_px": rs_y[0], "a_ratio": rs_y[1]},
                     "rs_readout_along_x": {"held_rmse_px": rs_x[0], "a_ratio": rs_x[1]}},
        "f_noise": {"static_sd_px": static_sd, "train_resid_sd_px": train_sd,
                    "expected_held_rmse_px_declared_2px": expected_held(t, DETECT_PX),
                    "expected_held_rmse_px_empirical": expected_held(t, train_sd),
                    "observed_over_expected_empirical": rm2 / expected_held(t, train_sd)},
        "v3_candidate": {"sigma_px": sig, "chi2": x2, "dof": len(t) - n, "p": float(chi2.sf(x2, len(t) - n)),
                         "pass": bool(chi2.sf(x2, len(t) - n) >= V3_ALPHA)},
        "g_scale": {"scale_width_mean_px": float(np.mean(wsc)) if wsc else None,
                    "scale_width_rel_sd": float(np.std(wsc, ddof=1) / np.mean(wsc)) if len(wsc) > 1 else None,
                    "mask_width": "not computable: tracks store mask centroid + SAM box only",
                    "held_out_px_depends_on_scale": False},
    }


def windows():
    v1 = json.loads(h.locate("evidence/S07/S07h/results.json").read_text(encoding="utf-8"))["rows"]
    v2r = json.loads(h.locate("evidence/S07/S07k/results.json").read_text(encoding="utf-8"))["rows"]
    out = []
    for tag, rows in (("v1", v1), ("v2", v2r)):
        for r in rows:
            if "fall_frames" not in r:
                continue
            sf = r.get("rules", {}).get("scale_frames")
            out.append((tag, r, list(range(sf[0], sf[1] + 1)) if sf else None))
    return out


def summarise(res):
    v1 = [r for r in res if r["analysis"] == "v1"]
    v2s = [r for r in res if r["analysis"] == "v2"]
    med = lambda xs: float(np.median([x for x in xs if x is not None]))  # noqa: E731
    return {
        "a_impact": {"v1_windows_with_impact": sum(r["a_impact"]["impact_in_window"] for r in v1), "v1_windows": len(v1),
                     "v2_windows_with_impact": sum(r["a_impact"]["impact_in_window"] for r in v2s), "v2_windows": len(v2s),
                     "v2_windows_held_accel_below_train": sum(
                         r["a_impact"]["accel_px_per_frame2_train_vs_held"][1] < r["a_impact"]["accel_px_per_frame2_train_vs_held"][0]
                         for r in v2s),
                     "v1_median_held_rmse_px": med([r["held_rmse_px"] for r in v1]),
                     "v2_median_held_rmse_px": med([r["held_rmse_px"] for r in v2s])},
        "b_shape": {"v2_windows_shape_change_gt_5pct": sum(r["b_shape"]["present"] for r in v2s),
                    "v2_median_max_width_change": med([r["b_shape"]["max_abs_width_change"] for r in v2s]),
                    "v2_median_max_height_change": med([r["b_shape"]["max_abs_height_change"] for r in v2s]),
                    "v2_median_height_growth_vs_speed_r": med([r["b_shape"]["height_growth_vs_speed_r"] for r in v2s]),
                    "v2_height_growth_slope_ms_range": [1e3 * min(r["b_shape"]["height_growth_vs_speed_slope_s"] for r in v2s),
                                                        1e3 * max(r["b_shape"]["height_growth_vs_speed_slope_s"] for r in v2s)]},
        "c_centroid": {"v2_windows_offset_drift_gt_3px": sum(r["c_centroid"]["material"] for r in v2s),
                       "v2_median_offset_range_px": med([r["c_centroid"]["offset_range_px"] for r in v2s]),
                       "v2_box_centre_held_pass": sum(r["c_centroid"]["held_rmse_box_centre_px"] <= HELD_PX for r in v2s)},
        "d_drag": {"v2_cubic_better": sum(r["d_drag"]["cubic_better"] for r in v2s),
                   "v2_cubic_held_pass": sum(r["d_drag"]["held_rmse_cubic_px"] <= HELD_PX for r in v2s),
                   "v2_median_k_per_s": med([r["d_drag"]["k_linear_drag_per_s"] for r in v2s]),
                   "v2_required_drag_in_plausible_range": sum(
                       r["d_drag"]["plausible_quadratic_drag_m_s2"][0] <= r["d_drag"]["required_drag_m_s2"]
                       <= r["d_drag"]["plausible_quadratic_drag_m_s2"][1] for r in v2s)},
        "e_timing": {"clips_vfr": sum(r["e_timing"]["vfr"] for r in v2s),
                     "max_rs_y_held_rmse_px": max(r["e_timing"]["rs_readout_along_y"]["held_rmse_px"] for r in v2s),
                     "max_rs_x_held_rmse_px": max(r["e_timing"]["rs_readout_along_x"]["held_rmse_px"] for r in v2s),
                     "rs_y_a_ratio_range": [min(r["e_timing"]["rs_readout_along_y"]["a_ratio"] for r in v2s),
                                            max(r["e_timing"]["rs_readout_along_y"]["a_ratio"] for r in v2s)]},
        "f_noise": {"v2_median_static_sd_px": med([r["f_noise"]["static_sd_px"] for r in v2s]),
                    "v2_median_train_resid_sd_px": med([r["f_noise"]["train_resid_sd_px"] for r in v2s]),
                    "v2_median_expected_held_declared_px": med([r["f_noise"]["expected_held_rmse_px_declared_2px"] for r in v2s]),
                    "v2_expected_declared_gt_threshold": sum(r["f_noise"]["expected_held_rmse_px_declared_2px"] > HELD_PX for r in v2s),
                    "v2_median_expected_held_empirical_px": med([r["f_noise"]["expected_held_rmse_px_empirical"] for r in v2s]),
                    "v2_expected_empirical_ge_threshold": sum(r["f_noise"]["expected_held_rmse_px_empirical"] >= HELD_PX for r in v2s),
                    "v2_median_observed_over_expected": med([r["f_noise"]["observed_over_expected_empirical"] for r in v2s])},
        "v3_candidate_hypothesis": {"v1_pass": sum(r["v3_candidate"]["pass"] for r in v1),
                                    "v2_pass": sum(r["v3_candidate"]["pass"] for r in v2s),
                                    "v2_p": {r["clip"]: r["v3_candidate"]["p"] for r in v2s}},
        "g_scale": {"v2_median_scale_width_rel_sd": med([r["g_scale"]["scale_width_rel_sd"] for r in v2s]),
                    "v2_median_g_shift_m_s2_from_width_sd": med([r["g"] * r["g_scale"]["scale_width_rel_sd"] for r in v2s
                                                               if r["g_scale"]["scale_width_rel_sd"] is not None])},
    }


def run():
    res = []
    for tag, row, scale in windows():
        fr, W, H = load(row["clip"])
        if scale is None:  # v1: up to 5 tracked frames ending 2 before release (same geometry as the v2 rule)
            scale = [i for i in range(row["fall_frames"][0] - 6, row["fall_frames"][0] - 1) if i in fr]
        a = analyse(fr, W, H, *row["fall_frames"], scale, row["m_per_px"])
        assert abs(a["held_rmse_px"] - row["held_rmse_px"]) < 0.05, (tag, row["clip"], a["held_rmse_px"], row["held_rmse_px"])
        res.append({"clip": row["clip"], "analysis": tag, "g": row["g"], **a})
    return {"label": "DIAGNOSIS — derived from MEASURED owner-clip SAM 3.1 tracks; ASSUMPTIONS labelled; 9.79 never used",
            "assumptions": {"rs_readout_s": RS_READOUT_S, "rho": RHO, "cd": CD, "mass_kg": MASS_KG, "area_m2": AREA_M2},
            "thresholds": {"held_pass_px": HELD_PX, "impact_ratio": IMPACT_RATIO, "shape_tol": SHAPE_TOL,
                           "offset_tol_px": OFFSET_TOL_PX, "vfr_tol_s": VFR_TOL_S},
            "summary": summarise(res), "windows": res}


def self_check():  # synthetic only; never touches owner data
    fps, a = 30.0, 14000.0  # px/s^2
    fr = {}
    for i in range(30, 60):
        t = i / fps
        fall = max(t - 40 / fps, 0)
        y = 300 + 0.5 * a * fall ** 2 if i <= 52 else fr[52]["y"] + 2 * (i - 52)  # impact after f52
        fr[i] = {"t": t, "x": 500.0, "y": y, "yb": y + 1.0, "w": 280.0, "h": 120.0}
    r = analyse(fr, 1080, 1920, 41, 52, list(range(35, 40)), 0.0007)
    assert r["held_rmse_px"] < 1e-6 and not r["a_impact"]["impact_in_window"], r["a_impact"]
    assert abs(r["d_drag"]["k_linear_drag_per_s"]) < 1e-3 and r["c_centroid"]["offset_range_px"] < 1e-9
    assert r["e_timing"]["rs_readout_along_y"]["held_rmse_px"] > 0.1 and r["e_timing"]["rs_readout_along_x"]["held_rmse_px"] < 1e-6
    assert not r["e_timing"]["vfr"] and r["f_noise"]["expected_held_rmse_px_declared_2px"] > DETECT_PX
    r = analyse(fr, 1080, 1920, 41, 55, list(range(35, 40)), 0.0007)
    assert r["a_impact"]["impact_in_window"] and r["held_rmse_px"] > HELD_PX
    assert expected_held(np.arange(9) / fps, 1.0) > 1.0
    print("S07l self-check OK (synthetic)")


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        self_check()
    else:
        out = run()
        HERE.joinpath("results.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
        print(json.dumps(out["summary"], indent=1))

