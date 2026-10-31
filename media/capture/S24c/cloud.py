# S24c beat 3: RM02 MapAnything point cloud (real S05b npz, gitignored) + S05d floor normal arrow. Run from repo root.
import json,subprocess,os,numpy as np
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
NPZ=os.environ['RM02_NPZ'];z=np.load(NPZ)
P=[];C=[]
for v in range(4):
    p=z['view%d_pts3d'%v].reshape(-1,3);c=z['view%d_conf'%v].reshape(-1);im=z['view%d_img_no_norm'%v].reshape(-1,3)
    k=c>=np.quantile(c,.5);P.append(p[k]);C.append(im[k])
P=np.concatenate(P);C=np.concatenate(C);C=C/255 if C.max()>1.5 else C
rng=np.random.default_rng(0);i=rng.choice(len(P),30000,replace=False);P=P[i];C=np.clip(C[i],0,1)
s=json.load(open('evidence/S05/S05d/RESULT.json'))['RM02'];n=np.array(s['floor']['normal_down'])
m=np.median(P,0);L=np.ptp(P,0).max()*.35
os.makedirs('media/capture/S24c/_cloud',exist_ok=True)
for f in range(36):
    fig=plt.figure(figsize=(12.8,7.2),dpi=100);fig.patch.set_facecolor('#0b0f14');ax=fig.add_subplot(111,projection='3d');ax.set_facecolor('#0b0f14')
    ax.scatter(P[:,0],P[:,2],-P[:,1],c=C,s=1.2)  # x right, z depth, -y up (camera y points down)
    ax.quiver(m[0],m[2],-m[1],n[0]*L,n[2]*L,-n[1]*L,color='#f33',lw=3)
    ax.set_axis_off();ax.view_init(elev=15,azim=-60+f*10)
    fig.text(.5,.94,'RM02 · MapAnything point cloud (4 views, conf >= median, 30k pts) · red arrow = S05d floor-normal (down)',color='w',ha='center',fontsize=14)
    fig.text(.5,.06,'Floor-normal spread %.5f° (bootstrap 1 sd) · Metric scale: ABSTAINED (unverified) · model units, not metres'%s['floor']['normal_bootstrap_std_deg'],color='w',ha='center',fontsize=16)
    fig.text(.01,.01,'RM02: Andy Barbour - Tracking shot of empty classroom - Pexels (Pexels License)',color='#cfd',fontsize=9)
    fig.savefig('media/capture/S24c/_cloud/f%02d.png'%f,facecolor=fig.get_facecolor());plt.close(fig)
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','6','-i','media/capture/S24c/_cloud/f%02d.png','-c:v','libvpx-vp9','-pix_fmt','yuv420p','media/capture/S24c/beat3-cloud.webm'],check=True)
subprocess.run(['ffmpeg','-y','-loglevel','error','-i','media/capture/S24c/_cloud/f03.png','-vf','split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse','media/capture/S24c/beat3-cloud.png'],check=True)

