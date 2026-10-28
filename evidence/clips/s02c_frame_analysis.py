"""Local visual-evidence probe; not a physics/calibration or production tracker.

Run from S02c worktree: python evidence/clips/s02c_frame_analysis.py OUTPUT_DIR
Input videos stay local; derived images remain in OUTPUT_DIR and are not staged.
"""
import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
ROOT = Path(__file__).resolve().parents[2]
cv2.setNumThreads(2)


def bob():
    cap = cv2.VideoCapture(str(ROOT / 'test-data/public/PD02.mp4'))
    ok, frame = cap.read()
    assert ok and frame.shape[:2] == (1080, 1920)
    # Frame 0 manual seed: gold bob, not its reflection below.
    x, y, w, h = 500, 301, 111, 111
    template = cv2.cvtColor(frame[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)
    rows = []
    frames = 0
    tiles = []
    prev = None
    with (OUT / 'PD02-track.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['frame', 'nominal_seconds', 'x', 'y', 'w', 'h', 'match', 'mean_abs_frame_delta'])
        while ok:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            left, top = max(0, x-45), max(0, y-45)
            right, bottom = min(gray.shape[1], x+w+45), min(gray.shape[0], y+h+45)
            corr = cv2.matchTemplate(gray[top:bottom, left:right], template, cv2.TM_CCOEFF_NORMED)
            _, score, _, loc = cv2.minMaxLoc(corr)
            x, y = left+loc[0], top+loc[1]
            thumb = cv2.resize(gray, (192, 108))
            delta = 0.0 if prev is None else float(np.mean(cv2.absdiff(thumb, prev)))
            prev = thumb
            row = [frames, round(frames/30, 6), x, y, w, h, round(score, 5), round(delta, 4)]
            writer.writerow(row)
            rows.append(row)
            # Keep contextual, full-rate crops for manual audit of *every* box.
            crop = frame[max(0,y-20):min(1080,y+h+20), max(0,x-20):min(1920,x+w+20)].copy()
            cv2.rectangle(crop, (20,20), (20+w,20+h), (0,0,255), 2)
            crop = cv2.resize(crop, (150,150))
            cv2.putText(crop, str(frames), (3,14), cv2.FONT_HERSHEY_SIMPLEX, .43, (0,0,255), 1)
            tiles.append(crop)
            if len(tiles) == 50:
                grid = np.vstack([np.hstack(tiles[i:i+10]) for i in range(0,50,10)])
                cv2.imwrite(str(OUT / f'PD02-allframes-{frames//50:02d}.jpg'), grid)
                tiles = []
            if frames % 30 == 0:
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0,0,255), 4)
                cv2.putText(frame, f'frame {frames} score {score:.3f}', (30,80), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0,0,255), 3)
                cv2.imwrite(str(OUT / f'PD02-check-{frames:04d}.jpg'), frame)
            frames += 1
            ok, frame = cap.read()
    if tiles:
        while len(tiles) < 50:
            tiles.append(np.zeros((150,150,3), dtype=np.uint8))
        grid = np.vstack([np.hstack(tiles[i:i+10]) for i in range(0,50,10)])
        cv2.imwrite(str(OUT / f'PD02-allframes-{frames//50:02d}.jpg'), grid)
    cap.release()
    return {'decoded_frames': frames, 'first_frame': rows[0], 'last_frame': rows[-1],
            'minimum_match': min(rows, key=lambda r:r[6]),
            'maximum_frame_delta': max(rows[1:], key=lambda r:r[7])}


