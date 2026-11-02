"""Isolated local verification server. No provider credentials, no paid routers, only public sample and CPU fit."""
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from fastapi import FastAPI
from Build.api.storage import Store, create_router, sample
from Build.api import room, experiment
from Build.api.room.objects import create_router as object_router
from Build.api.workspace.analysis import create_router as analysis_router

os.environ["WORKSPACE_INTERNAL_TOKEN"] = "n58-local-public-only"
store = Store(ROOT / "evidence/N58/local-data")
# Share only the canonical public, hash-verified bytes. Never discover or load owner recordings.
sample.BUNDLE = ROOT.parents[1] / "evidence/S13l/reconstruct/bundle"
if not sample.BUNDLE.is_dir():
    raise RuntimeError("canonical public RM04 sample bundle missing")
sample.seed(store, "n58_public")
app = FastAPI()
app.include_router(create_router(store))
app.include_router(room.create_router(store, remote=lambda *a: None))
app.include_router(object_router(store, segment=lambda *a: (_ for _ in ()).throw(RuntimeError("paid work disabled in local verification"))))
app.include_router(experiment.create_router(store))
app.include_router(analysis_router(lambda *a: None))

@app.get("/internal/workspace/health")
def health():
    return {"status": "ok"}

@app.get("/internal/workspace/gpu/status")
def gpu():
    return {"state": "red", "queue_length": 0, "source": "local fixture, no GPU used"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=18558)
