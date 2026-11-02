import json

from Build.api.storage.preview import track_preview, project_previews
from Build.api.storage.files import Store
from Build.api.experiment import _SCHEMA


def test_only_actual_frame_pixels_not_relative_trajectory_and_bounded_size():
    plot = track_preview({"trajectory": {"x": [0, 1], "y": [0, 1], "unit": "px"}})
    assert plot["kind"] == "plot" and plot["points"] == [[0, 1], [1, 0]]
    assert "not aligned to video" in plot["label"]
    assert track_preview({"track": {"width": 20, "height": 30, "frames": [[0, 0, float('nan'), 1]]}}) is None
    result = {"track": {"width": 20, "height": 30, "frames": [[i, i / 30, i % 20, i % 30] for i in range(800)]}}
    preview = track_preview(result)
    assert len(preview["points"]) <= 160
    assert preview["points"][:2] == [[0, 0], [5, 5]]
    assert preview["label"].startswith("MEASURED")
    assert preview["kind"] == "frame"


def test_latest_done_preview_is_owner_scoped(tmp_path):
    store = Store(tmp_path)
    try:
        assert project_previews(store, "a") == {}
        store.db.execute(_SCHEMA)
        result = json.dumps({"track": {"width": 10, "height": 10, "frames": [[0, 0, 2, 3], [1, .1, 4, 5]]}})
        for eid, owner, updated, data in [("old", "a", "1", result), ("new", "a", "2", "{}"), ("private", "b", "3", result)]:
            store.db.execute("INSERT INTO experiments VALUES (?,?,?,?,?,?,?,?,?,?)", (eid, owner, "project", "file", "done", "{}", data, None, "1", updated))
        assert project_previews(store, "a") == {"project": None}
        assert project_previews(store, "b")["project"]["points"] == [[2, 3], [4, 5]]
        assert project_previews(store, "b")["project"]["file_id"] == "file"
    finally:
        store.db.close()
