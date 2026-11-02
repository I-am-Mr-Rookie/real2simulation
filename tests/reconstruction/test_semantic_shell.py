"""N52 semantic shell regressions. Synthetic masks/points only, no network or private media."""
from unittest.mock import patch
import json
import io

import numpy as np
import pytest

from Build.measurement import hosted_sam
from Build.reconstruction import object_lift, room_shell as rs
from Build.reconstruction._sam_mask_codec import _encode_raster


def test_colour_uses_box_local_sam_mask_at_the_correct_frame_pixels():
    bits = np.array([[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]], np.uint8)
    encoded = _encode_raster(bits.ravel().tolist(), 4, 3)
    text = f"<0f>7<|box;x1=4;y1=5;x2=7;y2=7;w=12;h=10|><|mask;x=0;y=0;data=3,4,{encoded}|>"
    instance, = hosted_sam.image_instances(text, 12, 10)
    rgb = np.full((10, 12, 3), 0.5)
    rgb[5:7, 5:7] = [0.1, 0.7, 0.2]
    assert rs.hex_color(rgb[instance["mask"]]) == "#1ab333"
    assert instance["mask"].sum() == 4
    assert not instance["mask"][:5].any()
    with pytest.raises(ValueError, match="dimensions"):
        hosted_sam.image_instances(text, 13, 10)
    with pytest.raises(ValueError):
        hosted_sam.image_instances(text.replace("data=3,4,", "data=4,4,"), 12, 10)
    with pytest.raises(ValueError):
        hosted_sam.image_instances(text.replace(encoded, encoded[:-1]), 12, 10)
    response = {"status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": text}]}]}
    with patch.object(object_lift, "_sam_image", return_value=response):
        boxes = object_lift.sam_text(b"png", "chair", 12, 10)
    assert json.loads(json.dumps(boxes)) == [[4, 5, 7, 7]]  # historical box caches/callers stay compatible
    np.testing.assert_array_equal(boxes[0].mask, instance["mask"])
    response["output"][0]["content"][0]["text"] = text.replace(encoded, encoded[:-1])
    with patch.object(object_lift, "_sam_image", return_value=response):
        fallback, = object_lift.sam_text(b"png", "chair", 12, 10)
    assert fallback.mask is None and "decode failed" in fallback.mask_error
    with patch.object(object_lift, "_sam_image", return_value=response), pytest.raises(ValueError, match="dimensions"):
        object_lift.sam_text(b"png", "chair", 13, 10)  # fallback must not weaken the box/frame boundary


def points_view():
    x, y = np.meshgrid(np.linspace(-0.6, 0.6, 30), np.linspace(0.7, 1.8, 30))
    pts = np.stack([x, y, np.full_like(x, 1.4)], axis=-1)
    return {"pts_img": pts, "mask": np.ones(900, bool)}


ROOM = {"scale": {"metres_per_model_unit": 1}}


def test_opening_projects_to_extent_wall_and_clips_its_height():
    walls = [{"axis": 1, "side": 1, "plane": 2.0, "span": [-2, 2], "height": 1.6, "status": "EXTENT"},
             {"axis": 0, "side": -1, "plane": -2.0, "span": [-2, 2], "height": 2.5, "status": "FIT"}]
    with patch.object(rs.live_room, "load_views", return_value=[points_view()]), \
         patch.object(object_lift, "_room_frame", return_value=(np.eye(3), np.zeros(3))):
        hole = rs.opening(b"fake", 0, [0, 0, 29, 29], ROOM, 0, walls, "window")
        door = rs.opening(b"fake", 0, [0, 0, 29, 29], ROOM, 0, walls, "door")
    assert hole["wall"] == 0 and "EXTENT" in hole["placement"]
    assert hole["y"][1] == 1.6 and door["y"][0] == 0
    panels = rs.wall_objects(0, walls, [hole])
    assert any(o.get("look", {}).get("category") == "window" for o in panels)


def proxy(position=(0, 0.45, 0), size=(0.6, 0.9, 0.6)):
    return {"position": list(position), "size": list(size), "rotation": [0, 0, 0, 1], "points": 900,
            "mask": np.ones((30, 30), bool), "size_sd": [0.1] * 3}


