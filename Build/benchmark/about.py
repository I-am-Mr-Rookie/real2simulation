"""S21e: generate app About data from frozen S21 evidence + Gate A checkpoint. No number is typed here.

python Build/benchmark/about.py   -> writes Build/web/src/about/about.json
"""
import hashlib, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import manifest as mf

SOURCES = {
    "errors": "evidence/S21/S21b-errors.json",
    "predictions": "evidence/S21/S21c-predictions.json",
    "costs": "evidence/S21/S21d-costs.json",
    "gate_a": "evidence/S14/GATE_A.json",
}
OUT = mf.ROOT / "Build/web/src/about/about.json"
KEEP = ("id", "class", "scene", "value", "unit", "reason", "note")


def build():
    raw = {k: (mf.ROOT / p).read_bytes() for k, p in SOURCES.items()}
    doc = {k: json.loads(b) for k, b in raw.items()}
    gates = {json.dumps(doc[k]["gates"], sort_keys=True) for k in ("errors", "predictions", "costs")}
    if len(gates) != 1:
        raise ValueError(f"S21 outputs disagree on gates: {gates}")
    a = doc["gate_a"]
    if a.get("gate") != "A" or not a.get("never_plain_met"):
        raise ValueError("Gate A checkpoint missing or claims plain MET")
    return {
        "schema": "about/1",
        "generated_by": "Build/benchmark/about.py",
        "rule": "every value copied from the pinned evidence below; never retyped",
        "sources": {k: {"path": SOURCES[k], "sha256": hashlib.sha256(b).hexdigest()} for k, b in raw.items()},
        "gates": {**json.loads(gates.pop()), "gate_a": a["verdict"], "gate_a_label": a["label"]},
        "gate_a_known_limits": a["known_limits"],
        "sections": {
            k: {"summary": doc[k]["summary"],
                "rows": [{f: r[f] for f in KEEP if f in r} for r in doc[k]["rows"]]}
            for k in ("errors", "predictions", "costs")
        },
    }


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(build(), indent=1) + "\n", encoding="utf-8")
    print(OUT)
