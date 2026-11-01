"""N03: per-user file storage, quotas and projects for the live product.

Metadata in SQLite (stdlib sqlite3), bytes on disk under R2S_DATA_DIR. Routes sit behind the same
internal-token + owner gate as the other workspace routers; the Clerk BFF proxy is the only caller.
Deleted files keep their row (deleted_at) so the daily upload count is not refunded by deleting.
"""
import functools
import os
import re
import shutil
import sqlite3
import subprocess
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import FileResponse

from Build.api.workspace.auth import error, require_owner
from Build.pipeline.uploads import sniff_ok

MAX_FILE = 200 * 1024 * 1024
MAX_USER = 1024 * 1024 * 1024
MAX_DAILY = 20
MAX_SECONDS = 120.0
DHAKA = timezone(timedelta(hours=6))
TYPES = {".mp4": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm", ".jpg": "image/jpeg",
         ".jpeg": "image/jpeg", ".png": "image/png"}
_ID = re.compile(r"[0-9a-f]{32}")
_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, user TEXT NOT NULL,
  mode TEXT NOT NULL CHECK (mode IN ('room', 'experiment')), title TEXT NOT NULL, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS files (id TEXT PRIMARY KEY, user TEXT NOT NULL, project_id TEXT, name TEXT NOT NULL,
  media_type TEXT NOT NULL, size INTEGER NOT NULL, duration_s REAL, created TEXT NOT NULL, dhaka_day TEXT NOT NULL,
  deleted_at TEXT);
