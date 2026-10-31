"""S07m: pre-registered v3 predictive held-out check (rules: Run-System/Runs/S07m-orch180/PLAN.md, committed first).
v3 = S07l v3_candidate, reused unchanged via diagnose.run(): sigma = max(train resid sd, 2 px), held variance
sigma^2 (1 + leverage) from the floor(2n/3) quadratic fit, PASS iff chi-square p >= 0.05. Windows/g/u frozen from
S07h (v1) and S07k (v2). Inputs: existing track JSONs + results.json only; no tracking/video/model/Modal/GPU/Meta.
9.79 is used only for the copied coverage flags; nothing is selected by closeness to 9.79.
Run from repo root: python -B evidence/S07/S07m/measure_v3.py [--self-check]"""
import json, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "S07l"))
import diagnose as dl  # noqa: E402  (-> S07k measure_v2 -> S07h measure_heldout -> S07i measure_own01)

SRC = {"v1": "evidence/S07/S07h/results.json", "v2": "evidence/S07/S07k/results.json"}


def row_out(w, row):
    v3, b, c = w["v3_candidate"], w["b_shape"], w["c_centroid"]
    return {"clip": w["clip"], "analysis": w["analysis"], "frames": w["frames"], "n": w["n"],
            "g": row["g"], "u": row["u"], "z": row["z"], "in_1u": row["in_1u"], "in_2u": row["in_2u"],
            "held_rmse_px": w["held_rmse_px"], "sigma_px": v3["sigma_px"], "chi2": v3["chi2"], "dof": v3["dof"],
            "p": v3["p"], "v3_pass": v3["pass"], "impact_in_window": w["a_impact"]["impact_in_window"],
            "validated_conditional": bool(v3["pass"] and not w["a_impact"]["impact_in_window"]),
            "alongside": {"max_width_change": b["max_abs_width_change"], "max_height_change": b["max_abs_height_change"],
                          "height_growth_vs_speed_r": b["height_growth_vs_speed_r"],
                          "centroid_minus_box_offset_range_px": c["offset_range_px"],
                          "rs_20ms_assumed_held_rmse_px": w["e_timing"]["rs_readout_along_y"]["held_rmse_px"]}}


def coverage(rs):
    cnt = lambda xs: {"n": len(xs), "in_1u": sum(r["in_1u"] for r in xs), "in_2u": sum(r["in_2u"] for r in xs)}  # noqa: E731
    return {"all_measured": cnt(rs), "v3_pass_only": cnt([r for r in rs if r["v3_pass"]]),
            "v3_pass": sum(r["v3_pass"] for r in rs), "validated_conditional": sum(r["validated_conditional"] for r in rs)}


def assemble(wins, srcs):
    out, abst = [], []
    for tag, d in srcs.items():
        rows = {r["clip"]: r for r in d["rows"]}
        out += [row_out(w, rows[w["clip"]]) for w in wins if w["analysis"] == tag]
        abst += [{"analysis": tag, "clip": r["clip"], "abstain": r.get("abstain", "no window")}
                 for r in d["rows"] if "fall_frames" not in r]
    cov = {tag: coverage([r for r in out if r["analysis"] == tag]) for tag in srcs}
    return out, abst, cov


def run():
    wins = dl.run()["windows"]  # asserts each held RMSE reproduces its pipeline row (<0.05 px)
    srcs = {t: json.loads(dl.h.locate(p).read_text(encoding="utf-8")) for t, p in SRC.items()}
    rows, abst, cov = assemble(wins, srcs)
    ok = [f"{r['analysis']} {r['clip']}" for r in rows if r["validated_conditional"]]
    return {"label": "THIRD ANALYSIS (v3, pre-registered after seeing v1/v2 fail; forking-paths caveat) - MEASURED owner-clip "
                     "SAM 3.1 tracks; user-declared scale, phone clock unverified, rolling shutter assumed",
            "rules": "Run-System/Runs/S07m-orch180/PLAN.md", "alpha": dl.V3_ALPHA, "detect_px": dl.DETECT_PX,
            "rows": rows, "abstained": abst, "coverage": cov,
            "bottom_line": ("validated (conditional) windows: " + ", ".join(ok)) if ok else "no clip is a validated measurement"}


