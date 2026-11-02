"""Actual stage script in a tiny committed synthetic repo. No network, deploy or real credentials."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def test_api_stage_requires_hash_verified_public_archive(tmp_path):
    root = tmp_path / "repo"
    stage = root / "infra/railway/dev/stage.py"
    stage.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "infra/railway/dev/stage.py", stage)
    (stage.parent / "api.Dockerfile").write_text("FROM scratch\nARG R2S_SOURCE_REVISION\n")
    (root / "Build/api").mkdir(parents=True)
    (root / "Build/api/app.py").write_text("# synthetic staging fixture\n")
    bundle = root / "evidence/S13l/reconstruct/bundle"
    bundle.mkdir(parents=True)
    archive = bundle / "RM04-mapanything.npz"
    archive.write_bytes(b"SYNTHETIC archive fixture")
    manifest = root / "Build/pipeline/recorded/RM04-S13l-mapanything.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps({"files": {archive.name: {"sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}}}))
    def git(*args):
        return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    git("init")
    git("add", "Build", "infra")  # the bundle remains local-only
    git("-c", "user.name=N58 synthetic test", "-c", "user.email=n58@example.com", "commit", "-m", "synthetic staging fixture")
    def run(name):
        return subprocess.run([sys.executable, str(stage), "api", str(tmp_path / name)], capture_output=True, text=True)
    ok = run("valid")
    assert ok.returncode == 0, ok.stderr
    assert (tmp_path / "valid/evidence/S13l/reconstruct/bundle" / archive.name).read_bytes() == archive.read_bytes()
    archive.write_bytes(b"changed")
    bad = run("bad-hash")
    assert bad.returncode != 0 and "sha256" in bad.stderr
    assert not (tmp_path / "bad-hash").exists()
    archive.unlink()
    missing = run("missing")
    assert missing.returncode != 0 and "Required public RM04 sample asset missing" in missing.stderr
    assert not (tmp_path / "missing").exists()
