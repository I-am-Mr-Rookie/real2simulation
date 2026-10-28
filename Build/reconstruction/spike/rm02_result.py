"""Persist received output without claiming remote cleanup or probe success."""
import hashlib
import os
from pathlib import Path

from rm02_watchdog import atomic_json


def persist_result(directory, result):
    receipt, data = result
    if (len(data) != receipt["output_bytes"]
            or hashlib.sha256(data).hexdigest() != receipt["output_sha256"]):
        raise ValueError("Received payload does not match its result receipt")
    directory = Path(directory)
    local = directory / "local"
    local.mkdir(parents=True, exist_ok=True)
    destination = local / "RM02-mapanything.npz"
    temporary = destination.with_suffix(".npz.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, destination)
    # Per-file atomicity, not a multi-file transaction; marker commits completed bytes.
    atomic_json(directory / "result-received.json",
                dict(receipt, remote_cleanup_status="PENDING"))
