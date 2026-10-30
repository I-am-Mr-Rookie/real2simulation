"""Generate a new event-only upload context from committed allowlisted sources."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
service, destination = sys.argv[1:]
SNAPSHOT = "Build/web/library-snapshot/guest.json"
# Same one-liner as Build/web/src/app/api/library/guest.mjs GUEST_SCRIPT (guest.py stays the only projection logic).
GUEST = ('import base64,json,sys;from Build.library.guest import load_guest;m,o=load_guest();'
         'sys.stdout.write(json.dumps({"manifest":m,"objects":{k:base64.b64encode(v).decode() for k,v in o.items()}}))')
if service not in {"web", "api", "worker"}:
    raise ValueError("Unknown staging service")
target = Path(destination).resolve()
if target.exists():
    raise FileExistsError("Use a fresh staging destination")
revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
prefixes = {
    # Web imports ../simulator and ../lab outside Build/web/src: stage only those exact modules.
    "web": ("Build/web/src/", "Build/web/public/", "Build/web/package.json", "Build/web/next.config.js", "Build/lab/session-service.mjs",
            "Build/library/loader.mjs",
            *(f"Build/simulator/{m}.mjs" for m in ("trajectories", "extended-templates", "mystery-g", "replay", "rk4"))),
    # Workspace routers import these packages and read the recorded S13h/S14g replay + clip approval at runtime.
    "api": ("Build/api/", "Build/agent/", "Build/fitter/", "Build/pipeline/", "Build/real2sim/", "Build/reports/",
            "contracts/", "clips.csv", "evidence/owner/S02/APPROVAL.md", "evidence/clips/S02c-acquisition.json",
            "evidence/S13/S13h/live/", "evidence/S14/S14g-fix3-live.json"),
    "worker": ("Build/worker/health/", "Build/api/health/dependencies.py"),
}[service]
files = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", revision], cwd=root, text=True).splitlines()
selected = [p for p in files if any(p.startswith(x) if x.endswith("/") else p == x for x in prefixes)]
dockerfile = f"infra/railway/dev/{service}.Dockerfile"
if not selected or dockerfile not in files:
    raise ValueError("Missing committed staging sources or Dockerfile")
for source in selected + [dockerfile]:
    if any(x in Path(source).parts for x in ("archive", ".env", "node_modules", ".next", "__pycache__")):
        raise ValueError("Forbidden staging source path")
snapshot = None
if service == "web":
    # load_guest reads the working tree: refuse tracked edits so the snapshot matches `revision` (raises on diff).
    subprocess.check_output(["git", "diff", "--quiet", "HEAD", "--", "Build", "test-data", "evidence"], cwd=root)
    snapshot = subprocess.check_output([sys.executable, "-B", "-c", GUEST], cwd=root)
    objects = json.loads(snapshot)["objects"]
    for key, value in objects.items():
        if hashlib.sha256(base64.b64decode(value, validate=True)).hexdigest() != key:
            raise ValueError("Guest snapshot object hash mismatch")
# Claim exclusively after validation: a competing creator must never be overwritten.
target.mkdir(parents=True, exist_ok=False)
manifest = {"service": service, "source_revision": revision, "files": {}}
for source in selected + [dockerfile]:
    content = subprocess.check_output(["git", "show", f"{revision}:{source}"], cwd=root)
    name = "Dockerfile" if source == dockerfile else source
    if name == "Dockerfile":
        content = content.replace(b"ARG R2S_SOURCE_REVISION\n", f"ARG R2S_SOURCE_REVISION={revision}\n".encode())
    output = target / name
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(content)
    manifest["files"][name] = hashlib.sha256(content).hexdigest()
if snapshot is not None:
    (target / SNAPSHOT).parent.mkdir(parents=True, exist_ok=True)
    (target / SNAPSHOT).write_bytes(snapshot)
    manifest["files"][SNAPSHOT] = hashlib.sha256(snapshot).hexdigest()
(target / "context-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"service": service, "source_revision": revision, "files": len(manifest["files"]), "destination": str(target)}))
