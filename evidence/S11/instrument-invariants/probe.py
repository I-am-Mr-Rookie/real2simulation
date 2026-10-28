"""Repeatable CPU-only exact-rational S11 quantization audit; no product edits."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests/instruments"))
from test_r14_invariants import exact_quantize, observations


def examine(value, resolution):
    results = []
    for name, item in observations(value, resolution).items():
        truth = -value if name == "camera.y" else value
        expected = exact_quantize(truth, resolution)
        results.append({"instrument": name, "input": truth, "input_hex": truth.hex(),
                        "resolution": resolution, "resolution_hex": resolution.hex(),
                        "expected": expected, "expected_hex": expected.hex(),
                        "observed": item, "observed_hex": item["value"].hex(),
                        "matches": item["value"] == expected})
    return results


if __name__ == "__main__":
    cases = {
        "strictly_below_half": (math.nextafter(0.5, 0.0), 1.0),
        "exact_odd_lattice": (float(2 ** 52 + 1), 1.0),
        "exact_subnormal_lattice": (math.nextafter(sys.float_info.min, math.inf), math.ulp(0.0)),
    }
    frozen = {name: examine(*args) for name, args in cases.items()}
    sweep = []
    for exponent in (-1074, -1022, -900, -100, 0, 100, 900):
        resolution = math.ldexp(1.0, exponent)
        for ticks in (0.0, 0.25, math.nextafter(0.5, 0.0), 0.5, 1.0, 1.5, float(2 ** 52 + 1)):
            value = ticks * resolution
            sweep.extend(examine(value, resolution))
    files = ("Build/instruments/synthetic.py", "contracts/fit/quantity.py", "Build/lab/pipeline.py")
    result = {
        "source_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files},
        "oracle": "Fraction.from_float; exact integer quotient/remainder; half-away ties; final float conversion",
        "frozen": frozen,
        "dyadic_sweep": {"observations": len(sweep), "mismatches": sum(not row["matches"] for row in sweep),
                         "cases": sweep},
    }
    target = Path(__file__).with_name("probe.json")
    target.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(target), "frozen_mismatches": sum(not row["matches"] for rows in frozen.values() for row in rows),
                      "sweep_observations": len(sweep), "sweep_mismatches": result["dyadic_sweep"]["mismatches"]}))
