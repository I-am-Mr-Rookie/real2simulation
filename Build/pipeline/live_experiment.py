"""N07 Mode B live pipeline: a user's own experiment clip -> hosted SAM 3.1 track -> scale -> fitter -> result.

Numbers come only from ffprobe (frame times), the SAM response (box centres in pixels) and Build/fitter. Scale is
the user's known size of the tracked object (its longest visible side, e.g. a ball diameter) over the median
tracked box size; without one the result stays in pixels, labelled scale unverified (no metric number invented).
Times are the container's playback timestamps; slow motion or frame-rate conversion changes every time-based value.
"""
import json
import math
import shutil
import statistics
import subprocess

from Build.api.workspace.analysis import SCALE_LABEL_USER, user_scale
from Build.fitter import FitError, jacobian_covariance, select_model
from Build.measurement import hosted_sam

TRACK_LABEL = "MEASURED: hosted SAM 3.1 box centres in image pixels"
NO_SCALE = "scale unverified: no known size given, so results are in pixels; no metric value"
CLOCK = "playback timestamps; capture clock unverified (slow motion would change every time-based value)"
MIN_POINTS = 5


def probe(path):
    """(width, height, [pts_s per decoded frame]) of the first video stream via ffprobe."""
    exe = shutil.which("ffprobe")
    if not exe:
        raise ValueError("ffprobe is not installed, so frame times are unknown")
    out = subprocess.run([exe, "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:frame=best_effort_timestamp_time", "-of", "json", str(path)],
                         capture_output=True, text=True, timeout=300)
    j = json.loads(out.stdout or "{}")
    try:
        s = j["streams"][0]
        times = [float(f["best_effort_timestamp_time"]) for f in j["frames"]]
    except (KeyError, IndexError, ValueError, TypeError):
        raise ValueError("file is not a readable video") from None
    if not times:
        raise ValueError("video has no decodable frames")
    return int(s["width"]), int(s["height"]), times


def hosted_track(path, target_text=None, point=None, size=None, frames=hosted_sam.MAX_FRAMES):
    """Hosted SAM 3.1: upload + one paid, cap-reserved track call. point = (x, y) source pixels on frame 0."""
    file_id = hosted_sam.upload(path)
    if point is not None:
        # shortcut: probe size is the coded size; a rotated phone clip may need swapped w/h if SAM rejects it
        prompt = hosted_sam.point_prompt(1, [(point[0], point[1], True)], size[0], size[1], 0)
    else:
        prompt = target_text
    return hosted_sam.result(hosted_sam.track(file_id, prompt, max_frames=frames), 1 if point is not None else None)


def run(path, target_text=None, point=None, known_size=None, tracker=hosted_track, backup=None):
    """Full live run; tracker/backup are injectable (tests use recorded responses, no network)."""
    w, h, times = probe(path)
    try:
        tr, source = tracker(path, target_text, point, (w, h), len(times)), "hosted SAM 3.1 (Meta Model API)"
    except Exception:
        if backup is None:
            raise
        tr, source = backup(path, target_text, point, (w, h), len(times)), "Modal SAM 3.1 backup"
    track = {**track_record(tr, times), "source": source}
    return {**analyse(track, known_size), "track": track,
            "cost_usd": round(tr.get("cost_usd", 0.0), 6), "video_frames_processed": tr.get("video_frames_processed")}


def track_record(tr, times):
    """hosted_sam.result -> stored track: frames [[k, t_s, x_px, y_px, box_w, box_h]] (image y down)."""
    if tr["frame_count"] != len(times):
        raise ValueError(f"tracker returned {tr['frame_count']} frames, the video has {len(times)}")
    return {"label": TRACK_LABEL, "object_id": tr["object_id"], "width": tr["width"], "height": tr["height"],
            "frames": [[k, times[k], x, y, b[2] - b[0], b[3] - b[1]] for k, x, y, b in tr["points"]],
            "missing": tr["missing"], "point_method": "box_centre"}


def moving_segment(frames):
    """The run of moving frames around the fastest step (moving = centre step above 10% of the largest step).

    A single still step between moving ones is a repeated frame (e.g. 25p content in a 30p file), not a stop:
    it is bridged and the repeated frame is dropped so it cannot fake a pause in the fit.
    """
    if len(frames) < 2:
        return frames
    steps = [math.dist(a[2:4], b[2:4]) for a, b in zip(frames, frames[1:])]
    thr = max(1.5, 0.1 * max(steps))
    moving = [s > thr for s in steps]
    bridged = [m or (0 < i < len(steps) - 1 and moving[i - 1] and moving[i + 1]) for i, m in enumerate(moving)]
    a = b = steps.index(max(steps))
    while a > 0 and bridged[a - 1]:
        a -= 1
    while b + 1 < len(steps) and bridged[b + 1]:
        b += 1
    return [frames[a]] + [frames[i + 1] for i in range(a, b + 1) if moving[i]]


def _reversals(values, jitter):
    signs = [d > 0 for d in (b - a for a, b in zip(values, values[1:])) if abs(d) > jitter]
    return sum(a != b for a, b in zip(signs, signs[1:]))


