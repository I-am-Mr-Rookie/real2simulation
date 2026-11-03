"""Loopback synthetic workspace fixture. Real storage/room APIs; allowlisted UI GET and room DELETE only."""
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from fastapi import FastAPI
from fastapi.testclient import TestClient
from Build.api.room import create_router as room_router
from Build.api.storage import Store, create_router as storage_router

OWNER, TOKEN = "user_n82_synthetic", "n82-synthetic-local-token"
os.environ["WORKSPACE_INTERNAL_TOKEN"] = TOKEN
store = Store(ROOT / "evidence/N82/qa-data.local")
app = FastAPI()
app.include_router(storage_router(store))
app.include_router(room_router(store, remote=lambda _: None, stats=lambda: None))
client = TestClient(app)
names = [("a", "N82 desktop room"), ("b", "N82 phone room"), ("c", "N82 busy room"),
         ("d", "SAMPLE (RECORDED): synthetic kept"), ("e", "N82 retained room")]
for key, title in names:
    rid = key * 32
    store.db.execute("INSERT OR IGNORE INTO projects VALUES (?,?,?,?,?)", (rid, OWNER, "room", title, "2026-11-03T02:27:14Z"))
    d = store.root / "rooms" / OWNER / rid
    if d.exists():
        continue
    (d / "objects").mkdir(parents=True)
    for name, data in {"status.json": {"job_id": rid, "state": "queued" if key == "c" else "done", "project_id": rid, "sample": key == "d"},
                       "room.json": {"shell": {"kept": []}}, "scene.json": {"objects": ["synthetic saved edits"]}}.items():
        (d / name).write_text(json.dumps(data))
    (d / "mapanything.npz").write_bytes(b"synthetic archive\n" * 32768)
    (d / "objects/shape.glb").write_bytes(b"synthetic mesh")
if not store.list(OWNER):
    tmp = store.root / "tmp/video"
    tmp.write_bytes(b"synthetic uploaded video kept")
    store.add(OWNER, "original-video.mp4", "application/octet-stream", tmp, None)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, code, raw, mime="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path in ("/", "/workspace"):
            self.send(200, b'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>N82 local QA</title><link rel="stylesheet" href="/workspace.css"><style>body{margin:0;font:16px system-ui;background:#faf9f6;color:#242424}header,footer{padding:16px;max-width:1080px;margin:auto}header h1{font-size:20px}header p{font-size:13px}button{font:inherit;cursor:pointer}footer{max-width:300px;margin-left:16px}</style><div id="root"></div><script src="/qa.js"></script></html>', "text/html")
        elif self.path in ("/workspace.css", "/qa.js"):
            p = ROOT / ("Build/web/src/workspace/workspace.css" if self.path.endswith("css") else "evidence/N82/harness.local/qa.js")
            self.send(200, p.read_bytes(), "text/css" if self.path.endswith("css") else "text/javascript")
        elif self.path == "/api/workspace/gpu/status":
            self.send(200, b'{"state":"red","queue_length":0,"your_position":null}')
        elif self.path == "/api/workspace/experiments":
            self.send(200, b'{"experiments":[]}')
        elif self.path in ("/api/workspace/projects", "/api/workspace/files", "/api/workspace/rooms"):
            self.proxy("GET")
        else:
            self.send_error(404)

    def do_DELETE(self):
        if not re.fullmatch(r"/api/workspace/rooms/[a-e]{32}", self.path):
            self.send_error(405)
            return
        self.proxy("DELETE")

    def proxy(self, method):
        response = client.request(method, self.path.replace("/api/workspace/", "/internal/workspace/", 1),
                                  headers={"x-workspace-token": TOKEN, "x-workspace-owner": OWNER})
        if method == "DELETE":
            with (ROOT / "evidence/N82/local-deletes.jsonl").open("a", encoding="utf-8") as log:
                log.write(json.dumps({"method": method, "path": self.path, "status": response.status_code, "body": response.json()}) + "\n")
        self.send(response.status_code, response.content)


if __name__ == "__main__":
    assert all(re.fullmatch(r"[a-e]{32}", k * 32) for k, _ in names)
    print("http://localhost:8088", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8088), Handler).serve_forever()
