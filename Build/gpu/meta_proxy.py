"""N23 Plan B: US egress for Meta Model API calls (Railway egress gets an empty model list in every region).

Passthrough only: forwards /v1/<path> to api.meta.ai with the caller's own Authorization header; the daily cap
stays on the api side. Callers must send X-R2S-Proxy = MODEL_PROXY_TOKEN (shared secret, compared in constant time).
Deploy: MODEL_PROXY_TOKEN in the env (from .env), then
  uv run --python 3.12 --with modal==1.6.3 --env-file .env modal deploy Build/gpu/meta_proxy.py
Point the api at it with MODEL_API_BASE_URL=<printed url>/v1 and the same MODEL_PROXY_TOKEN.
"""
import os

import modal

UPSTREAM = "https://api.meta.ai"
app = modal.App("r2s-meta-proxy")
image = modal.Image.debian_slim(python_version="3.12").pip_install("fastapi[standard]==0.115.12")


@app.function(image=image, region="us-east", cpu=0.25, memory=256, timeout=900, scaledown_window=300,
              secrets=[modal.Secret.from_dict({"MODEL_PROXY_TOKEN": os.environ.get("MODEL_PROXY_TOKEN", "")})])
@modal.concurrent(max_inputs=20)
@modal.asgi_app()
def web():
    import hmac
    from urllib.error import HTTPError
    from urllib.request import Request as Out, urlopen

    from fastapi import FastAPI, Request
    from fastapi.concurrency import run_in_threadpool
    from fastapi.responses import Response

    api = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    token = os.environ["MODEL_PROXY_TOKEN"]
    assert len(token) >= 32, "MODEL_PROXY_TOKEN missing or short"

    def send(method, url, body, headers):
        try:
            with urlopen(Out(url, data=body, method=method, headers=headers), timeout=890) as r:
                return r.status, r.read(), r.headers.get("content-type", "application/json")
        except HTTPError as e:
            return e.code, e.read(), e.headers.get("content-type", "application/json")

    @api.api_route("/v1/{path:path}", methods=["GET", "POST"])
    async def forward(path: str, request: Request):
        if not hmac.compare_digest(request.headers.get("x-r2s-proxy", ""), token):
            return Response(status_code=403)
        headers = {k: v for k, v in request.headers.items() if k in ("authorization", "content-type")}
        query = f"?{request.url.query}" if request.url.query else ""
        body = await request.body() if request.method == "POST" else None
        status, data, ctype = await run_in_threadpool(send, request.method, f"{UPSTREAM}/v1/{path}{query}", body, headers)
        return Response(content=data, status_code=status, media_type=ctype)

    return api
