"""Hash existing product, contract and test files without reading private archives."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OWNED = "Build/web/src/lab/fit-contract.mjs"
BASELINE = HERE / "protected-before.json"

if sys.argv[1] == "before":
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    prefixes = ("Build/", "tests/", "contracts/", "schemas/",
                "evidence/S10/ui-contract-invariants/R15/prior-R14/")
    hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
              for name in names if name.startswith(prefixes)
              and name not in (OWNED, "tests/lab/ui-helper-oracle.test.mjs")
              and not Path(name).name.startswith(".env")}
    BASELINE.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"protected_files": len(hashes), "status": "CAPTURED"}))
else:
    hashes = json.loads(BASELINE.read_text(encoding="utf-8"))
    changed = [name for name, digest in hashes.items()
               if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest]
    result = {"protected_files": len(hashes), "changed": changed, "status": "PASS" if not changed else "FAIL"}
    (HERE / "protected-after.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    sys.exit(bool(changed))
