"""S07i: fix per-clip fall windows for OWN02-OWN12 BEFORE any SAM tracking (local CPU, no GPU).
Rule (fixed here, same yellow threshold as the S07g diagnostic, quarter resolution):
release = first frame (>= 10) > 2 px (= 8 px full-res) below the frames 0-9 median that STARTS a run of
>= 4 strictly increasing centroids ending > 10 px (40 px full-res) below that median (v1 without the run
test triggered on hand jitter at OWN03/09/10/11; revised before any tracking);
fall end = last frame of the strictly increasing centroid run after release;
window = [release - 6 (>= 5 held frames for the box-width scale), fall end + 2], clipped to the clip.
Colour failure => whole clip (flagged). Writes evidence/S07/S07i/fall-windows.json (refuses to overwrite).
Run from repo root: python evidence/S07/S07i/fall_windows.py"""
import csv, json, subprocess, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "evidence/S07/S07g"))
from diagnostic_colour import yellow  # noqa: E402  (reuse the S07g threshold, unchanged)

CANONICAL = Path("C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon")
CLIPS = [f"OWN{i:02d}" for i in range(2, 13)]
SW, SH = 270, 480  # quarter of 1080x1920 (OWN11 478x850 is resampled to the same grid)
PROMPT = "yellow book"
# Colour rule failed on OWN12 (front cover is not yellow); contact sheet of frames 24-63 (passthrough) shows
# the book stays in the hand while the camera pans down: no free fall, so it is NOT tracked (no GPU spend).
EXCLUDED = {"OWN12": "no free fall: book held throughout, camera pans (frame inspection f24-63); colour rule failed"}


def centroids(path):
    # passthrough = same frame numbering as modal_track._frames (cfr output duplicated OWN12's last frame)
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"scale={SW}:{SH}",
                                   "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    cys = []
    for rgb in np.frombuffer(raw, np.uint8).reshape(-1, SH, SW, 3):
        ys, _ = np.nonzero(yellow(rgb))
        cys.append(float(ys.mean()) if len(ys) >= 30 else None)
    return cys


def window(cys):
    n = len(cys)
    base = [c for c in cys[:10] if c is not None]
    if len(base) < 5:
        return 0, n - 1, "colour rule failed (no held yellow book in frames 0-9); whole clip"
    med = float(np.median(base))
    def falls(i):
        run = cys[i:i + 4]
        return (len(run) == 4 and None not in run and run[0] > med + 2 and run[3] > med + 10
                and all(a < b for a, b in zip(run, run[1:])))
    rel = next((i for i in range(10, n) if falls(i)), None)
    if rel is None:
        return 0, n - 1, "colour rule failed (no release found); whole clip"
    end = rel
    while end + 1 < n and cys[end + 1] is not None and cys[end + 1] > cys[end]:
        end += 1
    return max(0, rel - 6), min(n - 1, end + 2), f"release f{rel}, increasing run to f{end}"


def self_check():
    cys = [100.0] * 15 + [104.0, 99.0] + [100.0] * 3 + [103.0 + i * i for i in range(8)] + [90.0] * 5
    assert window(cys) == (14, 29, "release f20, increasing run to f27"), window(cys)  # f15 jitter ignored
    assert window([None] * 30)[:2] == (0, 29)
    print("self-check OK")


def main():
    dest = Path(__file__).with_name("fall-windows.json")
    if dest.exists():
        raise FileExistsError(f"{dest} already fixed; never re-derive after tracking")
    with (CANONICAL / "clips.csv").open(encoding="utf-8", newline="") as stream:
        rows = {r["clip_id"]: r for r in csv.DictReader(stream)}
    clips = []
    for cid in CLIPS:
        if cid in EXCLUDED:
            continue
        cys = centroids(CANONICAL / rows[cid]["local_path"])
        first, last, why = window(cys)
        clips.append({"clip": cid, "first": first, "last": last, "frames": len(cys), "prompt": PROMPT,
                      "object_id": 0, "out": f"evidence/S07/S07i/track-{cid.lower()}.json", "rule": why})
        print(cid, first, last, len(cys), why)
    dest.write_text(json.dumps({"rule": __doc__.splitlines()[1:7], "excluded": EXCLUDED, "clips": clips},
                               indent=1), encoding="utf-8")


if __name__ == "__main__":
    self_check() if "--self-check" in sys.argv else main()
