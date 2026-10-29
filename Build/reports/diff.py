"""S17e: re-run the fitter and diff every number a report shows against the fresh output (stdlib only).

Deliberately independent of contract.resolve / render._fmt: own path walk and own formatter, so a bug there cannot hide here.
Checks (1) fitter_digest, (2) every numbers[].value/uncertainty (exact value and type), (3) every numeric token in the rendered
HTML and TeX (tables, prose) is a fresh fitter value and every fresh reported value is shown, (4) every chart bar value.
"""
from __future__ import annotations

import base64
import re
from html import unescape
from typing import Any, Mapping

from Build.fitter.api import handle

from .contract import ReportError, digest
from .typeset import render_html, render_tex, tex_escape

_NUM = re.compile(r"-?\d+(?:\.\d+)?(?:e[+-]?\d+)?")


def _walk(obj: Any, path: str) -> Any:
    for key, idx in re.findall(r"([a-z_]+)|\[(\d+)\]", path):
        obj = obj[key] if key else obj[int(idx)]
    return obj


def _show(v: float | int) -> str:
    return str(v) if type(v) is int else format(v, ".6g")


def _tokens(doc: str, units: set[str], tex: bool) -> set[str]:
    doc = re.sub(r"sha256:[0-9a-f]{64}", " ", doc)  # digest hex is not a reported number
    if tex:
        doc = doc.split(r"\begin{document}", 1)[-1]  # preamble has font size etc.
    else:
        doc = unescape(re.sub(r"<[^>]*>", " ", re.sub(r"<style>.*?</style>", " ", doc, flags=re.S)))
    for u in sorted(units - {"1"}, key=len, reverse=True):  # unit text such as m/s^2 carries digits; unit "1" is kept as a token
        doc = doc.replace(tex_escape(u) if tex else u, " ")
    return set(_NUM.findall(doc))


def diff_report(report: Mapping[str, Any], request: Mapping[str, Any], docs: tuple[str, str] | None = None) -> dict[str, Any]:
    """Re-run the fitter on `request`; return {"mismatches": [...], "checked": {...}}. Empty mismatches == every number equals fitter output."""
    fresh = handle(request)
    if fresh.get("status") != "ok":
        return {"mismatches": [f"fitter_status:{fresh.get('status')}"], "checked": {}}
    bad: list[str] = []
    if report["fitter_digest"] != digest(fresh):
        bad.append("fitter_digest")
    shown, units, n_json = set(), set(), 0
    for nid, e in report["numbers"].items():
        units.add(e["unit"])
        for key, pkey in (("value", "path"), ("uncertainty", "uncertainty_path")):
            if key in e:
                want = _walk(fresh, e[pkey])
                n_json += 1
                if type(e[key]) is not type(want) or e[key] != want:
                    bad.append(f"json:{nid}.{key}")
                shown.add(_show(want))
    n = fresh["fit"]["n"]
    table = {_show(fresh["fit"][k][i]) for k in ("fitted", "residuals") for i in range(n)} | {str(i) for i in range(n)}
    expect = shown | table | ({"1"} if "1" in units else set())
    try:
        html, tex = docs or (render_html(report, fresh), render_tex(report, fresh))
    except ReportError as e:
        return {"mismatches": bad + [f"render_refused:{e}"], "checked": {"json_numbers": n_json}}
    toks = {}
    for name, doc, is_tex in (("html", html, False), ("tex", tex, True)):
        toks[name] = _tokens(doc, units, is_tex)
        bad += [f"{name}:unexpected_number:{t}" for t in sorted(toks[name] - expect)]
        bad += [f"{name}:missing_number:{t}" for t in sorted((shown | table) - toks[name])]
    # chart bars: g, residuals, then available AIC scores, in render order
    ms = fresh["model_selection"]
    want = [fresh["gravity"]["value"]] + list(fresh["fit"]["residuals"]) + [a for a, s in zip(ms["aic"], ms["aic_status"]) if s == "available"]
    got = []
    for b64 in re.findall(r'src="data:[^;"]+;base64,([^"]+)"', html):
        got += [float(v) for v in re.findall(r'data-value="([^"]+)"', base64.b64decode(b64).decode())]
    if got != [float(v) for v in want]:
        bad.append("chart_values")
    return {"mismatches": bad, "checked": {"json_numbers": n_json, "html_tokens": len(toks["html"]), "tex_tokens": len(toks["tex"]),
                                           "chart_values": len(got), "fitter_digest": digest(fresh)}}

