"""Fail-closed SAM 3.1 source/runtime preflight; never downloads or imports SAM."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import re
import subprocess
import sys
from pathlib import Path


MANIFEST = {
    "repository": "https://github.com/facebookresearch/sam3",
    "revision": "f1647e8d0c1d280991f4d1b7d974c2704537fe66",
    "files": {
        "pyproject.toml": "255f5d8d1db011459878e3de296a6afc84e03a8dda2bfa756a4de304aaff6366",
        "README.md": "da3dd047d18ef9a4b33557bf6f8187cf166218dc8aef40f2e18a67cc5249a502",
        "sam3/model_builder.py": "60cef72b1f7e4a2162d1c3f1ad2c0451bbbdc10e3484433a9aa2d016fed6b448",
        "sam3/__init__.py": "ca3821a125f767e6a35188603b51ef2501b1e7c3d1a90546ac567c5d2a80b9fb",
        "sam3/assets/bpe_simple_vocab_16e6.txt.gz": "924691ac288e54409236115652ad4aa250f48203de50a9e4722a6ecd48d6804a",
    },
    "requirements": {"python": ">=3.12", "torch": ">=2.7", "cuda": ">=12.6"},
    "builder": {"compile": False, "warm_up": False, "async_loading_frames": False,
                 "use_fa3": True, "use_rope_real": True},
    "build_system": ["setuptools>=61", "wheel"],
    "optional_kernels": ["flash-attn-3", "cc_torch"],
}


def _sha256(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_revision(root: Path) -> str | None:
    if root.is_symlink() or not root.is_dir():
        return None
    try:
        return subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def preflight(source: Path) -> dict:
    result = {"source": str(source), "manifest": MANIFEST, "checks": [],
              "source_ok": True, "dependency_ok": False, "runtime_ok": False}
    revision = _source_revision(source)
    result["checks"].append({"name": "git_revision", "expected": MANIFEST["revision"],
                              "observed": revision, "ok": revision == MANIFEST["revision"]})
    for relative, expected in MANIFEST["files"].items():
        path = source / relative
        observed = _sha256(path) if path.is_file() else None
        result["checks"].append({"name": f"sha256:{relative}", "expected": expected,
                                  "observed": observed, "ok": observed == expected})
    result["checks"].append({"name": "python", "expected": ">=3.12",
                              "observed": platform.python_version(),
                              "ok": sys.version_info >= (3, 12)})
    result["checks"].append({"name": "platform", "expected": "Linux x86_64",
                              "observed": f"{platform.system()} {platform.machine()}",
                              "ok": platform.system() == "Linux" and platform.machine().lower() in {"x86_64", "amd64"}})
    result["source_ok"] = all(check["ok"] for check in result["checks"])
    return result


def dependency_preflight(lock: Path) -> dict:
    """Compare installed distribution metadata to the exact generated lock.

    This deliberately uses importlib.metadata only: it does not import Torch,
    CUDA, SAM, or execute package code. CUDA/kernel availability stays unknown.
    """
    checks = []
    pattern = re.compile(r"^([A-Za-z0-9_.-]+)==([^ \\\n]+)")
    if not lock.is_file() or lock.is_symlink():
        return {"lock": str(lock), "checks": [], "dependency_ok": False}
    for line in lock.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        name, expected = match.groups()
        try:
            observed = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            observed = None
        checks.append({"name": name, "expected": expected, "observed": observed,
                       "ok": observed == expected})
    return {"lock": str(lock), "checks": checks,
            "dependency_ok": bool(checks) and all(item["ok"] for item in checks)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="checked-out SAM3 source directory")
    parser.add_argument("--json", action="store_true", help="emit machine-readable result")
    args = parser.parse_args()
    result = preflight(args.source.absolute())
    lock = Path(__file__).with_name("requirements-linux-py312.txt")
    result.update(dependency_preflight(lock))
    result["runtime_ok"] = False  # CUDA/SAM import and checkpoint remain intentionally unverified.
    result["ok"] = result["source_ok"] and result["dependency_ok"]
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else
          f"source_ok={result['source_ok']} dependency_ok={result['dependency_ok']} runtime_ok=false")
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
