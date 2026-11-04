"""N03: per-user file storage, quotas and projects for the live product.

Metadata in SQLite (stdlib sqlite3), bytes on disk under R2S_DATA_DIR. Routes sit behind the same
internal-token + owner gate as the other workspace routers; the Clerk BFF proxy is the only caller.
Deleted files keep their row (deleted_at) so the daily upload count is not refunded by deleting.
"""
import functools
import json
import os
import re
import shutil
import sqlite3
import subprocess
import threading
import uuid
from datetime import datetime, timedelta, timezone
from hashlib import sha256  # owner-id hash for the lab folder only; quota never hashes file bytes
from pathlib import Path

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import FileResponse

from Build.api.workspace.auth import error, require_owner
from Build.pipeline.uploads import sniff_ok
from Build.api.storage.preview import project_previews

MAX_FILE = 200 * 1024 * 1024
MAX_USER = 1024 * 1024 * 1024
MAX_DAILY = 20
MAX_SECONDS = 120.0
MAX_SNAPSHOT = 256 * 1024  # N56: lab preview image for the workspace project card
SNAPSHOT_TYPES = {"image/jpeg": b"\xff\xd8\xff", "image/png": b"\x89PNG\r\n\x1a\n", "image/webp": b"RIFF"}
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
    """Container duration via ffprobe; fails closed (503) when ffprobe is missing, 415 when unreadable."""
    exe = shutil.which("ffprobe")
    if not exe:
        raise error(503, "VALIDATOR_UNAVAILABLE", "video validation is unavailable; try again later")
    try:
        out = subprocess.run([exe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                             capture_output=True, text=True, timeout=30)
        seconds = float(out.stdout.strip())
    except (ValueError, subprocess.TimeoutExpired):
        seconds = float("nan")
    if not 0 < seconds < float("inf"):
        raise error(415, "UNSUPPORTED_MEDIA", "file is not a readable video") from None
    return seconds


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
        self._path, self._local = self.root / "r2s.sqlite3", threading.local()
        self.db.executescript(_SCHEMA)

    @property
    def db(self):
        # N89: one connection per thread; a shared one raised InterfaceError (HTTP 500) under concurrent requests.
        con = getattr(self._local, "con", None)
        if con is None:
            con = self._local.con = sqlite3.connect(self._path, timeout=30, isolation_level=None)
            con.row_factory = sqlite3.Row
        return con

    def _day(self):
        return self.now().astimezone(DHAKA).date().isoformat()

    def quota(self, user):
        used = self.db.execute("SELECT COALESCE(SUM(size), 0) FROM files WHERE user=? AND deleted_at IS NULL",
                               (user,)).fetchone()[0]
        rooms = self.root / "rooms" / user
        public_by_room, public_bytes = {}, 0
        for path in rooms.rglob("*"):
            try:
                if path.is_file():
                    parts = path.relative_to(rooms).parts
                    if parts[0] not in public_by_room:
                        try:
                            public = json.loads((rooms / parts[0] / "public.json").read_text(encoding="utf-8"))
                        except (OSError, ValueError):
                            public = {}
                        public_by_room[parts[0]] = public if isinstance(public, dict) else {}
                    entry = public_by_room[parts[0]].get("/".join(parts[1:]))
                    stat = path.stat()
                    # shortcut: server-owned size/mtime fingerprints; hash again if writers can preserve both.
                    if (path.name not in ("scene.json", "public.json") and isinstance(entry, dict)
                            and stat.st_size == entry.get("size") and stat.st_mtime_ns == entry.get("mtime_ns")):
                        public_bytes += stat.st_size
                    else:
                        used += stat.st_size
            except FileNotFoundError:
                pass  # a room artifact was replaced or removed during the scan
        for path in self.lab_dir(user).rglob("*"):  # N89: saved lab scenes and lab copies count too
            try:
                if path.is_file():
                    used += path.stat().st_size
            except FileNotFoundError:
                pass
        today = self.db.execute("SELECT COUNT(*) FROM files WHERE user=? AND dhaka_day=?",
                                (user, self._day())).fetchone()[0]
        midnight = datetime.combine(self.now().astimezone(DHAKA).date() + timedelta(days=1), datetime.min.time(), DHAKA)
        return {"storage_bytes_used": used, "storage_bytes_public": public_bytes, "storage_bytes_limit": MAX_USER,
                "storage_bytes_remaining": max(0, MAX_USER - used), "uploads_today": today,
                "uploads_daily_limit": MAX_DAILY, "uploads_remaining_today": max(0, MAX_DAILY - today),
                "uploads_reset_at": midnight.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

    def check_storage(self, user):
        # shortcut: no per-write size reservation; a job may overshoot by one room, add reservations for strict caps.
        q = self.quota(user)
        if q["storage_bytes_remaining"] <= 0:
            raise error(413, "QUOTA_STORAGE", "storage limit reached (1 GB per user)", quota=q)

    def check_daily(self, user):
        q = self.quota(user)
        if q["uploads_remaining_today"] <= 0:
            raise error(429, "QUOTA_UPLOADS",
                        f"Daily upload limit reached: {MAX_DAILY} uploads per day. It resets at {q['uploads_reset_at']}"
                        " (midnight Dhaka time). Deleting a file frees storage but does not give back an upload.",
                        reason="daily_upload_limit", reset_at=q["uploads_reset_at"], quota=q)

    def path(self, user, file_id):
        return self.root / "files" / user / file_id

    def lab_dir(self, user, project_id=None):
        # Same layout as Build/api/agent/lab_handlers._dir: R2S_DATA_DIR/lab/<owner hash>/<project>.
        d = self.root / "lab" / sha256(user.encode()).hexdigest()[:24]
        return d / project_id if project_id else d

    def has_lab(self, user, project_id):
        return (self.lab_dir(user, project_id) / "scene.json").is_file()

    def save_lab(self, user, project_id, text):
        """N89: quota-checked write of a project's validated lab scene. Caller holds self.lock."""
        f = self.lab_dir(user, project_id) / "scene.json"
        q = self.quota(user)
        if len(text.encode("utf-8")) - (f.stat().st_size if f.is_file() else 0) > q["storage_bytes_remaining"]:
            raise error(413, "QUOTA_STORAGE", "storage limit reached (1 GB per user)", quota=q)
        f.parent.mkdir(parents=True, exist_ok=True)
        tmp = f.with_suffix(".tmp")
        tmp.write_text(text, "utf-8")
        os.replace(tmp, f)

    def project(self, user, project_id):
        row = self.db.execute("SELECT * FROM projects WHERE id=? AND user=?", (project_id, user)).fetchone()
        if not row:
            raise error(404, "NOT_FOUND", "project not found")
        return dict(row)

    def add(self, user, name, media_type, tmp, duration, project_id=None):
        """Atomic quota check + insert + move into place; tmp is removed on any refusal by the caller."""
        size = tmp.stat().st_size
        file_id, now = uuid.uuid4().hex, self.now()
        dest = self.path(user, file_id)
        with self.lock:  # thread lock for this connection; BEGIN IMMEDIATE serializes other connections/processes
            self.db.execute("BEGIN IMMEDIATE")
            try:
                self.check_daily(user)
                q = self.quota(user)
                if size > q["storage_bytes_remaining"]:
                    raise error(413, "QUOTA_STORAGE", "storage limit reached (1 GB per user)", quota=q)
                self.db.execute("INSERT INTO files (id, user, project_id, name, media_type, size, duration_s,"
                                " created, dhaka_day) VALUES (?,?,?,?,?,?,?,?,?)",
                                (file_id, user, project_id, name, media_type, size, duration,
                                 now.strftime("%Y-%m-%dT%H:%M:%SZ"), self._day()))
                dest.parent.mkdir(exist_ok=True)
                os.replace(tmp, dest)
                self.db.execute("COMMIT")
            except BaseException:
                self.db.execute("ROLLBACK")
                dest.unlink(missing_ok=True)  # no unaccounted bytes on disk
                raise
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

    def lab_text(scene):
        # N89: the editor's own validator (node bridge) cleans the scene before it is stored.
        from Build.api.agent.lab_handlers import LabError, _node
        if not isinstance(scene, dict) or len(json.dumps(scene)) > 512 * 1024:
            raise error(422, "INVALID_INPUT", "scene must be a lab-scene-v1 object under 512 KiB")
        try:
            return json.dumps(_node({"op": "validate", "scene": scene})["scene"], indent=2)
        except LabError as exc:
            raise error(422, "LAB_INPUT", str(exc)) from None

    def insert_project(owner, mode, title, scene_text=None):
        row = (uuid.uuid4().hex, owner, mode, title, db().now().strftime("%Y-%m-%dT%H:%M:%SZ"))
        with db().lock:
            db().db.execute("INSERT INTO projects (id, user, mode, title, created) VALUES (?,?,?,?,?)", row)
            if scene_text is not None:
                try:
                    db().save_lab(owner, row[0], scene_text)
                except BaseException:
                    db().db.execute("DELETE FROM projects WHERE id=? AND user=?", (row[0], owner))
                    raise
        return {**db().project(owner, row[0]), "lab": scene_text is not None}

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
                if duration is not None and duration > MAX_SECONDS:  # video probe never returns None (fails closed)
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
        # N89: an optional scene makes a saved lab (template copy or "Make a copy"); its bytes use the owner's quota.
        if "scene" in payload and mode != "room":
            raise error(422, "INVALID_INPUT", "only room projects can hold a lab scene")
        text = lab_text(payload["scene"]) if "scene" in payload else None
        return {"project": insert_project(owner, mode, title.strip(), text), "quota": db().quota(owner)}

    @router.post("/projects/{project_id}/copy", status_code=201)
    def copy_project(project_id: str, payload: dict = Body(default={}), owner: str = Depends(require_owner)):
        src = db().project(owner, project_id)
        if not db().has_lab(owner, project_id):
            raise error(409, "NO_LAB", "only saved labs can be copied here; open the lab and use Make a copy")
        title = payload.get("title") or src["title"][:115] + " copy"
        if not isinstance(title, str) or not 0 < len(title.strip()) <= 120:
            raise error(422, "INVALID_INPUT", "title 1 to 120 characters")
        text = (db().lab_dir(owner, project_id) / "scene.json").read_text("utf-8")
        project = insert_project(owner, "room", title.strip(), text)
        src_snap, dst_snap = _snapshot(owner, project_id), _snapshot(owner, project["id"])
        if src_snap.is_file():  # card preview only; snapshots are outside the storage quota like every other snapshot
            shutil.copyfile(src_snap.with_suffix(".type"), dst_snap.with_suffix(".type"))
            shutil.copyfile(src_snap, dst_snap)
        return {"project": project, "quota": db().quota(owner)}

    @router.get("/projects")
    def list_projects(owner: str = Depends(require_owner)):
        previews = project_previews(db(), owner)
        rows = db().db.execute("SELECT * FROM projects WHERE user=? ORDER BY created DESC, id", (owner,))
        return {"projects": [{**dict(r), "snapshot_url": _snapshot_url(r["id"], owner), "track_preview": previews.get(r["id"]),
                              "lab": db().has_lab(owner, r["id"])} for r in rows]}

    # N56: one small owner-scoped preview per project (the lab canvas), overwritten on each save or finished run.
    def _snapshot(owner, project_id):
        return db().root / "snapshots" / owner / project_id

    def _snapshot_url(project_id, owner):
        p = _snapshot(owner, project_id)
        return f"/api/workspace/projects/{project_id}/snapshot?v={p.stat().st_mtime_ns}" if p.is_file() else None

    @router.put("/projects/{project_id}/snapshot")
    async def put_snapshot(project_id: str, request: Request, owner: str = Depends(require_owner)):
        db().project(owner, project_id)
        media_type = (request.headers.get("content-type") or "").split(";")[0].strip().lower()
        if media_type not in SNAPSHOT_TYPES:
            raise error(415, "UNSUPPORTED_TYPE", "snapshot must be image/jpeg, image/png or image/webp")
        data = await request.body()
        if len(data) > MAX_SNAPSHOT:
            raise error(413, "FILE_TOO_LARGE", "snapshot exceeds 256 KB")
        if not data.startswith(SNAPSHOT_TYPES[media_type]) or (media_type == "image/webp" and data[8:12] != b"WEBP"):
            raise error(415, "UNSUPPORTED_TYPE", "snapshot bytes do not match the declared image type")
        p = _snapshot(owner, project_id)
        p.parent.mkdir(parents=True, exist_ok=True)
        (p.with_suffix(".type")).write_text(media_type)
        p.write_bytes(data)
        return {"snapshot_url": _snapshot_url(project_id, owner)}

    @router.get("/projects/{project_id}/snapshot")
    def get_snapshot(project_id: str, owner: str = Depends(require_owner)):
        db().project(owner, project_id)
        p = _snapshot(owner, project_id)
        if not p.is_file():
            raise error(404, "NOT_FOUND", "no snapshot")
        return FileResponse(p, media_type=p.with_suffix(".type").read_text(), headers={"cache-control": "no-store"})

    @router.get("/projects/{project_id}")
    def get_project(project_id: str, owner: str = Depends(require_owner)):
        files = [f for f in db().list(owner) if f["project_id"] == project_id]
        return {"project": {**db().project(owner, project_id), "lab": db().has_lab(owner, project_id)}, "files": files}

    # N55: rename and delete. Delete keeps the files (they move to "no project"); file deletion stays explicit.
    @router.patch("/projects/{project_id}")
    def rename_project(project_id: str, payload: dict = Body(...), owner: str = Depends(require_owner)):
        title = payload.get("title")
        if not isinstance(title, str) or not 0 < len(title.strip()) <= 120:
            raise error(422, "INVALID_INPUT", "title 1 to 120 characters")
        db().project(owner, project_id)
        with db().lock:
            db().db.execute("UPDATE projects SET title=? WHERE id=? AND user=?", (title.strip(), project_id, owner))
        return {"project": db().project(owner, project_id)}

    @router.delete("/projects/{project_id}")
    def delete_project(project_id: str, owner: str = Depends(require_owner)):
        db().project(owner, project_id)
        with db().lock:
            p = _snapshot(owner, project_id)
            p.unlink(missing_ok=True)
            p.with_suffix(".type").unlink(missing_ok=True)
            shutil.rmtree(db().lab_dir(owner, project_id), ignore_errors=True)  # id checked above: this owner's project
            db().db.execute("UPDATE files SET project_id=NULL WHERE project_id=? AND user=?", (project_id, owner))
            db().db.execute("DELETE FROM projects WHERE id=? AND user=?", (project_id, owner))
        return {"deleted": project_id}

    return router
