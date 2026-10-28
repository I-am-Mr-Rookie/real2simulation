"""ST05 bounded orange-toss track (S02c2 STOCK shard). Local evidence probe, not a calibrated tracker.
Usage: python ST05_track.py CLIP OUT_CSV LO-HI [LO-HI ...]  -- all frames of Pexels 7117951 226x426 rendition;
each LO-HI is a free-flight segment (after release, before catch) chosen from the full-rate sheets.
Mask = orange HSV (skin/shirt/shelf excluded by saturation); largest blob centroid per frame."""
import cv2, numpy as np, sys, csv
cap = cv2.VideoCapture(sys.argv[1]); rows = []; prev = None
k = -1
while True:
    ok, f = cap.read(); k += 1
    if not ok: break
    m = cv2.inRange(cv2.cvtColor(f, cv2.COLOR_BGR2HSV), (5, 150, 120), (22, 255, 255))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    rep = prev is not None and cv2.absdiff(f, prev).max() == 0; prev = f
    if n > 1:
        j = 1 + int(np.argmax(st[1:, 4]))
        rows.append([k, round(k / 30, 4), round(cen[j][0], 1), round(cen[j][1], 1), int(st[j, 4]), int(st[j, 2]), int(st[j, 3]), int(rep)])
    else: rows.append([k, round(k / 30, 4), None, None, 0, 0, 0, int(rep)])
with open(sys.argv[2], 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['frame', 't_s', 'cx', 'cy', 'area', 'w', 'h', 'exact_repeat']); w.writerows(rows)
print(dict(frames=len(rows), exact_repeats=sum(r[7] for r in rows)))
for s in sys.argv[3:]:
    lo, hi = map(int, s.split('-'))
    seg = [r for r in rows if lo <= r[0] <= hi and r[2] is not None and not r[7]]
    t = np.array([r[1] for r in seg]); y = np.array([r[3] for r in seg])
    assert len(t) >= 8 and y.argmin() not in (0, len(y) - 1), (s, len(t), y)  # self-check: enough points, apex inside segment
    c = np.polyfit(t, y, 2); res = y - np.polyval(c, t)
    print(dict(seg=s, n=len(t), apex_frame=seg[int(y.argmin())][0], a_px_s2=round(2 * c[0], 1),
               rms_px=round(float(np.sqrt((res ** 2).mean())), 2), median_width_px=float(np.median([r[5] for r in seg]))))
