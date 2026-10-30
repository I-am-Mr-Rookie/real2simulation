"""Stdlib fail-closed cross-process exclusion and durable JSON replacement."""
import json
import os
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from Build.guardrails.admission import ReconstructionPaused, _unique_fields


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_fields)


def write_json(path, value):
    path = Path(path)
    temp = path.with_name(path.name + "." + uuid4().hex + ".tmp")
    try:
        with temp.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, default=str, indent=1)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


@contextmanager
def exclusive(path):
    """Contention/crashed-owner lock pauses; never auto-break a potentially live lock."""
    path = Path(path)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except OSError:
        raise ReconstructionPaused("Admission lock unavailable") from None
    try:
        os.write(descriptor, str(os.getpid()).encode("ascii"))
        os.fsync(descriptor)
        yield
    finally:
        os.close(descriptor)
        path.unlink()
