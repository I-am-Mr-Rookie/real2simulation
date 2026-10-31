# S24c beat 4/5 plots: real Build/fitter on ST03 prefix (19 frames), observed suffix f77-83. Run from repo root.
import json,sys,subprocess
sys.path.insert(0,'.')
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from Build.fitter.core import fit_least_squares,jacobian_covariance
r=json.load(open('evidence/S12/gate-rs/ST03-f58-83/result.json'))
oid=2;pts={}
for f,ids,bx in r['stream']:
    if oid in ids:
        b=bx[ids.index(oid)];pts[f+r['frame_map'][0][0]]=b[1]+b[3]/2  # stream index is local; frame_map[0][0] = source frame of index 0
fm=dict((a,b) for a,b in r['frame_map'])
pre=[f for f in sorted(pts) if f<=76];suf=[f for f in sorted(pts) if f>76]
t=[fm[f] for f in pre];y=[pts[f] for f in pre]
fit=fit_least_squares(t,y,2)  # core only accepts 'm'; values are image-height fractions, relabelled in the plot
se=jacobian_covariance(fit).standard_error;rel=se/abs(fit.coefficients[2])
print('n',fit.n,'rel',rel,'rmse',fit.rmse,'sufcount',len(suf))
ts=[fm[f] for f in suf];ys=[pts[f] for f in suf];pr=fit.predict(ts)
err=[abs(a-b) for a,b in zip(pr,ys)]
def plot(name,predict):
    fig,ax=plt.subplots(figsize=(12.8,7.2),dpi=100);fig.patch.set_facecolor('#0b0f14');ax.set_facecolor('#0b0f14')
    tt=[t[0]+i*(ts[-1]-t[0])/200 for i in range(201)] if predict else [t[0]+i*(t[-1]-t[0])/100 for i in range(101)]
    ft=fit.predict(tt)
    ax.plot(tt,ft,'#4af',lw=2,label='fitted parabola (Build/fitter, quadratic OLS)')
    ax.fill_between(tt,[a-fit.rmse for a in ft],[a+fit.rmse for a in ft],color='#4af',alpha=.25,label='band: +/- 1 residual RMSE (prefix)')
    ax.scatter(t,y,c='#ff0',s=30,label='SAM 3.1 track, prefix f58-76 (n=%d)'%fit.n)
    if predict: ax.scatter(ts,ys,c='#f55',s=40,marker='x',label='observed suffix f77-83 (revealed after sealing)')
    ax.invert_yaxis();ax.tick_params(colors='w');[s.set_color('#889') for s in ax.spines.values()]
    ax.set_xlabel('time (s, clip clock)',color='w');ax.set_ylabel('y (fraction of image height, down)',color='w')
    if predict:
        t0='Gate RS: NOT_MET - diagnostic RMS 0.1982 image heights, 7/466 frames scored' ;ax.set_title(t0+'\nillustration: plain quadratic extrapolation of the prefix, no floor (not the sealed prediction file)',color='w')
    else: ax.set_title('ST03 prefix f58-76 (n=%d): quadratic OLS fit, image-height units; uncertainty number: use BENCHMARK 0.07367'%fit.n,color='w')  # local OLS rel=0.0744 differs from BENCHMARK 0.07367, so not drawn
    ax.legend(facecolor='#123',labelcolor='w',loc='upper left');ax.text(.99,.02,'ST03: Roman Odintsov - Woman dropping apple on ground - Pexels (Pexels License)',transform=ax.transAxes,ha='right',color='#cfd',fontsize=9)
    fig.savefig('media/capture/S24c/'+name+'.png',facecolor=fig.get_facecolor());plt.close(fig)
plot('beat4-fit',False);plot('beat5-predict',True)
for n in ('beat4-fit','beat5-predict'):
    subprocess.run(['ffmpeg','-y','-loglevel','error','-loop','1','-t','8','-i','media/capture/S24c/%s.png'%n,'-c:v','libvpx-vp9','-pix_fmt','yuv420p','media/capture/S24c/%s.webm'%n],check=True)

