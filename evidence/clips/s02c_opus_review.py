"""S02c Opus review probe: full decode, median-background moving-blob track, contact sheet.
Usage: python evidence/clips/s02c_opus_review.py CLIP_PATH OUT_DIR [max_width]
Local evidence only; not a physics/calibration tracker. Derived images stay in OUT_DIR."""
import cv2, numpy as np, sys, json, csv
from pathlib import Path
src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
mw = int(sys.argv[3]) if len(sys.argv) > 3 else 960
cap = cv2.VideoCapture(str(src)); frames = []; pts = []
while True:
    ok, f = cap.read()
    if not ok: break
    pts.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
    s = mw / f.shape[1]
    frames.append(cv2.resize(f, None, fx=s, fy=s, interpolation=cv2.INTER_AREA) if s < 1 else f)
n = len(frames); assert n > 10, n
idx = np.linspace(0, n - 1, min(n, 60)).astype(int)
bg = np.median(np.stack([cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY) for i in idx]), axis=0).astype(np.uint8)
rows = []; prev = None; diffs = []
for i, f in enumerate(frames):
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    if prev is not None: diffs.append(float(np.mean(cv2.absdiff(g, prev))))
    prev = g
    m = cv2.morphologyEx((cv2.absdiff(g, bg) > 30).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    k, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if k > 1:
        j = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])); rows.append([i, round(pts[i], 4), round(cen[j][0], 1), round(cen[j][1], 1), int(st[j, 4])])
    else: rows.append([i, round(pts[i], 4), None, None, 0])
with (out / (src.stem + '-track.csv')).open('w', newline='') as fh:
    wr = csv.writer(fh); wr.writerow(['frame', 'pts_s', 'cx', 'cy', 'blob_area_px']); wr.writerows(rows)
sel = np.linspace(0, n - 1, 16).astype(int); tiles = []
for i in sel:
    t = frames[i].copy(); r = rows[i]
    if r[2] is not None: cv2.circle(t, (int(r[2]), int(r[3])), 12, (0, 0, 255), 2)
    cv2.putText(t, f'f{i} {pts[i]:.2f}s', (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    tiles.append(cv2.resize(t, (480, int(480 * t.shape[0] / t.shape[1]))))
grid = np.vstack([np.hstack(tiles[r * 4:(r + 1) * 4]) for r in range(4)])
cv2.imwrite(str(out / (src.stem + '-sheet.jpg')), grid, [cv2.IMWRITE_JPEG_QUALITY, 70])
gaps = np.diff(pts)
summ = dict(clip=src.name, decoded_frames=n, pts_first=pts[0], pts_last=pts[-1], pts_gap_median=float(np.median(gaps)), pts_gap_max=float(gaps.max()), nonmonotonic=int((gaps <= 0).sum()),
    frames_with_blob=sum(1 for r in rows if r[4] > 20), max_adjacent_mean_delta=max(diffs), median_adjacent_mean_delta=float(np.median(diffs)), size=frames[0].shape[:2])
print(json.dumps(summ))
