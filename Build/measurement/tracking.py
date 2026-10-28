"""Local SAM 3.1 training-prefix adapter; import never loads models or footage."""
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import re

from .inputs import Frame


def _local_path(value):
    if not isinstance(value, (str, Path)):
        raise ValueError("local filesystem path required")
    text = str(value)
    if "://" in text or text.startswith(("\\\\", "//")):
        raise ValueError("remote URLs/UNC resources are not supported")
    return Path(value)


@dataclass(frozen=True)
class TrainingTrack:
    training: tuple[Frame, ...]
    missing_frames: tuple[int, ...]
    metadata_json: str
    object_id: int

    def training_record(self):
        """Fresh JSON-compatible prefix, NOT a complete S07a evaluation record."""
        record = json.loads(self.metadata_json)
        record["frames"] = [asdict(frame) for frame in self.training]
        record["tracking"] = {
            "adapter": "sam3.1-local-multiplex-v1", "object_id": self.object_id,
            "point_method": "binary_mask_pixel_index_centroid",
            "missing_frames": list(self.missing_frames),
        }
        return record


def _context(metadata, frame_map, object_id):
    if not isinstance(metadata, dict) or "frames" in metadata or "held_out" in metadata:
        raise ValueError("metadata only; never pass held-out frames/coordinates")
    for key in ("clip_id", "licence", "provenance", "motion"):
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            raise ValueError(f"{key} required")
    if not isinstance(metadata.get("source_sha256"), str) or not re.fullmatch(
        r"[0-9a-f]{64}", metadata["source_sha256"]
    ):
        raise ValueError("source_sha256 must be lowercase hex")
    approval = metadata.get("approval")
    if not isinstance(approval, dict) or approval.get("scope") not in (
        "scene_tracking", "metric_measurement"
    ) or not isinstance(approval.get("evidence"), str) or not approval["evidence"].strip():
        raise ValueError("scoped approval receipt required; presence is not clearance")
    width, height = metadata.get("width_px"), metadata.get("height_px")
    if type(width) is not int or type(height) is not int or min(width, height) <= 0:
        raise ValueError("positive integer source dimensions required")
    split = metadata.get("last_training_frame")
    if type(split) is not int or split < 0 or type(object_id) is not int or object_id < 0:
        raise ValueError("nonnegative integer split and explicit object_id required")
    if not isinstance(frame_map, (tuple, list)) or len(frame_map) < 3:
        raise ValueError("at least three training frame mappings required")
    mapping = []
    for item in frame_map:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise ValueError("mapping entries are (source_frame_index, source_pts_s)")
        index, pts = item
        try:
            valid_pts = type(pts) in (int, float) and math.isfinite(pts) and pts >= 0
        except OverflowError:
            valid_pts = False
        if type(index) is not int or index < 0 or index > split or not valid_pts:
            raise ValueError("invalid training index/PTS or mapping crosses frozen split")
        if mapping and (index <= mapping[-1][0] or pts <= mapping[-1][1]):
            raise ValueError("source index and PTS must strictly increase")
        mapping.append((index, pts))
    if mapping[-1][0] != split:
        raise ValueError("mapping must end at frozen last_training_frame")
    try:
        snapshot = json.dumps(metadata, allow_nan=False, sort_keys=True)
    except (ValueError, TypeError, OverflowError) as error:
        raise ValueError("metadata must be finite JSON") from error
    return snapshot, tuple(mapping), width, height


