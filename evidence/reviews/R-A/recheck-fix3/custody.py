"""Small independent metadata/ledger audit; no model calls or credential-value inspection."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import tempfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
read = lambda p: json.loads(p.read_text(encoding="utf-8-sig"))
live = read(ROOT / "evidence/S14/S14g-fix3-live.json")
offline = read(ROOT / "evidence/S14/S14g-fix3-offline.json")
acq = {r["clip_id"]: r for r in read(ROOT / "evidence/clips/S02c-acquisition.json")["files"]}
rows = []
for row in live["specs"]:
    clip = row["case_id"]
    path = Path(tempfile.gettempdir()) / "S14g-fix3-kf" / clip / "manifest.json"
    manifest = read(path)
    assert manifest["source"]["sha256"] == row["source_sha256"] == acq[clip]["sha256"]
    assert manifest["provenance"]["clip_id"] == clip
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row["keyframe_manifest_sha256"]
    rows.append({"case_id": clip, "source_and_manifest_bound_to_acquisition": True,
                 "selected_frames": len(row["frames"]),
                 "time_sources": sorted({f["time_source"] for f in row["frames"]}),
                 "context_scale": row["scene_context"]["scale_status"],
                 "numeric_spec_scale": row["spec"]["scene"]["scale_status"]})
ledger = [json.loads(s) for s in (ROOT / "evidence/S14/S14g-fix3-ledger.jsonl").read_text().splitlines() if s]
expected = Counter({"spec-" + row["case_id"]: row["attempts"] for row in live["specs"]})
expected.update({f"turn-{i:02d}": row["attempts"] for i, row in enumerate(live["turns"])})
assert Counter(row["call"] for row in ledger) == expected
assert len(ledger) == 40 and all(row["http"] == 200 for row in ledger)
tree = ast.parse((ROOT / "evidence/S14/S14g_fix_oracle.py").read_text())
imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
imports += [name.name for node in ast.walk(tree) if isinstance(node, ast.Import) for name in node.names]
assert not any(name and (name.startswith("contracts.agent") or "numeric_issue" in name) for name in imports)
result = {"manifest_acquisition_bindings": rows, "live_ledger_calls": len(ledger),
          "ledger_labels_match_saved_attempts": True, "all_recorded_http_200": True,
          "oracle_imports_independent_of_runtime_numeric_predicate": True,
          "offline_vs_live_summary_differences": {
              key: {"offline": offline["summary"].get(key), "live": live["summary"].get(key)}
              for key in live["summary"] if live["summary"].get(key) != offline["summary"].get(key)},
          "live_turn_scene_count": len({r["scene_id"] for r in live["turns"]}),
          "live_mystery_turns": sum(r["mystery"] for r in live["turns"])}
(OUT / "custody.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print("PASS: 10 acquisition/manifest bindings; 40 recorded calls; oracle import independence; exact timing-source metadata saved")
