"""S06b dependency + licence audit of the dists actually installed in the Modal runtime image.

Input: receipt from runtime.py smoke ("licences" = importlib.metadata of every installed dist).
  python Build/gpu/licence_audit.py <smoke-remote.json> [audit.json]
Exit 0 only if every lock pin is installed at its exact version, no dist is denied (NC/ND/proprietary) and every
unknown/copyleft dist has a recorded REVIEWED decision below.
NVIDIA CUDA wheels (proprietary EULA, pulled by torch) are 'vendor_eula': private runtime use only, never redistributed.
Unknown = metadata gives no licence; never silently passed as permissive.
Duplicates = a dist installed at two versions (Modal injects its client deps into containers beside the lock).
"""
import json
import re
import sys
from pathlib import Path

import image_spec as s

DENY = re.compile(r"non-?commercial|\bcc[- ]by[- ](?:\w+-)*n[cd]\b|no ?deriv|proprietary", re.I)
STRONG_COPYLEFT = re.compile(r"(?<!L)(?<!Lesser )\b(A?GPL|GNU General Public)", re.I)
PERMISSIVE = re.compile(r"\b(MIT|BSD|Apache|PSF|Python Software Foundation|ISC|MPL|Mozilla|LGPL|Lesser General|"
                        r"Unlicense|zlib|HPND|CC0|Public Domain|0BSD|BSL-1\.0|Boost|CNRI|Historical Permission)", re.I)
# Human-reviewed decisions for dists whose metadata is empty or copyleft (name -> basis). Edit only with evidence.
REVIEWED = {
    "mapanything": "Apache-2.0 (metadata empty); evidence/S05/LICENSE_REVIEW.md row 'MapAnything code', retain notices",
    "plyfile": "GPL-3.0; private runtime dependency of mapanything only, not vendored/modified/redistributed; "
               "re-review before distributing any image or bundling it",
}


def norm(name):
    return re.sub(r"[-_.]+", "-", name or "").lower()


def classify(rec):
    text = " | ".join(filter(None, [rec.get("license_expression"), rec.get("license"), *rec.get("classifiers", [])]))
    if not text.strip():
        return "unknown", text
    if DENY.search(text):
        return ("vendor_eula" if norm(rec["name"]).startswith("nvidia-") else "denied"), text
    if STRONG_COPYLEFT.search(text) and not PERMISSIVE.search(text):
        return "copyleft_review", text
    return ("permissive" if PERMISSIVE.search(text) else "unknown"), text


def lock_pins(lock=s.LOCK):
    pins = {}
    for line in Path(lock).read_text().splitlines():
        line = line.split("#")[0].strip()
        if "==" in line:
            name, ver = line.split("==", 1)
            pins[norm(name.split("[")[0])] = ver.split(";")[0].strip()
        elif line.startswith("mapanything @ "):
            pins["mapanything"] = None  # code-rev zip; version checked via revisions, not here
    return pins


def audit(records, lock=s.LOCK):
    installed = {}
    for r in records:
        installed.setdefault(norm(r["name"]), set()).add(r["version"])
    pins = lock_pins(lock)
    missing = sorted(n for n in pins if n not in installed)
    mismatched = sorted(f"{n}: lock {v} not in installed {sorted(installed[n])}" for n, v in pins.items()
                        if v and n in installed and v not in installed[n])
    groups = {}
    for r in records:
        cls, text = classify(r)
        groups.setdefault(cls, []).append({"name": r["name"], "version": r["version"], "licence": text[:160]})
    unreviewed = sorted({d["name"] for k in ("unknown", "copyleft_review") for d in groups.get(k, [])
                         if norm(d["name"]) not in REVIEWED})
    errors = [f"missing pin: {n}" for n in missing] + [f"version drift: {m}" for m in mismatched] + \
             [f"denied licence: {d['name']} ({d['licence']})" for d in groups.get("denied", [])] + \
             [f"unreviewed licence: {n}" for n in unreviewed]
    return {"contract": "S06b-licence-audit/v1", "ok": not errors, "errors": errors,
            "installed_count": len(records), "unique_dists": len(installed), "lock_pin_count": len(pins),
            "duplicates": {n: sorted(v) for n, v in sorted(installed.items()) if len(v) > 1},
            "extra_not_in_lock": sorted(set(installed) - set(pins)),
            "counts": {k: len(v) for k, v in sorted(groups.items())},
            "reviewed": {n: REVIEWED[n] for n in sorted(REVIEWED) if n in installed},
            "review": {k: groups[k] for k in ("vendor_eula", "copyleft_review", "unknown") if k in groups},
            "groups": groups}


if __name__ == "__main__":
    result = audit(json.loads(Path(sys.argv[1]).read_text())["licences"])
    text = json.dumps(result, indent=1)
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(text + "\n")
    print(json.dumps({k: result[k] for k in ("ok", "errors", "installed_count", "unique_dists", "lock_pin_count",
                                               "duplicates", "extra_not_in_lock", "counts", "reviewed")}, indent=1))
    sys.exit(0 if result["ok"] else 1)
