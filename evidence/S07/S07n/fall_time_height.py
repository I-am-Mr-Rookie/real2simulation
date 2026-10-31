"""S07n: SYSTEM-DERIVED fall time t, drop height h and g_ht = 2h/t^2 from EXISTING owner-clip SAM 3.1 tracks.
No tracking, video, GPU, Modal or Meta call. Rules fixed before the run (see Run-System/Runs/S07n-orch186/PLAN.md):
  release  = last static frame before the S07k v2 sustained-move rule (two consecutive steps > 4 px); +/-1 frame
  impact   = last frame before the first velocity collapse (step < 0.5 x previous step, S07k DECEL); +/-1 frame
  t        = (impact - release)/30 s; each endpoint uniform +/-1 frame (covers quantisation + ambiguity)
  h        = (floor y - static y) px x m/px; floor y = max(y) of the two frames around the collapse; static y = median
             of the scale frames; m/px = 0.2028 m / mean SAM box width over <=5 static frames ending at release
  u_px     = hypot(2 px detection x sqrt2, change in centroid-minus-box-centre y between release and floor)
Run from repo root: python -B evidence/S07/S07n/fall_time_height.py [--self-check]"""
import hashlib, json, math, statistics, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "S07k"))
import measure_v2 as v2  # noqa: E402  (-> S07h measure_heldout -> S07i measure_own01: constants + locate)

m, h_ = v2.h.m, v2.h
FPS = 30.0
U_END_S = (1 / FPS) / math.sqrt(3)  # uniform +/-1 frame per endpoint
G_LOCAL = m.G_LOCAL                # comparison only


class Abstain(Exception):
    pass


def derive(frames, boxes, H):
    """frames: sorted dicts frame_index/pts_s/y_px; boxes: frame_index -> normalized xywh. Returns measurement dict."""
    fi, y = [f["frame_index"] for f in frames], [f["y_px"] for f in frames]

    def d(k):
        return y[k] - y[k - 1] if k > 0 and fi[k] == fi[k - 1] + 1 else None

    R = next((k for k in range(1, len(y) - 1) if (d(k) or 0) > v2.MOVE_PX and (d(k + 1) or 0) > v2.MOVE_PX), None)
    if R is None:
        raise Abstain("release not in track: no sustained centroid-y motion")
    rel = R - 1
    sc = [k for k in range(max(0, rel - v2.SCALE_N + 1), rel + 1) if fi[k] in boxes and fi[rel] - fi[k] == rel - k]
    if sc:  # post-first-run fix: OWN01 f46 SAM box includes the hand (421 vs 291 px); drop width outliers (v2 WIDTH_TOL)
        med = statistics.median(boxes[fi[k]][2] for k in sc)
        sc = [k for k in sc if abs(boxes[fi[k]][2] - med) <= v2.WIDTH_TOL * med]
    if len(sc) < v2.SCALE_MIN:
        raise Abstain(f"release not in track: fewer than {v2.SCALE_MIN} static tracked frames before motion at f{fi[R]}")
    ys = [y[k] for k in sc]
    if max(ys) - min(ys) > v2.STATIC_PX:
        raise Abstain(f"release not in track: pre-motion frames f{fi[sc[0]]}-f{fi[sc[-1]]} not static (y range {max(ys) - min(ys):.1f} px)")
    K = next((k for k in range(R + 1, len(y)) if d(k) is not None and d(k - 1) is not None and d(k) < v2.DECEL * d(k - 1)), None)
    if K is None:
        last = len(y) - 1
        mpp = m.EDGE_M / (sum(boxes[fi[k]][2] for k in sc) / len(sc))  # normalized width; x frame width below
        raise Abstain(f"impact not in track: track ends f{fi[last]} still falling",
                      {"release_frame": fi[rel], "last_tracked_frame": fi[last], "lower_bound_t_s": (fi[last] - fi[rel]) / FPS,
                       "lower_bound_h_px": y[last] - statistics.median(ys), "m_per_px_times_width": mpp})
    imp = K - 1
    floor_k = max((imp, K), key=lambda k: y[k])
    W = [boxes[fi[k]][2] for k in sc]
    off = lambda k: y[k] - (boxes[fi[k]][1] + boxes[fi[k]][3] / 2) * H if fi[k] in boxes else None
    return {"release_frame": fi[rel], "impact_frame": fi[imp], "collapse_frame": fi[K], "floor_frame": fi[floor_k],
            "scale_frames": [fi[sc[0]], fi[sc[-1]]], "y_static_px": statistics.median(ys), "y_floor_px": y[floor_k],
            "box_width_norm": W, "offset_static_px": off(rel), "offset_floor_px": off(floor_k),
            "pts_span_s": frames[imp]["pts_s"] - frames[rel]["pts_s"]}


