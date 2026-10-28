"""S02c Opus template tracker: seeds from s02c_opus_review track row, tracks every decoded frame both ways.
Usage: python evidence/clips/s02c_opus_track.py CLIP OUT_DIR SEED_FRAME BOX_PX [margin]  (960-px-wide working scale)
Writes CLIP-tmpl.csv and a 48-crop sheet for visual inspection. Image-space only; no physics/scale claim."""
import cv2, numpy as np, sys, csv, json
from pathlib import Path
src, out = Path(sys.argv[1]), Path(sys.argv[2]); seed = int(sys.argv[3]); B = int(sys.argv[4]); M = int(sys.argv[5]) if len(sys.argv) > 5 else 40
rows = list(csv.DictReader(open(out / (src.stem + '-track.csv'))))
cap = cv2.VideoCapture(str(src)); F = []
while True:
    ok, f = cap.read()
    if not ok: break
    s = 960 / f.shape[1]; F.append(cv2.resize(f, None, fx=s, fy=s, interpolation=cv2.INTER_AREA) if s < 1 else f)
G = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in F]
cx, cy = (float(sys.argv[6]), float(sys.argv[7])) if len(sys.argv) > 7 else (float(rows[seed]['cx']), float(rows[seed]['cy']))  # optional manual seed from inspected sheet
x0, y0 = int(cx - B / 2), int(cy - B / 2); T = G[seed][y0:y0 + B, x0:x0 + B].copy()
res = {seed: (x0, y0, 1.0)}
for rng in (range(seed + 1, len(G)), range(seed - 1, -1, -1)):
    x, y = x0, y0
    for i in rng:
        g = G[i]; l, t = max(0, x - M), max(0, y - M); r, b = min(g.shape[1], x + B + M), min(g.shape[0], y + B + M)
        c = cv2.matchTemplate(g[t:b, l:r], T, cv2.TM_CCOEFF_NORMED); _, sc, _, loc = cv2.minMaxLoc(c)
        x, y = l + loc[0], t + loc[1]; res[i] = (x, y, round(float(sc), 4))
with (out / (src.stem + '-tmpl.csv')).open('w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['frame', 'x', 'y', 'box', 'match']); [w.writerow([i, *res[i][:2], B, res[i][2]]) for i in sorted(res)]
sel = np.linspace(0, len(G) - 1, 48).astype(int); P = B + 2 * M; tiles = []
for i in sel:
    x, y, sc = res[i]; f = cv2.copyMakeBorder(F[i], P, P, P, P, cv2.BORDER_CONSTANT)
    crop = f[y + P - M:y + P + B + M, x + P - M:x + P + B + M].copy(); cv2.rectangle(crop, (M, M), (M + B, M + B), (0, 0, 255), 1)
    crop = cv2.resize(crop, (160, 160)); cv2.putText(crop, f'{i} {sc:.2f}', (2, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1); tiles.append(crop)
cv2.imwrite(str(out / (src.stem + '-crops.jpg')), np.vstack([np.hstack(tiles[r * 8:(r + 1) * 8]) for r in range(6)]), [cv2.IMWRITE_JPEG_QUALITY, 75])
sc = np.array([res[i][2] for i in sorted(res)])
print(json.dumps(dict(clip=src.name, frames=len(G), seed=seed, box=B, min_match=float(sc.min()), frames_below_0_5=int((sc < 0.5).sum()), median_match=float(np.median(sc)))))
