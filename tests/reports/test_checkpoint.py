"""S17f: checkpoint page = verbatim Gate A label + S14 provenance + named fallback (visibly synthetic fitter; no real-scene numbers)."""
import json
import re
import unittest
from html.parser import HTMLParser

from Build.reports import ReportError
from Build.reports.checkpoint import GATE_LABEL, GATE_VERDICT, load_gate, render_checkpoint, scene_provenance
from Build.reports.diff import diff_report
from tests.reports.fixture import synthetic_fitter_result, synthetic_report
from tests.reports.templates import MODELS, report as tpl_report, request as tpl_request

GATE = "evidence/S14/GATE_A.json"
OFF = "evidence/S14/S14g-fix7-offline.json"
FIT = synthetic_fitter_result()


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.t, self.th, self.lang = [], [], None

    def handle_starttag(self, tag, a):
        a = dict(a)
        self.t.append(tag)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "th":
            self.th.append(a.get("scope"))


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.gate, self.prov = load_gate(GATE), scene_provenance(OFF, "RM02")

    def test_complete_page_carries_label_verbatim_and_s14_counts(self):
        html, fb = render_checkpoint(synthetic_report(FIT), FIT, self.prov, self.gate)
        self.assertEqual(fb["status"], "complete")
        self.assertIn(f"{GATE_VERDICT}: {GATE_LABEL}", html)
        self.assertIn("0/10", html)  # setup-validator shown alongside, never hidden
        self.assertNotIn(">MET<", html)
        self.assertIn("report.html", html)
        self.assertIn("untagged", html)  # PDF honesty
        self.assertNotIn("rm02", html.replace(self.prov["scene_id"], ""))  # only copied identifiers

    def test_structure_is_accessible(self):
        for args in ((synthetic_report(FIT), FIT, self.prov, self.gate), (None, None, None, None)):
            p = P()
            p.feed(render_checkpoint(*args)[0])
            self.assertEqual(p.lang, "en")
            self.assertEqual(p.t.count("h1"), 1)
            self.assertEqual(p.t.count("main"), 1)
            self.assertTrue(all(s in ("row", "col") for s in p.th))
            self.assertNotIn("script", p.t)

    def test_each_missing_input_is_named_and_nothing_invented(self):
        rep = synthetic_report(FIT)
        cases = {"gate_a_record": (rep, FIT, self.prov, None), "recorded_scene_spec": (rep, FIT, None, self.gate),
                 "fitter_result": (None, None, self.prov, self.gate)}
        for name, args in cases.items():
            html, fb = render_checkpoint(*args)
            self.assertEqual(fb["missing"], [name])
            self.assertIn("Fallback: input missing", html)
            self.assertIn(f"<li>{name}</li>", html)
            if name == "gate_a_record":
                self.assertNotIn(GATE_VERDICT, html)  # no gate claim without its record
            if name == "fitter_result":
                self.assertNotIn("report.html", html)
                self.assertIsNone(re.search(r"\d+\.\d+", re.sub(r"<style>.*?</style>", "", html, flags=re.S)))  # no decimal without a fitter result
        html, fb = render_checkpoint(None, None, None, None)
        self.assertEqual(len(fb["missing"]), 3)

    def test_untraceable_report_falls_back(self):
        bad = synthetic_report(FIT)
        bad["numbers"]["g"] = {**bad["numbers"]["g"], "value": 1.0}
        html, fb = render_checkpoint(bad, FIT, self.prov, self.gate)
        self.assertEqual(fb["missing"], ["valid_report"])
        self.assertNotIn("report.html", html)

    def test_gate_record_cannot_be_reworded_or_missing(self):
        import json as j, tempfile, pathlib
        g = j.loads(pathlib.Path(GATE).read_text())
        g["label"] = "scale verified"
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d, "g.json")
            p.write_text(j.dumps(g))
            with self.assertRaises(ReportError):
                load_gate(p)
            self.assertIsNone(load_gate(pathlib.Path(d, "none.json")))
        self.assertIsNone(scene_provenance(OFF, "NOPE"))

    def test_s17e_numeric_diff_still_clean(self):
        for t in MODELS:
            self.assertEqual(diff_report(tpl_report(t), tpl_request(t))["mismatches"], [], t)

    def test_default_palette_contrast_wcag_aa(self):
        from Build.reports.typeset import _CSS
        c = {k: v for k, v in re.findall(r"--r-([a-z]+):var\(--r2s-[a-z-]+,(#[0-9a-f]{6})\)", _CSS)}

        def lum(h):
            ch = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            ch = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in ch]
            return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]

        def ratio(a, b):
            hi, lo = sorted((lum(c[a]), lum(c[b])), reverse=True)
            return (hi + 0.05) / (lo + 0.05)

        for fg in ("ink", "muted", "accent"):  # text on both page and card backgrounds
            for bg in ("bg", "surface"):
                self.assertGreaterEqual(ratio(fg, bg), 4.5, (fg, bg))
        self.assertGreaterEqual(ratio("focus", "bg"), 3.0)  # focus ring is a non-text indicator


if __name__ == "__main__":
    unittest.main()
