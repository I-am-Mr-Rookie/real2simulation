"""R-M read-only reproducers (synthetic inputs only; no real measurement)."""
import copy, json, math, sys
sys.path.insert(0, '.')
from Build.measurement.free_fall import fit_free_fall, evaluate_held_out, FitAbstention
from Build.measurement.uncertainty import propagate_uncertainty
from Build.measurement.gate_m import summarize, evaluate_record

S = 0.002; G = 9.81
def record(n=12, split=7, noise=(), pts0=0.0, ratio=1.0, suffix_shift=0.0, u_scale=1e-5):
    frames = []
    for i in range(n):
        t = i/30
        y = 100 + (0.5*G*t*t)/S + (noise[i] if i < len(noise) else 0) + (suffix_shift if i > split else 0)
        frames.append(dict(frame_index=i, pts_s=pts0 + t/ratio, x_px=10.0, y_px=y))
    return dict(clip_id='SYN', licence='CC0', provenance='synthetic', motion='earth_free_fall',
        source_sha256='0'*64, approval=dict(scope='metric_measurement', evidence='synthetic'),
        continuous_segment_evidence='synthetic', width_px=4000, height_px=100000,
        scale=dict(method='independent_reference', m_per_px=S, uncertainty_m_per_px=u_scale,
                   plane_verified=True, evidence='synthetic'),
        timebase=dict(capture_seconds_per_pts_second=ratio, uncertainty_factor=1e-4,
                      verified=True, evidence='synthetic'),
        frames=frames, last_training_frame=split)
def assume(n, det=0.5, ts=1e-4):
    return dict(independent_frame_errors=True, calibration_independent_of_frames=True,
        small_error_linearization=True, remaining_systematics_negligible=True,
        detection_std_px=[det]*n, timestamp_std_pts_s=[ts]*n,
        scale_clock_correlation=0.0, evidence='synthetic')
out = {}

# F1 summarize trusts caller-declared relative_error/coverage, not g
bad = [dict(g_m_s2=20.0, relative_error=0.0, uncertainty_covers_reference=True,
            capture_group=f'G{i}', blockers=[]) for i in range(3)]
s = summarize(bad); out['F1_inconsistent_trials_pass'] = (s['status'], s['gate_passed'], s['mean_g_m_s2'])

# F2 capture-group aliasing by whitespace/case
alias = [dict(g_m_s2=9.81, relative_error=0.0, uncertainty_covers_reference=True,
              capture_group=g, blockers=[]) for g in ('A', 'A ', 'a')]
s = summarize(alias); out['F2_alias_groups'] = (s['independent_measured_count'], s['gate_passed'])

# F3 evaluate_record output can never satisfy summarize
r = record(); res = evaluate_record(r, assume(8), metric_authorized=True, custody_verified=True)
out['F3_evaluate_record'] = dict(capture_group=res['capture_group'],
    covers=res['uncertainty_covers_reference'], blockers=res['blockers'], g=res['g_m_s2'])
out['F3_summary'] = summarize([dict(res) for _ in range(3)])['status']

# F4 held-out suffix ignored by gate: suffix shifted by 500 px (1 m) still same g/rel error
r2 = record(suffix_shift=500.0)
res2 = evaluate_record(r2, assume(8), metric_authorized=True, custody_verified=True)
out['F4_suffix_shift'] = dict(rel_err=res2['relative_error'], held_out_rmse_m=res2['held_out_rmse_m'])
r3 = record(n=9, split=7)  # one held-out frame accepted
out['F4_one_frame_suffix_ok'] = len(evaluate_held_out(fit_free_fall(r3), r3).frame_indices)

# F5 declared detection std not checked against residuals
noisy = record(noise=[0, 6, -6, 6, -6, 6, -6, 6])
fit = fit_free_fall(noisy)
u = propagate_uncertainty(noisy, assume(8, det=0.001))
out['F5_declared_vs_residual'] = dict(train_rmse_px=fit.training.rmse_m/S, declared_px=0.001,
    detection_std_m_s2=u.detection_standard_m_s2, g=fit.g_m_s2)

# F6 unbounded declared calibration uncertainty accepted (u_s = 10*s)
big = record(u_scale=10*S)
u6 = propagate_uncertainty(big, assume(8))
out['F6_huge_scale_uncertainty'] = dict(u_g=u6.standard_uncertainty_m_s2, g=u6.fit.g_m_s2)

# V1 timing Jacobian vs central finite difference on noisy record
def g_of(rec): return fit_free_fall(rec).g_m_s2
h = 1e-7; base = noisy; worst = 0
uj = propagate_uncertainty(base, dict(assume(8, det=0.0), timestamp_std_pts_s=[1.0]*8))
fd = []
for i in range(8):
    p, m = copy.deepcopy(base), copy.deepcopy(base)
    p['frames'][i]['pts_s'] += h; m['frames'][i]['pts_s'] -= h
    if i == 0: m['frames'][0]['pts_s'] = max(0.0, m['frames'][0]['pts_s'])
    fd.append((g_of(p)-g_of(m))/(2*h if i else h))
out['V1_timing_jacobian'] = dict(analytic_norm=uj.timestamp_standard_m_s2, fd_norm=math.hypot(*fd))

# V2 large PTS origin offset + slow-motion ratio recovery
off = record(pts0=1e6, ratio=0.25)
out['V2_offset_slowmo_g'] = fit_free_fall(off).g_m_s2
print(json.dumps(out, indent=1, default=str))