def quantities(d, Wpx):
    n = d["impact_frame"] - d["release_frame"]
    t = n / FPS
    u_t = math.hypot(math.sqrt(2) * U_END_S, t * m.CLOCK_U)
    widths = [w * Wpx for w in d["box_width_norm"]]
    mean = sum(widths) / len(widths)
    sd = statistics.stdev(widths)
    u_w = math.hypot(sd / math.sqrt(len(widths)), m.BOX_EDGE_U_PX)
    mpp = m.EDGE_M / mean
    u_mpp = mpp * math.hypot(u_w / mean, m.EDGE_U_M / m.EDGE_M)
    h_px = d["y_floor_px"] - d["y_static_px"]
    drift = abs(d["offset_floor_px"] - d["offset_static_px"]) if None not in (d["offset_floor_px"], d["offset_static_px"]) else 0.0
    u_px = math.hypot(m.DETECTION_STD_PX * math.sqrt(2), drift)
    h = h_px * mpp
    u_h = h * math.hypot(u_px / h_px, u_mpp / mpp)
    g = 2 * h / t ** 2
    u_g = g * math.hypot(u_h / h, 2 * u_t / t)
    return {"n_frames": n, "t_s": t, "u_t_s": u_t, "pts_span_s": d["pts_span_s"], "h_px": h_px, "u_px": u_px,
            "centroid_box_drift_px": drift, "m_per_px": mpp, "u_m_per_px": u_mpp, "h_m": h, "u_h_m": u_h,
            "g_ht": g, "u_g_ht": u_g, "rel_u_t": u_t / t, "rel_u_h": u_h / h, "rel_u_g": u_g / g}


def checks(q):
    assert abs(q["t_s"] - q["n_frames"] / FPS) < 1e-12
    assert abs(q["pts_span_s"] - q["t_s"]) <= 0.01 * q["t_s"] + 1e-3, "PTS span disagrees with n/30"
    assert abs(q["h_m"] - 0.5 * q["g_ht"] * q["t_s"] ** 2) < 1e-9
    assert min(q["u_t_s"], q["u_h_m"], q["u_g_ht"], q["u_px"], q["u_m_per_px"]) > 0


def fits():
    out = {}
    for tag, p in (("v1_S07h", "evidence/S07/S07h/results.json"), ("v2_S07k", "evidence/S07/S07k/results.json")):
        for r in json.loads(h_.locate(p).read_text(encoding="utf-8"))["rows"]:
            if "g" in r:
                out.setdefault(r["clip"], {})[tag] = {"g": r["g"], "u": r["u"], "fall_frames": r.get("fall_frames")}
    return out


