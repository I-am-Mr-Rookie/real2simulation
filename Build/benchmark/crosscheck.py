"""S21f: cross-check pitch-facing benchmark numbers against the generated S21 evidence.

python Build/benchmark/crosscheck.py   -> prints findings JSON; exit 1 if any mismatch.
Reads only; checks BENCHMARK.md (tables + prose numbers + count claims + gate labels),
Build/web/src/about/about.json and About.jsx against evidence/S21/*.json and evidence/S14/GATE_A.json.
"""
import json, math, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import manifest as mf
import about, costs

S21 = {k: about.SOURCES[k] for k in ("errors", "predictions", "costs")}
MD = mf.ROOT / "BENCHMARK.md"
JSX = mf.ROOT / "Build/web/src/about/About.jsx"
NUM = re.compile(r"(?<![\w.#/-])\d+\.\d+(?![\w.])")  # decimals only; integers are ids/thresholds
WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
PRICED = ("billed", "estimated", "reservation", "simulated")


def _nums(x, out):
    if isinstance(x, bool):
        return out
    if isinstance(x, (int, float)):
        out.append(float(x))
    elif isinstance(x, dict):
        for v in x.values():
            _nums(v, out)
    elif isinstance(x, list):
        for v in x:
            _nums(v, out)
    return out


def _close(a, b, rel=5e-3):
    return math.isclose(a, b, rel_tol=rel, abs_tol=1e-12)


def check(md_text=None, about_doc=None, jsx_text=None):
    docs = {k: json.loads((mf.ROOT / p).read_text(encoding="utf-8")) for k, p in S21.items()}
    gate_a = json.loads((mf.ROOT / about.SOURCES["gate_a"]).read_text(encoding="utf-8"))
    md = md_text if md_text is not None else MD.read_text(encoding="utf-8")
    ab = about_doc if about_doc is not None else json.loads(about.OUT.read_text(encoding="utf-8"))
    jsx = jsx_text if jsx_text is not None else JSX.read_text(encoding="utf-8")
    rows = {r["id"]: r for d in docs.values() for r in d["rows"]}
    evidence = _nums(docs, []) + _nums(gate_a, [])
    bad, checked = [], 0

    def flag(where, msg):
        bad.append({"where": where, "issue": msg})

    # 1. every BENCHMARK.md table row equals its evidence row (class, value, n)
    prose = []
    for i, line in enumerate(md.splitlines(), 1):
        if not line.startswith("|"):
            prose.append((i, line)); continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] == "id" or set(cells[0]) <= {"-"}:
            continue
        r = rows.get(cells[0])
        if r is None:
            flag(f"BENCHMARK.md:{i}", f"table id {cells[0]!r} not in S21 evidence"); continue
        checked += 1
        val = cells[3] if "scene" in r else cells[2]  # costs table has a scene column
        if cells[1] != r["class"]:
            flag(f"BENCHMARK.md:{i}", f"{cells[0]} class {cells[1]} != {r['class']}")
        if r["value"] is None:
            if val != "UNAVAILABLE":
                flag(f"BENCHMARK.md:{i}", f"{cells[0]} should be UNAVAILABLE, shows {val}")
        elif val == "UNAVAILABLE" or not _close(float(val), r["value"]):
            flag(f"BENCHMARK.md:{i}", f"{cells[0]} value {val} != evidence {r['value']}")
        if "scene" not in r and r.get("n") is not None and len(cells) > 5 and cells[5] and int(cells[5]) != r["n"]:
            flag(f"BENCHMARK.md:{i}", f"{cells[0]} n {cells[5]} != {r['n']}")

    # 2. prose: every decimal must be a value present in the evidence (no authored numbers)
    for i, line in prose:
        for m in NUM.finditer(re.sub(r"\]\([^)]*\)", "]", line)):
            checked += 1
            if not any(_close(float(m.group()), e) for e in evidence):
                flag(f"BENCHMARK.md:{i}", f"prose number {m.group()} not found in evidence")

    # 3. prose count claims
    claims = re.findall(r"(\d+) measured, (\d+) UNAVAILABLE", md)
    for (meas, unav), k in zip(claims, ("errors", "predictions")):
        checked += 1
        s = docs[k]["summary"]
        if (int(meas), int(unav)) != (s["measured"], s["unavailable"]):
            flag("BENCHMARK.md", f"{k} count claim {meas}/{unav} != summary {s}")
    if len(claims) != 2:
        flag("BENCHMARK.md", f"expected 2 measured/UNAVAILABLE count claims, found {len(claims)}")
    sp = docs["predictions"]["split"]
    for a, b in re.findall(r"(\d+) of (\d+) sealed frames", md):
        checked += 1
        if (int(a), int(b)) != (sp["scored"], sp["heldout"]):
            flag("BENCHMARK.md", f"'{a} of {b} sealed frames' != split {sp['scored']}/{sp['heldout']}")
    for word in re.findall(r"(\w+) post-freeze evidence\s+files", md):
        checked += 1
        if WORDS.get(word.lower()) != len(costs.EXTRA):
            flag("BENCHMARK.md", f"'{word} post-freeze evidence files' != len(costs.EXTRA)={len(costs.EXTRA)}")

    # 4. gate labels: exact verdicts, Gate A label verbatim, never plain MET
    g = docs["errors"]["gates"]
    for need in (f"Gate M **{g['gate_m']}**", f"Gate RS **{g['gate_rs']}**",
                 f"Gate A **{gate_a['verdict']}**", gate_a["label"]):
        checked += 1
        if need not in md:
            flag("BENCHMARK.md", f"missing gate label {need!r}")
    if re.search(r"Gate (M|RS|A)\W{0,4}MET\b", md):
        flag("BENCHMARK.md", "plain 'Gate X: MET' claim")

    # 5. about.json: regenerated equality + every row equals evidence + labels
    if ab != about.build():
        flag("about.json", "drifted from about.py regeneration")
    if (ab["gates"].get("gate_a"), ab["gates"].get("gate_a_label")) != (gate_a["verdict"], gate_a["label"]):
        flag("about.json", "Gate A verdict/label != GATE_A.json")
    for name, s in ab["sections"].items():
        if s["summary"] != docs[name]["summary"]:
            flag("about.json", f"{name} summary != evidence")
        for r in s["rows"]:
            checked += 1
            e = rows.get(r["id"])
            if e is None or r["value"] != e["value"] or r["class"] != e["class"]:
                flag("about.json", f"row {r['id']} != evidence")
            if r["class"] == "simulated" and "NOT spend" not in (r.get("note") or ""):
                flag("about.json", f"simulated row {r['id']} lacks 'NOT spend' simulation label")
            if r["class"] == "measured" and re.match(r"(m|m/s\^2|metres?)(\s|$)", r.get("unit") or ""):
                flag("about.json", f"measured metric-unit row {r['id']} while scale is unverified")

    # 6. About.jsx authors no numbers (comment lines and words like h2/sha256 excluded)
    code = "\n".join(l for l in jsx.splitlines() if not l.lstrip().startswith("//"))
    if re.search(r"\d", re.sub(r"[A-Za-z_]\w*", "w", code)):
        flag("About.jsx", "contains a numeric literal; values must come from about.json")
    return {"checked": checked, "mismatches": bad, "status": "PASS" if not bad else "FAIL"}


if __name__ == "__main__":
    res = check()
    print(json.dumps(res, indent=1))
    sys.exit(0 if res["status"] == "PASS" else 1)