def sanitize_responses(responses, metadata, frame_map, *, object_id):
    """Select one explicit stable ID; missing data remains missing, never filled.

    frame_map maps local predictor indices to original indices/PTS, prefix only.
    SAM's public response contains NumPy bool masks in original image dimensions.
    No bounding-box, confidence or assumed clock is substituted for a missing mask.
    """
    snapshot, mapping, width, height = _context(metadata, frame_map, object_id)
    import numpy as np

    try:
        iterator = iter(responses)
    except TypeError as error:
        raise ValueError("response stream must be iterable") from error
    observed = {}
    previous = -1
    for response in iterator:
        if not isinstance(response, dict):
            raise ValueError("response must be an object")
        index = response.get("frame_index")
        if type(index) is not int or not previous < index < len(mapping):
            raise ValueError("duplicate, unordered or out-of-prefix predictor frame")
        previous = index
        outputs = response.get("outputs")
        if not isinstance(outputs, dict):
            raise ValueError("outputs object required")
        try:
            ids = np.asarray(outputs["out_obj_ids"])
            masks = np.asarray(outputs["out_binary_masks"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("malformed SAM IDs/masks") from error
        if ids.ndim != 1 or ids.dtype.kind not in "iu" or (ids < 0).any():
            raise ValueError("object IDs must be nonnegative integers")
        if len(set(ids.tolist())) != len(ids):
            raise ValueError("duplicate object IDs are ambiguous")
        if masks.dtype.kind != "b" or masks.shape != (len(ids), height, width):
            raise ValueError("binary masks must have shape (objects, source_height, source_width)")
        selected = np.flatnonzero(ids == object_id)
        if not len(selected):
            continue
        mask = masks[selected[0]]
        # Axis sums avoid materializing an O(foreground_pixels) coordinate array.
        x_counts, y_counts = mask.sum(axis=0), mask.sum(axis=1)
        count = x_counts.sum()
        if not count:
            continue
        x = float(np.dot(x_counts, np.arange(width, dtype=float)) / count)
        y = float(np.dot(y_counts, np.arange(height, dtype=float)) / count)
        if not (math.isfinite(x) and math.isfinite(y) and 0 <= x < width and 0 <= y < height):
            raise ValueError("nonfinite or out-of-image centroid")
        source_index, pts = mapping[index]
        observed[index] = Frame(source_index, pts, x, y)
    return TrainingTrack(tuple(observed.values()),
                         tuple(source for i, (source, _) in enumerate(mapping) if i not in observed),
                         snapshot, object_id)


def load_local_predictor(checkpoint_path, *, execute=False):
    """Explicit heavy boundary. No weights download, auth, install or fallback."""
    if execute is not True:
        raise PermissionError("model construction requires explicit execute=True")
    checkpoint = _local_path(checkpoint_path)
    if not checkpoint.is_file() or checkpoint.is_symlink():
        raise ValueError("existing local SAM 3.1 checkpoint required")
    from sam3.model_builder import build_sam3_multiplex_video_predictor
    return build_sam3_multiplex_video_predictor(
        checkpoint_path=str(checkpoint.resolve()), compile=False, warm_up=False,
        async_loading_frames=False,
    )


def track_training(predictor, prefix_dir, metadata, frame_map, *, prompt, object_id,
                   execute=False):
    """Run documented local SAM calls on an independently prepared prefix ONLY.

    Custodian must verify rights, source/hash, JPEG geometry, mapping and custody.
    A frame limit on a full video cannot enforce holdout: start_session loads it.
    Therefore require an exact, separate 00000.jpg.. prefix directory, not MP4.
    """
    if execute is not True:
        raise PermissionError("tracking requires explicit execute=True")
    snapshot, mapping, _, _ = _context(metadata, frame_map, object_id)
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("nonempty text prompt required")
    directory = _local_path(prefix_dir)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("separate local prefix JPEG directory required")
    expected = {f"{i:05d}.jpg" for i in range(len(mapping))}
    entries = list(directory.iterdir())
    if {entry.name for entry in entries} != expected or any(
        not entry.is_file() or entry.is_symlink() for entry in entries
    ):
        raise ValueError("directory must contain exactly the mapped prefix JPEGs")
    response = predictor.handle_request(request={
        "type": "start_session", "resource_path": str(directory.resolve())})
    if not isinstance(response, dict) or not isinstance(response.get("session_id"), str) or not response["session_id"]:
        raise ValueError("predictor returned no usable session_id")
    session_id = response["session_id"]
    try:
        predictor.handle_request(request={"type": "add_prompt", "session_id": session_id,
                                          "frame_index": 0, "text": prompt})
        responses = predictor.handle_stream_request(request={
            "type": "propagate_in_video", "session_id": session_id,
            "propagation_direction": "forward", "start_frame_index": 0,
            "max_frame_num_to_track": len(mapping) - 1,
        })
        # Use propagated results, not the provisional add_prompt preview.
        return sanitize_responses(responses, json.loads(snapshot), mapping, object_id=object_id)
    finally:
        predictor.handle_request(request={"type": "close_session", "session_id": session_id})
