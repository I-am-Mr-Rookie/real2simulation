"""S07h: held-out/robustness g on owner clips OWN02-OWN06 with the FROZEN S07i pipeline.
evidence/S07/S07i/measure_own01.py is IMPORTED and its constants are untouched; only the per-clip frame rules from the
fixed fall-windows.json are supplied (pre-registered in Run-System/Runs/S07h-orch172/PLAN.md before any g was computed).
Run from repo root (worktree or canonical): python evidence/S07/S07h/measure_heldout.py [--self-check]"""
import hashlib, json, math, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "S07i"))
import measure_own01 as m  # noqa: E402  frozen S07i record()/window()/assume()/run() and constants
from Build.measurement.free_fall import FitAbstention  # noqa: E402  (m put the repo root on sys.path)

CLIPS = {"OWN02": "02_live_check", "OWN03": "03_test_clean", "OWN04": "04_test_shadow",
         "OWN05": "05_repeat_a", "OWN06": "05_repeat_b (sheet partly down)"}
PENDING = {"OWN07": "05_repeat_c", "OWN08": "05_repeat_d", "OWN09": "06 nosheet", "OWN10": "06 clutter",
           "OWN11": "06 lowres"}  # CUDA OOM in the batch track; S07j re-tracks
HELD_PASS_PX = 3 * m.DETECTION_STD_PX  # pre-registered: held-out RMSE within 3x the declared per-frame error
FROZEN = {"EDGE_M": 0.2028, "EDGE_U_M": 0.0005, "BOX_EDGE_U_PX": 2.0, "DETECTION_STD_PX": 2.0, "PTS_STD_S": 1e-4,
          "CLOCK_U": 1e-3, "START_PX": 8.0, "G_LOCAL": 9.79}


def locate(rel):
    return next(p for p in (m.ROOT / rel, m.CANONICAL / rel) if p.exists())


class _Bytes:  # feeds the frozen m.run() a window-truncated track instead of copying its fit/uncertainty code
    def __init__(self, b):
        self.b = b

    def read_bytes(self):
        return self.b


def plan(windows):
    """Per-clip rules from fall-windows.json: scale = release-6..release-2 (first 5 held frames); end = pre-registered fall end."""
    out = {}
    for c in windows["clips"]:
        rel, end = map(int, re.fullmatch(r"release f(\d+), increasing run to f(\d+)", c["rule"]).groups())
        assert c["first"] == max(rel - 6, 0), c
        out[c["clip"]] = {"track": c["out"], "scale_frames": [c["first"], c["first"] + 5], "fall_end": end,
                          "colour_release": rel}
    return out


def truncate(track, fall_end):
    track["record"]["frames"] = [f for f in track["record"]["frames"] if f["frame_index"] <= fall_end]
    return track


def run_clip(clip, p):
    raw = locate(p["track"]).read_bytes()
    base = {"clip": clip, "scene": CLIPS[clip], "track": p["track"], "track_sha256": hashlib.sha256(raw).hexdigest(),
            "rules": p}
    saved = m.SCALE_FRAMES, m.TRACK
    m.SCALE_FRAMES, m.TRACK = range(*p["scale_frames"]), _Bytes(json.dumps(truncate(json.loads(raw), p["fall_end"])).encode())
    try:
        res = m.run()
    except (FitAbstention, StopIteration, KeyError, IndexError, ValueError, ZeroDivisionError) as e:
        return {**base, "abstain": f"{type(e).__name__}: {e}"}
    finally:
        m.SCALE_FRAMES, m.TRACK = saved
    res["result"].pop("s07g_diagnostic")
    res.pop("track"), res.pop("track_sha256")
    held = res["mask_centroid"]["held_out"]["rmse_px"]
    return {**base, "label": f"MEASURED (owner clip {clip}, user-declared scale 0.2028 m, phone clock not externally verified)",
            **res, "held_out_pass": held <= HELD_PASS_PX}


