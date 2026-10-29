# Independent S11l check; run from candidate root: python <this> (cwd=candidate)
import math,random,sys
sys.path.insert(0,'Build')
from fitter.core import fit_motion, jacobian_covariance, _aic
random.seed(7); worst=0; flips=0; n_cmp=0
for trial in range(300):
    n=random.randint(4,30); ts=[i*0.03+random.random()*1e-3 for i in range(n)]
    ys=[2-0.5*9.81*t*t+random.gauss(0,10**random.uniform(-6,-1)) for t in ts]
    s=10**random.uniform(-7,-1) if trial%3 else 0.0
    fit=fit_motion(ts,ys,2)
    old=jacobian_covariance(fit,sigma=max(s, math.sqrt(fit.rss/fit.dof)),parameter_index=2)  # base 1325ae9 legacy path
    new=jacobian_covariance(fit,position_sigmas=(s,)*n,parameter_index=2)                    # b37f7b8 legacy path
    if old.valid!=new.valid: flips+=1; continue
    if old.valid: n_cmp+=1; worst=max(worst,abs(old.variance-new.variance)/old.variance)
    for d in (1,2):
        f=fit_motion(ts,ys,d); a_old=f.n*math.log(sum(e*e for e in f.residuals)/f.n)+2*f.k
        assert abs(a_old-_aic(f))<1e-8*max(1,abs(a_old))
print('legacy cmp',n_cmp,'validity flips',flips,'max rel var diff',worst)
f=fit_motion([0,1,2,3,4,5],[0,5e-320,0,5e-320,0,5e-320],1)
print('subnormal rss',f.rss,'rmse',f.rmse,'any',any(f.residuals),'aic',_aic(f))

