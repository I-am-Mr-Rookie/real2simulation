"""Isolated loopback QA fixture. Never mount this app in production; no real accounts, uploads or paid calls."""
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from Build.agent import core
from Build.api.agent import create_router
from Build.api.workspace.auth import require_owner

OUT = Path(__file__).resolve().parent / "runtime"
os.environ["R2S_DATA_DIR"] = str(OUT / "data")
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.dependency_overrides[require_owner] = lambda: "n71-synthetic"


def post(body):
    assert body["model"] in (core.MODEL, core.WONDER_MODEL)
    return {"output": [{"type": "message", "content": [{"type": "output_text",
            "text": "SIMULATED QA reply: ready to help with a physics experiment."}]}]}


app.include_router(create_router(post=post), prefix="/api")
# Exhaust only this synthetic owner's allowance through the actual server-side admission helper.
for _ in range(core.WONDER_DAILY_TURNS):
    core._claim_wonder_turn("n71-synthetic")


@app.get("/")
def index():
    return HTMLResponse('<!doctype html><html lang="en" data-theme="light" data-tone="light"><head>'
                        '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                        '<title>N71 local synthetic QA</title><link rel="icon" href="data:,"><link rel="stylesheet" href="/app.css"></head>'
                        '<body><main id="main"></main><script src="/bundle.js"></script></body></html>')


@app.get("/{asset}")
def asset(asset: str):
    if asset not in ("bundle.js", "app.css"):
        raise HTTPException(404)
    return FileResponse(OUT / asset)


@app.get("/api/workspace/files")
def files():
    return {"files": [], "quota": {"storage_bytes_used": 0, "storage_bytes_limit": 2 ** 30,
            "storage_bytes_remaining": 2 ** 30, "uploads_daily_limit": 20, "uploads_remaining_today": 20}}


@app.get("/api/workspace/gpu/status")
def gpu():
    return {"state": "red", "queue_length": 0}


@app.get("/api/workspace/{kind}")
def jobs(kind: str):
    if kind not in ("projects", "experiments", "rooms"):
        raise HTTPException(404)
    return {kind: []}
