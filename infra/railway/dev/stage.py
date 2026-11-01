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
# S13m: RM04 display bundle = gitignored local bytes (never in Git); baked into the api context only when present and
# sha-equal to the committed recorded manifest. Absent -> the API answers 503 DEPENDENCY_UNAVAILABLE.
BUNDLE, BUNDLE_MANIFEST = "evidence/S13l/reconstruct/bundle/", "Build/pipeline/recorded/RM04-S13l-mapanything.json"
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
            # N11 live product: on-demand Modal client, daily cap, hosted SAM, room pipeline, SAMPLE project result.
            "Build/gpu/", "Build/guardrails/", "Build/measurement/", "Build/reconstruction/", "evidence/N07/live-st03.json",
            "evidence/S05/upstream/revisions.json",  # N23: Build/gpu/image_spec.py reads it when a room job starts
            # Lab bridge and its transitive imports (rk4.mjs is listed below).
            *(f"Build/web/src/lab-editor/{m}.mjs" for m in ("agent-run", "scene", "physics", "frame")),
            "contracts/", "clips.csv", "evidence/owner/S02/APPROVAL.md", "evidence/clips/S02c-acquisition.json",
            "evidence/S13/S13h/live/", "evidence/S14/S14g-fix3-live.json", "evidence/S14/S14g-fix3-ledger.jsonl",
            # S15av lab bridge: Python setup/validation/instruments plus the Node simulator it spawns.
            "Build/lab/session-bridge.py", "Build/lab/regression.py", "Build/lab/simulate.mjs", "Build/templates/",
            "Build/instruments/", "Build/simulator/export_validated_setup.py", "test-data/synthetic/scene/room-v1/",
            *(f"Build/simulator/{m}.mjs" for m in ("trajectories", "extended-templates", "rk4"))),
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
bundle = {}
if service == "api" and BUNDLE_MANIFEST in files:
    recorded = json.loads(subprocess.check_output(["git", "show", f"{revision}:{BUNDLE_MANIFEST}"], cwd=root))["files"]
    bundle_root = root
    if not (root / BUNDLE).is_dir():
        # Worktrees share the canonical checkout's ignored, hash-verified display bundle.
        common = subprocess.check_output(["git", "rev-parse", "--git-common-dir"], cwd=root, text=True).strip()
        bundle_root = (root / common).resolve().parent
    for name, entry in recorded.items():
        if (bundle_root / BUNDLE / name).is_file():
            content = (bundle_root / BUNDLE / name).read_bytes()
            if hashlib.sha256(content).hexdigest() != entry["sha256"]:
                raise ValueError("RM04 bundle sha256 does not match the recorded manifest")
            bundle[BUNDLE + name] = content
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
for name, content in bundle.items():
    (target / name).parent.mkdir(parents=True, exist_ok=True)
    (target / name).write_bytes(content)
    manifest["files"][name] = hashlib.sha256(content).hexdigest()
(target / "context-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"service": service, "source_revision": revision, "files": len(manifest["files"]), "destination": str(target)}))