def test_size_prior_splits_mask_without_inventing_empty_cells():
    x, z = np.meshgrid(np.linspace(-0.74, 0.74, 30), np.linspace(-0.29, 0.29, 30))
    view = {"pts_img": np.stack([x, np.full_like(x, 0.5), z], axis=-1)}
    item = {"noun": "chair", "view": 0, "proxy": proxy(size=(1.5, 0.9, 0.6)), "instance": 0}
    with patch.object(rs.live_room, "load_views", return_value=[view]), \
         patch.object(object_lift, "_room_frame", return_value=(np.eye(3), np.zeros(3))):
        parts = rs.split_item(b"fake", ROOM, item)
    assert len(parts) == 2
    assert all(p["proxy"]["size"][0] <= 0.8 for p in parts)
    assert sum(p["proxy"]["mask"].sum() for p in parts) == 900
    assert not (parts[0]["proxy"]["mask"] & parts[1]["proxy"]["mask"]).any()
    assert all("MODEL-ESTIMATED" in p["split"] for p in parts)


def test_distinct_chairs_in_the_same_view_do_not_merge():
    proxies = [proxy(position=(-0.1, 0.45, 0)), proxy(position=(0.1, 0.45, 0))]
    with patch.object(object_lift, "lift", side_effect=proxies):
        kept, _ = rs.furniture(b"fake", ROOM, [(0, "chair", [0, 0, 29, 29])] * 2)
    assert len(kept) == 2


def test_chair_is_not_swallowed_by_a_nearby_table_and_live_box_mask_reaches_lift():
    p = proxy()
    table = {**proxy(), "camera": [0, 1.5, 0]}
    detection = object_lift.SamBox([0, 0, 29, 29], p["mask"])
    with patch.object(object_lift, "lift", side_effect=[table, p]) as lift, \
         patch.object(rs, "_heights", return_value=(np.full(900, 0.7), np.ones(900, bool))):
        kept, _ = rs.furniture(b"fake", ROOM, [(0, "table", [0, 0, 29, 29]), (0, "chair", detection)])
    assert lift.call_args.args[-1] is p["mask"]
    assert [it["noun"] for it in kept] == ["table", "chair"]


def test_colour_preserves_dark_uint8_values_and_ignores_invalid_points():
    assert rs.hex_color(np.array([[0, 1, 0]], np.uint8)) == "#000100"
    assert rs.hex_color([[np.nan, 0, 0], [0.1, 0.7, 0.2]]) == "#1ab333"


def test_hosted_instance_mask_reaches_the_finished_shell_colour():
    from tests.reconstruction.test_object_lift import room_npz, H, W
    original, hit = room_npz()
    archive = np.load(io.BytesIO(original))
    arrays = {name: archive[name] for name in archive.files}
    for view in range(2):
        arrays[f"view{view}_img_no_norm"][0][hit] = [0.125, 0.75, 0.25]
    buf = io.BytesIO()
    np.savez(buf, **arrays)
    npz = buf.getvalue()
    rr, cc = np.nonzero(hit)
    x1, y1, x2, y2 = int(cc.min()), int(rr.min()), int(cc.max()), int(rr.max())
    crop = hit[y1:y2 + 1, x1:x2 + 1]
    payload = _encode_raster(crop.astype(int).ravel().tolist(), crop.shape[1], crop.shape[0])
    text = f"<0f>0<|box;x1={x1};y1={y1};x2={x2};y2={y2};w={W};h={H}|><|mask;x=0;y=0;data={crop.shape[0]},{crop.shape[1]},{payload}|>"

    def response(png, prompt, *args):
        return {"status": "completed", "output": [{"type": "message", "content": [
            {"type": "output_text", "text": text if prompt == "chair" else ""}]}]}

    _, _, room, scene = rs.live_room.analyse(npz)
    with patch.object(object_lift, "_sam_image", side_effect=response):
        result, _, _ = rs.build(npz, room, scene, object_lift.sam_text)
    chairs = [o for o in result["objects"] if o.get("look", {}).get("category") == "chair"]
    assert len(chairs) == 1
    assert chairs[0]["look"]["color"] == "#20bf40"


def test_chair_front_faces_nearest_table_and_sofa_preserves_its_long_axis():
    items = [{"noun": "chair", "proxy": proxy()}, {"noun": "table", "proxy": proxy((2, 0.4, 0))},
             {"noun": "table", "proxy": proxy((-5, 0.4, 0))}, {"noun": "sofa", "proxy": proxy((0, 0.5, 2))}]
    rs.face_furniture(items, [0, 0, -3])
    q = items[0]["proxy"]["rotation"]
    yaw = 2 * np.arctan2(q[1], q[3])
    np.testing.assert_allclose([np.sin(yaw), np.cos(yaw)], [1, 0], atol=1e-5)
    q = items[-1]["proxy"]["rotation"]
    assert abs(q[1]) > 0.99  # back at +z, front toward the table at z=0
    chair = {"noun": "chair", "proxy": proxy()}
    rs.face_furniture([chair], [0, 0, -3])
    assert abs(chair["proxy"]["rotation"][1]) > 0.99
