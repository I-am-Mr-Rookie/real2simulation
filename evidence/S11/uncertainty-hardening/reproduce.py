"""Generate synthetic numerical evidence; run from the repository root."""
import json
import platform
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from Build.fitter import coverage_regression
from Build.fitter.api import handle


def quantity(value, unit, uncertainty):
    return {"value": value, "unit": unit, "uncertainty": uncertainty,
            "source": {"label": "simulated", "evidence": "S11 uncertainty regression"}}


def main():
    request = {
        "times": [quantity(i / 10, "s", .01) for i in range(20)],
        "positions": [quantity(1 + .4 * (i / 10) + 4.905 * (i / 10)**2, "m", .05)
                      for i in range(20)],
    }
    batches = [asdict(coverage_regression(seed=seed)) for seed in range(200)]
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "provenance": "simulated only",
        "api_request": request, "api_result": handle(request),
        "legacy_api_result": handle({**request, "uncertainty_model": "iid_fixed_clock_scale"}),
        "coverage_batches": batches,
        "aggregate_coverage": sum(b["covered"] for b in batches) / sum(b["seeds"] for b in batches),
        "failed_batches": [i for i, b in enumerate(batches) if b["status"] == "FAIL"],
    }
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
