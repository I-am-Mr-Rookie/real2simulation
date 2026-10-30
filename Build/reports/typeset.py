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

# Accessibility: AA ink-on-paper contrast, visible focus, skip link, print rules. diff.py strips <style> before the numeric diff.
# UI-d: formal-report home (serif headings, shared sans body, mono numbers), warm paper, one clay accent, hard offset shadow on
# screen only. CSP has no font-src: fonts are local-name stacks with system fallbacks, never fetched. No motion is used.
_CSS = (":root{--r-bg:var(--r2s-bg,#f5efe3);--r-surface:var(--r2s-surface,#fffcf5);--r-ink:var(--r2s-ink,#1d1f1c);"
        "--r-muted:var(--r2s-muted,#55514a);--r-border:var(--r2s-border,#8a8273);--r-hair:#d8cfbd;--r-accent:var(--r2s-accent,#9a3b16);"
        "--r-focus:var(--r2s-focus,#0b57d0);--r-shadow:var(--r2s-shadow,4px 4px 0 #1d1f1c);"
        "--r-serif:'Libre Baskerville','Crimson Pro',Baskerville,'Iowan Old Style','Palatino Linotype',Georgia,serif;"
        "--r-sans:var(--r2s-font-sans,'Instrument Sans','Segoe UI',system-ui,-apple-system,Roboto,'Helvetica Neue',Arial,sans-serif);"
        "--r-mono:var(--r2s-font-mono,'Space Mono','Source Code Pro',Consolas,'SFMono-Regular',Menlo,ui-monospace,monospace)}"
        "*,*::before,*::after{box-sizing:border-box}html{background:var(--r-bg);-webkit-text-size-adjust:100%}"
        "body{font-family:var(--r-sans);font-size:1.0625rem;line-height:1.6;color:var(--r-ink);background:var(--r-bg);"
        "max-width:46rem;margin:0 auto;padding:2.5rem 1.25rem 3rem;overflow-wrap:break-word}"
        "h1,h2{font-family:var(--r-serif);font-weight:700;line-height:1.2;letter-spacing:-.005em;text-wrap:balance}"
        "h1{font-size:clamp(1.75rem,5vw,2.4rem);margin:0 0 .75rem;padding-bottom:.9rem;border-bottom:3px double var(--r-ink)}"
        "h2{font-size:1.35rem;margin:2.25rem 0 .6rem}main>h2:first-of-type{margin-top:1.5rem;font-size:.8rem;font-family:var(--r-mono);"
        "font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--r-accent)}"
        "main>h2:first-of-type+p{font-family:var(--r-serif);font-size:1.15rem;line-height:1.55;margin:.25rem 0 .75rem}"
        "p{margin:.5rem 0 .9rem}ul{margin:.5rem 0 1.25rem;padding-left:1.25rem}li{margin:.2rem 0}li::marker{color:var(--r-accent)}"
        "section{margin-top:.5rem}a{color:var(--r-accent);text-underline-offset:.15em}"
        ".noprint{font-size:.9rem;color:var(--r-muted);background:var(--r-surface);border:1px solid var(--r-hair);"
        "border-left:3px solid var(--r-accent);padding:.5rem .75rem;border-radius:var(--r2s-radius,3px)}"
        ".tw{overflow-x:auto;margin:1.75rem 0;background:var(--r-surface);border:2px solid var(--r-ink);border-radius:var(--r2s-radius,3px);"
        "box-shadow:var(--r-shadow);padding:.25rem .75rem .75rem}"
        "table{border-collapse:collapse;width:100%;font-size:.95rem}"
        "caption{caption-side:top;text-align:left;padding:.6rem 0 .5rem;font-family:var(--r-serif);font-weight:700;font-size:1.05rem}"
        "th,td{border:0;border-bottom:1px solid var(--r-hair);padding:.45rem .75rem .45rem 0;text-align:left;vertical-align:top}"
        "thead th{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--r-muted);"
        "border-bottom:2px solid var(--r-ink);white-space:nowrap}"
        "tbody th{font-weight:600}tbody td{font-family:var(--r-mono);font-size:.875rem;font-variant-numeric:tabular-nums;color:var(--r-ink)}"
        "tbody tr:last-child>*{border-bottom:0}tbody tr:hover>*{background:var(--r-bg)}"
        ".tw:focus{outline:none}.tw:focus-visible,.skip:focus,a:focus-visible{outline:3px solid var(--r-focus);outline-offset:3px}"
        "img{display:block;max-width:100%;height:auto;margin:0 auto}"
        "figure{margin:1.75rem 0;background:var(--r-surface);border:2px solid var(--r-ink);border-radius:var(--r2s-radius,3px);"
        "box-shadow:var(--r-shadow);padding:1rem}"
        "figcaption{margin-top:.75rem;padding-top:.6rem;border-top:1px solid var(--r-hair);font-size:.875rem;color:var(--r-muted)}"
        ".skip{position:absolute;left:-999px;top:.75rem}.skip:focus{left:.75rem;z-index:1;background:var(--r-ink);color:var(--r-surface);"
        "padding:.5rem .9rem;border-radius:var(--r2s-radius,3px);font-weight:700;text-decoration:none}"
        "footer{margin-top:2.5rem;padding-top:.9rem;border-top:3px double var(--r-ink);color:var(--r-muted)}"
        "footer small{display:block;font-family:var(--r-mono);font-size:.78rem;line-height:1.6;overflow-wrap:anywhere}"
        "@media (max-width:30rem){body{padding:1.5rem 1rem 2rem;font-size:1rem}.tw,figure{box-shadow:3px 3px 0 var(--r-ink)}"
        ".tw{padding:.25rem .5rem .5rem}th,td{padding-right:.6rem}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}"
        "@media (forced-colors:active){.tw,figure{border-color:CanvasText;box-shadow:none}}"
        "@media print{.skip,.noprint{display:none}html,body{background:#fff;color:#000}body{max-width:none;margin:0;padding:0;font-size:11pt}"
        ".tw,figure{box-shadow:none;border:0;background:none;padding:0;overflow:visible}main>h2:first-of-type{color:#000}"
        "tbody tr:hover>*{background:none}tr,figure{break-inside:avoid}h1,h2,caption{break-after:avoid}thead{display:table-header-group}"
        "@page{margin:18mm}}")
