"""Owner-scoped room deletion. Synthetic files and blocked fake jobs only, no model calls."""
import json
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from Build.api.room import create_router, objects
from Build.api.storage.files import Store
from Build.reconstruction import shape_upgrade

A = {"x-workspace-token": "synthetic-delete-token", "x-workspace-owner": "user_deleteA"}
B = {**A, "x-workspace-owner": "user_deleteB"}
BASE = "/internal/workspace/rooms/"
RID = "a" * 32


@pytest.fixture
def api(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_INTERNAL_TOKEN", A["x-workspace-token"])
    store = Store(tmp_path / "data")
    app = FastAPI()
    app.include_router(create_router(store, remote=lambda _: None, stats=lambda: None))
    with TestClient(app) as client:
        yield client, store, app
    store.db.close()


def room(store, rid=RID, owner=A["x-workspace-owner"], **status):
    d = store.root / "rooms" / owner / rid
    (d / "objects").mkdir(parents=True)
    (d / "status.json").write_text(json.dumps({"job_id": rid, "state": "done", **status}))
    (d / "room.json").write_text(json.dumps({"shell": {"kept": []}}))
    (d / "scene.json").write_text('{"objects": ["saved edit"]}')
    (d / "mapanything.npz").write_bytes(b"synthetic archive")
    (d / "objects" / "room-object-1.glb").write_bytes(b"synthetic mesh")
    return d


def test_delete_is_owner_only_frees_storage_keeps_upload_and_other_rooms(api):
    c, store, _ = api
    d = room(store)
    sibling = room(store, "b" * 32)
    foreign = room(store, owner=B["x-workspace-owner"])
    tmp = store.root / "tmp" / "upload"
    tmp.write_bytes(b"uploaded video stays")
    clip = store.add(A["x-workspace-owner"], "video.mp4", "video/mp4", tmp, 3)
    before = store.quota(A["x-workspace-owner"])
    size = sum(p.stat().st_size for p in d.rglob("*") if p.is_file())
    assert c.delete(BASE + RID).status_code == 401
    missing = c.delete(BASE + "c" * 32, headers=B)
    # Same id exists in both owners: deleting B's id cannot touch A's room.
    assert c.delete(BASE + RID, headers=B).status_code == 200
    assert not foreign.exists() and d.exists()
    assert c.delete(BASE + RID, headers=B).status_code == missing.status_code == 404
    response = c.delete(BASE + RID, headers=A)
    assert response.status_code == 200, response.text
    assert response.json()["quota"]["storage_bytes_used"] == before["storage_bytes_used"] - size
    assert response.json()["quota"]["uploads_today"] == before["uploads_today"]
    assert not d.exists() and sibling.exists()
    assert store.path(A["x-workspace-owner"], clip["id"]).read_bytes() == b"uploaded video stays"
    assert c.get(BASE + RID, headers=A).status_code == 404
    assert [r["id"] for r in c.get(BASE[:-1], headers=A).json()["rooms"]] == ["b" * 32]


@pytest.mark.parametrize("state", ["queued", "running", "sampling", "reconstructing", "building lab shell"])
def test_build_states_refuse_deletion(api, state):
    c, store, _ = api
    d = room(store, state=state)
    assert c.delete(BASE + RID, headers=A).status_code == 409
    assert (d / "objects" / "room-object-1.glb").is_file()


@pytest.mark.parametrize("state", ["pending", "queued", "running"])
def test_sf3d_pending_or_running_refuses_deletion(api, state):
    c, store, _ = api
    d = room(store)
    (d / "room.json").write_text(json.dumps({"shell": {"kept": [{"upgrade": {"state": state}}]}}))
    assert c.delete(BASE + RID, headers=A).status_code == 409
    assert d.is_dir()


def test_sf3d_worker_still_finishing_refuses_deletion(api, monkeypatch):
    c, store, _ = api
    d = room(store)
    monkeypatch.setattr(shape_upgrade, "_running", {str(d)})
    assert c.delete(BASE + RID, headers=A).status_code == 409


def test_prepared_sf3d_batch_refuses_before_background_thread_starts(api):
    c, store, _ = api
    d = room(store)
    (d / "shape-upgrades.json").write_text(json.dumps({"inputs": [{"id": "object-1"}], "process": shape_upgrade._PROCESS}))
    assert c.delete(BASE + RID, headers=A).status_code == 409


@pytest.mark.parametrize("state", ["failed", "cancelled"])
def test_terminal_jobs_can_be_deleted(api, state):
    c, store, _ = api
    d = room(store, state=state)
    assert c.delete(BASE + RID, headers=A).status_code == 200
    assert not d.exists()


def test_linked_artifact_is_refused_before_any_removal(api, tmp_path):
    c, store, _ = api
    d = room(store)
    shared = tmp_path / "shared.glb"
    shared.write_bytes(b"shared pack must stay")
    try:
        (d / "objects" / "shared.glb").symlink_to(shared)
    except OSError:
        pytest.skip("host does not allow creating symbolic links")
    assert c.delete(BASE + RID, headers=A).status_code == 409
    assert shared.read_bytes() == b"shared pack must stay"
    assert (d / "status.json").is_file() and (d / "scene.json").is_file()


def test_escaping_resolved_path_is_refused_even_without_host_symlink_privileges(api, tmp_path, monkeypatch):
    c, store, _ = api
    d = room(store)
    original = Path.resolve
    mesh = d / "objects" / "room-object-1.glb"
    monkeypatch.setattr(Path, "resolve", lambda p, *a, **kw: tmp_path / "shared.glb" if p == mesh else original(p, *a, **kw))
    assert c.delete(BASE + RID, headers=A).status_code == 409
    assert mesh.is_file() and (d / "status.json").is_file()


def test_io_failure_keeps_status_for_retry(api, monkeypatch):
    c, store, _ = api
    d = room(store)
    original = Path.unlink
    with monkeypatch.context() as patch:
        def fail_mesh(path, *args, **kwargs):
            if path.name.endswith(".glb"):
                raise PermissionError("synthetic locked file")
            return original(path, *args, **kwargs)
        patch.setattr(Path, "unlink", fail_mesh)
        assert c.delete(BASE + RID, headers=A).status_code == 503
    assert (d / "status.json").is_file()
    assert c.delete(BASE + RID, headers=A).status_code == 200


@pytest.mark.parametrize("operation", ["shell", "objects"])
def test_inflight_manual_rebuild_or_object_job_is_busy_and_releases_after_error(api, monkeypatch, operation):
    c, store, app = api
    room(store)
    entered, release = threading.Event(), threading.Event()

    def blocked(*args, **kwargs):
        entered.set()
        assert release.wait(5), "test did not release the fake job"
        raise RuntimeError("synthetic job failed")

    monkeypatch.setattr(objects, "build_shell_files", blocked)
    monkeypatch.setattr(objects.object_lift, "view_png", lambda *_: (b"png", 10, 10))
    app.include_router(objects.create_router(store, segment=blocked))
    payload = {"sf3d": False} if operation == "shell" else {"view": 0, "point": [1, 1]}
    with ThreadPoolExecutor() as pool:
        future = pool.submit(c.post, BASE + RID + "/" + operation, headers=A, json=payload)
        try:
            assert entered.wait(5)
            assert c.delete(BASE + RID, headers=A).status_code == 409
        finally:
            release.set()
        assert future.result().status_code == 502
    assert c.delete(BASE + RID, headers=A).status_code == 200
