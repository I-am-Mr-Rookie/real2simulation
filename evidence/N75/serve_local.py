"""Loopback-only, GET-only QA fixture: real seed/storage/room routes + the local Next build.

Not a deployment/BFF/auth test. Never proxy uploads, agent turns, shell builds or other writes.
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

TOKEN, OWNER = "n75-synthetic-local-token", "user_n75_fixture"
os.environ["WORKSPACE_INTERNAL_TOKEN"] = TOKEN
sample.BUNDLE = Path(sys.argv[1])
store = Store(ROOT / "evidence/N75/qa.local")
sample.seed(store, OWNER)
app = FastAPI()
app.include_router(create_router(store))
app.include_router(room.create_router(store))
app.include_router(object_router(store))
client = TestClient(app)
d = next((store.root / "rooms" / OWNER).iterdir())
url = f"http://localhost:8075/lab?editor=1&room={d.name}"
(ROOT / "evidence/N75/local-fixture.json").write_text(json.dumps({"url": url, "room": d.name,
    "scope": "isolated synthetic owner, actual sample seed/API routes, local Next build, GET-only adapter"}, indent=2) + "\n")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path.startswith("/api/workspace/"):
            response = client.get("/internal/workspace/" + self.path[len("/api/workspace/"):],
                                  headers={"x-workspace-token": TOKEN, "x-workspace-owner": OWNER})
            code, headers, data = response.status_code, response.headers, response.content
            with (ROOT / "evidence/N75/requests.local.jsonl").open("a", encoding="utf-8") as log:
                log.write(json.dumps({"path": self.path, "status": code, "bytes": len(data)}) + "\n")
        else:
            upstream = http.client.HTTPConnection("127.0.0.1", 3075, timeout=30)
            upstream.request("GET", self.path, headers={"Host": "localhost:8075"})
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


print(url, flush=True)
ThreadingHTTPServer(("127.0.0.1", 8075), Handler).serve_forever()