CHART_ALT = {"gravity": "Bar chart of the fitted gravity value with one-sigma error bar; exact values are in the summary table.",
             "residuals": "Bar chart of fit residuals per sample; exact values are in the residuals table.",
             "model_selection": "Bar chart of AIC per candidate model, lower is better; exact scores are in the summary table."}

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
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         f"<title>{p(report['title'])}</title>", "<style>" + _CSS + "</style></head><body>",
         '<a class="skip" href="#main">Skip to report content</a><main id="main">',
         f"<h1>{p(report['title'])}</h1>",
         '<p class="noprint">To save a PDF, use your browser Print command and choose Save as PDF.</p>',
         f"<h2>{_h(t['name'])}</h2>", f"<p>{_h(t['model'])}</p>",
         "<ul>" + "".join(f"<li>{_h(a)}</li>" for a in t["assumptions"]) + "</ul>"]
    for s in report["sections"]:
        o.append(f'<section id="{_h(s["id"])}" aria-labelledby="h-{_h(s["id"])}"><h2 id="h-{_h(s["id"])}">{p(s["title"])}</h2>'
                 + "".join(f"<p>{p(x)}</p>" for x in s["text"]) + "</section>")
    for tb in tables:
        # scrollable wrapper is focusable so keyboard users can pan a wide table; first column is the row header
        o.append(f'<div class="tw" role="region" aria-label="{_h(tb["caption"])}" tabindex="0"><table id="{_h(tb["id"])}">'
                 f'<caption>{_h(tb["caption"])}</caption><thead><tr>'
                 + "".join(f'<th scope="col">{_h(c["header"])}</th>' for c in tb["columns"]) + "</tr></thead><tbody>")
        for r in tb["rows"]:
            o.append("<tr>" + "".join(("<th scope=\"row\">" if i == 0 else "<td>") + _h(str(r.get(c["key"], ""))) + ("</th>" if i == 0 else "</td>")
                                      for i, c in enumerate(tb["columns"])) + "</tr>")
        o.append("</tbody></table></div>")
    for k, svg in charts.items():  # data-URI img: the SVG cannot touch the page DOM or run script
        o.append(f'<figure><img alt="{_h(CHART_ALT[k])}" src="data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}">'
                 f"<figcaption>{_h(CHART_ALT[k])}</figcaption></figure>")
    o.append(f"</main><footer><small>fitter_digest {_h(report['fitter_digest'])}; labels: {_h(', '.join(tables[0]['labels']))}</small></footer>")
    return "\n".join(o + ["</body></html>"]) + "\n"


def render_tex(report: Mapping[str, Any], fitter: Mapping[str, Any]) -> str:
    tables = build_tables(report, fitter)
    t, nums = TEMPLATE_TEXT[report["template"]], report["numbers"]
    p = lambda s: _prose(s, nums, tex_escape, r"$\pm$")
    o = [r"\documentclass[11pt]{article}", r"\usepackage{longtable}", r"\usepackage[pdfusetitle,pdflang={en}]{hyperref}",  # PDF title + language
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
