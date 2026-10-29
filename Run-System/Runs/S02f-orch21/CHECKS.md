# Fresh verification — S02f-orch21
## Evidence self-check
Run from this worktree root with Python UTF-8 mode. No media/network/product execution.
```python
import json, re, subprocess
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote
root = Path.cwd()
d = root / "evidence/clips/calibration-recovery/S02f/orch13"
run = root / "Run-System/Runs/S02f-orch21"
s = json.loads((d / "shortlist.json").read_text(encoding="utf-8"))
assert s["additional_distinct_routes"] == 1 and s["media_downloaded"] is False
assert s["parent_S02f_completed"] is False and len(s["candidates"]) == 3
assert len({c["id"] for c in s["candidates"]}) == 3
text = (d / "SOURCES.md").read_text(encoding="utf-8") + (d / "RESEARCH.md").read_text(encoding="utf-8")
def source_key(u):
    p = urlparse(u)
    if p.hostname == "commons.wikimedia.org":
        title = parse_qs(p.query).get("title", [unquote(p.path.removeprefix("/wiki/"))])[0]
        return p.hostname, unquote(title).replace("_", " ")
    return p.hostname, unquote(p.path)
keys = {source_key(u) for u in re.findall(r"\]\((https?://[^\s]+)\)", text)}
for c in s["candidates"]:
    assert c["disposition"] == "REJECTED" and c["eligible"] is False
    assert c["independent_qualified_trials"] == 0 and len(c["unmet_facts"]) >= 3
    assert c["metric_scale"]["uncertainty_mm"] is None
    assert all(source_key(u) in keys for u in c["primary_pages"])
f = s["candidates"][0]
assert f["rights"]["licence"] == "CC BY-SA 3.0"
assert f["clock"]["frequency_hz"] == 20 and f["clock"]["nominal_spacing_s"] == 0.05
assert not f["metric_scale"]["physical_witness_documented"]
assert not f["metric_scale"]["coplanarity_documented"]
assert s["candidates"][2]["native_video_or_ordered_frame_sequence_located"] is None
for md in [*d.glob("*.md"), *run.glob("*.md")]:
    for link in re.findall(r"\]\(([^)]+)\)", md.read_text(encoding="utf-8")):
        if not link.startswith(("http://", "https://", "#")):
            assert (md.parent / link).resolve().exists(), (md, link)
assert subprocess.check_output(["git", "diff", "HEAD", "--", "STATE.md", "QUEUE.md", "RUNS.md", "DECISIONS_LOG.md", "clips.csv"], text=True) == ""
print("PASS: 3 unique REJECTED records; 0 qualified trials; exactly 1 additional route.")
print("PASS: source citation coverage and local links; nominal strobe clock and unknown uncertainties preserved.")
print("PASS: cat montage native ordering remains explicitly unverified; controls/manifest unchanged.")
```

## Observed checks / repairs
- Initial inline Python run failed with Windows cp1252 UnicodeDecodeError on curly source quotes. Re-run with explicit UTF-8 reads / Python -X utf8 passed. The shell's trailing git command initially masked the Python exit status; final command checks exit status immediately. No evidence conclusion depended on the failed check.
- Final self-check executed after final evidence edits: PASS (exit0), 3 rejected records / 0 qualified trials / 1 additional route; citation/local-link checks and unchanged-control checks PASS.
- Staged exact-seven-file Owns check PASS (exit0). Initial cached diff check flagged blank EOF lines; repaired all seven, then cached whitespace check PASS (exit0). Final substantive verification completed 2026-10-29T12:38:39+00:00; receipt finalization followed.
- git diff --check and git diff --cached --check: whitespace validation.
- Staged path set must be exactly these seven files: three evidence files SOURCES.md / RESEARCH.md / shortlist.json, and four run files PLAN.md / TIMEBOX.json / REPORT.md / CHECKS.md.
- python Run-System/worker_timebox.py check Run-System/Runs/S02f-orch21/TIMEBOX.json: validates full1800s contract and recorded ordering; substantive acceptance is separately evidenced.
- No product test suite run: product code was untouched. No paid compute/GPU/model job or actual-media check. Read-only web tools were used.
