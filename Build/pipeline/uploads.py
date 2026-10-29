"""S13b resumable upload service on the S13a contract, with a local filesystem store.

The store directory stands in for a bucket: no network, account, credential or spend.
One directory per upload: meta.json (owner, session DTO, committed chunk hashes) + data.part.
"""
import hashlib
import json
import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

from Build.pipeline.contracts import POLICY, chunk_decision, errors

UP = POLICY["upload"]
_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")
_QT_ATOMS = {b"ftyp", b"moov", b"mdat", b"wide", b"free", b"skip"}


class UploadError(Exception):
    """code: contract error code; decision: chunk_decision result; committed_bytes: resume point."""

    def __init__(self, code, message, decision=None, committed_bytes=None):
        super().__init__(message)
        self.code, self.decision, self.committed_bytes = code, decision, committed_bytes


def sniff_ok(media_type, head):
    """Container magic check on the first chunk; the validate stage still ffprobes (S13c)."""
    if media_type == "video/webm":
        return head[:4] == b"\x1a\x45\xdf\xa3"
    # shortcut: mp4 vs quicktime brand is not distinguished; ffprobe in validate decides.
    return head[4:8] == b"ftyp" or (media_type == "video/quicktime" and head[4:8] in _QT_ATOMS)


def _utc(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class UploadService:
    # shortcut: no cross-process lock per upload; one worker per store until S13d/queue adds locking.
    def __init__(self, root, now=lambda: datetime.now(timezone.utc)):
        self.root, self.now = Path(root), now
        self.root.mkdir(parents=True, exist_ok=True)

    def _dir(self, upload_id):
        if not isinstance(upload_id, str) or not _ID.match(upload_id):
            raise UploadError("INVALID_INPUT", "bad upload_id")
        return self.root / upload_id

    def _save(self, d, meta):
        tmp = d / "meta.json.tmp"
        tmp.write_text(json.dumps(meta), encoding="utf-8")
        os.replace(tmp, d / "meta.json")  # atomic commit point for committed_bytes

    def _load(self, owner, upload_id):
        d = self._dir(upload_id)
        if not isinstance(owner, str) or not _ID.match(owner):
            raise UploadError("UNAUTHORIZED", "unauthorized")
        try:
            meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise UploadError("NOT_FOUND", "upload not found") from None
        if not secrets.compare_digest(meta["owner"], owner):
            raise UploadError("UNAUTHORIZED", "unauthorized")  # never returns the other user's session
        s = meta["session"]
        if s["status"] == "open" and _utc(self.now()) >= s["expires_at"]:
            s["status"] = "expired"
            self._save(d, meta)
        return d, meta

    def _reject(self, d, meta, message):
        meta["session"].update(status="rejected",
                               error={"code": "INVALID_INPUT", "message": message, "retryable": False})
        self._save(d, meta)
        raise UploadError("INVALID_INPUT", message, decision="rejected")

    def create(self, owner, media_type, size_bytes, sha256):
        if not isinstance(owner, str) or not _ID.match(owner):
            raise UploadError("UNAUTHORIZED", "unauthorized")
        if media_type not in UP["media_types"]:
            raise UploadError("INVALID_INPUT", "unsupported media_type")
        if type(size_bytes) is not int or not 1 <= size_bytes <= UP["max_file_bytes"]:
            raise UploadError("INVALID_INPUT", "size_bytes out of range")
        if not isinstance(sha256, str) or not _SHA.match(sha256):
            raise UploadError("INVALID_INPUT", "sha256 must be 64 lowercase hex")
        upload_id = "up_" + secrets.token_hex(16)
        session = {"contract_version": "1.0.0", "kind": "upload_session", "upload_id": upload_id,
                   "job_id": None, "media_type": media_type, "size_bytes": size_bytes,
                   "sha256": sha256, "chunk_bytes": UP["chunk_bytes"], "committed_bytes": 0,
                   "status": "open", "expires_at": _utc(self.now() + timedelta(seconds=UP["session_ttl_s"])),
                   "error": None}
        assert not errors(session), errors(session)
        d = self.root / upload_id
        d.mkdir()
        (d / "data.part").write_bytes(b"")
        self._save(d, {"owner": owner, "session": session, "chunks": []})
        return dict(session)

    def get(self, owner, upload_id):
        """Resume point after interruption: client continues at committed_bytes."""
        return dict(self._load(owner, upload_id)[1]["session"])

    def put_chunk(self, owner, upload_id, offset, data):
        d, meta = self._load(owner, upload_id)
        s = meta["session"]
        if type(offset) is not int or offset < 0 or not isinstance(data, (bytes, bytearray)):
            raise UploadError("INVALID_INPUT", "bad offset or body")
        digest = hashlib.sha256(data).hexdigest()
        i = offset // s["chunk_bytes"]
        stored = meta["chunks"][i] if offset < s["committed_bytes"] and i < len(meta["chunks"]) else None
        decision = chunk_decision(s, offset, len(data), digest, stored)
        if decision.startswith("reject"):
            raise UploadError("INVALID_INPUT", decision, decision, s["committed_bytes"])
        if decision == "accept":
            if offset == 0 and not sniff_ok(s["media_type"], bytes(data[:12])):
                self._reject(d, meta, "content does not match media_type")
            with open(d / "data.part", "r+b") as f:  # bytes land before the meta commit
                f.seek(offset)
                f.write(data)
                f.truncate()  # drop torn bytes from an interrupted earlier write
                f.flush()
                os.fsync(f.fileno())
            meta["chunks"].append(digest)
            s["committed_bytes"] = offset + len(data)
            self._save(d, meta)
        ack = {"contract_version": "1.0.0", "kind": "chunk_ack", "upload_id": upload_id,
               "offset": offset, "length": len(data), "chunk_sha256": digest,
               "committed_bytes": s["committed_bytes"], "duplicate": decision == "duplicate"}
        assert not errors(ack), errors(ack)
        return ack

    def complete(self, owner, upload_id):
        d, meta = self._load(owner, upload_id)
        s = meta["session"]
        if s["status"] == "complete":
            return dict(s)  # idempotent
        if s["status"] != "open":
            raise UploadError("INVALID_INPUT", "reject_closed", "reject_closed", s["committed_bytes"])
        if s["committed_bytes"] != s["size_bytes"]:
            raise UploadError("INVALID_INPUT", "incomplete", "incomplete", s["committed_bytes"])
        h = hashlib.sha256()
        with open(d / "data.part", "rb") as f:
            for block in iter(lambda: f.read(1 << 20), b""):
                h.update(block)
        if h.hexdigest() != s["sha256"]:
            self._reject(d, meta, "whole-file sha256 mismatch")
        s.update(status="complete", job_id="job_" + secrets.token_hex(16))
        self._save(d, meta)
        return dict(s)
