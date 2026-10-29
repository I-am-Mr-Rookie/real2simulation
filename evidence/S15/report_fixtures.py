"""S15i fixture: a report built ONLY through the public Build.reports interface from the S15h fit fixture.
SYNTHETIC inputs; not gate, calibration, real-scene or physical evidence. Usage (repo root): python evidence/S15/report_fixtures.py [--check]"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Build.reports import SCHEMA, digest, number_entry, validate_report  # noqa: E402

FIT = ROOT / "tests/workspace/fixtures/fit-output.json"
OUT = ROOT / "tests/workspace/fixtures/report-output.json"


def build():
    fit = json.loads(FIT.read_text(encoding="utf-8"))["output"]
    numbers = {"gravity": number_entry(fit, "gravity.value", "gravity.uncertainty"), "rmse": number_entry(fit, "fit.rmse"),
               "observations": number_entry(fit, "fit.n")}
    report = {"schema": SCHEMA, "template": "free_fall", "fitter_digest": digest(fit), "title": "Synthetic free-fall report",
              "sections": [{"id": "result", "title": "Result", "text": ["Fitted gravity is {{gravity}} from {{observations}} observations."]},
                           {"id": "quality", "title": "Fit quality", "text": ["Residual RMSE is {{rmse}}."]}],
              "numbers": numbers}
    return {"provenance": "SYNTHETIC inputs; report built via Build.reports.number_entry and checked by validate_report.",
            "report": validate_report(report, fit)}


if __name__ == "__main__":
    text = json.dumps(build(), indent=1, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        sys.exit(0 if OUT.read_text(encoding="utf-8") == text else "report fixture drifted: rerun without --check")
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT))
