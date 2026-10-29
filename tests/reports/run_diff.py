"""python -m tests.reports.run_diff <evidence dir>: re-run the fitter per template, diff every number, write numeric_diff.json."""
import json
import sys
from pathlib import Path

from Build.reports.diff import diff_report

from .templates import MODELS, report, request

if __name__ == "__main__":
    res = {t: diff_report(report(t), request(t)) for t in MODELS}
    Path(sys.argv[1], "numeric_diff.json").write_text(json.dumps(
        {"scope": "visibly synthetic fixtures; fitter re-run per template; no gate/real-scene/physical evidence", "templates": res}, indent=1, sort_keys=True))
    print({t: (len(r["mismatches"]), r["checked"].get("json_numbers")) for t, r in res.items()})
    sys.exit(any(r["mismatches"] for r in res.values()))

