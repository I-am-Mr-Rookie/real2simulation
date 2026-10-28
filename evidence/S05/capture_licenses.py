"""Reproduce public licence-text snapshots at reviewed immutable revisions.

No weights, gated endpoints, authentication or model calls. Run from any cwd.
"""
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).with_name("upstream")


def main():
    revisions = json.loads((ROOT / "revisions.json").read_text(encoding="utf-8"))
    map_code = revisions["map_code"]["revision"]
    map_weights = revisions["map_weights"]["revision"]
    sam_code = revisions["sam_code"]["revision"]
    sources = {
        "map_readme": f"https://raw.githubusercontent.com/facebookresearch/map-anything/{map_code}/README.md",
        "map_license": f"https://raw.githubusercontent.com/facebookresearch/map-anything/{map_code}/LICENSE",
        "map_weights": f"https://huggingface.co/facebook/map-anything-apache/raw/{map_weights}/README.md",
        "sam_readme": f"https://raw.githubusercontent.com/facebookresearch/sam-3d-objects/{sam_code}/README.md",
        "sam_license": f"https://raw.githubusercontent.com/facebookresearch/sam-3d-objects/{sam_code}/LICENSE",
    }
    evidence = []
    for name, url in sources.items():
        with urllib.request.urlopen(url, timeout=30) as response:
            raw = response.read()
        # Keep legal wording intact; normalize upstream trailing spaces only so
        # repository whitespace checks remain strict for all authored files.
        data = b"\n".join(line.rstrip(b" \t\r") for line in raw.split(b"\n"))
        (ROOT / f"{name}.txt").write_bytes(data)
        evidence.append({"name": name, "url": url, "bytes": len(data),
                         "sha256": hashlib.sha256(data).hexdigest(),
                         "raw_bytes": len(raw), "raw_sha256": hashlib.sha256(raw).hexdigest(),
                         "normalization": "strip trailing spaces/tabs/CR per line; preserve wording",
                         "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()})
    evidence.append({"name": "map_weight_license",
                     "url": "https://huggingface.co/facebook/map-anything-apache/raw/main/LICENSE",
                     "status": "HTTP 404 during initial S05a review; official model card declares Apache-2.0"})
    (ROOT / "sources.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print("Saved 5 immutable public licence/documentation snapshots; no weights or inference")


if __name__ == "__main__":
    main()
