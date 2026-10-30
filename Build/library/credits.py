"""Write the credit line for every validated library demo (S18h); no downloads."""
import csv
import json
from pathlib import Path

from Build.library.guest import CATALOGUES
from Build.library.validate import ROOT, credit, validate_file


def build(root=ROOT):
    root = Path(root)
    artifacts = root / "test-data/library-artifacts"
    with (root / "clips.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    lines = {}
    for name in ("manifest.json", *CATALOGUES):
        for demo in validate_file(artifacts / name, artifacts, root)["demos"]:
            lines.setdefault(demo["id"], credit(demo, rows) | {"catalogues": []})["catalogues"].append(name)
    output = root / "evidence/S18/S18h-credits.json"
    output.write_text(json.dumps({"credits": list(lines.values())}, indent=2) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    print(build())
