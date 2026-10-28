"""R14-instrument-gate independent reproduction: pinned 82791f3 _quantize vs exact Fraction oracle (dyadic grids only)."""
import sys, math, random
from fractions import Fraction as F
SRC = sys.argv[1]
sys.path.insert(0, SRC); sys.path.insert(0, SRC + "/Build")
from instruments import synthetic as s
q = s._quantize
def orc(v, r):
    x = F(abs(v)) / F(r); w = x.numerator // x.denominator; m = w + (x - w >= F(1, 2))
    return math.copysign(float(m * F(r)), v) if v else 0.0
H = float.fromhex
edges = [(0.49999999999999994, 1.0, 0.0), (0.5, 1.0, 1.0), (-0.5, 1.0, -1.0), (2.5, 1.0, 3.0),
         (H('0x1.0000000000001p+52'), 1.0, None), (H('0x1.0000000000001p-1022'), 5e-324, None),
         (2**52 - 0.5, 1.0, 2.0**52), (2**51 + 0.5, 1.0, 2.0**51 + 1), (2.0**53, 1.0, None),
         (1.7976931348623157e308, 1.0, None), (5e-324, 1.0, 0.0), (-0.4, 1.0, -0.0), (-0.0, 1.0, 0.0),
         (H('0x1.8p-1074'), 5e-324, None)]
fail = 0
for v, r, e in edges:
    e = v if e is None else e; o = q(v, r)
    ok = o == e and math.copysign(1, o) == math.copysign(1, e); fail += not ok
    print(v.hex(), r, o.hex(), "OK" if ok else "BAD")
d = q(1.25, 0.1); fail += d != 1.3
print("decimal fixture 1.25/0.1 ->", d, "| exact-Fraction policy would give", orc(1.25, 0.1))
for v, r in [(1e308, 1e-308), (1.7976931348623157e308, 0.5)]:
    try: q(v, r); print("NOREJECT", v, r); fail += 1
    except ValueError as err: print("reject", v, r, err)
rng = random.Random(14); n = bad = 0
for _ in range(200000):
    r = 2.0 ** rng.randint(-1074 if rng.random() < .1 else -60, 60)
    k = rng.randint(0, 2 ** rng.randint(1, 60)); fr = rng.choice([0, F(1, 2), F(rng.random())])
    try: v = float((k + fr) * F(r)) * rng.choice([1, -1])
    except OverflowError: continue
    if not math.isfinite(v): continue
    try: o = q(v, r)
    except ValueError: continue
    n += 1; bad += o != orc(v, r)
print("dyadic sweep", n, "mismatch", bad); fail += bad
c = s.camera_observation(0, 0.0, -0.0, -0.3, time_resolution_s=1.0, pixel_resolution_px=1.0, time_uncertainty_s=0,
                         pixel_uncertainty_px=0, time_bias_s=0, pixel_bias_px=0)
print("camera", {k: v["value"] for k, v in c.items() if isinstance(v, dict) and "value" in v})
sys.exit(1 if fail else 0)

