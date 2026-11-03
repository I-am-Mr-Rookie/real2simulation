"""Loopback read-only comparison, restricted public RM02 assets and installed Three.js."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
import mimetypes

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence/N80"
THREE = Path("C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/Build/web/node_modules/three")


def asset(url):
    path = unquote(urlsplit(url).path)
    if path == "/":
        return OUT / "compare.html"
    if path == "/sf3d-shape.mjs":
        return ROOT / "Build/web/src/lab-editor/sf3d-shape.mjs"
    if path.startswith("/three/"):
        base, tail = THREE, path[7:]
    elif path.startswith("/assets/before/"):
        base, tail = OUT / "before.local", path[15:]
    elif path.startswith("/assets/after/"):
        base, tail = OUT / "after.local", path[14:]
    else:
        return None
    target = (base / tail).resolve()
    return target if target.is_relative_to(base.resolve()) and target.is_file() else None


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        target = asset(self.path)
        if target is None or not target.is_file():
            self.send_error(404)
            return
        raw = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/javascript" if target.suffix in (".js", ".mjs") else mimetypes.guess_type(target.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


if __name__ == "__main__":
    assert asset("/assets/after/../../spend.json") is None
    assert asset("/.env") is None
    print("Public RM02 comparison: http://localhost:8080", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8080), Handler).serve_forever()
