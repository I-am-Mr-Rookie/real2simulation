"""Read-only pg_dump; private local archive is ignored and never printed."""
import base64
import hashlib
import json
import shlex
from datetime import datetime, timezone
from pathlib import Path

from remote import ROOT, remote


def decode_backup(output):
    header, encoded = output.split(b"\nN38_DUMP\n", 1)
    expected = header.splitlines()[-1].split()[0].decode()
    data = base64.b64decode(b"".join(encoded.split()), validate=True)
    if not data.startswith(b"PGDMP") or hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("Backup format/checksum verification failed")
    return data, expected


if __name__ == "__main__":
    command = "sh -c " + shlex.quote('set -eu; file=$(mktemp /tmp/n38-pg-XXXXXXXX.dump); '
        'pg_dump -Fc --no-password -U "$PGUSER" -d "$PGDATABASE" -f "$file"; '
        'pg_restore --list "$file" >/dev/null; sha256sum "$file"; '
        'printf "\\nN38_DUMP\\n"; base64 "$file"')
    data, digest = decode_backup(remote("Postgres", command))
    target = ROOT / "private/postgres-before.dump"
    target.parent.mkdir(exist_ok=True)
    with target.open("xb") as stream:
        stream.write(data)
    receipt = {"observed_utc": datetime.now(timezone.utc).isoformat(),
               "path": "evidence/N38/private/postgres-before.dump", "bytes": len(data),
               "sha256": digest, "remote_pg_restore_list": "pass",
               "local_format_and_transfer_checksum": "pass", "restore_drill": "not run"}
    (ROOT / "backup-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
