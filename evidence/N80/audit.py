"""CPU-only verification of public RM02 candidates, unchanged geometry and canonical spend."""
import hashlib
import json
import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence/N80"
CANONICAL = Path("C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon")
sys.path.insert(0, str(ROOT))
from Build.guardrails import daily_cap


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    old, new = OUT / "before.local", OUT / "after.local"
    original = read(ROOT / "evidence/N75/bundle-manifest.json")
    candidate = read(new / "bundle-manifest.json")
    shared = CANONICAL / "evidence/S13l/reconstruct/bundle"
    assert all(sha(shared / n) == info["sha256"] for n, info in original["files"].items())
    assert all(sha(new / n) == info["sha256"] for n, info in candidate["files"].items())
    a = {o["id"]: o for o in read(old / "RM02-sample-scene.json")["objects"]}
    b = {o["id"]: o for o in read(new / "RM02-sample-scene.json")["objects"]}
    assert len(a) == len(b) == 23 and a.keys() == b.keys()
    assert all(a[i].get(k) == b[i].get(k) for i in a for k in ("position", "size", "rotation"))
    ids = {f"room-object-{i}" for i in (1, 2, 4, 7)}
    assert {i for i in b if b[i].get("shape", {}).get("type") == "mesh"} == ids
    fit = []
    for oid in sorted(ids):
        raw = (new / f"RM02-{oid}.glb").read_bytes()
        assert raw[:4] == b"glTF"
        gltf = json.loads(raw[20:20+int.from_bytes(raw[12:16], "little")])
        for node in gltf["nodes"]:
            assert node.get("matrix", np.eye(4).ravel().tolist()) == np.eye(4).ravel().tolist()
            assert node.get("rotation", [0, 0, 0, 1]) == [0, 0, 0, 1]
            assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
        bounds = [gltf["accessors"][p["attributes"]["POSITION"]] for m in gltf["meshes"] for p in m["primitives"]]
        lo, hi = np.min([a["min"] for a in bounds], axis=0), np.max([a["max"] for a in bounds], axis=0)
        vertices = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
        assert np.isfinite(vertices).all()
        turns = b[oid]["shape"]["quarter_turns"]
        angle = turns * np.pi / 2
        rotated = np.column_stack([vertices[:, 0]*np.cos(angle)+vertices[:, 2]*np.sin(angle), vertices[:, 1],
                                   -vertices[:, 0]*np.sin(angle)+vertices[:, 2]*np.cos(angle)])
        extent = np.ptp(rotated, axis=0)
        assert (extent > 0).all()
        scales = np.asarray(b[oid]["size"]) / extent
        fit.append({"id": oid, "raw_extent_after_yaw": extent.tolist(), "proxy_size": b[oid]["size"],
                    "axis_scale": scales.tolist(), "max_min_axis_scale_ratio": float(scales.max()/scales.min())})
    with sqlite3.connect(CANONICAL / "data/spend.sqlite3") as con:
        con.row_factory = sqlite3.Row
        rows = [dict(r) for r in con.execute("SELECT label,reserved,actual,reserved_at,settled_at FROM spend WHERE label LIKE 'N80 public RM02 %'")]
    assert rows and all(r["actual"] is not None for r in rows)
    total = sum(r["actual"] for r in rows) * daily_cap.UNIT
    assert total <= 3
    from Build.api.storage import Store, sample
    with tempfile.TemporaryDirectory(prefix="n80-public-") as temp:
        temp = Path(temp)
        store = Store(temp / "data")
        manifest = read(OUT / "qa-manifest.local.json")
        legacy = temp / "legacy.json"
        legacy.write_text(json.dumps({k: v for k, v in manifest.items() if k != "sample_shell"}))
        try:
            sample.seed(store, "user_n80_audit", OUT / "qa-bundle.local", legacy)
            d = next((store.root / "rooms/user_n80_audit").iterdir())
            assert not read(d / "scene.json")["objects"]
            with patch("Build.api.room.objects.build_shell_files", side_effect=AssertionError("unexpected reconstruction")), \
                 patch("Build.gpu.sf3d.generate_remote", side_effect=AssertionError("unexpected GPU")):
                sample.seed(store, "user_n80_audit", OUT / "qa-bundle.local", OUT / "qa-manifest.local.json")
                assert len(read(d / "scene.json")["objects"]) == 23
                snapshot = {p.name: p.read_bytes() for p in d.glob("*.json")}
                sample.seed(store, "user_n80_audit", OUT / "qa-bundle.local", OUT / "qa-manifest.local.json")
                assert snapshot == {p.name: p.read_bytes() for p in d.glob("*.json")}
                sample.seed(store, "user_n80_second", OUT / "qa-bundle.local", OUT / "qa-manifest.local.json")
        finally:
            store.db.close()
    result = {"source": "public RM02 only", "objects": len(b), "mesh_ids": sorted(ids), "geometry_unchanged": True,
              "original_shared_pack_unchanged": True, "candidate_hashes_valid": True, "promoted": False,
              "candidate_legacy_repair_idempotent": True, "candidate_second_user_seeded_without_inference": True,
              "paid_crop_calls": sum("N31 sf3d" in r["label"] for r in rows),
              "idle_tail_reservations": sum("idle tail" in r["label"] for r in rows),
              "charged_or_reserved_usd": float(total), "cost_basis": "conservative ledger estimates, not provider bill",
              "fit": fit, "limitation": "Client independently rescales each axis to the proxy box; Python-only uniform fitting would not repair visual aspect."}
    (OUT / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "fit"}))


if __name__ == "__main__":
    main()
