"""S15aw: freeze per-frame chart series for each stored owner-clip result into Build/api/workspace/owner_clips.json.
Reuses the S07l/S07m pipeline unchanged (load, floor(2n/3) prefix quadratic, v3 sigma); no tracking/video/model/GPU.
Pixel space only (the m/s^2 value stays the stored S07h g). Run from repo root: python -B evidence/S15aw/build_series.py [--check]"""
import json, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "evidence/S07/S07l"))
import diagnose as dl  # noqa: E402

CLIPS = ROOT / "Build/api/workspace/owner_clips.json"
V3 = ROOT / "evidence/S07/S07m/results.json"
r4 = lambda x: round(float(x), 6)  # noqa: E731  (6 dp: the held-out extrapolation is sensitive to t rounding)


def series(clip, f0, f1, sigma):
    fr, _, _ = dl.load(clip)
    fis = [i for i in range(f0, f1 + 1) if i in fr]
    t, y = (np.array([fr[i][k] for i in fis]) for k in ("t", "y"))
    n, tt = len(t) * 2 // 3, t - t[0]
    p, _, _ = dl.held(t, y, 2)  # same prefix fit S07h/S07m used
    inv = np.linalg.inv(np.vander(tt[:n], 3).T @ np.vander(tt[:n], 3))
    ts = np.linspace(0, tt[-1], 41)
    lev = np.einsum("ij,jk,ik->i", np.vander(ts, 3), inv, np.vander(ts, 3))
    return {"label": "RECORDED replay of MEASURED SAM 3.1 track points; curve SIMULATED (quadratic fit to the prefix)",
            "source": "evidence/S07/S07l/diagnose.py load/held + evidence/S07/S07m v3 sigma (S15aw build_series.py)",
            "units": {"t": "s", "y": "px (image y, down)"}, "sigma_px": r4(sigma), "n_train": n,
            "band": "1-sigma predictive band: sigma_px * sqrt(1 + leverage) (S07m v3 held-out variance)",
            "points": [{"frame": f, "t_s": r4(a), "y_px": r4(b), "held_out": k >= n} for k, (f, a, b) in enumerate(zip(fis, tt, y))],
            "model": [{"t_s": r4(a), "y_px": r4(np.polyval(p, a)), "band_px": r4(sigma * np.sqrt(1 + h)), "prediction": bool(a > tt[n - 1])}
                      for a, h in zip(ts, lev)]}


def build():
    doc = json.loads(CLIPS.read_text(encoding="utf-8"))
    rows = {r["clip"]: r for r in json.loads(V3.read_text(encoding="utf-8"))["rows"] if r["analysis"] == "v1"}
    for c, e in doc["clips"].items():
        if e.get("measurement"):
            r = rows[c]
            e["series"] = series(c, *r["frames"], r["sigma_px"])
    return doc


if __name__ == "__main__":
    doc = build()
    for c, e in doc["clips"].items():  # self-check: held RMSE of the stored series reproduces the stored measurement
        if "series" in e:
            pts = e["series"]["points"]
            n = e["series"]["n_train"]
            p = np.polyfit([q["t_s"] for q in pts[:n]], [q["y_px"] for q in pts[:n]], 2)
            rm = np.sqrt(np.mean([(q["y_px"] - np.polyval(p, q["t_s"])) ** 2 for q in pts[n:]]))
            assert abs(rm - e["measurement"]["held_out_rmse_px"]) < 0.06, (c, rm)
    text = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        assert CLIPS.read_text(encoding="utf-8") == text, "owner_clips.json series out of date"
    else:
        CLIPS.write_text(text, encoding="utf-8")
    print("ok", sum("series" in e for e in doc["clips"].values()), "series")