def room():
    cap = cv2.VideoCapture(str(ROOT / 'test-data/public/RM04.mp4'))
    ok, original = cap.read()
    assert ok and original.shape[:2] == (2160,3840)
    # Decode each original frame, work at half dimensions; coords are half-res pixels.
    first = cv2.resize(original, (1920,1080), interpolation=cv2.INTER_AREA)
    gray0 = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
    wallmask = np.zeros_like(gray0)
    wallmask[200:540, 650:1310] = 255  # chalkboard on rear wall
    desk_mask = np.zeros_like(gray0)
    desk_mask[700:825, 620:1450] = 255  # front table edges/corners
    wall = cv2.goodFeaturesToTrack(gray0, 200, 0.01, 8, mask=wallmask).reshape(-1, 2)
    # Hand-selected visible front table corners, plus automatically detected context.
    corners = np.array([[635,790],[1442,790],[700,716],[1328,716]], dtype=np.float32)
    desk = np.vstack([corners, cv2.goodFeaturesToTrack(gray0, 80, 0.01, 8, mask=desk_mask).reshape(-1, 2)])
    points0 = np.vstack([wall, desk]).astype(np.float32)
    nwall = len(wall)
    points = points0.copy()
    alive = np.ones(len(points), bool)
    prevgray = gray0
    rows = []
    frames = 0
    while True:
        if frames:
            ok, original = cap.read()
            if not ok:
                break
            frame = cv2.resize(original, (1920,1080), interpolation=cv2.INTER_AREA)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            active = np.flatnonzero(alive)
            p0 = points[active].reshape(-1,1,2)
            p1, st, _ = cv2.calcOpticalFlowPyrLK(prevgray, gray, p0, None, winSize=(25,25), maxLevel=3)
            back, st2, _ = cv2.calcOpticalFlowPyrLK(gray, prevgray, p1, None, winSize=(25,25), maxLevel=3)
            fb = np.linalg.norm((back-p0).reshape(-1,2), axis=1)
            good = st.ravel().astype(bool) & st2.ravel().astype(bool) & (fb < 1.0)
            alive[active[~good]] = False
            points[active[good]] = p1.reshape(-1,2)[good]
            prevgray = gray
        else:
            frame = first.copy()
        wi = np.flatnonzero(alive[:nwall])
        di = np.flatnonzero(alive[nwall:]) + nwall
        median_res = None
        max_res = None
        inliers = 0
        corner_res = [None] * 4
        if len(wi) >= 4 and len(di):
            H, inlier = cv2.findHomography(points0[wi], points[wi], cv2.RANSAC, 2.0)
            if H is not None:
                inliers = int(inlier.sum())
                predicted = cv2.perspectiveTransform(points0[di].reshape(-1,1,2), H).reshape(-1,2)
                residual = np.linalg.norm(predicted-points[di], axis=1)
                for j, idx in enumerate(di):
                    if idx-nwall < 4:
                        corner_res[idx-nwall] = float(residual[j])
                median_res = float(np.median(residual))
                max_res = float(np.max(residual))
        rows.append([frames, round(frames/25, 6), len(wi), inliers, len(di), median_res, max_res, *corner_res])
        if frames % 25 == 0:
            for i in np.flatnonzero(alive):
                cv2.circle(frame, tuple(np.round(points[i]).astype(int)), 4, (0,255,0) if i<nwall else (0,0,255), -1)
            cv2.putText(frame, f'frame {frames} wall green / foreground red', (30,80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)
            cv2.imwrite(str(OUT / f'RM04-check-{frames:04d}.jpg'), frame)
        frames += 1
    cap.release()
    with (OUT / 'RM04-flow.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['frame','nominal_seconds','wall_tracks','wall_inliers','foreground_tracks','median_residual_halfres_px','max_residual_halfres_px','front_left','front_right','back_left','back_right'])
        writer.writerows(rows)
    return {'decoded_frames':frames, 'initial_wall_features':nwall, 'initial_foreground_features':len(desk),
            'first_frame':rows[0], 'frame_100':rows[100] if len(rows)>100 else None,
            'frame_200':rows[200] if len(rows)>200 else None, 'last_frame':rows[-1]}


result = {'PD02': bob(), 'RM04': room()}
(OUT / 'summary.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
