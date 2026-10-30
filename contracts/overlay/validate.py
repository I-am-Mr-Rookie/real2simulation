"""overlay/2.0.0: predicted traces tied to clip id, source sha and the source PTS frame timebase.

Stdlib only. validate() returns immutable traces; renderers consume them read-only.
Values are image-height fractions (scale-free); Gate M NOT_MET is mandatory.
overlay/1.0.0 (prediction/v1 digests over [kind, model, trace] only) is readable solely with legacy=True.
"""
import hashlib
import json
import math
from typing import NamedTuple

VERSION, LEGACY_VERSION = "overlay/2.0.0", "overlay/1.0.0"
PTS_TOL_S = 1e-6  # same tolerance as the S12c errata vs presentation-map agreement check
KEYS = {"contract_version", "clip_id", "source_sha256", "provenance", "units", "gate_m", "limits",
        "timebase", "traces"}
LEGACY_TRACE_KEYS = {"kind", "clip_id", "training_sha256", "suffix_identity_sha256", "model", "trace",
                     "sha256", "gate_m"}
TRACE_KEYS = LEGACY_TRACE_KEYS | {"source_sha256", "suffix_count", "commitment"}
PROVENANCE = {"synthetic", "image-derived"}


class OverlayError(ValueError):
    pass


class Trace(NamedTuple):
    kind: str
    prediction_sha256: str
    model: str
    rows: tuple  # ((frame_index, pts_s, value, sigma_or_None), ...)
    commitment: str = "prediction/v2"


def _sha(obj):
    # Identical to Build.real2sim.boundary._sha (prediction hashes are recomputed with it).
    return hashlib.sha256(json.dumps(obj, separators=(",", ":")).encode()).hexdigest()


def frame_map_sha256(frame_map):
    """frame_map: {frame_index: pts_s} from the source presentation map."""
    return _sha(sorted([int(i), float(p)] for i, p in frame_map.items()))


def _num(v):
    return type(v) in (int, float) and math.isfinite(v)


def _commitment(t):
    # Identical to Build.real2sim.predict.commitment_sha256 for prediction/v2 (R-RS F1-R custody binding).
    return _sha(["prediction/v2", t["kind"], t["model"], t["trace"], t["clip_id"], t["source_sha256"],
                 t["training_sha256"], t["suffix_identity_sha256"], t["suffix_count"]])


def validate(doc, clip_id, source_sha256, frame_map, legacy=False):
    """Raise OverlayError unless doc aligns with this clip/source/timebase; return tuple of Trace."""
    def need(ok, why):
        if not ok:
            raise OverlayError(why)
    need(isinstance(doc, dict) and set(doc) == KEYS, "overlay fields differ from the overlay contract")
    v1 = doc["contract_version"] == LEGACY_VERSION
    need(doc["contract_version"] == VERSION or (v1 and legacy),
         "unsupported contract_version (overlay/1.0.0 is legacy-audit only: legacy=True, never new evidence)")
    need(doc["gate_m"] == "NOT_MET", "gate_m must be NOT_MET")
    need(doc["units"] == "image-height fraction", "units must be scale-free image-height fraction")
    need(doc["provenance"] in PROVENANCE, "provenance must be synthetic or image-derived")
    need(doc["clip_id"] == clip_id, "overlay is for a different clip")
    need(doc["source_sha256"] == source_sha256, "overlay is for a different source file")
    tb = doc["timebase"]
    need(isinstance(tb, dict) and tb.get("kind") == "pts_s", "timebase kind must be pts_s")
    need(tb.get("frame_map_sha256") == frame_map_sha256(frame_map), "timebase differs from the source frame map")
    pts = {int(i): float(p) for i, p in frame_map.items()}
    need(isinstance(doc["traces"], list) and doc["traces"], "at least one trace required")
    out = []
    for n, t in enumerate(doc["traces"]):
        need(isinstance(t, dict) and set(t) == (LEGACY_TRACE_KEYS if v1 else TRACE_KEYS), f"traces[{n}]: fields differ")
        need(t["clip_id"] == clip_id and t["gate_m"] == "NOT_MET", f"traces[{n}]: clip or gate_m mismatch")
        if v1:
            need(_sha([t["kind"], t["model"], t["trace"]]) == t["sha256"], f"traces[{n}]: trace changed after hashing")
        else:
            need(t["commitment"] == "prediction/v2" and t["source_sha256"] == source_sha256,
                 f"traces[{n}]: not a prediction/v2 commitment for this source")
            need(_commitment(t) == t["sha256"], f"traces[{n}]: trace or custody metadata changed after commitment")
        rows = tuple(tuple(r) for r in t["trace"])
        need(rows, f"traces[{n}]: empty trace")
        for r in rows:
            need(len(r) == 4 and type(r[0]) is int and _num(r[1]) and _num(r[2])
                 and (r[3] is None or (_num(r[3]) and r[3] >= 0)), f"traces[{n}]: malformed row {r}")
            need(r[0] in pts and abs(r[1] - pts[r[0]]) <= PTS_TOL_S,
                 f"traces[{n}]: frame {r[0]} not aligned to the source timebase")
        need(all(b[0] > a[0] for a, b in zip(rows, rows[1:])), f"traces[{n}]: frames must increase")
        # R-RS F1: the declared seal hash must be the hash of this trace's complete (frame, PTS) identities.
        need(_sha([[r[0], r[1]] for r in rows]) == t["suffix_identity_sha256"],
             f"traces[{n}]: suffix_identity_sha256 does not match the trace's sealed (frame, PTS) identities")
        need(v1 or t["suffix_count"] == len(rows), f"traces[{n}]: suffix_count differs from the complete trace")
        out.append(Trace(t["kind"], t["sha256"], t["model"], rows, "prediction/v1" if v1 else "prediction/v2"))
    return tuple(out)