def row(clip, r):
    if "abstain" in r:
        return {"clip": clip, "scene": r["scene"], "abstain": r["abstain"]}
    res, c = r["result"], r["mask_centroid"]
    g, u = res["g"], res["u_total"]
    return {"clip": clip, "scene": r.get("scene", "01 (S07i)"), "g": g, "u": u, "z": (g - m.G_LOCAL) / u,
            "in_1u": abs(g - m.G_LOCAL) <= u, "in_2u": abs(g - m.G_LOCAL) <= 2 * u,
            "g_box": r["box_centre"]["g"], "fall_frames": c["fall_frames"], "n_frames": c["fall_frames"][1] - c["fall_frames"][0] + 1,
            "held_rmse_px": c["held_out"]["rmse_px"], "held_residuals_px": c["held_out"]["residuals_px"],
            "held_out_pass": c["held_out"]["rmse_px"] <= HELD_PASS_PX, "m_per_px": c["m_per_px"]}


def run():
    assert {k: getattr(m, k) for k in FROZEN} == FROZEN, "S07i constants changed"
    rules = plan(json.loads(locate("evidence/S07/S07i/fall-windows.json").read_text(encoding="utf-8")))
    clips = {c: run_clip(c, rules[c]) for c in CLIPS}
    own01 = json.loads(locate("evidence/S07/S07i/result-own01.json").read_text(encoding="utf-8"))
    rows = [row("OWN01", own01)] + [row(c, r) for c, r in clips.items()]
    meas = [r for r in rows if "g" in r]
    rep = None
    a, b = (next((r for r in meas if r["clip"] == k), None) for k in ("OWN05", "OWN06"))
    if a and b:
        d = a["g"] - b["g"]
        rep = {"pair": "OWN05 (05a) vs OWN06 (05b)", "diff": d, "u_diff": math.hypot(a["u"], b["u"]),
               "z_diff": d / math.hypot(a["u"], b["u"]), "pending": "05c/05d (OWN07/OWN08) not tracked (CUDA OOM, S07j)"}
    return {"label": "MEASURED per clip (user-declared scale, phone clock not externally verified); comparison to local 9.79 only",
            "rules": "Run-System/Runs/S07h-orch172/PLAN.md (pre-registered)", "held_out_pass_px": HELD_PASS_PX,
            "rows": rows, "clips": clips, "repeatability_05": rep,
            "coverage": {"measured": len(meas), "in_1u": sum(r["in_1u"] for r in meas), "in_2u": sum(r["in_2u"] for r in meas),
                         "held_out_pass": sum(r["held_out_pass"] for r in meas)},
            "pending": PENDING, "excluded": {"OWN12": "no free fall (S07i)"}}


def table(out):
    lines = ["| clip | scene | g ± u (m/s²) | z vs 9.79 | in 2u | fall frames (n) | held-out RMSE px | held-out |",
             "|---|---|---|---|---|---|---|---|"]
    for r in out["rows"]:
        if "abstain" in r:
            lines.append(f"| {r['clip']} | {r['scene']} | ABSTAIN: {r['abstain']} | – | – | – | – | – |")
        else:
            lines.append(f"| {r['clip']} | {r['scene']} | {r['g']:.2f} ± {r['u']:.2f} | {r['z']:+.2f} | {'yes' if r['in_2u'] else 'no'} | "
                         f"f{r['fall_frames'][0]}–{r['fall_frames'][1]} ({r['n_frames']}) | {r['held_rmse_px']:.1f} | {'PASS' if r['held_out_pass'] else 'FAIL'} |")
    return "\n".join(lines)


def self_check():
    p = plan({"clips": [{"clip": "X", "first": 42, "out": "t", "rule": "release f48, increasing run to f59"}]})["X"]
    assert p["scale_frames"] == [42, 47] and p["fall_end"] == 59, p
    t = truncate({"record": {"frames": [{"frame_index": i} for i in range(42, 62)]}}, 59)
    assert t["record"]["frames"][-1]["frame_index"] == 59
    m.self_check()  # frozen S07i window/split check + OWN01 still reproduces
    out = run()
    assert len(out["rows"]) == 6 and all("g" in r or r["abstain"] for r in out["rows"])
    assert all(5 < r["g"] < 15 for r in out["rows"] if "g" in r), out["rows"]
    assert m.SCALE_FRAMES == range(40, 45), "frozen globals restored"
    print("S07h self-check OK")


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        self_check()
    else:
        res = run()
        HERE.joinpath("results.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        print(table(res))
        print(json.dumps({"coverage": res["coverage"], "repeatability_05": res["repeatability_05"]}, indent=1))
