"""Differential test of every cached public RM02 mask against the unchanged strict Meta codec in the base commit."""
import json
import re
import subprocess
import sys
import time
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Build.measurement import hosted_sam
from Build.reconstruction import _sam_mask_codec as fast

BASE = "b635d89e"


def strict_codec():
    strict = types.ModuleType("strict_codec")
    exec(subprocess.run(["git", "show", f"{BASE}:Build/reconstruction/_sam_mask_codec.py"],
                        check=True, capture_output=True, text=True).stdout, strict.__dict__)
    return strict


def main():
    cache, output = map(Path, sys.argv[1:])
    strict = strict_codec()
    masks = []
    for path in sorted(cache.glob("*.json")):
        text = hosted_sam.output_text(json.loads(path.read_text()))
        for match in re.finditer(r"<\|mask;x=0;y=0;data=(\d+),(\d+),([^|]*)\|>", text):
            height, width, payload = match.groups()
            masks.append(types.SimpleNamespace(width=int(width), height=int(height), payload=payload,
                                               encoding="one_bit" if payload.startswith("!") else "lossless"))
    results, times = [], {}
    for name, codec in (("strict", strict), ("fused", fast)):
        start = time.perf_counter()
        rasters = [codec.decode_mask_to_raster(mask) for mask in masks]
        times[name + "_s"] = time.perf_counter() - start
        results.append(rasters)
    assert masks and results[0] == results[1]
    summary = {"label": "MEASURED local serial decode plus strict validation; public RM02 cached replies",
               "base": BASE, "mask_records": len(masks), "identical": True, **times}
    output.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
