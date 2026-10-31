"""S13i: owner-scoped resumable upload + job status/progress routes with a RECORDED-replay executor (S15m §2).

Reuses UploadService (S13b), JobRunner/MemoryStore (S13d), progress (S13g), require_owner (S14i) and the
S02 approval/registry readers (score.approved). Uploads are accepted only for a sha256 of an owner-approved,
clips.csv-listed clip. The only executor replays evidence/S13/S13h (labelled RECORDED, original UTC
timestamps) plus, for understand, the accepted S14g-fix3 spec (S13k): it never imports modal/boto3, launches a
process, spends or calls Meta. Not mounted here (S04m mounts this and analysis.create_router(scene_resolver(store))).
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

from fastapi import APIRouter, Body, Depends, Query, Request, Response

from Build.api.workspace.auth import error, require_owner
from Build.pipeline.contracts import STAGES
from Build.pipeline.jobs import JobRunner, MemoryStore, StageError, _now
from Build.pipeline.uploads import UploadError, UploadService
from Build.real2sim.score import APPROVAL, REGISTRY, approved

ROOT = Path(__file__).resolve().parents[3]
RECORDING = ROOT / "evidence/S13/S13h/live"
LABEL = "RECORDED S13h-orch46"
# S13h never ran understand: that stage replays the accepted live S14g-fix3 Muse spec for the same input (S13k).
UNDERSTOOD = ROOT / "evidence/S14/S14g-fix3-live.json"
UNDERSTAND_LABEL = "RECORDED S14g-fix3"
_JOB = re.compile(r"job_[0-9a-f]{32}")
# S13h stage name -> (contract stage, result key holding that stage's output sha256). keyframes: manifest bytes.
_OUT = {"validate": ("validate", "sha256"), "keyframes": ("keyframes", None), "segment": ("segment", "segmentation_sha256"),
        "reconstruct": ("reconstruct", "reconstruction_sha256"), "viewable": ("package", "scene_sha256")}
# S15v: owner phone clips (OWNER_RECORDED, PRIVATE_PROCESSING_ONLY in clips.csv). Hashes + the stored S07i result are a
# tracked copy (the API image ships Build/, not evidence/S07); tests/api-workspace re-derives it from the evidence files.
OWNER_CLIPS = Path(__file__).with_name("owner_clips.json")
# S15az (Gate D D6): the stored 0.2028 m is the owner's earlier declaration, not this user's answer.
SCALE_LABEL = "owner-declared scale (recorded), not verified"
# S15y: owner clips have no recording and live execution is off, so no stage runs; that is a no-scene state, not a failure.
NO_SCENE = "no scene: owner clip, scene reconstruction not run"
# S13m: RM04 MapAnything display bundle (S13l). Bytes never enter Git; stage.py bakes them into the API image at this
# same relative path when present. WORKSPACE_SCENE_DIR overrides; served only if sha256 equals the recorded manifest.
SCENE_DIR = ROOT / "evidence/S13l/reconstruct/bundle"
BUNDLE_MANIFEST = ROOT / "Build/pipeline/recorded/RM04-S13l-mapanything.json"
BUNDLE_FILES = ("scene.json", "points.ply", "points-mobile.ply")


def owner_job(job_id):
    """Non-failure job state for an owner clip (deliberately NOT the shell job DTO: there is no scene artifact)."""
    return {"job_id": job_id, "status": "no_scene", "label": NO_SCENE}


@functools.cache
def owner_clips(root=ROOT):
    """{sha256: clip_id} for 30 fps clips.csv rows with status OWNER_RECORDED and a PRIVATE_PROCESSING_ONLY owner grant."""
    with open(root / "clips.csv", encoding="utf-8", newline="") as f:
        rows = {r["clip_id"]: r for r in csv.DictReader(f)
                if r["status"] == "OWNER_RECORDED" and r["owner_approved"].startswith("PRIVATE_PROCESSING_ONLY")
                and r["file_fps"] == "30/1"}
    clips = json.loads(OWNER_CLIPS.read_text(encoding="utf-8"))["clips"]
    return {e["sha256"]: c for c, e in clips.items() if c in rows and re.fullmatch(r"[0-9a-f]{64}", e.get("sha256", ""))}


def owner_measurement(clip_id):
    """Job result for an owner clip: stored frozen-v1 MEASURED g ± u + S07m v3 verdict as a RECORDED replay, else an explicit abstain."""
    e = json.loads(OWNER_CLIPS.read_text(encoding="utf-8"))["clips"].get(clip_id, {})
    base = {"clip_id": clip_id, "input_label": "OWNER_RECORDED / RECORDED",
            "scale": {"reference": e.get("scale_reference"), "value_m": e.get("scale_value_m"), "label": SCALE_LABEL,
                      "reference_px": e.get("scale_reference_px"), "reference_px_source": e.get("scale_reference_px_source")}}
    m = e.get("measurement")
    if not m:
        return {**base, "status": "abstain", "label": "UNCERTAIN: no measurement",
                "message": f"No stored measurement for this clip ({e.get('abstain', 'no v1 result')}); tracking does not run in "
                           "the product yet; g is not reported (abstain, not an error)."}
    series = {"series": e["series"]} if "series" in e else {}  # S15aw: frozen per-frame chart data (additive field)
    return {**base, "status": "recorded", "label": "RECORDED replay of a MEASURED result", **m,
            "measured_label": m["measured_label"].replace("user-declared scale", "owner-declared scale (recorded)"),
            "caveat": owner_caveat(m, e.get("scale_value_m")), **series}


def owner_caveat(m, scale_m):
    """S15aa: one caveat for every stored owner result, from the S07m v3 verdict (replaces the miscalibrated S07h 6 px rule)."""
    v = m["v3"]
    tail = ("A PASS is conditional on these assumptions and is not accuracy: it can still sit far from the local 9.79 m/s^2."
            if v["verdict"] == "PASS" else "A MEASURED value with a failed held-out check, not a validated measurement.")
    return (f"Held-out check {v['verdict']}: chi2/dof = {v['chi2']}/{v['dof']} = {v['chi2_per_dof']}, p = {v['p']} "
            "(S07m v3 predictive chi-square; a THIRD, post-hoc analysis chosen after v1/v2 failed, forking-paths caveat). "
            f"Scale owner-declared (recorded) ({scale_m} m, not verified); phone clock not externally verified. {tail}")


@functools.cache
def approved_shas(root=ROOT):
    """{sha256: clip_id} for clips.csv rows that the S02 owner grant approves (tracked registry hashes) + owner_clips()."""
    with open(root / "clips.csv", encoding="utf-8", newline="") as f:
        listed = {r["clip_id"] for r in csv.DictReader(f)}
    grant = (root / APPROVAL).read_text(encoding="utf-8")
    files = json.loads((root / REGISTRY).read_text(encoding="utf-8"))["files"]
    return {e["sha256"]: e["clip_id"] for e in files
            if e.get("clip_id") in listed and approved(e["clip_id"], grant) and re.fullmatch(r"[0-9a-f]{64}", e.get("sha256", ""))
            } | owner_clips(root)


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


def load_understanding(input_sha256, path=UNDERSTOOD):
    """(spec record, ledger utc | None) for the single valid recorded spec of this exact input, else None.

    utc comes from the sibling ledger's one `spec-<case_id>` call; ambiguous or absent -> None (time not recorded).
    """
    try:
        found = [s for s in json.loads(path.read_text(encoding="utf-8"))["specs"]
                 if s.get("source_sha256") == input_sha256 and s.get("valid") is True and isinstance(s.get("spec"), dict)]
        if len(found) != 1:
            return None
        ledger = path.with_name(path.name.replace("-live.json", "-ledger.jsonl"))
        call = f"spec-{found[0]['case_id']}"
        utcs = [r["utc"] for r in map(json.loads, ledger.read_text(encoding="utf-8").splitlines() if ledger.exists() else [])
                if r.get("call") == call and r.get("http") == 200]
        return found[0], (utcs[0].replace("+00:00", "Z") if len(utcs) == 1 else None)
    except (OSError, KeyError, TypeError, ValueError):
        return None


def recorded_runner(store, input_sha256, rec=RECORDING, understood=UNDERSTOOD):
    """JobRunner whose workers return recorded outputs and whose clock replays the recorded UTC times.

    A stage absent from the recording fails DEPENDENCY_UNAVAILABLE (never retried); events from that point carry
    the actual replay time. understand (not run in S13h) replays the S14g-fix3 spec for the same input, if any;
    its output_sha256 is sha256 of the recorded accepted model text. Without one the replay stops there.
    """
    rec_stages = load_recording(input_sha256, rec)
    labels = {s: LABEL for s in rec_stages}
    understanding = load_understanding(input_sha256, understood) if rec_stages and "understand" not in rec_stages else None
    if understanding:
        spec, utc = understanding
        sha = hashlib.sha256(spec["accepted_text"].encode("utf-8")).hexdigest()
        rec_stages["understand"], labels["understand"] = (utc, utc, sha), UNDERSTAND_LABEL
    times = []
    for stage in STAGES:  # JobRunner emits started+succeeded per stage, in STAGES order
        if stage not in rec_stages:
            break
        times += rec_stages[stage][:2]  # None (time not recorded) -> actual replay time
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
                  "stage_labels": {s: labels[s] for s in STAGES if s in labels},
                  "note": "replay of recorded S13h events with their original UTC timestamps; not a live run"}
    if understanding:
        provenance["understand"] = {"label": UNDERSTAND_LABEL, "live": False, "case_id": spec["case_id"],
                                    "source": understood.name, "call": f"spec-{spec['case_id']}",
                                    "recorded_utc": utc or "time not recorded"}
    return runner, provenance


def shell_scene(job_id):
    """S04g shell scene for a ready replayed job; scene_id is the job_id, which scene_resolver accepts."""
    return {"scene_id": job_id, "scene_version": "1.0.0", "access": "private", "evidence": "reconstructed"}


def scene_resolver(store, understood=UNDERSTOOD):
    """analysis.SceneResolver: scene_id = a READY job owned by owner -> (recorded base_spec, scene_context, root).

    The recorded scene_context is not an authoritative bundle, so /spec reports that as 422 (never a default).
    """
    def resolve(owner, scene_id):
        if not _JOB.fullmatch(scene_id) or store.get(f"job:{scene_id}:owner") != owner:
            return None
        prov = json.loads(store.get(f"job:{scene_id}:provenance") or "{}")
        if prov.get("executor") == "none":  # S15y owner clip: no base spec or scene; analysis asks scene-free questions
            return {"owner_clip": prov.get("measurement")}, None, None
        if JobRunner(store, {}).progress(scene_id, 0, shell_scene(scene_id))["job"]["status"] != "ready":
            return None
        found = load_understanding(store.get(f"job:{scene_id}:input"), understood)
        return (found[0]["spec"], found[0]["scene_context"], ROOT) if found else None
    return resolve


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


def create_router(store=None, uploads=None, shas=None, recording=RECORDING, understood=UNDERSTOOD, owners=owner_clips,
                  scene_dir=None) -> APIRouter:
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
        clip = owners().get(session["sha256"])
        if clip is not None:  # S15v/S15y: no in-product tracking and no scene; replay the stored result or abstain
            prov = {"executor": "none", "label": NO_SCENE, "live": False, "recorded_stages": [], "stage_labels": {},
                    "note": "Track: RECORDED (precomputed SAM 3.1, not run live); no scene is reconstructed. "
                            "The fit runs on the server after your known-size answer. Nothing failed.",
                    "measurement": owner_measurement(clip)}
        else:
            runner, prov = recorded_runner(store, session["sha256"], recording, understood)
        store.set(f"job:{job_id}:provenance", json.dumps(prov))
        store.set(f"job:{job_id}:input", session["sha256"])
        store.set(f"job:{job_id}:owner", owner)  # last: owned() never sees an owner without provenance
        if clip is not None:
            return {"upload": session, "job": owner_job(job_id), "provenance": prov}
        # shortcut: replay runs inline (instant, no I/O beyond the store); a live executor needs a queue worker.
        return {"upload": session, "job": runner.run(job_id, session["sha256"], shell_scene(job_id)), "provenance": prov}

    @router.get("/jobs/{job_id}")
    def job(job_id: str, after: int = Query(0, ge=0), owner: str = Depends(require_owner)):
        prov = owned(owner, job_id)
        if prov.get("executor") == "none":
            return {"kind": "job_progress", "job_id": job_id, "events": [], "job": owner_job(job_id), "provenance": prov}
        return {**JobRunner(store, {}).progress(job_id, after, shell_scene(job_id)), "provenance": prov}

    @router.get("/scenes/{job_id}/bundle/{name}")
    def bundle(job_id: str, name: str, owner: str = Depends(require_owner)):
        """S13m: RM04 display-only geometry for a READY recorded job of the approved RM04 clip (scale unverified)."""
        prov = owned(owner, job_id)
        if (name not in BUNDLE_FILES or prov.get("executor") != "recorded"
                or shas().get(store.get(f"job:{job_id}:input")) != "RM04"
                or JobRunner(store, {}).progress(job_id, 0, shell_scene(job_id))["job"]["status"] != "ready"):
            raise error(404, "NOT_FOUND", "scene bundle file not found")
        try:
            want = json.loads(BUNDLE_MANIFEST.read_text(encoding="utf-8"))["files"][name]["sha256"]
            data = (Path(scene_dir or os.environ.get("WORKSPACE_SCENE_DIR") or SCENE_DIR) / name).read_bytes()
        except (OSError, KeyError, TypeError, ValueError):
            raise error(503, "DEPENDENCY_UNAVAILABLE", "scene bundle is not available on this server") from None
        if hashlib.sha256(data).hexdigest() != want:
            raise error(503, "DEPENDENCY_UNAVAILABLE", "scene bundle failed its sha256 check")
        if name == "scene.json":  # verified bytes, re-bound to this job: the viewer gate requires manifest id == scene_id
            data = json.dumps({**json.loads(data), "id": job_id}, indent=1).encode("utf-8")
        return Response(data, media_type="application/json" if name == "scene.json" else "application/octet-stream",
                        headers={"cache-control": "no-store", "x-r2s-source-sha256": want})

    return router

