"""Generate a new event-only upload context from committed allowlisted sources."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
service, destination = sys.argv[1:]
assert service in {"web", "api", "worker"}
target = Path(destination).resolve()
assert not target.exists(), "Use a fresh staging destination"
revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
prefixes = {
    "web": ("Build/web/src/", "Build/web/package.json"),
    "api": ("Build/api/health/",),
    "worker": ("Build/worker/health/", "Build/api/health/dependencies.py"),
}[service]
files = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", revision], cwd=root, text=True).splitlines()
selected = [p for p in files if any(p.startswith(x) if x.endswith("/") else p == x for x in prefixes)]
dockerfile = f"infra/railway/dev/{service}.Dockerfile"
assert selected and dockerfile in files
manifest = {"service": service, "source_revision": revision, "files": {}}
for source in selected + [dockerfile]:
    assert not any(x in Path(source).parts for x in ("archive", ".env", "node_modules", ".next", "__pycache__"))
    content = subprocess.check_output(["git", "show", f"{revision}:{source}"], cwd=root)
    name = "Dockerfile" if source == dockerfile else source
    if name == "Dockerfile":
        content = content.replace(b"ARG R2S_SOURCE_REVISION\n", f"ARG R2S_SOURCE_REVISION={revision}\n".encode())
    output = target / name
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(content)
    manifest["files"][name] = hashlib.sha256(content).hexdigest()
(target / "context-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"service": service, "source_revision": revision, "files": len(manifest["files"]), "destination": str(target)}))
