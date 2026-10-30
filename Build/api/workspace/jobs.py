"""S13i: owner-scoped resumable upload + job status/progress routes with a RECORDED-replay executor (S15m §2).

Reuses UploadService (S13b), JobRunner/MemoryStore (S13d), progress (S13g), require_owner (S14i) and the
S02 approval/registry readers (score.approved). Uploads are accepted only for a sha256 of an owner-approved,
clips.csv-listed clip. The only executor replays evidence/S13/S13h (labelled RECORDED, original UTC
timestamps): it never imports modal/boto3, launches a process, spends or calls Meta. Not mounted here (S04m).
"""
import csv
import functools
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

from typing import Any

from fastapi import APIRouter, Body, Depends, Query, Request

from Build.api.workspace.auth import error, require_owner
from Build.pipeline.contracts import STAGES
from Build.pipeline.jobs import JobRunner, MemoryStore, StageError, _now
from Build.pipeline.uploads import UploadError, UploadService
from Build.real2sim.score import APPROVAL, REGISTRY, approved

ROOT = Path(__file__).resolve().parents[3]
RECORDING = ROOT / "evidence/S13/S13h/live"
LABEL = "RECORDED S13h-orch46"
_JOB = re.compile(r"job_[0-9a-f]{32}")
# S13h stage name -> (contract stage, result key holding that stage's output sha256). keyframes: manifest bytes.
_OUT = {"validate": ("validate", "sha256"), "keyframes": ("keyframes", None), "segment": ("segment", "segmentation_sha256"),
        "reconstruct": ("reconstruct", "reconstruction_sha256"), "viewable": ("package", "scene_sha256")}


@functools.cache
def approved_shas(root=ROOT):
    """{sha256: clip_id} for clips.csv rows that the S02 owner grant approves; hashes come from the tracked registry."""
    with open(root / "clips.csv", encoding="utf-8", newline="") as f:
        listed = {r["clip_id"] for r in csv.DictReader(f)}
    grant = (root / APPROVAL).read_text(encoding="utf-8")
    files = json.loads((root / REGISTRY).read_text(encoding="utf-8"))["files"]
    return {e["sha256"]: e["clip_id"] for e in files
            if e.get("clip_id") in listed and approved(e["clip_id"], grant) and re.fullmatch(r"[0-9a-f]{64}", e.get("sha256", ""))}


def load_recording(input_sha256, rec=RECORDING):
    """{contract stage: (started_at, ended_at, output_sha256)} for the recorded run of this exact input, else {}."""
    try:
        timing = json.loads((rec / "timing.json").read_text(encoding="utf-8"))
        stages = {s["stage"]: s for s in timing["stages"] if s.get("error") is None}
        if stages["validate"]["result"]["sha256"] != input_sha256:
            return {}
        out = {}
        for name, (stage, key) in _OUT.items():
            s = stages.get(name)
            if s is None:
                continue
            sha = (s["result"][key] if key else hashlib.sha256((rec / "keyframes/manifest.json").read_bytes()).hexdigest())
            out[stage] = tuple(t.replace("+00:00", "Z") for t in (s["started_at"], s["ended_at"])) + (sha,)
        return out
    except (OSError, KeyError, TypeError, ValueError):
        return {}  # unreadable recording == no recording


def recorded_runner(store, input_sha256, rec=RECORDING):
    """JobRunner whose workers return recorded outputs and whose clock replays the recorded UTC times.

    A stage absent from the recording fails DEPENDENCY_UNAVAILABLE (never retried); events from that point carry
    the actual replay time. S13h did not run understand, so an RM04 replay stops there (no invented output).
    """
    rec_stages = load_recording(input_sha256, rec)
    times = []
    for stage in STAGES:  # JobRunner emits started+succeeded per stage, in STAGES order
        if stage not in rec_stages:
            break
        times += rec_stages[stage][:2]
    clock = iter(times)

    def worker(stage):
        def run(key):
            if stage not in rec_stages:
                why = "no recording for this input" if not rec_stages else f"{stage} was not run in {LABEL}"
                raise StageError("DEPENDENCY_UNAVAILABLE", f"{why}; live execution is not enabled", False)
            return rec_stages[stage][2]
        return run

    runner = JobRunner(store, {s: worker(s) for s in STAGES}, sleep=lambda s: None, now=lambda: next(clock, None) or _now())
    provenance = {"executor": "recorded", "label": LABEL, "live": False,
                  "recorded_stages": [s for s in STAGES if s in rec_stages],
                  "note": "replay of recorded S13h events with their original UTC timestamps; not a live run"}
    return runner, provenance


