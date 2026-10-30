"""Verify canonical-test applicability and preserve historical audit artifacts; no product writes."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
CANONICAL = ROOT.parents[1]
PATHS = ["Build/real2sim", "contracts/overlay", "tests/prediction", "Build/pipeline/gpu_stages.py",
         "Build/simulator"]


def git(*args, cwd=ROOT):
    return subprocess.check_output(["git", *args], cwd=cwd)


out = {"reviewed_snapshot": git("rev-parse", "HEAD").decode().strip(),
       "canonical_head_at_verification": git("rev-parse", "HEAD", cwd=CANONICAL).decode().strip(),
       "files": {}}
for name in git("ls-files", "--", *PATHS).decode().splitlines():
    own, canonical = (ROOT / name).read_bytes(), (CANONICAL / name).read_bytes()
    equal = own == canonical
    assert equal or own.replace(b"\r\n", b"\n") == canonical.replace(b"\r\n", b"\n"), name
    out["files"][name] = {"sha256": hashlib.sha256(own).hexdigest(), "canonical_sha256":
                           hashlib.sha256(canonical).hexdigest(), "byte_identical": equal}
out["historical_artifacts_unchanged"] = []
for name in ("prediction-ST03.json", "overlay-ST03.json", "overlay-pendulum-SYNTHETIC.json"):
    rel = "evidence/S12/" + name
    assert git("show", "9d1a9ae:" + rel) == (ROOT / rel).read_bytes().replace(b"\r\n", b"\n")
    out["historical_artifacts_unchanged"].append(rel)
print(json.dumps(out, indent=2))