def readme(out):
    f = lambda x: "-" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.2f}"  # noqa: E731
    L = ["# S07m - v3 predictive held-out check (THIRD analysis)", "", out["label"], "",
         "Rules: ../../../" + out["rules"] + ". Script: measure_v3.py. Data: results.json.", "",
         "| set | clip | frames | g +/- u (m/s^2) | in 1u/2u | held RMSE px | sigma px | chi2/dof | p | v3 | impact | max w/h change | h~speed r | centroid drift px | RS20ms px |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["rows"]:
        a = r["alongside"]
        L.append(f"| {r['analysis']} | {r['clip']} | f{r['frames'][0]}-f{r['frames'][1]} | {r['g']:.2f} +/- {r['u']:.2f} | "
                 f"{'Y' if r['in_1u'] else 'N'}/{'Y' if r['in_2u'] else 'N'} | {r['held_rmse_px']:.1f} | {r['sigma_px']:.2f} | "
                 f"{r['chi2']:.1f}/{r['dof']} | {r['p']:.2g} | {'PASS' if r['v3_pass'] else 'FAIL'} | {'Y' if r['impact_in_window'] else 'N'} | "
                 f"{f(a['max_width_change'])}/{f(a['max_height_change'])} | {f(a['height_growth_vs_speed_r'])} | "
                 f"{f(a['centroid_minus_box_offset_range_px'])} | {f(a['rs_20ms_assumed_held_rmse_px'])} |")
    L += ["", "Abstained: " + "; ".join(f"{a['analysis']} {a['clip']} ({a['abstain']})" for a in out["abstained"]), "",
          "Coverage vs 9.79 (copied S07h/S07k flags): " + json.dumps(out["coverage"]), "",
          f"**Bottom line:** {out['bottom_line']}."]
    return "\n".join(L) + "\n"


def self_check():  # synthetic only; never touches owner data
    fps, a = 30.0, 14000.0
    fr = {}
    for i in range(30, 60):
        t, fall = i / fps, max(i / fps - 40 / fps, 0)
        y = 300 + 0.5 * a * fall ** 2 if i <= 52 else fr[52]["y"] + 2 * (i - 52)  # impact after f52
        fr[i] = {"t": t, "x": 500.0, "y": y, "yb": y + 1.0, "w": 280.0, "h": 120.0}
    good = dl.analyse(fr, 1080, 1920, 41, 52, list(range(35, 40)), 0.0007)
    bad = dl.analyse(fr, 1080, 1920, 41, 55, list(range(35, 40)), 0.0007)
    assert good["v3_candidate"]["pass"] and good["v3_candidate"]["sigma_px"] == dl.DETECT_PX
    assert not bad["v3_candidate"]["pass"] and bad["a_impact"]["impact_in_window"]
    g, b = dict(good, clip="X1", analysis="v1"), dict(bad, clip="X2", analysis="v1")
    src = {"v1": {"rows": [{"clip": "X1", "g": 9.0, "u": 1.0, "z": -0.79, "in_1u": True, "in_2u": True, "fall_frames": [41, 52]},
                           {"clip": "X2", "g": 5.0, "u": 1.0, "z": -4.79, "in_1u": False, "in_2u": False, "fall_frames": [41, 55]},
                           {"clip": "X3", "abstain": "synthetic"}]}}
    rows, abst, cov = assemble([g, b], src)
    assert [r["validated_conditional"] for r in rows] == [True, False] and len(abst) == 1
    assert cov["v1"]["v3_pass_only"] == {"n": 1, "in_1u": 1, "in_2u": 1} and cov["v1"]["all_measured"]["n"] == 2
    readme({"label": "s", "rules": "r", "rows": rows, "abstained": abst, "coverage": cov, "bottom_line": "s"})
    print("S07m self-check OK (synthetic)")


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        self_check()
    else:
        res = run()
        HERE.joinpath("results.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        HERE.joinpath("README.md").write_text(readme(res), encoding="utf-8")
        print(json.dumps({"coverage": res["coverage"], "bottom_line": res["bottom_line"]}, indent=1))

