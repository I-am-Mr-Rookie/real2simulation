"""Compile the four template reports to PDF (MiKTeX/TeX Live pdflatex) with an explicit HTML print fallback (stdlib only).

Never fakes success: a PDF is only listed if pdflatex exited 0 AND produced the file; otherwise any stale PDF is removed and the
manifest entry is {"status": "html-print-fallback"} pointing at report.html (CSP-locked, charts embedded; print to PDF from a browser).
"""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Mapping

from .typeset import TEMPLATE_TEXT, write_documents

# Pinned flags: no shell escape (hostile text cannot run commands), no MiKTeX auto-install (no network side effects).
_CMD = ["-interaction=nonstopmode", "-halt-on-error", "-no-shell-escape", "--disable-installer"]


def compile_pdf(tex: str | Path, binary: str | None = None, timeout: int = 120) -> dict[str, Any]:
    """Compile report.tex in place; two passes so longtable widths settle. Returns a manifest entry."""
    tex = Path(tex)
    exe = binary or shutil.which("pdflatex")
    pdf = tex.with_suffix(".pdf")
    pdf.unlink(missing_ok=True)  # a stale PDF must never pass for a fresh compile
    fb = {"status": "html-print-fallback", "html": tex.with_suffix(".html").name, "pdf": None}
    if not exe:
        return {**fb, "reason": "pdflatex not found"}
    try:
        for _ in range(2):
            r = subprocess.run([exe, *_CMD, tex.name], cwd=tex.parent, capture_output=True, text=True, errors="replace", timeout=timeout)
            if r.returncode:
                pdf.unlink(missing_ok=True)
                return {**fb, "reason": "pdflatex exit %d" % r.returncode, "log_tail": r.stdout[-400:]}
    except (OSError, subprocess.TimeoutExpired) as e:
        pdf.unlink(missing_ok=True)
        return {**fb, "reason": type(e).__name__}
    if not pdf.is_file() or pdf.stat().st_size < 1000:
        pdf.unlink(missing_ok=True)
        return {**fb, "reason": "no pdf produced"}
    m = re.search(r"\((\d+) pages?", tex.with_suffix(".log").read_text(errors="replace"))
    return {"status": "pdf", "html": fb["html"], "pdf": pdf.name, "pages": int(m.group(1)) if m else None,
            "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest()}


def compile_all(make_report, fitter: Mapping[str, Any], outdir: str | Path, binary: str | None = None) -> dict[str, dict[str, Any]]:
    """make_report(template) -> report dict; writes outdir/<template>/report.{html,tex,pdf} and returns {template: entry}."""
    out = Path(outdir)
    res = {}
    for tpl in TEMPLATE_TEXT:
        tex = write_documents(make_report(tpl), fitter, out / tpl)[1]
        res[tpl] = compile_pdf(tex, binary)
        if res[tpl]["status"] == "pdf":  # keep only deliverables; aux/log stay on failure for diagnosis
            for ext in (".aux", ".log"):
                tex.with_suffix(ext).unlink(missing_ok=True)
    return res

