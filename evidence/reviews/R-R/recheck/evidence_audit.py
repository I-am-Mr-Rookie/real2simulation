"""Read-only S05f custody and conditional paper-aspect audit; output only beside this file."""
import importlib.util
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
sys.path.insert(0, str(OUT.parent))
sys.path.insert(0, str(ROOT / "Build/reconstruction/spike"))
import check_traceability as trace
import gate_r as gate


def main():
    assert (gate.SCALE_TOL, gate.ANGLE_TOL_DEG, gate.GPU_MIN_PER_SCENE, gate.MIN_SCALE_PASSES) == (0.1, 5, 4, 2)
    assert gate.COHORT == ("RM02", "RM04", "RM05")
    frames = trace.read("evidence/S05/S05f/RESULT.json")
    prior = trace.read("evidence/S05/S05d/RESULT.json")
    receipts = trace.read("evidence/S05/S05c/RESULT.json")
    sheets = trace.read("evidence/S05/S05f/frames.json")
    rows = []
    manifest = trace.read("evidence/S05/S05d/manifest.json")
    for entry in manifest:
        cid = entry["clip_id"]
        expected = receipts["scenes"][cid]["npz_sha256"]
        actual = trace.sha(Path(entry["npz"]))
        assert actual == expected == frames[cid]["npz_sha256"] == sheets[cid]["npz_sha256"]
        for field in ("floor", "gravity", "npz_sha256"):
            assert frames[cid][field] == prior[cid][field], (cid, field)
        assert frames[cid]["metric_scale"]["status"] == frames[cid]["a4_plane_normal"]["status"] == "ABSTAIN"
        assert not entry["refs"]
        sheet = ROOT / "evidence/S05/S05f" / sheets[cid]["sheet"]
        assert trace.sha(sheet) == sheets[cid]["sheet_sha256"]
        rows.append({"clip": cid, "npz_sha256": actual, "sheet_sha256": trace.sha(sheet),
                     "no_accepted_references": True, "floor_gravity_unchanged": True})

    # Import diagnostic functions without main(), which would write into the S05 owner's paths.
    spec = importlib.util.spec_from_file_location("paper_diagnostic", ROOT / "evidence/S05/S05f/rm02_paper_diagnostic.py")
    diag = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(diag)
    points = diag.sf.load_views(manifest[0]["npz"])[0]["pts_img"]
    long_edge, short_edge = diag.edges(points, diag.CORNERS)
    rng = diag.np.random.default_rng(0)
    aspects = []
    for _ in range(500):
        corners = [[r + int(rng.integers(-2, 3)), c + int(rng.integers(-2, 3))] for r, c in diag.CORNERS]
        a, b = diag.edges(points, corners)
        aspects.append(a / b)
    interval = diag.np.percentile(aspects, [5, 95]).tolist()
    saved = trace.read("evidence/S05/S05f/rm02-paper-diagnostic.json")
    assert abs(float(long_edge / short_edge) - saved["aspect"]) < 1e-12
    assert interval == saved["aspect_p5_p95"]
    assert not interval[0] <= 297 / 210 <= interval[1]
    assert interval[0] <= 279.4 / 215.9 <= interval[1]
    paths = ["Build/reconstruction/spike/gate_r.py", "Build/reconstruction/spike/scene_frame.py",
             "Build/reconstruction/spike/test_gate_r.py", "Build/reconstruction/spike/test_scene_frame.py",
             "evidence/S05/S05f/GATE_R.md", "evidence/S05/S05f/GATE_R.json",
             "evidence/S05/S05f/REVIEW_PACKET.md", "evidence/S05/S05f/rm02-paper-diagnostic.json"]
    result = {"custody": rows, "reviewed_hashes": {p: trace.sha(ROOT / p) for p in paths},
              "paper_aspect": float(long_edge / short_edge), "conditional_jitter_p5_p95": interval,
              "interpretation": "Conditional model-space diagnostic only, not an identity test or calibrated confidence interval. Ambiguity warrants abstention; does not prove non-A4 or Letter."}
    (OUT / "evidence-audit.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("Custody 3/3, contact-sheet hashes 3/3, no accepted references, thresholds fixed; RM02 aspect/jitter reproduced")


if __name__ == "__main__":
    main()
