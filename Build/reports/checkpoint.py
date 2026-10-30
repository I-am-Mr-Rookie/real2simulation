"""S17f: checkpoint page = Gate A label + recorded-scene (S14) provenance + explicit fallback when an input is missing.

Separate file from report.html on purpose: S17e diffs report.html/tex and flags any numeral that is not a fitter value, while
gate counts and scene ids are identifiers copied verbatim from S14 JSON (with pointers), never computed or typed here.
No S14 spec number is shown; numbers stay fitter-only. Offline, stdlib only.
"""
from __future__ import annotations

import json
from html import escape as _h
from pathlib import Path
from typing import Any, Mapping

from .contract import ReportError, validate_report
from .typeset import _CSS, render_html

GATE_VERDICT = "MET_AMENDED_Q16"
GATE_LABEL = "scale unverified, not setup-validated"  # verbatim; GATE_A.json must carry exactly this
_COUNTS = (("numeric_contract_valid_specs", "Numeric-contract specs"), ("setup_validator_valid_specs", "Production setup-validator specs"))


def load_gate(path: str | Path) -> dict[str, Any] | None:
    """GATE_A.json -> checked record, or None when absent (caller renders the fallback; no gate status is invented)."""
    p = Path(path)
    if not p.is_file():
        return None
    g = json.loads(p.read_text(encoding="utf-8"))
    if g.get("verdict") != GATE_VERDICT or g.get("label") != GATE_LABEL or g.get("never_plain_met") is not True:
        raise ReportError("gate_a_record_not_amended_label")  # never upgrade or reword the label
    return g


def scene_provenance(offline: str | Path, case_id: str) -> dict[str, str] | None:
    """Strings only, copied from an S14 offline replay JSON entry; None if the scene is absent."""
    spec = next((s for s in json.loads(Path(offline).read_text(encoding="utf-8"))["numeric_contract_specs"] if s["case_id"] == case_id), None)
    if spec is None:
        return None
    c = spec["scene_context"]
    return {"case_id": spec["case_id"], "scene_id": spec["scene_id"], "template": spec["template"], "licence": spec["licence"],
            "source_url": spec["source_url"], "source_sha256": spec["source_sha256"], "scale_status": c["scale_status"],
            "gravity_status": c["gravity_status"], "bundle_bound": spec["bundle_bound"]}


def fallback_record(missing: list[str]) -> dict[str, Any]:
    return {"status": "input-missing" if missing else "complete", "missing": sorted(missing),
            "shown": "no values, no gate claim" if missing else "report.html linked"}


def _rows(pairs) -> str:
    return "".join(f'<tr><th scope="row">{_h(k)}</th><td>{_h(v)}</td></tr>' for k, v in pairs)


def render_checkpoint(report: Mapping[str, Any] | None, fitter: Mapping[str, Any] | None, prov: Mapping[str, str] | None,
                      gate: Mapping[str, Any] | None) -> tuple[str, dict[str, Any]]:
    """Return (html, fallback_record). Missing/invalid input -> named fallback section; nothing is guessed."""
    missing = []
    if gate is None:
        missing.append("gate_a_record")
    if prov is None:
        missing.append("recorded_scene_spec")
    if report is None or fitter is None:
        missing.append("fitter_result")
    else:
        try:
            validate_report(report, fitter)  # report must still trace to this fitter output
            render_html(report, fitter)
        except ReportError:
            missing.append("valid_report")
    o = ['<!DOCTYPE html>', '<html lang="en"><head><meta charset="utf-8">',
         '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">', "<title>Checkpoint status</title>",
         "<style>" + _CSS + "</style></head><body>", '<a class="skip" href="#main">Skip to checkpoint content</a><main id="main">',
         "<h1>Checkpoint status</h1>"]
    if gate:
        o.append('<section aria-labelledby="h-gate"><h2 id="h-gate">Gate A</h2><p><strong>%s: %s</strong></p>' % (_h(gate["verdict"]), _h(gate["label"])))
        rows = [(lbl, gate["counts"][k]["value"] + " (" + gate["counts"][k]["pointer"] + ")") for k, lbl in _COUNTS]
        o.append('<div class="tw" role="region" aria-label="Gate A counts" tabindex="0"><table><caption>Gate A counts, copied from S14 JSON</caption>'
                 '<thead><tr><th scope="col">Item</th><th scope="col">Value (source pointer)</th></tr></thead><tbody>' + _rows(rows) + "</tbody></table></div></section>")
    if prov:
        o.append('<section aria-labelledby="h-scene"><h2 id="h-scene">Recorded scene</h2><div class="tw" role="region" aria-label="Recorded scene provenance" tabindex="0">'
                 '<table><caption>Recorded scene provenance (identifiers only; no measured values)</caption><thead><tr><th scope="col">Field</th>'
                 '<th scope="col">Value</th></tr></thead><tbody>' + _rows(prov.items()) + "</tbody></table></div></section>")
    if report is not None and "valid_report" not in missing and "fitter_result" not in missing:
        o.append('<p><a href="report.html">Open the report (accessible HTML)</a>. The PDF is a print artefact, untagged; '
                 'use browser Print, Save as PDF from the HTML.</p>')
    if missing:
        o.append('<section role="alert" aria-labelledby="h-fb"><h2 id="h-fb">Fallback: input missing</h2><p>Not shown because the input is missing or invalid, '
                 'so no value and no gate claim is made for it:</p><ul>' + "".join(f"<li>{_h(m)}</li>" for m in sorted(missing)) + "</ul></section>")
    o.append("</main><footer><small>Offline checkpoint page; no model call.</small></footer></body></html>")
    return "\n".join(o) + "\n", fallback_record(missing)
