"""S12a withheld-frame boundary: freeze held-out suffix before any fit.

Scale-free (image-height-normalized) only. Gate M is NOT_MET: no calibrated g,
scale, clock or physical-accuracy claim may come from anything in this module.
"""
from dataclasses import dataclass
import hashlib
import json
import math
import sys
from pathlib import Path

from Build.fitter import select_model

GATE_M = "NOT_MET"
LIMITS = ("Gate M NOT_MET: no calibrated scale or capture clock",
          "positions are image-height fractions, not metres; no calibrated g",
          "no physical-accuracy claim")


def _sha(rows):
    text = json.dumps(rows, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()


@dataclass(frozen=True)
class Boundary:
    """Holds the training prefix and only HASHES of the suffix (never its values)."""
    clip_id: str
    source_sha256: str
    last_training_frame: int
    training: tuple  # ((frame_index, pts_s, y_norm), ...)
    training_sha256: str
    suffix_identity_sha256: str  # (frame_index, pts_s) sealed before any fit
    suffix_observation_sha256: str | None  # None until suffix is tracked
    suffix_count: int
    gate_m: str = GATE_M


def _increasing(rows, what):
    for row in rows:
        if type(row[0]) is not int or row[0] < 0 or type(row[1]) not in (int, float) \
                or not math.isfinite(row[1]):
            raise ValueError(f"{what}: integer frame_index and finite pts_s required")
    if any(b[0] <= a[0] or b[1] <= a[1] for a, b in zip(rows, rows[1:])):
        raise ValueError(f"{what}: frame indices and PTS must strictly increase")


def split(record, suffix_identities=None):
    """Return (Boundary, sealed_suffix).

    Suffix observations come from record frames after last_training_frame; for
    an untracked suffix pass suffix_identities [(frame_index, pts_s), ...] instead.
    Every suffix frame must follow the prefix in BOTH index and PTS (no overlap).
    """
    last, height = record["last_training_frame"], record["height_px"]
    if type(last) is not int or type(height) is not int or height <= 0:
        raise ValueError("integer last_training_frame and positive height_px required")
    rows = [(f["frame_index"], f["pts_s"], f["y_px"]) for f in record["frames"]]
    _increasing(rows, "frames")
    if any(type(y) not in (int, float) or not 0 <= y < height for *_, y in rows):
        raise ValueError("y_px must lie inside the source image")
    training = tuple((i, p, y / height) for i, p, y in rows if i <= last)
    observed = tuple((i, p, y / height) for i, p, y in rows if i > last)
    if len(training) < 3 or training[-1][0] != last:
        raise ValueError("split must end a >=3-frame training prefix")
    if observed and suffix_identities is not None:
        raise ValueError("give suffix observations OR identities, not both")
    identities = tuple((i, p) for i, p, _ in observed) if observed else \
        tuple((i, p) for i, p in (suffix_identities or ()))
    if not identities:
        raise ValueError("nonempty held-out suffix required")
    _increasing(identities, "suffix")
    if identities[0][0] <= last or identities[0][1] <= training[-1][1]:
        raise ValueError("suffix overlaps the training prefix (index or PTS)")
    sealed = observed or identities
    return Boundary(record["clip_id"], record["source_sha256"], last, training,
                    _sha(training), _sha(identities),
                    _sha(observed) if observed else None, len(identities)), sealed


def verify(boundary, sealed):
    """Raise unless the prefix and suffix are identical to what was frozen."""
    if _sha(boundary.training) != boundary.training_sha256:
        raise ValueError("training prefix changed after freeze")
    if _sha(tuple((i, p) for i, p, *_ in sealed)) != boundary.suffix_identity_sha256:
        raise ValueError("held-out suffix identities changed after freeze")
    if boundary.suffix_observation_sha256 is not None and \
            _sha(tuple(sealed)) != boundary.suffix_observation_sha256:
        raise ValueError("held-out suffix observations changed after freeze")


def fit_prefix(boundary, degrees=(1, 2)):
    """Fit ONLY boundary.training; the suffix is not reachable from a Boundary."""
    origin = boundary.training[0][1]
    # shortcut: fitter labels positions "m"; values are image-height fractions (Gate M NOT_MET).
    return select_model([p - origin for _, p, _ in boundary.training],
                        [y for *_, y in boundary.training], degrees)


def record_json(boundary, **extra):
    fields = {k: v for k, v in boundary.__dict__.items() if k != "training"}
    return {"boundary": fields | {"training_count": len(boundary.training)},
            "gate_m": GATE_M, "units": "image-height fraction (scale-free)",
            "limitations": list(LIMITS)} | extra


def main(root=Path(__file__).resolve().parents[2]):
    """Freeze the real ST03 boundary from accepted S07b evidence (no media, no fit)."""
    def load(rel):
        raw = (root / rel).read_bytes()
        return json.loads(raw), {"path": rel, "sha256": hashlib.sha256(raw).hexdigest()}
    result, track_src = load("evidence/S07/S07b/orch14/result.json")
    pmap, map_src = load("evidence/S07/S07b/recovery3/presentation-map.json")
    gate, gate_src = load("evidence/S07/S07f/actual-gate-m.json")
    record = result["record"]
    source_pts = {f["source_frame_index"]: float(f["pts_time"]) for f in pmap["frames"]}
    conflicts = [{"frame_index": f["frame_index"], "record_pts_s": f["pts_s"],
                  "source_map_pts_s": source_pts[f["frame_index"]]}
                 for f in record["frames"]
                 if abs(f["pts_s"] - source_pts[f["frame_index"]]) > 1e-6]
    last_pts = max([f["pts_s"] for f in record["frames"]] +
                   [c["source_map_pts_s"] for c in conflicts])
    after = [(i, p) for i, p in sorted(source_pts.items()) if i > record["last_training_frame"]]
    # Quarantine suffix frames whose PTS a conflicting training timestamp already used.
    quarantined = [i for i, p in after if p <= last_pts]
    boundary, _ = split(record, [(i, p) for i, p in after if p > last_pts])
    out = record_json(
        boundary, gate_m_source=gate_src | {"status": gate["gate"]["status"]},
        inputs=[track_src, map_src], pts_conflicts=conflicts,
        quarantined_suffix_frames=quarantined, fit_run=False,
        note=("Suffix observations NOT tracked yet; S12c must track exactly these sealed "
              "identities and verify() before scoring. Prefix fit withheld until the "
              "PTS conflict is resolved by S07 owner/controller."))
    path = root / "evidence/S12/boundary-ST03.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"{path.relative_to(root).as_posix()} gate_m={GATE_M} conflicts={len(conflicts)} "
          f"quarantined={quarantined} suffix={boundary.suffix_count}")


if __name__ == "__main__":
    sys.exit(main())
