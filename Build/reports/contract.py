"""Report data contract: every number is a reference into fitter output.

A report is JSON with NO raw numerics outside `numbers`. Narrative text holds only
`{{id}}` placeholders that resolve to `numbers` entries; each entry is re-resolved against the
fitter result by path and must match it exactly, with the fitter's own unit and
source label (a label is never upgraded, e.g. simulated -> measured).
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from typing import Any, Mapping

SCHEMA = "r2s.report/1"
TEMPLATES = frozenset(("free_fall", "pendulum", "projectile", "ramp"))
LABELS = frozenset(("measured", "simulated"))
_ID = re.compile(r"[a-z][a-z_]*")  # digit-free so ids cannot smuggle numerals into prose
_PLACEHOLDER = re.compile(r"\{\{([^{}]*)\}\}")
_PATH = re.compile(r"^([a-z_]+)(?:\.([a-z_]+))?(?:\[(\d+)\])?$")
# shortcut: English number words only; other languages/spelled fractions need a real NLP check, upgrade if S14 text is multilingual.
_WORDS = re.compile(r"\b(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
                    r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|"
                    r"forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|half|"
                    r"quarter|dozen|point|once|twice|double|triple)\b", re.I)
_TOP = frozenset(("schema", "template", "fitter_digest", "title", "sections", "numbers"))
_SECTION = frozenset(("id", "title", "text"))
_ENTRY = frozenset(("path", "value", "unit", "label", "uncertainty_path", "uncertainty"))
# path -> (unit source, source object). Unit is read from the fitter result, never typed by an author.
_FIELDS = {
    "gravity.value": ("gravity.unit", "gravity.source"),
    "gravity.uncertainty": ("gravity.unit", "gravity.source"),
    "covariance.variance": ("covariance.variance_unit", "covariance.source"),
    "covariance.standard_error": ("covariance.standard_error_unit", "covariance.source"),
    "fit.rss": (("fit.units.position", "^2"), "fit.source"),
    "fit.rmse": ("fit.units.position", "fit.source"),
    "fit.fitted": ("fit.units.position", "fit.source"),
    "fit.residuals": ("fit.units.position", "fit.source"),
    "fit.dof": ("1", "fit.source"),
    "fit.n": ("1", "fit.source"),
    "fit.rank": ("1", "fit.source"),
    "uncertainty.residual_variance_floor": (("fit.units.position", "^2"), "fit.source"),
    "model_selection.aic": ("1", "model_selection.source"),
    "model_selection.selected_degree": ("1", "model_selection.source"),
}


class ReportError(ValueError):
    """Report violates the numeric-traceability contract."""


def digest(fitter_result: Mapping[str, Any]) -> str:
    blob = json.dumps(fitter_result, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return "sha256:" + hashlib.sha256(blob.encode()).hexdigest()


def _num(value: Any, name: str) -> float | int:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ReportError(f"{name}_must_be_finite_number")
    return value


def _get(result: Mapping[str, Any], dotted: str) -> Any:
    node: Any = result
    for part in dotted.split("."):
        if not isinstance(node, Mapping) or part not in node:
            raise ReportError(f"fitter_field_missing: {dotted}")
        node = node[part]
    return node


def resolve(fitter_result: Mapping[str, Any], path: str) -> tuple[float | int, str, str]:
    """Return (value, unit, label) for a fitter path like `gravity.value` or `fit.residuals[2]`."""
    if not isinstance(fitter_result, Mapping) or fitter_result.get("status") != "ok":
        raise ReportError("fitter_result_must_have_status_ok")
    m = _PATH.match(path) if isinstance(path, str) else None
    if not m:
        raise ReportError(f"bad_path: {path!r}")
    field = m.group(1) + ("." + m.group(2) if m.group(2) else "")
    if field not in _FIELDS:
        raise ReportError(f"path_not_reportable: {field}")
    node = _get(fitter_result, field)
    if m.group(3) is not None:
        if not isinstance(node, list) or int(m.group(3)) >= len(node):
            raise ReportError(f"index_out_of_range: {path}")
        node = node[int(m.group(3))]
    elif isinstance(node, list):
        raise ReportError(f"index_required: {path}")
    unit_src, label_src = _FIELDS[field]
    unit = unit_src if unit_src == "1" else (
        _get(fitter_result, unit_src[0]) + unit_src[1] if isinstance(unit_src, tuple) else _get(fitter_result, unit_src))
    if not isinstance(unit, str) or not unit:
        raise ReportError(f"fitter_unit_missing: {path}")
    label = _get(fitter_result, label_src).get("label")
    if label not in LABELS:
        raise ReportError(f"fitter_label_invalid: {path}")
    return _num(node, path), unit, label


def number_entry(fitter_result: Mapping[str, Any], path: str, uncertainty_path: str | None = None) -> dict[str, Any]:
    """The only intended way to create a `numbers` entry: copy it from fitter output."""
    value, unit, label = resolve(fitter_result, path)
    entry: dict[str, Any] = {"path": path, "value": value, "unit": unit, "label": label}
    if uncertainty_path is not None:
        u, u_unit, _ = resolve(fitter_result, uncertainty_path)
        if u_unit != unit:
            raise ReportError("uncertainty_unit_must_match_value_unit")
        entry.update(uncertainty_path=uncertainty_path, uncertainty=u)
    return entry


def _prose(text: Any, name: str) -> list[str]:
    """Validate narrative; return placeholder ids. Digits, numerals and number words are refused."""
    if not isinstance(text, str) or not text.strip():
        raise ReportError(f"{name}_must_be_nonempty_string")
    ids = _PLACEHOLDER.findall(text)
    rest = _PLACEHOLDER.sub(" ", text)
    if "{{" in rest or "}}" in rest:
        raise ReportError(f"{name}_malformed_placeholder")
    if any(unicodedata.numeric(c, None) is not None for c in rest) or _WORDS.search(rest):
        raise ReportError(f"{name}_contains_unreferenced_number")
    return ids


def validate_report(report: Any, fitter_result: Mapping[str, Any]) -> dict[str, Any]:
    """Return `report` if every number traces to `fitter_result`; else raise ReportError."""
    if not isinstance(report, Mapping) or set(report) != _TOP:
        raise ReportError(f"report_fields_must_be_exactly: {sorted(_TOP)}")
    if report["schema"] != SCHEMA:
        raise ReportError("unsupported_schema")
    if report["template"] not in TEMPLATES:
        raise ReportError("unknown_template")
    if report["fitter_digest"] != digest(fitter_result):
        raise ReportError("fitter_digest_mismatch")
    numbers = report["numbers"]
    if not isinstance(numbers, Mapping):
        raise ReportError("numbers_must_be_object")
    for nid, entry in numbers.items():
        if not isinstance(nid, str) or not _ID.fullmatch(nid):
            raise ReportError(f"bad_number_id: {nid!r}")
        if not isinstance(entry, Mapping) or not {"path", "value", "unit", "label"} <= set(entry) <= _ENTRY:
            raise ReportError(f"bad_number_entry: {nid}")
        value, unit, label = resolve(fitter_result, entry["path"])
        if type(entry["value"]) is not type(value) or entry["value"] != value:
            raise ReportError(f"value_not_from_fitter: {nid}")
        if entry["unit"] != unit or entry["label"] != label:
            raise ReportError(f"unit_or_label_not_from_fitter: {nid}")
        if ("uncertainty" in entry) != ("uncertainty_path" in entry):
            raise ReportError(f"uncertainty_needs_path_and_value: {nid}")
        if "uncertainty" in entry:
            u, u_unit, _ = resolve(fitter_result, entry["uncertainty_path"])
            if type(entry["uncertainty"]) is not type(u) or entry["uncertainty"] != u or u_unit != unit:
                raise ReportError(f"uncertainty_not_from_fitter: {nid}")
    used: set[str] = set()
    ids = _prose(report["title"], "title")
    if not isinstance(report["sections"], list) or not report["sections"]:
        raise ReportError("sections_must_be_nonempty_list")
    for i, sec in enumerate(report["sections"]):
        if not isinstance(sec, Mapping) or set(sec) != _SECTION:
            raise ReportError(f"section[{i}]_fields_must_be_exactly: {sorted(_SECTION)}")
        if not isinstance(sec["id"], str) or not _ID.fullmatch(sec["id"]):
            raise ReportError(f"section[{i}]_bad_id")
        ids += _prose(sec["title"], f"section[{i}].title")
        if not isinstance(sec["text"], list) or not sec["text"]:
            raise ReportError(f"section[{i}].text_must_be_nonempty_list")
        for j, para in enumerate(sec["text"]):
            ids += _prose(para, f"section[{i}].text[{j}]")
    used.update(ids)
    unknown = used - set(numbers)
    if unknown:
        raise ReportError(f"placeholder_without_number: {sorted(unknown)}")
    return dict(report)
