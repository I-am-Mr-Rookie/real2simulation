"""S07k: SECOND ANALYSIS (v2) of owner clips with a pre-registered, track-internal fall-window rule.
Rule fixed in Run-System/Runs/S07k-orch174/PLAN.md before this script existed. The frozen S07i fit/uncertainty
(evidence/S07/S07i/measure_own01.py) and S07h helpers are IMPORTED; only window()/SCALE_FRAMES/TRACK are swapped per clip.
Run from repo root (worktree or canonical): python evidence/S07/S07k/measure_v2.py [--self-check]"""
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "S07h"))
import measure_heldout as h  # noqa: E402  (puts S07i + repo root on sys.path)
m = h.m
from Build.measurement.free_fall import FitAbstention  # noqa: E402

MOVE_PX, STATIC_PX, SCALE_N, SCALE_MIN, WIDTH_TOL, DECEL, N_MIN = 4.0, 6.0, 5, 3, 0.10, 0.5, 8  # PLAN.md, pre-registered
TRACKS = {"OWN01": "evidence/S07/S07g/track-own01.json",
          **{c: f"evidence/S07/S07i/track-own{c[-2:]}.json" for c in h.CLIPS}}
SCENES = {"OWN01": "01 (S07i)", **h.CLIPS}


class Abstain(Exception):
    pass


def box_widths(track):
    W = track["record"]["width_px"]
    return {track["frame_map"][i][0]: b[0][2] * W for i, _, b in track["stream"] if b}


def v2_rule(frames, width):
    """frames sorted by frame_index; width: frame_index -> SAM box width px. Returns (scale frame indices, fall segment)."""
    fi, y = [f["frame_index"] for f in frames], [f["y_px"] for f in frames]

    def d(k):
        return y[k] - y[k - 1] if k > 0 and fi[k] == fi[k - 1] + 1 else None

    R = next((k for k in range(1, len(frames) - 1) if (d(k) or 0) > MOVE_PX and (d(k + 1) or 0) > MOVE_PX), None)
    if R is None:
        raise Abstain("no sustained centroid-y release")
    sc, nxt = [], R - 1
    for k in range(R - 2, -1, -1):
        if len(sc) == SCALE_N or fi[k] != fi[nxt] - 1 or fi[k] not in width:
            break
        sc.insert(0, k)
        nxt = k
    if len(sc) < SCALE_MIN:
        raise Abstain(f"only {len(sc)} tracked scale frames before release f{fi[R]}")
    ys = [y[k] for k in sc]
    if max(ys) - min(ys) > STATIC_PX:
        raise Abstain(f"scale frames f{fi[sc[0]]}-f{fi[sc[-1]]} not static (y range {max(ys) - min(ys):.1f} px)")
    w0 = sum(width[fi[k]] for k in sc) / len(sc)
    E = R
    for k in range(R + 1, len(frames)):
        dk = d(k)
        if dk is None or fi[k] not in width or abs(width[fi[k]] - w0) > WIDTH_TOL * w0 or dk < DECEL * d(k - 1):
            break
        E = k
    seg = frames[R:E + 1]
    if len(seg) < N_MIN:
        raise Abstain(f"fall window f{fi[R]}-f{fi[E]} has {len(seg)} < {N_MIN} frames")
    return [fi[k] for k in sc], seg


