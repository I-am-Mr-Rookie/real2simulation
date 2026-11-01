"""S06a pinned MapAnything GPU image contract and offline CPU dry run (no Modal, no network)."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # inside a Modal container this is just "/"
# Referenced, not copied: S05b-orch14 ran this exact lock on A10G (S05c owns spike/ concurrently).
LOCK = ROOT / "Build/reconstruction/spike/requirements-linux-py311.txt"
REVISIONS = ROOT / "evidence/S05/upstream/revisions.json"
# sha256 of the LF-normalized lock (= git blob bytes); mismatch means the runtime changed: re-pin here.
LOCK_SHA256 = "cc352969c963e6dc5d689e83b1e4cce7f052e418ffc2299d27c29af9cd183330"
PYTHON = "3.11"
GPU = "L4"
MODEL_ID = "facebook/map-anything-apache"
NC_MODEL_IDS = {"facebook/map-anything"}  # non-commercial checkpoint; never bake
CODE_REV = "3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9"
WEIGHT_REV = "00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a"
REQUIRED_PINS = ("torch==2.8.0", "torchvision==0.23.0", "torchaudio==2.8.0",
                 "numpy==2.2.6", "timm==1.0.20", "huggingface-hub==2.3.0")
HF_HOME = "/weights/hf"


def lock_sha256(path=LOCK):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def dry_run(lock=LOCK, revisions=REVISIONS):
    """Validate every pin the image depends on; returns the spec plus an errors list."""
    errors = []
    lines = [l.strip() for l in Path(lock).read_text().splitlines()]
    reqs = [l for l in lines if l and not l.startswith("#")]
    digest = lock_sha256(lock)
    if digest != LOCK_SHA256:
        errors.append(f"lock sha256 drift: {digest}")
    errors += [f"unpinned requirement: {r}" for r in reqs
               if "==" not in r and not r.endswith(f"/{CODE_REV}.zip")]
    errors += [f"missing pin: {p}" for p in REQUIRED_PINS if p not in reqs]
    if not any(r.startswith("mapanything @ ") and r.endswith(f"/{CODE_REV}.zip") for r in reqs):
        errors.append("mapanything not pinned to code revision")
    rev = json.loads(Path(revisions).read_text())
    if rev["map_code"]["revision"] != CODE_REV:
        errors.append("code revision differs from S05 revisions.json")
    weights = rev["map_weights"]
    if weights["revision"] != WEIGHT_REV:
        errors.append("weight revision differs from S05 revisions.json")
    if weights["license"] != "apache-2.0" or weights["gated"] is not False:
        errors.append("weights not ungated apache-2.0")
    if MODEL_ID in NC_MODEL_IDS:
        errors.append("NC checkpoint selected")
    lock_path = Path(lock).resolve()
    return {
        "contract": "S06a-gpu-image/v1", "ok": not errors, "errors": errors,
        "python": PYTHON, "gpu": GPU, "base": "modal.Image.debian_slim",
        "lock": lock_path.relative_to(ROOT).as_posix() if lock_path.is_relative_to(ROOT) else str(lock),
        "lock_sha256_lf": digest, "requirement_count": len(reqs),
        "model_id": MODEL_ID, "code_revision": CODE_REV, "weight_revision": WEIGHT_REV,
        "weights_license": weights["license"], "hf_home": HF_HOME,
        "runtime_env": {"HF_HOME": HF_HOME, "HF_HUB_OFFLINE": "1"},
    }


if __name__ == "__main__":
    result = dry_run()
    text = json.dumps(result, indent=1)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).parent.mkdir(parents=True, exist_ok=True)
        Path(sys.argv[1]).write_text(text + "\n")
    print(text)
    sys.exit(0 if result["ok"] else 1)
