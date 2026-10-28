"""ST03 bounded apple track (S02c2 STOCK shard). Local evidence probe, not a calibrated tracker.
Usage: python ST03_track.py CLIP OUT_CSV  -- frames 50..95 of Pexels 12723966 720x1366 rendition.
Mask = (|frame - median(f96..110)| > 25) AND apple-like HSV, ROI x<380; largest blob centroid."""
import cv2, numpy as np, sys, csv
cap = cv2.VideoCapture(sys.argv[1]); fr = {}
i = 0
while i <= 110:
    ok, f = cap.read(); assert ok, i
    if i >= 50: fr[i] = f[:, :380]
    i += 1
bg = np.median(np.stack([fr[k] for k in range(96, 111)]), axis=0).astype(np.uint8)
rows = []
for k in range(50, 96):
    f = fr[k]; hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    col = cv2.inRange(hsv, (22, 40, 120), (45, 200, 255)) > 0
    dif = cv2.absdiff(f, bg).max(axis=2) > 25
    m = cv2.morphologyEx((col & dif).astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n > 1:
        j = 1 + int(np.argmax(st[1:, 4]))
        rows.append([k, round(k * 1001 / 30000, 4), round(cen[j][0], 1), round(cen[j][1], 1), int(st[j, 4]), int(st[j, 2]), int(st[j, 3])])
    else: rows.append([k, round(k * 1001 / 30000, 4), None, None, 0, 0, 0])
with open(sys.argv[2], 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['frame', 't_s', 'cx', 'cy', 'area', 'w', 'h']); w.writerows(rows)
# Free-fall segment f58..f76 (release..last frame before ground contact). The 29.97p container repeats
# every 6th frame (25p->30p cadence), so drop exact repeats and step unique frames at 1/25 s.
u = [r for i, r in enumerate(rows) if 58 <= r[0] <= 76 and (r[2], r[3]) != (rows[i - 1][2], rows[i - 1][3])]
seg = [r for r in u if r[4] > 1000]  # skip partial/blurred blobs
idx = {r[0]: i for i, r in enumerate(u)}
t = np.array([idx[r[0]] / 25 for r in seg]); y = np.array([r[3] for r in seg]); wd = np.array([r[5] for r in seg])
assert len(t) >= 8 and np.all(np.diff(y) > 0), (len(t), y)  # self-check: enough points, monotonic descent
c = np.polyfit(t, y, 2); res = y - np.polyval(c, t)
print(dict(n=len(t), repeats_dropped=19 - len(u), frames=[r[0] for r in seg], a_px_s2=round(2 * c[0], 1),
           rms_px=round(float(np.sqrt((res ** 2).mean())), 2), median_width_px=float(np.median(wd))))
