"""Full-rate LK flow probe over a segment: tracked features, median motion, single-homography inlier ratio,
and fundamental-matrix inlier ratio (parallax evidence when homography explains far fewer than F).
Usage: python evidence/clips/s02c_opus_flow.py CLIP OUT_CSV START_S END_S [STRIDE]. Not reconstruction or scale evidence."""
import cv2, numpy as np, sys, csv, json
src, outp, a, b = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
K = int(sys.argv[5]) if len(sys.argv) > 5 else 1  # compare each frame with the frame K decoded frames earlier
cap = cv2.VideoCapture(src); cap.set(cv2.CAP_PROP_POS_MSEC, a * 1000)
hist = []; rows = []; n = 0
while True:
    ok, f = cap.read(); t = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
    if not ok or t > b: break
    g = cv2.cvtColor(cv2.resize(f, (640, 360), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY); n += 1
    prev = hist[0] if len(hist) == K else None
    if prev is not None:
        p0 = cv2.goodFeaturesToTrack(prev, 400, 0.01, 8)
        p1, st, _ = cv2.calcOpticalFlowPyrLK(prev, g, p0, None); pb, st2, _ = cv2.calcOpticalFlowPyrLK(g, prev, p1, None)
        ok2 = (st.ravel() == 1) & (st2.ravel() == 1) & (np.linalg.norm((pb - p0).reshape(-1, 2), axis=1) < 1)
        q0, q1 = p0.reshape(-1, 2)[ok2], p1.reshape(-1, 2)[ok2]; mag = float(np.median(np.linalg.norm(q1 - q0, axis=1))) if len(q0) else 0
        hr = fr = None
        if len(q0) >= 30 and mag > 0.5:
            _, mh = cv2.findHomography(q0, q1, cv2.RANSAC, 1.0); _, mf = cv2.findFundamentalMat(q0, q1, cv2.FM_RANSAC, 1.0, 0.99)
            hr = float(mh.mean()) if mh is not None else None; fr = float(mf.mean()) if mf is not None else None
        rows.append([n, round(t, 3), len(q0), round(mag, 3), hr, fr])
    hist = (hist + [g])[-K:]
with open(outp, 'w', newline='') as fh: w = csv.writer(fh); w.writerow(['i', 't', 'tracked', 'median_px', 'H_inlier', 'F_inlier']); w.writerows(rows)
H = np.array([r[4] for r in rows if r[4] is not None]); F = np.array([r[5] for r in rows if r[5] is not None])
print(json.dumps(dict(clip=src, start=a, end=b, frames=n, pairs=len(rows), tracked_median=float(np.median([r[2] for r in rows])), tracked_min=min(r[2] for r in rows),
    moving_pairs=len(H), H_inlier_median=float(np.median(H)) if len(H) else None, F_inlier_median=float(np.median(F)) if len(F) else None, pairs_H_below_0_6=int((H < 0.6).sum()))))