def run():
    stored = fits()
    rows = []
    for clip, p in v2.TRACKS.items():
        raw = h_.locate(p).read_bytes()
        tr = json.loads(raw)
        rec = tr["record"]
        frames = sorted(rec["frames"], key=lambda f: f["frame_index"])
        boxes = {tr["frame_map"][i][0]: b[0] for i, _, b in tr["stream"] if b}
        base = {"clip": clip, "track": p, "track_sha256": hashlib.sha256(raw).hexdigest(), "fit": stored.get(clip, {})}
        try:
            d = derive(frames, boxes, rec["height_px"])
        except Abstain as e:
            row = {**base, "abstain": e.args[0]}
            if len(e.args) > 1:
                lb = e.args[1]
                lb["lower_bound_h_m"] = lb["lower_bound_h_px"] * lb.pop("m_per_px_times_width") / rec["width_px"]
                row["lower_bound"] = lb
            rows.append(row)
            continue
        q = quantities(d, rec["width_px"])
        checks(q)
        for f in base["fit"].values():
            f["z_g_ht_vs_fit"] = (q["g_ht"] - f["g"]) / math.hypot(q["u_g_ht"], f["u"])
        q["z_vs_local"] = (q["g_ht"] - G_LOCAL) / q["u_g_ht"]
        rows.append({**base, **{k: v for k, v in d.items() if k != "box_width_norm"}, **q,
                     "label": "MEASURED (conditional: user-declared scale 0.2028 m, phone clock unverified, rolling shutter assumed)"})
    return {"label": "MEASURED, SYSTEM-DERIVED fall time / drop height (conditional: user-declared scale, phone clock unverified, rolling shutter assumed)",
            "rules": "Run-System/Runs/S07n-orch186/PLAN.md", "fps": FPS, "local_g_comparison_only": G_LOCAL, "rows": rows}


def fmt(x, u, p=3):
    return f"{x:.{p}f} ± {u:.{p}f}"


def table(out):
    L = ["| clip | release f | impact f | t (s) | h (m) | g_ht = 2h/t² (m/s²) | rel u t/h/g | fit v1 g ± u | fit v2 g ± u | z(g_ht−v1) | z(g_ht−9.79) |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["rows"]:
        f1, f2 = r["fit"].get("v1_S07h"), r["fit"].get("v2_S07k")
        fs = [fmt(f["g"], f["u"], 2) if f else "—" for f in (f1, f2)]
        if "abstain" in r:
            lb = r.get("lower_bound")
            note = (f" (release f{lb['release_frame']}; LOWER BOUNDS only: t ≥ {lb['lower_bound_t_s']:.3f} s,"
                    f" h ≥ {lb['lower_bound_h_px']:.0f} px ≈ {lb['lower_bound_h_m']:.3f} m)") if lb else ""
            L.append(f"| {r['clip']} | ABSTAIN: {r['abstain']}{note} | | | | | | {fs[0]} | {fs[1]} | | |")
            continue
        z = f"{f1['z_g_ht_vs_fit']:+.2f}" if f1 else "—"
        L.append(f"| {r['clip']} | {r['release_frame']} | {r['impact_frame']} | {fmt(r['t_s'], r['u_t_s'])} | "
                 f"{fmt(r['h_m'], r['u_h_m'])} | {fmt(r['g_ht'], r['u_g_ht'], 2)} | "
                 f"{r['rel_u_t']:.0%}/{r['rel_u_h']:.0%}/{r['rel_u_g']:.0%} | {fs[0]} | {fs[1]} | {z} | {r['z_vs_local']:+.2f} |")
    return "\n".join(L)


def self_check():  # synthetic only; never touches owner data
    g, mpp_true, H = 9.8, 0.2028 / 200, 1920
    frames, boxes = [], {}
    for i in range(30):
        tt = max(0.0, (i - 10) / FPS)
        yy = min(300 + 0.5 * g * tt ** 2 / mpp_true, 1500)
        frames.append({"frame_index": i, "pts_s": i / FPS, "y_px": yy})
        boxes[i] = (0.3, (yy - 50) / H, 200 / 1080, 100 / H)
    d = derive(frames, boxes, H)
    assert d["release_frame"] == 10, d
    q = quantities(d, 1080)
    checks(q)
    assert abs(q["g_ht"] - g) < 3 * q["u_g_ht"], q
    try:
        derive(frames[:20], boxes, H)
        raise AssertionError("expected impact abstain")
    except Abstain as e:
        assert "impact not in track" in e.args[0]
    print("self-check OK", round(q["g_ht"], 3), round(q["u_g_ht"], 3))


if __name__ == "__main__":
    self_check()
    if "--self-check" in sys.argv:
        sys.exit(0)
    res = run()
    (HERE / "results.json").write_text(json.dumps(res, indent=1, sort_keys=True), encoding="utf-8")
    (HERE / "table.md").write_text(table(res) + "\n", encoding="utf-8")
    print("wrote results.json + table.md;", sum("abstain" not in r for r in res["rows"]), "measured rows")
