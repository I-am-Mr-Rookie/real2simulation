"""S02c v3 original-frame probe (BN02 green-ball mask, PJ01 motion blobs). Evidence only; not calibration.
Usage: python evidence/clips/s02c_v3_analysis.py OUTPUT_DIR"""
import csv, json, sys
from pathlib import Path
import cv2, numpy as np
OUT=Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
ROOT=Path(__file__).resolve().parents[2]
res={}
# BN02: HSV green mask per decoded frame
cap=cv2.VideoCapture(str(ROOT/'test-data/public/BN02.webm')); i=0; rows=[]
while True:
    ok,f=cap.read()
    if not ok: break
    s=cv2.resize(f,(480,270)); h=cv2.cvtColor(s,cv2.COLOR_BGR2HSV)
    m=cv2.inRange(h,(30,80,60),(55,255,255))
    ys,xs=np.nonzero(m); a=len(xs)
    rows.append([i,cap.get(cv2.CAP_PROP_POS_MSEC)/1000,a,float(xs.mean()) if a else '',int(ys.max()) if a else '',int(ys.min()) if a else ''])
    i+=1
with (OUT/'BN02-mask.csv').open('w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['frame','pts_s','green_px','cx','bottom_y','top_y']); w.writerows(rows)
res['BN02']={'frames':i,'rows_with_mask':sum(1 for r in rows if r[2]>2000)}
# PJ01: frame-difference small-blob detections
cap=cv2.VideoCapture(str(ROOT/'test-data/public/PJ01.webm')); prev=None; i=0; det=[]
while True:
    ok,f=cap.read()
    if not ok: break
    g=cv2.GaussianBlur(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY),(3,3),0)
    if prev is not None:
        d=cv2.threshold(cv2.absdiff(g,prev),25,255,cv2.THRESH_BINARY)[1]
        n,_,st,cen=cv2.connectedComponentsWithStats(d)
        tot=int(d.sum()//255)
        small=[(float(cen[k][0]),float(cen[k][1]),int(st[k][4])) for k in range(1,n) if 3<=st[k][4]<=150]
        det.append([i,cap.get(cv2.CAP_PROP_POS_MSEC)/1000,tot,len(small),json.dumps(small[:5])])
    prev=g; i+=1
with (OUT/'PJ01-diff.csv').open('w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['frame','pts_s','changed_px','small_blobs','first5']); w.writerows(det)
res['PJ01']={'frames':i}
print(json.dumps(res))