def run_clip(clip):
    raw = h.locate(TRACKS[clip]).read_bytes()
    track = json.loads(raw)
    base = {"clip": clip, "scene": SCENES[clip], "track": TRACKS[clip], "track_sha256": hashlib.sha256(raw).hexdigest()}
    frames = sorted(track["record"]["frames"], key=lambda f: f["frame_index"])
    try:
        sc, seg = v2_rule(frames, box_widths(track))
    except Abstain as e:
        return {**base, "abstain": f"v2 rule: {e}"}
    keep = {f["frame_index"] for f in seg}
    rules = {"scale_frames": [sc[0], sc[-1]], "release": seg[0]["frame_index"], "fall_end": seg[-1]["frame_index"]}

    def window(fr):  # replaces S07i window(); same floor(2n/3) split
        s = [f for f in fr if f["frame_index"] in keep]
        return s, s[len(s) * 2 // 3 - 1]["frame_index"]

    saved = m.SCALE_FRAMES, m.TRACK, m.window
    m.SCALE_FRAMES, m.TRACK, m.window = range(sc[0], sc[-1] + 1), h._Bytes(raw), window
    try:
        res = m.run()
    except (FitAbstention, StopIteration, KeyError, IndexError, ValueError, ZeroDivisionError) as e:
        return {**base, "rules": rules, "abstain": f"{type(e).__name__}: {e}"}
    finally:
        m.SCALE_FRAMES, m.TRACK, m.window = saved
    res["result"].pop("s07g_diagnostic")
    res.pop("track"), res.pop("track_sha256")
    return {**base, "rules": rules, **res,
            "label": f"MEASURED, SECOND ANALYSIS v2 (owner clip {clip}, user-declared scale 0.2028 m, phone clock not externally verified)"}


def run():
    assert {k: getattr(m, k) for k in h.FROZEN} == h.FROZEN, "S07i constants changed"
    clips = {c: run_clip(c) for c in TRACKS}
    rows = [{**h.row(c, r), **({"rules": r["rules"]} if "rules" in r else {})} for c, r in clips.items()]
    v1 = {r["clip"]: r for r in json.loads(h.locate("evidence/S07/S07h/results.json").read_text(encoding="utf-8"))["rows"]}
    meas = [r for r in rows if "g" in r]
    return {"label": "SECOND ANALYSIS (v2) — MEASURED per clip; user-declared scale, phone clock not externally verified; 9.79 comparison only",
            "rules": "Run-System/Runs/S07k-orch174/PLAN.md (pre-registered v2)",
            "constants": {"MOVE_PX": MOVE_PX, "STATIC_PX": STATIC_PX, "SCALE_N": SCALE_N, "SCALE_MIN": SCALE_MIN,
                          "WIDTH_TOL": WIDTH_TOL, "DECEL": DECEL, "N_MIN": N_MIN, "held_out_pass_px": h.HELD_PASS_PX},
            "rows": rows, "clips": clips, "v1_rows": v1,
            "coverage": {"clips": len(rows), "measured": len(meas), "abstained": len(rows) - len(meas),
                         "in_1u": sum(r["in_1u"] for r in meas), "in_2u": sum(r["in_2u"] for r in meas),
                         "held_out_pass": sum(r["held_out_pass"] for r in meas)},
            "pending": {k: v + " (track file has 0 frames: CUDA OOM, S07j)" for k, v in h.PENDING.items()},
            "excluded": {"OWN12": "no free fall (S07i)"}}


def table(out):
    def cell(r):
        if r is None or "abstain" in r:
            return f"ABSTAIN ({r['abstain']})" if r else "–", "–"
        return (f"{r['g']:.2f} ± {r['u']:.2f} (z {r['z']:+.2f}) f{r['fall_frames'][0]}–{r['fall_frames'][1]} n={r['n_frames']}",
                f"{r['held_rmse_px']:.1f} {'PASS' if r['held_out_pass'] else 'FAIL'}")
    lines = ["| clip | v1 g ± u, window | v1 held-out px | v2 g ± u, window | v2 held-out px |", "|---|---|---|---|---|"]
    for r in out["rows"]:
        a, b = cell(out["v1_rows"].get(r["clip"])), cell(r)
        lines.append(f"| {r['clip']} | {a[0]} | {a[1]} | {b[0]} | {b[1]} |")
    return "\n".join(lines)


def self_check():  # synthetic frames only; never touches owner data
    def synth(width_at=None):
        fr = [{"frame_index": i, "y_px": 100.0 + (i % 2) + (15 * (i - 46) ** 2 if 46 < i < 57 else 0)} for i in range(40, 57)]
        fr += [{"frame_index": i, "y_px": fr[-1]["y_px"] + 1} for i in range(57, 60)]  # impact: velocity collapses
        return fr, {i: (300.0 if width_at and i >= width_at else 200.0) for i in range(40, 60)}
    sc, seg = v2_rule(*synth())
    assert (sc, seg[0]["frame_index"], seg[-1]["frame_index"]) == ([41, 42, 43, 44, 45], 47, 56), (sc, seg[0], seg[-1])
    try:
        v2_rule(*synth(width_at=52))
        raise AssertionError("width change must end the window and abstain (<8 frames)")
    except Abstain as e:
        assert "f47-f51" in str(e), e
    static = [{"frame_index": i, "y_px": 100.0} for i in range(40, 60)]
    try:
        v2_rule(static, {i: 200.0 for i in range(40, 60)})
        raise AssertionError("static track must abstain")
    except Abstain:
        pass
    assert {k: getattr(m, k) for k in h.FROZEN} == h.FROZEN and m.SCALE_FRAMES == range(40, 45)
    print("S07k self-check OK (synthetic only)")


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        self_check()
    else:
        res = run()
        HERE.joinpath("results.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        print(table(res))
        print(json.dumps({"coverage": res["coverage"], "abstains": {r["clip"]: r["abstain"] for r in res["rows"] if "abstain" in r}}, indent=1))
