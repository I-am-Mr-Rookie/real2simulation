"""Loopback public RM02 comparison, original committed loader versus working-tree loader."""
import hashlib
import json
import mimetypes
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = Path("C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon")
N80 = Path("C:/Users/HP/.codex/worktrees/n80-orch325/2026-10-26 - Meta Global AI Developer Hackathon/evidence/N80/after.local")
PACKS = {"n75": CANONICAL / "evidence/S13l/reconstruct/bundle", "n80": N80}
THREE = CANONICAL / "Build/web/node_modules/three"
BASE = "4eaf48583c2eeca2811309ca4a11cb7dd9f12759"
OLD = subprocess.check_output(["git", "show", BASE + ":Build/web/src/lab-editor/sf3d-shape.mjs"], cwd=ROOT)
ALLOWED = {"RM02-sample-scene.json", *(f"RM02-room-object-{i}.glb" for i in (1, 2, 4, 7))}


def asset(url):
    path = unquote(urlsplit(url).path)
    if path == "/":
        return ROOT / "evidence/N81/compare.html"
    if path == "/sf3d-shape.mjs":
        return ROOT / "Build/web/src/lab-editor/sf3d-shape.mjs"
    if path.startswith("/three/"):
        target = (THREE / path[7:]).resolve()
        return target if target.is_relative_to(THREE.resolve()) and target.is_file() else None
    parts = path.split("/")
    if len(parts) == 4 and parts[1] == "assets" and parts[2] in PACKS and parts[3] in ALLOWED:
        return PACKS[parts[2]] / parts[3]
    return None


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        target = asset(self.path)
        if self.path == "/before-shape.mjs":
            raw, mime = OLD, "text/javascript"
        elif target is not None and target.is_file():
            raw = target.read_bytes()
            mime = "text/javascript" if target.suffix in (".js", ".mjs") else mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


if __name__ == "__main__":
    assert asset("/.env") is None and asset("/assets/n75/../../.env") is None
    for pack, base in PACKS.items():
        manifest = json.loads((ROOT / "evidence/N75/bundle-manifest.json" if pack == "n75" else N80 / "bundle-manifest.json").read_text())
        assert all(hashlib.sha256((base / name).read_bytes()).hexdigest() == manifest["files"][name]["sha256"] for name in ALLOWED)
    print("http://localhost:8087", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8087), Handler).serve_forever()