def default_store():
    url = os.environ.get("REDIS_URL")
    if not url:
        # shortcut: per-process memory, lost on restart; S04m sets REDIS_URL for the dev API.
        return MemoryStore()
    import redis  # redis-py; added to the API image by S04m
    return redis.Redis.from_url(url, decode_responses=True)


def _upload_error(exc: UploadError):
    if exc.code in ("UNAUTHORIZED", "NOT_FOUND"):  # other owners' uploads are indistinguishable from missing ones
        return error(404, "NOT_FOUND", "upload not found")
    return error(422, exc.code, str(exc), decision=exc.decision, committed_bytes=exc.committed_bytes)


def create_router(store=None, uploads=None, shas=None, recording=RECORDING) -> APIRouter:
    store = store if store is not None else default_store()
    uploads = uploads or UploadService(os.environ.get("WORKSPACE_UPLOAD_DIR") or Path(tempfile.gettempdir()) / "r2s-uploads")
    shas = approved_shas if shas is None else shas
    router = APIRouter(prefix="/internal/workspace", dependencies=[Depends(require_owner)])

    def call(fn, *args):
        try:
            return fn(*args)
        except UploadError as exc:
            raise _upload_error(exc) from None

    def owned(owner, job_id):
        if not _JOB.fullmatch(job_id) or store.get(f"job:{job_id}:owner") != owner:
            raise error(404, "NOT_FOUND", "job not found")
        return json.loads(store.get(f"job:{job_id}:provenance"))

    @router.post("/uploads")
    def create(body: Any = Body(...), owner: str = Depends(require_owner)):
        sha = body.get("sha256") if isinstance(body, dict) else None
        if not isinstance(sha, str) or sha not in shas():
            raise error(422, "INVALID_INPUT", "sha256 is not an owner-approved clips.csv clip")
        return call(uploads.create, owner, body.get("media_type"), body.get("size_bytes"), sha)

    @router.get("/uploads/{upload_id}")
    def resume(upload_id: str, owner: str = Depends(require_owner)):
        return call(uploads.get, owner, upload_id)  # client continues at committed_bytes

    @router.put("/uploads/{upload_id}/chunks/{offset}")
    async def chunk(upload_id: str, offset: int, request: Request, owner: str = Depends(require_owner)):
        return call(uploads.put_chunk, owner, upload_id, offset, await request.body())

    @router.post("/uploads/{upload_id}/complete")
    def complete(upload_id: str, owner: str = Depends(require_owner)):
        session = call(uploads.complete, owner, upload_id)
        job_id = session["job_id"]
        runner, prov = recorded_runner(store, session["sha256"], recording)
        store.set(f"job:{job_id}:provenance", json.dumps(prov))
        store.set(f"job:{job_id}:owner", owner)  # last: owned() never sees an owner without provenance
        # shortcut: replay runs inline (instant, no I/O beyond the store); a live executor needs a queue worker.
        return {"upload": session, "job": runner.run(job_id, session["sha256"]), "provenance": prov}

    @router.get("/jobs/{job_id}")
    def job(job_id: str, after: int = Query(0, ge=0), owner: str = Depends(require_owner)):
        prov = owned(owner, job_id)
        return {**JobRunner(store, {}).progress(job_id, after), "provenance": prov}

    return router