def _axis(t, v):
    """AIC choice of constant velocity vs constant acceleration (Build/fitter) for one axis, in pixels."""
    sel = select_model(t, v, (1, 2))
    fit = next(c for c in sel.candidates if c.degree == sel.selected_degree)
    out = {"model": "constant_acceleration" if fit.degree == 2 else "constant_velocity", "aic": list(sel.aic),
           "rmse_px": fit.rmse, "n": fit.n}
    if fit.degree == 2:
        cov = jacobian_covariance(fit, parameter_index=2)
        out["accel_px_s2"] = 2 * fit.coefficients[2]
        out["accel_sigma_px_s2"] = 2 * cov.standard_error if cov.valid else None
    return out


def _quantity(name, a_px, s_px, mpp, scale_rel):
    """1 sigma = fitter standard error (iid residuals) combined with the scale spread; clock held fixed."""
    if mpp is None:
        return {"name": name, "value": a_px, "unit": "px/s^2", "uncertainty": s_px, "label": NO_SCALE}
    v = a_px * mpp
    u = abs(v) * math.hypot(s_px / a_px, scale_rel) if s_px is not None and a_px else None
    return {"name": name, "value": v, "unit": "m/s^2", "uncertainty": u, "label": "MEASURED",
            "uncertainty_note": "1 sigma: fitter residuals + tracked box size spread; known-size error not included"}


def analyse(track, known_size=None, segment=None):
    """Segment, scale and fit a stored track; every number is ffprobe, SAM or fitter output.

    segment = (first_frame, last_frame) overrides the automatic moving segment (re-fit without a new SAM call).
    """
    frames = track["frames"]
    if len(frames) < MIN_POINTS:
        return {"status": "abstain", "reason": f"only {len(frames)} tracked frames; need {MIN_POINTS}"}
    seg = [f for f in frames if segment[0] <= f[0] <= segment[1]] if segment else moving_segment(frames)
    if len(seg) < MIN_POINTS:
        return {"status": "abstain", "reason": f"moving segment has {len(seg)} frames; need {MIN_POINTS}"}
    t0, x0, y0 = seg[0][1], seg[0][2], seg[0][3]
    t = [f[1] - t0 for f in seg]
    xs, ys = [f[2] - x0 for f in seg], [y0 - f[3] for f in seg]  # y up from here on
    scale = user_scale({"text": known_size}) if known_size else None
    if scale and scale["status"] == "declared":
        sizes = [max(f[4], f[5]) for f in seg]
        ref = statistics.median(sizes)
        mpp, scale_rel = scale["length_m"] / ref, statistics.pstdev(sizes) / ref
        scale = {**scale, "reference_px": ref, "metres_per_px": mpp, "relative_sigma": scale_rel,
                 "method": "known size / median longest side of the tracked box (motion blur inflates boxes)"}
        unit, label = "m", f"MEASURED, scale {SCALE_LABEL_USER}"
    else:
        mpp, scale_rel, unit, label = None, 0.0, "px", NO_SCALE
        scale = scale or {"status": "abstain", "label": NO_SCALE}
    result = {"status": "ok", "label": label, "clock": CLOCK, "units": unit, "scale": scale, "fit": None,
              "segment": {"first_frame": seg[0][0], "last_frame": seg[-1][0], "frames": len(seg), "duration_s": t[-1]}}
    full_x = [f[2] for f in frames]
    if _reversals(full_x, max(2.0, 0.05 * (max(full_x) - min(full_x)))) >= 3:
        result.update(motion="periodic (pendulum-like)",
                      note="The fitter has no pendulum model yet, so no period or g is reported for this clip.")
    else:
        try:
            fx, fy = _axis(t, xs), _axis(t, ys)
        except FitError as exc:
            return {**result, "status": "abstain", "reason": f"fitter rejected the track: {exc}"}
        result["fit"] = {"x": fx, "y": fy, "model_selection": "AIC over degree 1 and 2 per axis (Build/fitter)"}
        ax = fx.get("accel_px_s2", 0.0)
        if fy["model"] == "constant_acceleration" and abs(ax) < 0.1 * abs(fy["accel_px_s2"]):  # drag/perspective
            result["motion"] = "free_fall" if max(xs) - min(xs) < 0.1 * (max(ys) - min(ys)) else "projectile"
            result["quantity"] = _quantity("vertical acceleration (g if only gravity acts)", -fy["accel_px_s2"],
                                           fy["accel_sigma_px_s2"], mpp, scale_rel)
        elif fy["model"] == "constant_acceleration":
            result["motion"] = "incline_or_curved"
            a = math.hypot(fx["accel_px_s2"], fy["accel_px_s2"])
            s = (math.hypot(fx["accel_px_s2"] * (fx["accel_sigma_px_s2"] or 0), fy["accel_px_s2"]
                            * (fy["accel_sigma_px_s2"] or 0)) / a) if a else None
            result["quantity"] = _quantity("acceleration along the path (g sin(angle) minus friction)", a, s, mpp,
                                           scale_rel)
        else:
            result["motion"] = "constant_velocity_or_unclear"
            result["note"] = "No constant vertical acceleration was found, so no g is reported."
    k = mpp or 1.0
    result["trajectory"] = {"axes": "x right, y up, origin at the first segment point", "unit": unit,
                            "t_s": t, "x": [v * k for v in xs], "y": [v * k for v in ys], "frame": [f[0] for f in seg]}
    return result