CREATE INDEX IF NOT EXISTS files_user ON files (user, dhaka_day);
"""


def video_seconds(path):
    """Container duration via ffprobe; None when ffprobe is not installed (size-only limits then apply)."""
    exe = shutil.which("ffprobe")
    if not exe:
        return None
    out = subprocess.run([exe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, timeout=30)
    try:
        return float(out.stdout.strip())
    except ValueError:
        raise error(415, "UNSUPPORTED_MEDIA", "file is not a readable video") from None


def _sniff(media_type, head):
    if media_type == "image/jpeg":
        return head[:3] == b"\xff\xd8\xff"
    if media_type == "image/png":
        return head[:8] == b"\x89PNG\r\n\x1a\n"
    return sniff_ok(media_type, head)


class Store:
    def __init__(self, root=None, now=None):
        self.root = Path(root or os.environ.get("R2S_DATA_DIR") or Path.home() / ".r2s-data")
        (self.root / "files").mkdir(parents=True, exist_ok=True)
        (self.root / "tmp").mkdir(exist_ok=True)
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.lock = threading.Lock()  # one writer at a time: quota check + insert must not interleave
        self.db = sqlite3.connect(self.root / "r2s.sqlite3", check_same_thread=False, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(_SCHEMA)

    def _day(self):
        return self.now().astimezone(DHAKA).date().isoformat()

    def quota(self, user):
        used = self.db.execute("SELECT COALESCE(SUM(size), 0) FROM files WHERE user=? AND deleted_at IS NULL",
                               (user,)).fetchone()[0]
        today = self.db.execute("SELECT COUNT(*) FROM files WHERE user=? AND dhaka_day=?",
                                (user, self._day())).fetchone()[0]
        midnight = datetime.combine(self.now().astimezone(DHAKA).date() + timedelta(days=1), datetime.min.time(), DHAKA)
        return {"storage_bytes_used": used, "storage_bytes_limit": MAX_USER,
                "storage_bytes_remaining": max(0, MAX_USER - used), "uploads_today": today,
                "uploads_daily_limit": MAX_DAILY, "uploads_remaining_today": max(0, MAX_DAILY - today),
                "uploads_reset_at": midnight.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

    def check_daily(self, user):
        q = self.quota(user)
        if q["uploads_remaining_today"] <= 0:
            raise error(429, "QUOTA_UPLOADS", "daily upload limit reached (20 per Dhaka day)", quota=q)

    def path(self, user, file_id):
        return self.root / "files" / user / file_id

    def project(self, user, project_id):
        row = self.db.execute("SELECT * FROM projects WHERE id=? AND user=?", (project_id, user)).fetchone()
        if not row:
            raise error(404, "NOT_FOUND", "project not found")
        return dict(row)

    def add(self, user, name, media_type, tmp, duration, project_id=None):
        """Atomic quota check + insert + move into place; tmp is removed on any refusal by the caller."""
        size = tmp.stat().st_size
        with self.lock:
            self.check_daily(user)
            q = self.quota(user)
            if size > q["storage_bytes_remaining"]:
                raise error(413, "QUOTA_STORAGE", "storage limit reached (1 GB per user)", quota=q)
            file_id, now = uuid.uuid4().hex, self.now()
            dest = self.path(user, file_id)
            dest.parent.mkdir(exist_ok=True)
            os.replace(tmp, dest)
            self.db.execute("INSERT INTO files (id, user, project_id, name, media_type, size, duration_s, created,"
                            " dhaka_day) VALUES (?,?,?,?,?,?,?,?,?)",
                            (file_id, user, project_id, name, media_type, size, duration,
                             now.strftime("%Y-%m-%dT%H:%M:%SZ"), self._day()))
        return self.get(user, file_id)

    def get(self, user, file_id):
        row = _ID.fullmatch(file_id) and self.db.execute(
            "SELECT id, project_id, name, media_type, size, duration_s, created FROM files"
            " WHERE id=? AND user=? AND deleted_at IS NULL", (file_id, user)).fetchone()
        if not row:
            raise error(404, "NOT_FOUND", "file not found")
        return dict(row)

    def list(self, user):
        rows = self.db.execute("SELECT id, project_id, name, media_type, size, duration_s, created FROM files"
                               " WHERE user=? AND deleted_at IS NULL ORDER BY created DESC, id", (user,))
        return [dict(r) for r in rows]

    def delete(self, user, file_id):
        self.get(user, file_id)
        with self.lock:
            self.db.execute("UPDATE files SET deleted_at=? WHERE id=? AND user=?",
                            (self.now().strftime("%Y-%m-%dT%H:%M:%SZ"), file_id, user))
            self.path(user, file_id).unlink(missing_ok=True)


_default = functools.cache(Store)


def create_router(store=None, probe=video_seconds) -> APIRouter:
    db = (lambda: store) if store else _default  # lazy: app start and liveness never touch the disk
    router = APIRouter(prefix="/internal/workspace", dependencies=[Depends(require_owner)])

    @router.post("/files", status_code=201)
    async def upload(request: Request, owner: str = Depends(require_owner)):
        db().check_daily(owner)  # refuse before reading the body
        declared = request.headers.get("content-length", "")
        if declared.isdigit() and int(declared) > MAX_FILE + 1_048_576:  # multipart overhead allowance
            raise error(413, "FILE_TOO_LARGE", "file exceeds 200 MB", quota=db().quota(owner))
        form = await request.form(max_files=1, max_fields=4)
        try:
            part, project_id = form.get("file"), form.get("project_id") or None
            if part is None or isinstance(part, str):
                raise error(422, "INVALID_INPUT", "multipart field 'file' is required")
            if project_id is not None:
                db().project(owner, str(project_id))
            name = Path(part.filename or "").name[:200]
            media_type = TYPES.get(Path(name).suffix.lower())
            if not media_type:
                raise error(415, "UNSUPPORTED_MEDIA", "allowed: mp4, mov, webm, jpg, png")
            tmp = db().root / "tmp" / uuid.uuid4().hex
            try:
                size = 0
                with tmp.open("wb") as out:
                    while chunk := await part.read(1_048_576):
                        size += len(chunk)
                        if size > MAX_FILE:
                            raise error(413, "FILE_TOO_LARGE", "file exceeds 200 MB", quota=db().quota(owner))
                        out.write(chunk)
                with tmp.open("rb") as f:
                    if not _sniff(media_type, f.read(16)):
                        raise error(415, "UNSUPPORTED_MEDIA", "file content does not match its type")
                duration = probe(tmp) if media_type.startswith("video/") else None
                if duration is not None and duration > MAX_SECONDS:
                    raise error(422, "VIDEO_TOO_LONG", f"video is {duration:.1f} s; limit is 120 s")
                record = db().add(owner, name, media_type, tmp, duration, project_id)
            finally:
                tmp.unlink(missing_ok=True)
        finally:
            await form.close()
        return {"file": record, "quota": db().quota(owner)}

    @router.get("/files")
    def list_files(owner: str = Depends(require_owner)):
        return {"files": db().list(owner), "quota": db().quota(owner)}

    @router.get("/files/{file_id}")
    def get_file(file_id: str, owner: str = Depends(require_owner)):
        return {"file": db().get(owner, file_id)}

    @router.get("/files/{file_id}/content")
    def download(file_id: str, owner: str = Depends(require_owner)):
        meta = db().get(owner, file_id)  # FileResponse serves Range requests (206) itself
        return FileResponse(db().path(owner, file_id), media_type=meta["media_type"], filename=meta["name"],
                            content_disposition_type="inline", headers={"cache-control": "no-store"})

    @router.delete("/files/{file_id}")
    def delete_file(file_id: str, owner: str = Depends(require_owner)):
        db().delete(owner, file_id)
        return {"deleted": file_id, "quota": db().quota(owner)}

    @router.post("/projects", status_code=201)
    def create_project(payload: dict = Body(...), owner: str = Depends(require_owner)):
        mode, title = payload.get("mode"), payload.get("title")
        if mode not in ("room", "experiment") or not isinstance(title, str) or not 0 < len(title.strip()) <= 120:
            raise error(422, "INVALID_INPUT", "mode must be room or experiment; title 1 to 120 characters")
        row = (uuid.uuid4().hex, owner, mode, title.strip(), db().now().strftime("%Y-%m-%dT%H:%M:%SZ"))
        with db().lock:
            db().db.execute("INSERT INTO projects (id, user, mode, title, created) VALUES (?,?,?,?,?)", row)
        return {"project": db().project(owner, row[0])}

    @router.get("/projects")
    def list_projects(owner: str = Depends(require_owner)):
        rows = db().db.execute("SELECT * FROM projects WHERE user=? ORDER BY created DESC, id", (owner,))
        return {"projects": [dict(r) for r in rows]}

    @router.get("/projects/{project_id}")
    def get_project(project_id: str, owner: str = Depends(require_owner)):
        files = [f for f in db().list(owner) if f["project_id"] == project_id]
        return {"project": db().project(owner, project_id), "files": files}

    return router
