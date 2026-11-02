"""One public RM02 cached-shell build, optional <=$3 SF3D batch; never per-user inference.

Run from the repository root with existing Modal credentials loaded in the process.
The source is N53's local replay of N49 RM02; SAM replies are N52's public cache.
"""
import argparse
import hashlib
import io
import json
import sqlite3
import sys
import threading
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Build.api.room.objects import build_shell_files
from Build.guardrails import daily_cap
from Build.measurement import hosted_sam
from Build.reconstruction import live_room, shape_upgrade

SOURCE_SHA = "82e6cc99142b9791ad30c18ac2c92106a30a0082b61d6063aace74d31c986154"
PREFIX = "N75 public RM02 "


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("sam_cache", type=Path)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--paid-once", action="store_true")
    args = parser.parse_args()
    raw = (args.source / "mapanything.npz").read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError("Only the approved cached N49 public RM02 archive is allowed")
    job = ROOT / "evidence/N75/build.local"
    job.mkdir(exist_ok=False)
    (job / "mapanything.npz").write_bytes(raw)
    live_room.finish(job)

    def detect(png, noun, width, height):
        key = hashlib.sha256(f"{width}x{height}".encode() + Image.open(io.BytesIO(png)).convert("RGB").tobytes()).hexdigest()[:16]
        response = json.loads((args.sam_cache / f"{key}-{noun}.json").read_text())
        return hosted_sam.image_instances(hosted_sam.output_text(response), width, height)

    original = daily_cap.reserve
    lock = threading.Lock()

    def row_units():
        with sqlite3.connect(args.ledger) as con:
            return con.execute("SELECT COALESCE(SUM(COALESCE(actual,reserved)),0) FROM spend WHERE label LIKE ?",
                               (PREFIX + "%",)).fetchone()[0]

    def reserve(provider, amount, label="", **kwargs):
        if Path(kwargs.get("path") or daily_cap.default_path()).resolve() != args.ledger.resolve():
            raise RuntimeError("N75 must use the existing canonical daily ledger")
        with lock:
            if row_units() + daily_cap._units(amount) > daily_cap._units("3"):
                raise daily_cap.CapExceeded("N75 $3 total including outstanding reservations")
            return original(provider, amount, PREFIX + label, **kwargs)

    daily_cap.reserve = reserve
    try:
        shell, scene = build_shell_files(job, detect, defer=args.paid_once)
        if args.paid_once:
            shape_upgrade.run(job, "n75_public_rm02", cap_db=args.ledger,
                              gpu_db=args.ledger.parent / "gpu.sqlite3")
        room = json.loads((job / "room.json").read_text())
        scene = json.loads((job / "scene.json").read_text())
        meshes = [o for o in scene["objects"] if o.get("shape", {}).get("type") == "mesh"]
        if args.paid_once and not meshes:
            raise RuntimeError("No SF3D mesh completed; retain the honest fallback and spend receipt")
        bundle = ROOT / "evidence/N75/bundle.local"
        bundle.mkdir(exist_ok=False)
        files = {}

        def asset(name, data):
            (bundle / name).write_bytes(data)
            files[name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            return name

        archive = asset("RM02-mapanything.npz", raw)
        ply = asset("RM02-room.ply", (job / "room.ply").read_bytes())
        mesh_files = {o["id"]: asset(f"RM02-{o['id']}.glb", (job / "objects" / f"{o['id']}.glb").read_bytes()) for o in meshes}
        scene_file = asset("RM02-sample-scene.json", (json.dumps(scene, separators=(",", ":")) + "\n").encode())
        room_file = asset("RM02-sample-room.json", (json.dumps(room, separators=(",", ":")) + "\n").encode())
        template = {"schema": "sample-room-shell/1", "source": "RM02, public Pexels classroom, N49 reconstruction/N52 SAM cache",
                    "archive": archive, "point_cloud": ply, "scene": scene_file, "room": room_file, "meshes": mesh_files}
        (ROOT / "evidence/N75/bundle-manifest.json").write_text(json.dumps({"sample_shell": template, "files": files}, indent=2) + "\n")
        print(json.dumps({"objects": len(scene["objects"]), "meshes": len(meshes), "bundle": str(bundle)}), flush=True)
    finally:
        daily_cap.reserve = original
        with sqlite3.connect(args.ledger) as con:
            con.row_factory = sqlite3.Row
            rows = [dict(r) for r in con.execute("SELECT id,provider,label,reserved,actual,reserved_at,settled_at FROM spend WHERE label LIKE ?",
                                               (PREFIX + "%",))]
        receipt = {"row_cap_usd": 3, "source_archive_sha256": SOURCE_SHA,
                   "source": "public RM02; cached MapAnything/SAM, no new reconstruction or segmentation",
                   "cost_basis": "daily_cap conservative GPU wall-time plus idle estimates, not provider bill",
                   "model": "stabilityai/stable-fast-3d", "units_per_job": "one RGBA crop -> one mesh",
                   "ledger_integer_unit_usd": str(daily_cap.UNIT),
                   "jobs": [{**r, "reserved_usd": float(r["reserved"] * daily_cap.UNIT),
                             "settled_usd": float(r["actual"] * daily_cap.UNIT) if r["actual"] is not None else None} for r in rows],
                   "total_charged_or_reserved_usd": float(row_units() * daily_cap.UNIT)}
        (ROOT / "evidence/N75/spend.json").write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
