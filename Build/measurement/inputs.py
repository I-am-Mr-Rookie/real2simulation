"""Tracking input boundary; eligibility is not a measurement or verification receipt."""
from dataclasses import dataclass
import math
import re


@dataclass(frozen=True)
class Frame:
    frame_index: int
    pts_s: float
    x_px: float
    y_px: float


@dataclass(frozen=True)
class TrackingInput:
    training: tuple[Frame, ...]
    held_out: tuple[Frame, ...]
    blockers: tuple[str, ...]

    @property
    def metric_eligible(self):
        return not self.blockers


def _number(value, name, *, positive=False):
    try:
        finite = type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError(f"{name} must be finite numeric, not boolean")
    if value < 0 or (positive and value == 0):
        raise ValueError(f"{name} out of range")
    return value


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def validate_input(data):
    """Reject malformed data; retain explicit scientific/permission abstentions.

    Evidence strings are references for review, not proof checked by this function.
    Do not send held_out to a tracker/fitter/calibrator. See README for custody.
    """
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    for key in ("clip_id", "licence", "provenance", "motion"):
        if not _text(data.get(key)):
            raise ValueError(f"{key} required")
    if not isinstance(data.get("source_sha256"), str) or not re.fullmatch(
        r"[0-9a-f]{64}", data["source_sha256"]
    ):
        raise ValueError("source_sha256 must be lowercase hex")
    approval = data.get("approval")
    if not isinstance(approval, dict) or approval.get("scope") not in (
        "scene_tracking", "metric_measurement"
    ) or not _text(approval.get("evidence")):
        raise ValueError("explicit scoped approval evidence required")
    blockers = []
    if approval["scope"] != "metric_measurement":
        blockers.append("metric_use_not_approved")
    if data["motion"] != "earth_free_fall":
        blockers.append("not_earth_free_fall")
    if not _text(data.get("continuous_segment_evidence")):
        blockers.append("continuous_segment_unverified")

    scale = data.get("scale")
    clock = data.get("timebase")
    for section, name, fields in (
        (scale, "scale", (("m_per_px", True), ("uncertainty_m_per_px", False))),
        (clock, "timebase", (("capture_seconds_per_pts_second", True),
                             ("uncertainty_factor", False))),
    ):
        if section is not None and not isinstance(section, dict):
            raise ValueError(f"{name} must be null or an object")
        if section is not None:
            for field, positive in fields:
                if field in section:
                    _number(section[field], f"{name}.{field}", positive=positive)
    if not (scale and scale.get("method") == "independent_reference"
            and scale.get("plane_verified") is True and _text(scale.get("evidence"))
            and "m_per_px" in scale and "uncertainty_m_per_px" in scale):
        blockers.append("scale_unverified")
    if not (clock and clock.get("verified") is True and _text(clock.get("evidence"))
            and "capture_seconds_per_pts_second" in clock and "uncertainty_factor" in clock):
        blockers.append("capture_timebase_unverified")

    width, height = data.get("width_px"), data.get("height_px")
    if type(width) is not int or type(height) is not int or min(width, height) <= 0:
        raise ValueError("positive integer image dimensions required")
    frames = data.get("frames")
    split = data.get("last_training_frame")
    if not isinstance(frames, list) or type(split) is not int:
        raise ValueError("frames list and integer last_training_frame required")
    parsed = []
    for item in frames:
        if not isinstance(item, dict):
            raise ValueError("frame must be an object")
        index = item.get("frame_index")
        if type(index) is not int or index < 0:
            raise ValueError("frame_index must be a nonnegative integer")
        pts, x, y = (_number(item.get(key), key) for key in ("pts_s", "x_px", "y_px"))
        if x >= width or y >= height:
            raise ValueError("coordinates outside source image")
        if parsed and (index <= parsed[-1].frame_index or pts <= parsed[-1].pts_s):
            raise ValueError("frame indices and video PTS must strictly increase")
        parsed.append(Frame(index, pts, x, y))
    training = tuple(f for f in parsed if f.frame_index <= split)
    held_out = tuple(f for f in parsed if f.frame_index > split)
    if len(training) < 3 or not held_out or training[-1].frame_index != split:
        raise ValueError("split must end a >=3-frame prefix and leave a nonempty suffix")
    return TrackingInput(training, held_out, tuple(blockers))
