"""Validate fresh audit coverage, errata consistency, and old/fixed extraction. Offline only."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

from audit import OUT, ROOT, differences, pairs, self_check

self_check()
audit = json.loads((OUT / "audit.json").read_text())
assert audit["counts"] == {"OK": 18, "WRONG": 5}
sources = {c: json.loads((OUT / f"{c}-full-presentation.json").read_text())["frames"]
           for c in audit["sources"]}
checked, last_frames = 0, set()
for result in audit["results"]:
    raw = (ROOT / result["file"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == result["sha256"]
    pts = [float(f["pts_time"]) for f in sources[result["clip_id"]]]
    rows = list(pairs(json.loads(raw)))
    assert differences(rows, pts) == result["differences"]
    checked += len(rows)
    if "errata" in result:
        errata = json.loads((ROOT / result["errata"]).read_text())
        assert errata["original_sha256"] == result["sha256"]
        assert errata["errata_for"] == result["file"]
        assert not differences(list(pairs(errata)), pts)
        assert [r[0] for r in errata["frame_map"]] == sorted({i for _, i, _ in rows})
    if "/frame_map/" in " ".join(pointer for pointer, _, _ in rows):
        last_frames.add((result["clip_id"], max(i for _, i, _ in rows)))

# Execute only the existing local timestamp helper, without importing Modal or torch.
tree = ast.parse((ROOT / "Build/measurement/runtime/modal_track.py").read_text())
function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_pts")
margin = next(n for n in tree.body if isinstance(n, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id == "REORDER_MARGIN" for t in n.targets))
namespace = {"subprocess": subprocess}
exec(compile(ast.Module(body=[margin, function], type_ignores=[]), "modal_track._pts", "exec"), namespace)
reproductions = []
for clip, last in sorted(last_frames):
    path = Path(audit["sources"][clip]["command"][-1])
    truth = [float(f["pts_time"]) for f in sources[clip]][:last + 1]
    assert namespace["_pts"](path, last) == truth
    old_command = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                   "frame=pts_time", "-of", "csv=p=0", "-read_intervals", f"%+#{last + 1}", str(path)]
    old = [float(x.strip().strip(",")) for x in subprocess.check_output(old_command, text=True).split()]
    changed = [{"frame_index": i, "old_pts_s": p, "corrected_pts_s": truth[i]}
               for i, p in enumerate(old) if i <= last and abs(p - truth[i]) > 1e-6]
    reproductions.append({"clip_id": clip, "last": last, "fixed_equals_full_stream": True,
                          "old_command": old_command, "old_returned_frames": len(old), "old_differences": changed})
for result in audit["results"]:
    if result["status"] == "WRONG":
        expected = next(r for r in reproductions if r["clip_id"] == result["clip_id"]
                        and r["last"] == max(b["frame_index"] for b in result["differences"]))
        assert {b["frame_index"] for b in result["differences"]} == {b["frame_index"] for b in expected["old_differences"]}
(OUT / "checks.json").write_text(json.dumps({"status": "PASS", "timestamp_occurrences_checked": checked,
    "files_checked": len(audit["results"]), "corrected_maps_checked": 5,
    "old_and_fixed_reproductions": reproductions}, indent=2) + "\n")
print(f"PASS: {len(audit['results'])} files; {checked} timestamp occurrences; 5 correction maps; {len(reproductions)} old/fixed ffprobe comparisons")
