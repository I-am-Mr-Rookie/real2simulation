"""Loopback-only browser harness for public data, never shipped or connected to DEV/owner data."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError


class LocalProxy(BaseHTTPRequestHandler):
    def do_GET(self):
        self.forward()

    do_POST = do_PUT = do_PATCH = do_DELETE = do_GET

    def forward(self):
        workspace = self.path.startswith("/api/workspace/")
        tail = self.path[len("/api/workspace"):] if workspace else self.path
        if workspace and tail == "/session":
            return self.respond(200, b'{"userKey":"n58-public-sample"}', "application/json")
        if workspace and tail.startswith("/agent/"):
            if tail == "/agent/lab/scene":
                return self.respond(200, b'{"scene":{"objects":[]}}', "application/json")
            if tail == "/agent/lab/report":
                return self.respond(200, b'{"markdown":""}', "application/json")
            return self.respond(503, b'{"detail":{"message":"Paid operation disabled in local verification."}}', "application/json")
        if workspace and self.command == "POST" and tail.split("?")[0].rsplit("/", 1)[-1] in {"rooms", "experiments", "objects", "shell"}:
            return self.respond(503, b'{"detail":{"message":"Paid operation disabled in local verification."}}', "application/json")
        base = "http://127.0.0.1:18558/internal/workspace" if workspace else "http://127.0.0.1:18559"
        headers = {"content-type": self.headers.get("content-type", "application/json")}
        if workspace:
            headers.update({"x-workspace-owner": "n58_public", "x-workspace-token": "n58-local-public-only"})
        data = self.rfile.read(int(self.headers.get("content-length", 0))) if self.command not in {"GET", "HEAD"} else None
        try:
            response = urlopen(Request(base + tail, data=data, headers=headers, method=self.command), timeout=90)
        except HTTPError as error:
            response = error
        with response:
            self.respond(response.status, response.read(), response.headers.get("content-type", "application/octet-stream"))

    def respond(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 18560), LocalProxy).serve_forever()
