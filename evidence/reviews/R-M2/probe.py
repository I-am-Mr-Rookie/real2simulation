"""R-M2 read-only synthetic probes of S07f summarize(); run from source root: python -B <this>."""
import json, math, sys
sys.path.insert(0, '.')
from Build.measurement.gate_m import summarize, REFERENCE_G


def o(g, grp, cov=True, bl=None, **k):
    d = dict(g_m_s2=g, uncertainty_covers_reference=cov, capture_group=grp, blockers=bl or [])
    d.update(k)
    return d


class EqTrue:  # truthy, == anything
    def __bool__(self): return True
    def __eq__(self, other): return True


class F(float): pass  # stands in for numpy.float64 (a float subclass)


V = dict(independence_verified=True)
hi, lo = REFERENCE_G*1.05, REFERENCE_G*.95
R = dict(
    hi_edge=summarize([o(hi, 'A'), o(hi, 'B'), o(5, 'C')], **V)['gate_passed'],
    hi_next=summarize([o(math.nextafter(hi, 9e9), 'A'), o(hi, 'B'), o(5, 'C')], **V)['gate_passed'],
    hi_edge_err=abs(hi-REFERENCE_G)/REFERENCE_G, lo_edge_err=abs(lo-REFERENCE_G)/REFERENCE_G,
    bool_g_measured=summarize([o(True, 'A'), o(9.81, 'B'), o(9.81, 'C')], **V)['measured_count'],
    inf=summarize([o(math.inf, 'A'), o(9.81, 'B'), o(9.81, 'C')], **V)['gate_passed'],
    nan=summarize([o(math.nan, 'A'), o(9.81, 'B'), o(9.81, 'C')], **V)['gate_passed'],
    dict_self_flag=summarize([o(9.81, g, independence_verified=True) for g in 'ABC'])['gate_passed'],
    eq_true_obj=summarize([o(9.81, g) for g in 'ABC'], independence_verified=EqTrue())['gate_passed'],
    zwsp_ids=summarize([o(9.81, 'A'), o(9.81, '\u200bA'), o(9.81, 'B')], **V)['independent_measured_count'],
    nbsp_ids=summarize([o(9.81, 'A'), o(9.81, '\u00a0A'), o(9.81, 'B')], **V)['independent_measured_count'],
    nfc_nfd_ids=summarize([o(9.81, '\u00e9'), o(9.81, 'e\u0301'), o(9.81, 'B')], **V)['independent_measured_count'],
    cov_truthy_1=summarize([o(9.81, g, cov=1) for g in 'ABC'], **V)['gate_passed'],
    blockers_str=summarize([o(9.81, g, bl='x') for g in 'ABC'], **V)['gate_passed'],
    four_trials=summarize([o(9.81, g) for g in 'ABCD'], **V)['gate_passed'],
    unmeasured_third=summarize([o(9.81, 'A'), o(9.81, 'B'), o(None, 'C')], **V)['status'],
    float_subclass=summarize([o(F(9.81), g) for g in 'ABC'], **V),
    nonstr_groups=summarize([o(9.81, i) for i in (1, 2, 3)], **V)['independent_measured_count'],
)
for name, arg in (('nondict', [1, 2, 3]), ('generator', (o(9.81, g) for g in 'ABC'))):
    try:
        R[name] = summarize(arg, **V)['gate_passed']
    except Exception as error:
        R[name] = type(error).__name__
fs = R['float_subclass']
R['float_subclass'] = {k: fs[k] for k in ('status', 'physics_evaluation', 'measured_count', 'gate_passed')}
print(json.dumps(R, indent=1))
