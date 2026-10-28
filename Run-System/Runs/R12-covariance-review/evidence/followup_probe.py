"""R12 follow-up: arithmetic check of lost-residual-floor bound (simulation only)."""
import sys, math
from fractions import Fraction as F
sys.path.insert(0, "Build")
from fitter import fit_least_squares, jacobian_covariance
u = math.ulp(0.0)
# 1) premise: a nonzero square rounds to 0 only if exactly < u/2 (round-to-nearest-even ties to 0 at u/2)
for r in (1e-162, 2.0**-538, 2.0**-537.5 if False else 2.0**-537):
    sq = r * r; print("r", r, "r*r", sq, "exact<u/2", F(r)**2 < F(u)/2, "exact<u", F(r)**2 < F(u))
    if sq == 0: assert F(r)**2 <= F(u)/2
fit = fit_least_squares((0., 1e-10, 2e-10), (0., 1e-162, 0.), degree=1)
exact_rss = sum(F(x)**2 for x in fit.residuals)
bound = u * (fit.n / fit.dof)
print("n,dof", fit.n, fit.dof, "rss", fit.rss, "exact floor RSS/dof", float(exact_rss / fit.dof), "bound", bound)
assert fit.rss == 0 and exact_rss > 0 and exact_rss / fit.dof < F(bound)
# 2) behaviour straddling the bound
for s2, want in ((u, False), (bound, False), (math.nextafter(bound, 1), True), (2 * bound, True), (.01, True)):
    s = math.sqrt(s2); r = jacobian_covariance(fit, position_sigmas=(s,) * 3)
    eff = s * s
    print(f"declared var={eff!r} > bound={eff > bound} valid={r.valid} se={r.standard_error}")
    assert r.valid == (eff > bound)
    if r.valid: assert r.standard_error > 0
# 3) a single zero declared row with lost floor is unavailable; sigma=0 known path unchanged
assert not jacobian_covariance(fit, position_sigmas=(.1, 0., .1)).valid
z = jacobian_covariance(fit, sigma=0); assert z.valid and z.standard_error == 0
# 4) original P2 repro unchanged
f2 = fit_least_squares((0., 1., 2., 3.), (0., 0., 1e-165, 0.))
assert not jacobian_covariance(f2).valid and jacobian_covariance(f2, position_sigmas=(.1,)*4).standard_error == .05
print("FOLLOWUP PROBE PASS")

