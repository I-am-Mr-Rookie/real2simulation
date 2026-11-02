"""Loopback GET-only adapter: real sample API + local Next build + read-only Files fixture.

No authentication bypass in the app, remote proxy, uploads, agent calls or build jobs.
Run Next on 3078, render-files.mjs, then this script with the approved public bundle path.
"""
import http.client
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from fastapi import FastAPI
from fastapi.testclient import TestClient
from Build.api import room
from Build.api.room.objects import create_router as object_router
from Build.api.storage import Store, create_router, sample

TOKEN, OWNER = "n78-synthetic-local-token", "user_n78_fixture"
os.environ["WORKSPACE_INTERNAL_TOKEN"] = TOKEN
sample.BUNDLE = Path(sys.argv[1])
store = Store(ROOT / "evidence/N78/qa.local")
sample.seed(store, OWNER)
app = FastAPI()
app.include_router(create_router(store))
app.include_router(room.create_router(store))
app.include_router(object_router(store))
client = TestClient(app)
room_id = next((store.root / "rooms" / OWNER).iterdir()).name


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/files-fixture":
            code, headers, data = 200, {"Content-Type": "text/html; charset=utf-8"}, (ROOT / "evidence/N78/files.local.html").read_bytes()
        elif self.path.startswith("/api/workspace/"):
            response = client.get("/internal/workspace/" + self.path[len("/api/workspace/"):],
                                  headers={"x-workspace-token": TOKEN, "x-workspace-owner": OWNER})
            code, headers, data = response.status_code, response.headers, response.content
        else:
            upstream = http.client.HTTPConnection("127.0.0.1", 3078, timeout=30)
            upstream.request("GET", self.path, headers={"Host": "localhost:8078"})
            response = upstream.getresponse()
            code, headers, data = response.status, dict(response.getheaders()), response.read()
            upstream.close()
        self.send_response(code)
        for key, value in headers.items():
            if key.lower() not in ("content-length", "transfer-encoding", "connection"):
                self.send_header(key, value)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


fixture = {"files": "http://localhost:8078/files-fixture", "lab": f"http://localhost:8078/lab?editor=1&room={room_id}"}
(ROOT / "evidence/N78/local-fixture.json").write_text(json.dumps(fixture, indent=2) + "\n")
print(json.dumps(fixture), flush=True)
ThreadingHTTPServer(("127.0.0.1", 8078), Handler).serve_forever()
