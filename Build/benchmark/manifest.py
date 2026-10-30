"""S21a frozen benchmark manifest: validator + held-out leakage check (stdlib only).

python Build/benchmark/manifest.py check [manifest.json]  -> JSON summary, exit 1 on any error.
"""
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = Path(__file__).with_name("manifest.json")
CLASSES = {"measured", "simulated", "unavailable"}


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _load(m):
    docs, errs = {}, []
    for name, e in m["evidence"].items():
        p = ROOT / e["path"]
        if not p.is_file():
            errs.append(f"evidence {name}: missing {e['path']}")
            continue
        raw = p.read_bytes()
        if hashlib.sha256(raw).hexdigest() != e["sha256"]:
            errs.append(f"evidence {name}: sha256 mismatch {e['path']}")
            continue
        docs[name] = json.loads(raw)
    return docs, errs


def resolve(docs, ref):
    """RFC 6901 pointer into a pinned evidence doc; raises KeyError/IndexError when absent."""
    node = docs[ref["evidence"]]
    for tok in ref["pointer"].split("/")[1:]:
        tok = tok.replace("~1", "/").replace("~0", "~")
        node = node[int(tok)] if isinstance(node, list) else node[tok]
    return node


def _authored_numbers(node, path):
    if _num(node):
        yield path
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from _authored_numbers(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _authored_numbers(v, f"{path}/{i}")


def _refs(node):
    if isinstance(node, dict):
        if "evidence" in node and "pointer" in node:
            yield node
        else:
            for v in node.values():
                yield from _refs(v)
    elif isinstance(node, list):
        for v in node:
            yield from _refs(v)


def validate(m, docs):
    # "key" selects a field inside each frame record (0 = first column); it is a selector, not a reported number.
    errs = [f"authored number at {p}" for k in ("gates", "clips", "split", "metrics")
            for p in _authored_numbers(m[k], "/" + k) if not p.endswith("/key")]
    for ref in _refs([m["gates"], m["clips"], m["split"], m["metrics"]]):
        if ref["evidence"] not in m["evidence"]:
            errs.append(f"unknown evidence {ref['evidence']}")
        elif ref["evidence"] in docs:
            try:
                resolve(docs, ref)
            except (KeyError, IndexError, ValueError, TypeError):
                errs.append(f"dangling pointer {ref['evidence']}{ref['pointer']}")
    if errs:
        return errs, []
    rows, ids = [], set()
    for x in m["metrics"]:
        if x["id"] in ids or x["class"] not in CLASSES:
            errs.append(f"metric {x['id']}: duplicate id or bad class")
        ids.add(x["id"])
        v = resolve(docs, x["value"])
        if x["class"] == "unavailable":
            if v is not None or not x.get("reason") or not resolve(docs, x["reason"]):
                errs.append(f"metric {x['id']}: unavailable needs null value + evidence reason")
        else:
            v = len(v) if isinstance(v, list) else v  # list-valued evidence reports its count
            if not _num(v):
                errs.append(f"metric {x['id']}: {x['class']} value is not a number")
        sc = x.get("sample_count")
        sc = resolve(docs, sc) if isinstance(sc, dict) else sc
        rows.append({"id": x["id"], "class": x["class"], "value": v,
                     "unit": resolve(docs, x["unit"]) if isinstance(x["unit"], dict) else x["unit"],
                     "uncertainty": resolve(docs, x["uncertainty"]) if "uncertainty" in x else None,
                     "sample_count": len(sc) if isinstance(sc, list) else sc})
    return errs, rows


def leakage(m, docs):
    """No held-out frame may be in (or precede the end of) the fitting prefix."""
    s = m["split"]
    r = lambda ref: resolve(docs, ref)
    frames = lambda ref: [f[ref["key"]] for f in r(ref)]
    train, held = frames(s["train_frames"]), frames(s["heldout_frames"])
    after = r(s["scored_frames"]["after"])
    scored = [f for f in frames(s["scored_frames"]) if f > after]
    ltf = {r(s["boundary_last_training_frame"]), r(s["prediction_last_training_frame"]), after}
    errs = []
    if not train or not held:
        errs.append("empty train or held-out set")
    elif set(train) & set(held):
        errs.append(f"leak: frames in both sets {sorted(set(train) & set(held))[:5]}")
    elif max(train) >= min(held):
        errs.append("leak: training frames not strictly before held-out frames")
    if len(ltf) != 1 or (train and max(train) not in ltf):
        errs.append(f"boundary disagreement: last_training_frame {sorted(ltf)} vs max(train)")
    if len(train) != r(s["training_count"]) or len(held) != r(s["suffix_count"]):
        errs.append("count mismatch vs sealed boundary")
    if not set(scored) <= set(held):
        errs.append("scored frames outside sealed held-out set")
    for k in ("training_sha256", "prediction_sha256"):
        if len({r(x) for x in s[k]}) != 1:
            errs.append(f"{k} differs across evidence")
    if r(s["suffix_observations_read_at_fit"]) is not False:
        errs.append("held-out observations were read at fit time")
    return errs, {"train": len(train), "train_range": [min(train), max(train)] if train else None,
                  "heldout": len(held), "heldout_range": [min(held), max(held)] if held else None,
                  "scored": len(scored)}


def check(m):
    docs, errs = _load(m)
    rows, split = [], None
    if not errs:
        errs, rows = validate(m, docs)
    if not errs:
        lerrs, split = leakage(m, docs)
        errs += lerrs
    gates = {k: resolve(docs, g) for k, g in m["gates"].items()} if not errs else None
    return {"ok": not errs, "errors": errs, "gates": gates, "split": split, "metrics": rows}


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] != "check":
        sys.exit(__doc__)
    out = check(json.loads(Path(sys.argv[2] if len(sys.argv) > 2 else DEFAULT).read_text(encoding="utf-8")))
    print(json.dumps(out, indent=1))
    sys.exit(0 if out["ok"] else 1)
