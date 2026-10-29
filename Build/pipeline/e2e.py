"""S13h: time one approved clip through the dev upload-to-scene path, stage by stage, with UTC timestamps.

No HTTP upload/job route exists in Build/api or Build/web, so this drives the same pipeline modules directly:
upload (UploadService, policy chunk size; complete() verifies whole-file sha) -> validate (uploaded sha == the
clips.csv file for CLIP) -> keyframes -> segment (Modal SAM3.1) -> reconstruct (Modal MapAnything) -> viewable
(contracts/scene bundle validated by reconstruct). understand (Meta) is not run: no Meta spend in the S13h budget.
Writes timing.json after every stage; stops at the first failure (measured failure, never retried here).
python -m Build.pipeline.e2e CLIP FIRST LAST PROMPT OBJECT_ID RECONSTRUCT_MANIFEST OUT_DIR [CLIPS_CSV]
"""
import csv
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from Build.pipeline import gpu_stages, keyframes
from Build.pipeline.contracts import POLICY
from Build.pipeline.uploads import UploadService


def _utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def main(clip, first, last, prompt, oid, manifest, out, clips_csv):
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    with open(clips_csv, encoding="utf-8", newline="") as f:
        row = next(r for r in csv.DictReader(f) if r["clip_id"] == clip)
    src = (Path(clips_csv).parent / row["local_path"]).resolve()
    doc = {"kind": "s13h_e2e_timing", "clip": clip, "deadline_s": POLICY["retry"]["job_deadline_s"], "started_at": _utc(),
           "stages": [], "understand": "not run (Meta spend outside S13h budget; live-verified separately in S13e)"}
    t0 = time.monotonic()

    def step(name, fn):
        at, s = _utc(), time.monotonic()
        try:
            res, err = fn(), None
        except Exception as e:  # noqa: BLE001 - recorded as the measured failure
            res, err = None, f"{type(e).__name__} {getattr(e, 'code', '')}: {e}"[:400]
        doc["stages"].append({"stage": name, "started_at": at, "ended_at": _utc(),
                              "elapsed_s": round(time.monotonic() - s, 2), "result": res, "error": err})
        doc["total_s"] = round(time.monotonic() - t0, 2)
        doc["status"] = "failed" if err else ("viewable" if name == "viewable" else "running")
        doc["within_deadline"] = doc["total_s"] < doc["deadline_s"]
        (out / "timing.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
        if err:
            sys.exit(f"{name} failed: {err}")
        return res

    def upload():
        data = src.read_bytes()
        svc, owner = UploadService(out / "upload-store"), "dev_owner"
        s = svc.create(owner, "video/mp4", len(data), hashlib.sha256(data).hexdigest())
        for off in range(0, len(data), s["chunk_bytes"]):
            svc.put_chunk(owner, s["upload_id"], off, data[off:off + s["chunk_bytes"]])
        s = svc.complete(owner, s["upload_id"])
        return {"upload_id": s["upload_id"], "status": s["status"], "bytes": s["size_bytes"], "sha256": s["sha256"],
                "chunks": -(-s["size_bytes"] // s["chunk_bytes"])}

    up = step("upload", upload)

    def validate():
        got = hashlib.sha256((out / "upload-store" / up["upload_id"] / "data.part").read_bytes()).hexdigest()
        if got != hashlib.sha256(src.read_bytes()).hexdigest():
            raise ValueError("uploaded bytes are not the approved clips.csv file")
        return {"sha256": got, "binding": f"{clip} via sha256 == clips.csv local_path"}

    step("validate", validate)
    # keyframes.provenance binds by the clips.csv path, so it reads the sha-identical approved file, not data.part.
    step("keyframes", lambda: {"keyframes": len(keyframes.extract(clip, src, out / "keyframes", clips_csv)["keyframes"])})
    ledger = out / "gpu-ledger.jsonl"
    step("segment", lambda: {"segmentation_sha256": gpu_stages.segment(
        f"segment:{clip}:{first}-{last}:{prompt}:{oid}",
        gpu_stages.sam_call(clip, int(first), int(last), prompt, int(oid), out / "segment" / "raw-result.json"),
        out / "segment", ledger, prompt, int(oid))})
    key = "reconstruct:" + hashlib.sha256(Path(manifest).read_bytes()).hexdigest()
    step("reconstruct", lambda: {"reconstruction_sha256": gpu_stages.reconstruct(
        key, clip, Path(manifest).resolve(), out / "reconstruct", ledger)})

    def viewable():
        rec = json.loads((out / "reconstruct" / "reconstruction.json").read_text(encoding="utf-8"))
        return {k: rec[k] for k in ("scene_id", "scene_sha256", "point_count", "synthetic")}

    step("viewable", viewable)
    return doc


if __name__ == "__main__":
    d = main(*sys.argv[1:8], sys.argv[8] if len(sys.argv) > 8 else str(gpu_stages.ROOT / "clips.csv"))
    print(json.dumps({"status": d["status"], "total_s": d["total_s"], "within_deadline": d["within_deadline"]}))
