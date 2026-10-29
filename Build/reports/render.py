"""Deterministic report tables and SVG charts (stdlib only), built from a *validated* report + fitter result.

Every value, unit, uncertainty and source label is read through `contract.resolve` (i.e. copied from the fitter
output), never typed here. Same input -> byte-identical output (no timestamps, fixed number formats).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping
from xml.sax.saxutils import escape

from .contract import ReportError, resolve, validate_report


def _fmt(v: float | int) -> str:
    return str(v) if type(v) is int else format(v, ".6g")  # display only; rows keep the exact value


def _table(tid: str, caption: str, columns: list[dict[str, str]], rows: list[dict[str, Any]], digest: str) -> dict[str, Any]:
    return {"id": tid, "caption": caption, "columns": columns, "rows": rows, "fitter_digest": digest,
            "labels": sorted({r["label"] for r in rows})}


def build_tables(report: Mapping[str, Any], fitter: Mapping[str, Any]) -> list[dict[str, Any]]:
    validate_report(report, fitter)  # refuses untraceable numbers before anything is drawn
    d = report["fitter_digest"]
    summary = []
    for nid in sorted(report["numbers"]):
        e = report["numbers"][nid]
        row = {"id": nid, "path": e["path"], "value": e["value"], "display": _fmt(e["value"]), "unit": e["unit"], "label": e["label"]}
        if "uncertainty" in e:  # same unit as value (enforced by contract); one-sigma per fitter, see assumptions
            row.update(uncertainty=e["uncertainty"], uncertainty_display=_fmt(e["uncertainty"]), uncertainty_path=e["uncertainty_path"])
        summary.append(row)
    cols = [{"key": "id", "header": "Quantity"}, {"key": "display", "header": "Value"}, {"key": "unit", "header": "Unit"},
            {"key": "uncertainty_display", "header": "Uncertainty (same unit)"}, {"key": "label", "header": "Source label"}]
    tables = [_table("summary", "Reported quantities (values copied from fitter output)", cols, summary, d)]
    n = resolve(fitter, "fit.n")[0]
    res = []
    for i in range(n):
        f, unit, label = resolve(fitter, f"fit.fitted[{i}]")
        r, r_unit, r_label = resolve(fitter, f"fit.residuals[{i}]")
        if (r_unit, r_label) != (unit, label):
            raise ReportError("fitted_and_residual_unit_or_label_differ")
        res.append({"sample": i, "fitted": f, "residual": r, "unit": unit, "label": label, "fitted_display": _fmt(f), "residual_display": _fmt(r)})
    cols = [{"key": "sample", "header": "Sample"}, {"key": "fitted_display", "header": "Fitted"},
            {"key": "residual_display", "header": "Residual"}, {"key": "unit", "header": "Unit"}, {"key": "label", "header": "Source label"}]
    tables.append(_table("residuals", "Fit residuals per sample", cols, res, d))
    return tables


def _bar_svg(title: str, cats: list[str], vals: list[float | int], errs: list[float] | None, unit: str, label: str, digest: str) -> str:
    """Vertical bars (optional symmetric error bars) with zero line; unit, source label and fitter digest are in the SVG text."""
    W, H, L, R, T, B = 480, 300, 70, 20, 40, 60
    lo = min([0.0] + [v - (errs[i] if errs else 0) for i, v in enumerate(vals)])
    hi = max([0.0] + [v + (errs[i] if errs else 0) for i, v in enumerate(vals)])
    span = (hi - lo) or 1.0
    y = lambda v: T + (H - T - B) * (hi - v) / span
    bw = (W - L - R) / len(vals)
    mid = (T + H - B) / 2
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="sans-serif" font-size="11">',
         f"<title>{escape(title)}</title>", f"<desc>fitter_digest={escape(digest)}; unit={escape(unit)}; source label={escape(label)}</desc>",
         f'<rect width="{W}" height="{H}" fill="white"/>', f'<text x="{W / 2:.2f}" y="18" text-anchor="middle" font-size="13">{escape(title)}</text>',
         f'<text x="14" y="{mid:.2f}" text-anchor="middle" transform="rotate(-90 14 {mid:.2f})">value [{escape(unit)}]</text>',
         f'<text x="{W / 2:.2f}" y="{H - 8}" text-anchor="middle">source: {escape(label)} (from fitter output)</text>']
    for v in (lo, hi):
        o.append(f'<text x="{L - 4}" y="{y(v) + 4:.2f}" text-anchor="end">{escape(_fmt(v))}</text>')
    o.append(f'<line x1="{L}" y1="{y(0):.2f}" x2="{W - R}" y2="{y(0):.2f}" stroke="black"/>')
    for i, (c, v) in enumerate(zip(cats, vals)):
        x0, y0, y1 = L + i * bw + bw * 0.15, y(max(v, 0)), y(min(v, 0))
        o.append(f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{bw * 0.7:.2f}" height="{max(y1 - y0, 0.5):.2f}" fill="#4878a8" data-value="{v!r}"/>')
        if errs:
            xc = x0 + bw * 0.35
            o.append(f'<line x1="{xc:.2f}" y1="{y(v - errs[i]):.2f}" x2="{xc:.2f}" y2="{y(v + errs[i]):.2f}" stroke="black" data-uncertainty="{errs[i]!r}"/>')
        o.append(f'<text x="{x0 + bw * 0.35:.2f}" y="{H - B + 14}" text-anchor="middle">{escape(c)}</text>')
    return "\n".join(o + ["</svg>"]) + "\n"


def build_charts(report: Mapping[str, Any], fitter: Mapping[str, Any]) -> dict[str, str]:
    validate_report(report, fitter)
    d = report["fitter_digest"]
    g, g_unit, g_label = resolve(fitter, "gravity.value")
    u, _, _ = resolve(fitter, "gravity.uncertainty")
    charts = {"gravity": _bar_svg("Fitted g with one-sigma uncertainty", ["g"], [g], [u], g_unit, g_label, d)}
    n = resolve(fitter, "fit.n")[0]
    rs = [resolve(fitter, f"fit.residuals[{i}]") for i in range(n)]
    charts["residuals"] = _bar_svg("Fit residuals", [str(i) for i in range(n)], [r[0] for r in rs], None, rs[0][1], rs[0][2], d)
    ms = fitter["model_selection"]  # unavailable (non-finite) scores are skipped, never drawn as numbers
    idx = [i for i, s in enumerate(ms["aic_status"]) if s == "available"]
    if idx:
        sc = [resolve(fitter, f"model_selection.aic[{i}]") for i in idx]
        charts["model_selection"] = _bar_svg("AIC per candidate model (lower is better)", [f"#{i + 1}" for i in idx],
                                             [s[0] for s in sc], None, sc[0][1], sc[0][2], d)
    return charts


def write_all(report: Mapping[str, Any], fitter: Mapping[str, Any], outdir: str | Path) -> list[Path]:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    tables, charts = build_tables(report, fitter), build_charts(report, fitter)
    paths = [out / "tables.json"] + [out / f"chart_{k}.svg" for k in charts]
    paths[0].write_text(json.dumps(tables, indent=1, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    for p, svg in zip(paths[1:], charts.values()):
        p.write_text(svg, encoding="utf-8", newline="\n")
    return paths
