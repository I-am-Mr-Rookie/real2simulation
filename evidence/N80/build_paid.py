"""Run the named N75 pack builder once, four public RM02 crops, canonical ledger and $3 total.

Candidate pack stays local until visual approval. Original N75 receipts/manifest are restored.
"""
import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
CANONICAL = Path("C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon")
OUT = ROOT / "evidence/N80"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse-dir", type=Path)
    reuse = parser.parse_args().reuse_dir
    load_dotenv(CANONICAL / ".env", override=False)
    from Build.guardrails import daily_cap
    from Build.reconstruction import shape_upgrade
    ledger = CANONICAL / "data/spend.sqlite3"
    print(json.dumps(daily_cap.today(ledger), default=str), flush=True)
    source = OUT / "source.local"
    assert not (ROOT / "evidence/N75/build.local").exists(), "Never retry a started build"
    source.mkdir(exist_ok=True)
    shutil.copyfile(CANONICAL / "evidence/S13l/reconstruct/bundle/RM02-mapanything.npz", source / "mapanything.npz")
    before, after = OUT / "before.local", OUT / "after.local"
    before.mkdir(exist_ok=True)
    after.mkdir(exist_ok=True)
    for f in (CANONICAL / "evidence/S13l/reconstruct/bundle").iterdir():
        if f.is_file():
            shutil.copy2(f, before / f.name)
    spec = importlib.util.spec_from_file_location("n75_builder", ROOT / "evidence/N75/build_sample.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    builder.PREFIX = "N80 public RM02 "
    real_run = shape_upgrade.run

    def checked_run(job, owner, **kwargs):
        work = json.loads((job / "shape-upgrades.json").read_text())
        inputs = work["inputs"]
        assert {x["id"] for x in inputs} == {f"room-object-{i}" for i in (1, 2, 4, 7)} and len(inputs) == 4
        if reuse is None:
            return real_run(job, "n80_public_rm02", **kwargs)
        old = reuse.resolve()
        assert old.is_relative_to(OUT.resolve())
        prior = {i["id"]: i for i in json.loads((old / "shape-upgrades.json").read_text())["inputs"]}
        scene = {o["id"]: o for o in json.loads((old / "scene.json").read_text())["objects"]}
        room = {o["id"]: o for o in json.loads((old / "room.json").read_text())["shell"]["kept"]}
        pending = []
        for i in inputs:
            previous = prior[i["id"]]
            if (i["proxy"] != previous["proxy"] or (job / "objects" / i["png"]).read_bytes() !=
                    (old / "objects" / previous["png"]).read_bytes()):
                pending.append(i)
                continue
            upgrade = {**room[i["id"]]["upgrade"], "cached_from": f"N80 {old.name}, identical crop and fit"}
            shape_upgrade._update(job, work["batch"], i["id"], upgrade, scene[i["id"]]["shape"],
                                  (old / "objects" / f"{i['id']}.glb").read_bytes())
            i["modal_call_id"] = previous["modal_call_id"]
        shape_upgrade.live_room._write(job / "shape-upgrades.json", {**work, "inputs": pending})
        print(json.dumps({"new_inference": [i["id"] for i in pending], "reused": len(inputs)-len(pending)}), flush=True)
        try:
            return real_run(job, "n80_public_rm02", **kwargs)
        finally:
            finished = json.loads((job / "shape-upgrades.json").read_text())
            completed = {i["id"]: i for i in finished["inputs"]}
            inputs = [completed.get(i["id"], i) for i in inputs]
            shape_upgrade.live_room._write(job / "shape-upgrades.json", {**finished, "inputs": inputs})

    originals = {name: (ROOT / "evidence/N75" / name).read_bytes() for name in ("spend.json", "bundle-manifest.json")}
    shape_upgrade.run = checked_run
    sys.argv = ["build_sample.py", str(source), str(CANONICAL / ".worktrees/N52-orch297/evidence/N52/rm02/sam"), str(ledger), "--paid-once"]
    (OUT / "spend.json").write_text(json.dumps({"status": "NOT_STARTED", "row_cap_usd": 3, "jobs": []}) + "\n")
    try:
        builder.main()
        for f in (ROOT / "evidence/N75/bundle.local").iterdir():
            shutil.copy2(f, after / f.name)
        shutil.copy2(ROOT / "evidence/N75/bundle-manifest.json", after / "bundle-manifest.json")
        upgrades = json.loads((ROOT / "evidence/N75/build.local/shape-upgrades.json").read_text())
        room = json.loads((ROOT / "evidence/N75/build.local/room.json").read_text())
        states = {x["id"]: x.get("upgrade", {}).get("state") for x in room["shell"]["kept"]}
        assert all(states[x["id"]] == "ready" for x in upgrades["inputs"]), "Incomplete batch; retain old pack"
        (OUT / "upgrades.json").write_text(json.dumps(upgrades, indent=2) + "\n")
    finally:
        receipt = ROOT / "evidence/N75/spend.json"
        if receipt.read_bytes() != originals["spend.json"]:
            shutil.copy2(receipt, OUT / "spend.json")
        for name, data in originals.items():
            (ROOT / "evidence/N75" / name).write_bytes(data)
        shape_upgrade.run = real_run


if __name__ == "__main__":
    main()
