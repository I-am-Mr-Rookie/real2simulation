"""Read-only evidence-chain audit; writes only this review's traceability.json."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    frames = read("evidence/S05/S05d/RESULT.json")
    receipts = read("evidence/S05/S05c/RESULT.json")
    manifest = read("evidence/S05/S05d/manifest.json")
    ledger = read("evidence/S05/S05b/orch14/job-ledger.json")
    with (ROOT / "clips.csv").open(encoding="utf-8-sig", newline="") as stream:
        clips = {row["clip_id"]: row for row in csv.DictReader(stream)}
    rows = []
    for entry in manifest:
        cid = entry["clip_id"]
        expected = receipts["scenes"][cid]["npz_sha256"]
        assert frames[cid]["npz_sha256"] == expected
        path = Path(entry["npz"])
        actual = sha(path) if path.exists() else None
        if actual is not None:
            assert actual == expected, cid
        rows.append({"clip": cid, "npz_sha256": expected,
                     "local_npz_exists": path.exists(), "actual_npz_sha256": actual,
                     "receipt_and_frame_hash_equal": True, "refs": entry["refs"],
                     "gravity_applicable": entry["gravity_applicable"],
                     "source_url": clips[cid]["source_url"],
                     "licence": clips[cid]["licence"],
                     "csv_approval_historical": clips[cid]["owner_approved"],
                     "current_scoped_approval": "evidence/owner/S02/APPROVAL.md"})
    success = [row for row in ledger["gpu_attempts"] if row.get("client", "").startswith("OK")]
    assert len(success) == 1
    assert success[0]["output_sha256"] == frames["RM02"]["npz_sha256"]
    paths = ["Build/reconstruction/spike/gate_r.py", "Build/reconstruction/spike/scene_frame.py",
             "Build/reconstruction/spike/test_gate_r.py", "contracts/scene/scene.schema.json",
             "contracts/scene/validate_scene.py", "evidence/S05/S05d/RESULT.json",
             "evidence/S05/S05d/manifest.json", "evidence/S05/S05c/RESULT.json",
             "evidence/S05/S05c/input.json", "evidence/S05/S05b/orch14/job-ledger.json",
             "evidence/S05/S05e/GATE_R.json", "evidence/S05/LICENSE_REVIEW.md",
             "evidence/owner/S02/APPROVAL.md", "STATE.md", "QUEUE.md", "clips.csv"]
    output = {"review_scope": "offline existing evidence; no new GPU/scene measurements",
              "input_sha256": {p: sha(ROOT / p) for p in paths}, "scenes": rows,
              "model": receipts["model"], "code_revision": receipts["code_revision"],
              "weight_revision": receipts["weight_revision"],
              "successful_rm02_function_s": success[0]["function_elapsed_s"],
              "all_rm02_attempts_function_s": sum(a["function_elapsed_s"] for a in ledger["gpu_attempts"]),
              "s05c_function_s": receipts["function_elapsed_s"],
              "limitations": ["Source video bytes and live billing not rechecked.",
                              "CSV NO is historical; scoped APPROVAL.md is controlling.",
                              "Hash equality proves custody, not reference identity/calibration.",
                              "Manifest references and A4 annotations are absent."]}
    Path(__file__).with_name("traceability.json").write_text(
        json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("Receipt/frame hash equality: 3/3; actual local NPZ matches:",
          sum(row["actual_npz_sha256"] == row["npz_sha256"] for row in rows), "/3")
    print("Scale refs:", sum(bool(row["refs"]) for row in rows), "/3; no new physical evidence")


if __name__ == "__main__":
    main()
