"""Crop sheet around s02c_opus_review blob centroids (48 evenly spaced decoded frames) for visual verification.
Usage: python evidence/clips/s02c_opus_blobcrops.py CLIP OUT_DIR WORK_WIDTH HALF_BOX"""
import cv2, numpy as np, sys, csv, json
from pathlib import Path
src, out, W, H = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
rows = list(csv.DictReader(open(out / (src.stem + '-track.csv'))))
sel = set(np.linspace(0, len(rows) - 1, 48).astype(int).tolist()); cap = cv2.VideoCapture(str(src)); tiles = []; i = 0
while True:
    ok, f = cap.read()
    if not ok: break
    if i in sel:
        s = W / f.shape[1]; f = cv2.resize(f, None, fx=s, fy=s, interpolation=cv2.INTER_AREA) if s < 1 else f
        f = cv2.copyMakeBorder(f, H, H, H, H, cv2.BORDER_CONSTANT); r = rows[i]
        x, y = (int(float(r['cx'])) + H, int(float(r['cy'])) + H) if r['cx'] else (H, H)
        c = cv2.resize(f[y - H:y + H, x - H:x + H].copy(), (160, 160)); cv2.circle(c, (80, 80), 3, (0, 0, 255), -1)
        cv2.putText(c, f'{i} a{r["blob_area_px"]}', (2, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1); tiles.append(c)
    i += 1
cv2.imwrite(str(out / (src.stem + '-blobcrops.jpg')), np.vstack([np.hstack(tiles[r * 8:(r + 1) * 8]) for r in range(6)]), [cv2.IMWRITE_JPEG_QUALITY, 75])
a = np.array([int(r['blob_area_px']) for r in rows]); print(json.dumps(dict(clip=src.name, frames=len(rows), blob_area_median=float(np.median(a)), blob_area_p5=float(np.percentile(a, 5)), blob_area_p95=float(np.percentile(a, 95)))))
