"""Offline source-manifest acceptance checks, not clip qualification or Gate M."""
import csv
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]


def check():
    with (ROOT / "clips.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert rows and all(None not in row for row in rows), "Malformed CSV"
    assert len({row["clip_id"] for row in rows}) == len(rows), "Duplicate IDs"
    falls = [row for row in rows if row["experiment"] == "free_fall"]
    assert len(falls) >= 3, "Need >=3 terrestrial fall candidates"
    assert len({row["capture_group"] for row in falls}) >= 3, "Avoid counting variants as independent sources"
    assert any(row["clip_id"] == "AP15" for row in rows), "Apollo 15 missing"
    receipts = json.loads((Path(__file__).with_name("S02a-provenance.json")).read_text(encoding="utf-8"))
    evidence = {item["clip_id"]: item for item in receipts["files"]}
    # S02a evidence applies only to its own candidates; later runs add other
    # providers and maintain separate provenance without weakening these checks.
    for row in (row for row in rows if row['clip_id'] in evidence):
        for key in ("source_url", "original_source_url", "download_url", "creator", "licence", "licence_url", "attribution", "adaptation_notes", "scale_reference", "scale_status", "timebase_status", "suitability", "capture_group", "evidence_path"):
            assert row[key], (row["clip_id"], key)
        for key in ("source_url", "original_source_url", "download_url", "licence_url"):
            url = urlparse(row[key])
            assert url.scheme == "https" and url.netloc, (row["clip_id"], key)
        assert urlparse(row["source_url"]).hostname == "commons.wikimedia.org"
        assert row["licence"] in {"CC-BY-SA-4.0", "PD-USGov-NASA"}
        assert row["status"] == "UNAPPROVED_CANDIDATE" and row["owner_approved"] == "NO"
        assert row["scale_value_m"] == "", "Do not invent a calibrated scale"
        if row["local_path"]:
            assert (ROOT / row["local_path"]).is_file(), (row["clip_id"], "missing file")
        assert (ROOT / row["evidence_path"].split("#")[0]).is_file()
        proof = evidence[row["clip_id"]]
        assert proof["http_status"] == 200 and proof["declared_licence"] == row["licence"]
        assert proof["source_url"] == row["source_url"] and proof["revision_id"]
        assert len(proof["page_sha256"]) == 64 and proof["licence_excerpt"]
        assert urlparse(proof["original_media_url"]).hostname == "upload.wikimedia.org"
        if row["clip_id"] != "AP15":
            assert proof["original_media_url"] == row["download_url"]
    assert receipts["nasa_original"]["http_status"] == 200
    assert receipts["nasa_original"]["linked_media_url"] == next(row["download_url"] for row in rows if row["clip_id"] == "AP15")
    print(f"PASS: {len(falls)} fall candidates / {len(set(row['capture_group'] for row in falls))} provisional groups + Apollo 15; provenance and unknowns explicit")
    print("NOT VERIFIED: physical calibration, local file metadata, complete visual playback, owner approval, Gate M")


if __name__ == "__main__":
    check()
