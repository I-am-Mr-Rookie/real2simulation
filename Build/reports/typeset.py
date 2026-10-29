"""HTML and TeX report documents (stdlib only) from a *validated* report + fitter result.

Safety: all dynamic text (title, section titles, paragraphs, units, labels) is escaped for the target format
AFTER placeholders are split out; numbers come only through contract.resolve via render.build_tables.
Template-specific text lives in TEMPLATE_TEXT (static, digit-free so it can carry no hidden numbers).
Same input -> byte-identical output (no timestamps).
"""
from __future__ import annotations

import base64
from html import escape as _h
from pathlib import Path
from typing import Any, Mapping

from .contract import _PLACEHOLDER
from .render import _fmt, build_charts, build_tables

# shortcut: the fitter is one polynomial model, so template text only names the context; per-template physics can grow when S12 adds models.
TEMPLATE_TEXT: dict[str, dict[str, Any]] = {
    "free_fall": {"name": "Free fall", "model": "Vertical position against time; gravity comes from the curvature of the fitted polynomial.",
                  "assumptions": ["Motion is vertical with negligible drag.", "Time and position share one origin."]},
    "pendulum": {"name": "Pendulum", "model": "Pendulum motion summarised by the same polynomial fit of position against time.",
                 "assumptions": ["Small swing angle is assumed by the template.", "Pivot and bob are treated as ideal."]},
    "projectile": {"name": "Projectile", "model": "Vertical component of projectile motion fitted against time.",
                   "assumptions": ["Launch is treated as an ideal point mass.", "Air resistance is neglected."]},
    "ramp": {"name": "Inclined ramp", "model": "Position along a ramp fitted against time.",
             "assumptions": ["Friction is neglected by the template.", "Ramp angle is held fixed."]},
}

_TEX = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&", "#": r"\#", "^": r"\textasciicircum{}",
        "_": r"\_", "~": r"\textasciitilde{}", "%": r"\%", "<": r"\textless{}", ">": r"\textgreater{}", "|": r"\textbar{}",
        '"': r"{\ttfamily\symbol{34}}", "\x60": r"{\ttfamily\symbol{96}}", "[": "{[}", "]": "{]}"}  # symbol: OT1-safe


def tex_escape(s: str) -> str:
    out = []
    for c in s:
        if c in _TEX:
            out.append(_TEX[c])
        elif c in "\n\t\r":
            out.append(" ")
        elif c < " " or c == "\x7f":
            continue  # control characters can break TeX input; drop
        elif ord(c) > 126:
            out.append(r"\texttt{U+%04X}" % ord(c))  # no font/encoding guesswork for non-ASCII
        else:
            out.append(c)
    return "".join(out)


def _prose(text: str, numbers: Mapping[str, Any], esc, pm: str) -> str:
    parts, pos = [], 0
    for m in _PLACEHOLDER.finditer(text):
        parts.append(esc(text[pos:m.start()]))
        e = numbers[m.group(1)]  # ids already proven present by validate_report
        val = esc(_fmt(e["value"])) + (f" {pm} " + esc(_fmt(e["uncertainty"])) if "uncertainty" in e else "")
        unit = "" if e["unit"] == "1" else " " + esc(e["unit"])  # "1" is the contract's dimensionless unit
        parts.append(f"{val}{unit} ({esc(e['label'])})")
        pos = m.end()
    return "".join(parts) + esc(text[pos:])


def render_html(report: Mapping[str, Any], fitter: Mapping[str, Any]) -> str:
    tables, charts = build_tables(report, fitter), build_charts(report, fitter)  # both validate first
    t, nums = TEMPLATE_TEXT[report["template"]], report["numbers"]  # template membership enforced by validate_report
    p = lambda s: _prose(s, nums, _h, "\u00b1")
    o = ['<!DOCTYPE html>', '<html lang="en"><head><meta charset="utf-8">',
         '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; img-src data:; style-src \'unsafe-inline\'">',
         f"<title>{p(report['title'])}</title>",
         "<style>body{font-family:sans-serif;max-width:48rem;margin:2rem auto}table{border-collapse:collapse}"
         "td,th{border:1px solid #888;padding:.2rem .5rem;text-align:left}</style></head><body>",
         f"<h1>{p(report['title'])}</h1>", f"<h2>{_h(t['name'])}</h2>", f"<p>{_h(t['model'])}</p>",
         "<ul>" + "".join(f"<li>{_h(a)}</li>" for a in t["assumptions"]) + "</ul>"]
    for s in report["sections"]:
        o.append(f'<section id="{_h(s["id"])}"><h2>{p(s["title"])}</h2>' + "".join(f"<p>{p(x)}</p>" for x in s["text"]) + "</section>")
    for tb in tables:
        o.append(f'<table id="{_h(tb["id"])}"><caption>{_h(tb["caption"])}</caption><tr>'
                 + "".join(f'<th>{_h(c["header"])}</th>' for c in tb["columns"]) + "</tr>")
        for r in tb["rows"]:
            o.append("<tr>" + "".join(f'<td>{_h(str(r.get(c["key"], "")))}</td>' for c in tb["columns"]) + "</tr>")
        o.append("</table>")
    for k, svg in charts.items():  # data-URI img: the SVG cannot touch the page DOM or run script
        o.append(f'<p><img alt="{_h(k)} chart" src="data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"></p>')
    o.append(f"<footer><small>fitter_digest {_h(report['fitter_digest'])}; labels: {_h(', '.join(tables[0]['labels']))}</small></footer>")
    return "\n".join(o + ["</body></html>"]) + "\n"


def render_tex(report: Mapping[str, Any], fitter: Mapping[str, Any]) -> str:
    tables = build_tables(report, fitter)
    t, nums = TEMPLATE_TEXT[report["template"]], report["numbers"]
    p = lambda s: _prose(s, nums, tex_escape, r"$\pm$")
    o = [r"\documentclass[11pt]{article}", r"\usepackage{longtable}",
         "\\title{" + p(report["title"]) + "}", r"\author{}\date{}", r"\begin{document}\maketitle",
         "\\section*{" + tex_escape(t["name"]) + "}", tex_escape(t["model"]) + "\n",
         r"\begin{itemize}" + "".join("\n\\item " + tex_escape(a) for a in t["assumptions"]) + "\n" + r"\end{itemize}"]
    for s in report["sections"]:
        o.append("\\section*{" + p(s["title"]) + "}\n" + "\n\n".join(p(x) for x in s["text"]))
    for tb in tables:
        cols = tb["columns"]
        o += ["\\begin{longtable}{" + "l" * len(cols) + "}", "\\caption{" + tex_escape(tb["caption"]) + r"}\\ \hline",
              " & ".join(tex_escape(c["header"]) for c in cols) + r" \\ \hline \endhead"]
        o += [" & ".join(tex_escape(str(r.get(c["key"], ""))) for c in cols) + r" \\" for r in tb["rows"]]
        o.append(r"\hline\end{longtable}")
    o.append("\\noindent fitter\\_digest " + tex_escape(report["fitter_digest"]) + "; labels: " + tex_escape(", ".join(tables[0]["labels"])))
    return "\n".join(o + [r"\end{document}"]) + "\n"


def write_documents(report: Mapping[str, Any], fitter: Mapping[str, Any], outdir: str | Path) -> list[Path]:
    html, tex = render_html(report, fitter), render_tex(report, fitter)  # render first: a refused report writes nothing
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    paths = [out / "report.html", out / "report.tex"]
    for path, s in zip(paths, (html, tex)):
        path.write_text(s, encoding="utf-8", newline="\n")
    return paths
