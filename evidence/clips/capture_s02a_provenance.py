"""Read public source pages only; save compact provenance, never download media."""
import csv
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]


def fetch(url):
    request = Request(url, headers={"User-Agent": "Real2Simulation-S02a/1.0 (public source research)"})
    with urlopen(request, timeout=25) as response:
        raw = response.read()
        return response.status, response.url, raw


def capture():
    rows = list(csv.DictReader((ROOT / "clips.csv").open(encoding="utf-8", newline="")))
    records = []
    for row in rows:
        status, final_url, raw = fetch(row["source_url"])
        page = raw.decode("utf-8")
        # Restrict licence evidence to the FILE declaration, not Commons' footer.
        plain = html.unescape(re.sub(r"<[^>]+>", " ", page))
        plain = re.sub(r"\s+", " ", plain)
        if row["licence"] == "CC-BY-SA-4.0":
            marker = re.search(r"This file is licensed under the.{0,120}?Attribution-Share Alike 4\.0 International.{0,30}?license", plain)
        else:
            marker = re.search(r"This file is in the public domain in the United States because it was solely created by NASA", plain)
        if not marker:
            raise ValueError(f"File-specific licence declaration missing: {row['clip_id']}")
        revisions = re.findall(r"oldid=(\d+)", page)
        media = re.search(r'class="fullMedia".*?href="([^"]+)"', page, re.S)
        if not media:
            raise ValueError(f"Original media link missing: {row['clip_id']}")
        original = html.unescape(media.group(1)).split("?")[0]
        records.append({
            "clip_id": row["clip_id"], "checked_utc": datetime.now(timezone.utc).isoformat(),
            "source_url": row["source_url"], "final_url": final_url, "http_status": status,
            "page_sha256": hashlib.sha256(raw).hexdigest(),
            "revision_id": revisions[0] if revisions else None,
            "declared_licence": row["licence"], "licence_excerpt": marker.group(0),
            "original_media_url": original,
        })
    # Verify the NASA-hosted alternative is actually linked from the official page.
    apollo = next(row for row in rows if row["clip_id"] == "AP15")
    status, final_url, raw = fetch(apollo["original_source_url"])
    assert apollo["download_url"] in html.unescape(raw.decode("utf-8"))
    nasa = {"source_url": final_url, "http_status": status,
            "page_sha256": hashlib.sha256(raw).hexdigest(),
            "linked_media_url": apollo["download_url"],
            "checked_utc": datetime.now(timezone.utc).isoformat()}
    output = {"scope": "Source pages only; no local media or measured metadata", "files": records, "nasa_original": nasa}
    target = Path(__file__).with_name("S02a-provenance.json")
    target.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(records)} file-specific rights declarations + NASA original link; no media downloaded")


if __name__ == "__main__":
    capture()
