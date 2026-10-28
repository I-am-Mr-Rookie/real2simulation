"""S02c RM02 scene-motion probe: LK flow on every decoded frame (half-res). Evidence only.
Usage: python evidence/clips/s02c_rm02_flow.py OUTPUT_DIR"""
import csv, json, sys
from pathlib import Path
import cv2, numpy as np
OUT=Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
ROOT=Path(__file__).resolve().parents[2]
cap=cv2.VideoCapture(str(ROOT/'test-data/public/RM02.mp4'))
prev=None; rows=[]; i=0
while True:
    ok,f=cap.read()
    if not ok: break
    g=cv2.cvtColor(cv2.resize(f,(960,540)),cv2.COLOR_BGR2GRAY)
    if prev is not None:
        p0=cv2.goodFeaturesToTrack(prev,400,0.01,8)
        p1,st,_=cv2.calcOpticalFlowPyrLK(prev,g,p0,None)
        pb,stb,_=cv2.calcOpticalFlowPyrLK(g,prev,p1,None)
        good=(st.ravel()==1)&(stb.ravel()==1)&(np.linalg.norm((pb-p0).reshape(-1,2),axis=1)<1.0)
        a=p0.reshape(-1,2)[good]; b=p1.reshape(-1,2)[good]; d=b-a
        H,inl=cv2.findHomography(a,b,cv2.RANSAC,1.0) if len(a)>=8 else (None,None)
        ir=float(inl.mean()) if inl is not None else 0.0
        rows.append([i,len(a),float(np.median(d[:,0])),float(np.median(d[:,1])),float(np.percentile(np.abs(d[:,0]),90)-np.percentile(np.abs(d[:,0]),10)),ir])
    prev=g; i+=1
with (OUT/'RM02-flow.csv').open('w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['frame','tracked','med_dx','med_dy','abs_dx_p90_minus_p10','homography_inlier_ratio_1px']); w.writerows(rows)
r=np.array([x[1:] for x in rows])
print(json.dumps({'frames':i,'min_tracked':int(r[:,0].min()),'median_tracked':float(np.median(r[:,0])),'median_dx':float(np.median(r[:,1])),'median_dy':float(np.median(r[:,2])),'median_dx_spread':float(np.median(r[:,3])),'median_inlier_ratio':float(np.median(r[:,4])),'frames_inlier_lt_0.6':int((r[:,4]<0.6).sum())}))
