import unittest

from Build.reports.diff import diff_report
from Build.reports.typeset import render_html, render_tex
from Build.fitter.api import handle

from .templates import MODELS, report, request


class NumericDiff(unittest.TestCase):
    def test_every_template_report_equals_fresh_fitter_run(self):
        digests = set()
        for tpl in MODELS:
            out = diff_report(report(tpl), request(tpl))
            self.assertEqual(out["mismatches"], [], tpl)
            self.assertGreaterEqual(out["checked"]["json_numbers"], 15)
            self.assertGreaterEqual(out["checked"]["chart_values"], 10)
            digests.add(out["checked"]["fitter_digest"])
        self.assertEqual(len(digests), 4)  # four genuinely different fitter runs

    def test_tampered_json_number_is_caught(self):
        r = report("ramp")
        r["numbers"]["g"]["value"] += 1e-9
        self.assertTrue(any(m.startswith(("json:g", "render_refused")) for m in diff_report(r, request("ramp"))["mismatches"]))

    def test_report_from_other_fitter_run_is_caught(self):
        out = diff_report(report("free_fall"), request("pendulum"))
        self.assertIn("fitter_digest", out["mismatches"])

    def test_tampered_rendered_documents_are_caught(self):
        tpl, r = "projectile", report("projectile")
        fresh = handle(request(tpl))
        html, tex = render_html(r, fresh), render_tex(r, fresh)
        g = format(fresh["gravity"]["value"], ".6g")
        self.assertIn(g, html)
        self.assertIn(g, tex)
        self.assertEqual(diff_report(r, request(tpl), (html, tex))["mismatches"], [])
        bad = diff_report(r, request(tpl), (html.replace(g, "9.81", 1), tex))["mismatches"]
        self.assertTrue(any(m.startswith("html:unexpected_number:9.81") for m in bad), bad)
        bad = diff_report(r, request(tpl), (html, tex.replace(g, "9.81")))["mismatches"]
        self.assertTrue(any(m.startswith("tex:unexpected_number") for m in bad) and any(m.startswith("tex:missing_number") for m in bad), bad)

    def test_tampered_chart_is_caught(self):
        import base64, re
        tpl, r = "ramp", report("ramp")
        html = render_html(r, handle(request(tpl)))
        b64 = re.search(r'base64,([^"]+)"', html).group(1)
        svg = base64.b64decode(b64).decode()
        svg2 = re.sub(r'data-value="[^"]+"', 'data-value="1.0"', svg, count=1)
        html2 = html.replace(b64, base64.b64encode(svg2.encode()).decode())
        tex = render_tex(r, handle(request(tpl)))
        self.assertIn("chart_values", diff_report(r, request(tpl), (html2, tex))["mismatches"])


if __name__ == "__main__":
    unittest.main()

