import copy
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from Build.reports import ReportError, digest, number_entry, render_html, render_tex, write_documents
from Build.reports.typeset import TEMPLATE_TEXT, tex_escape
from tests.reports.fixture import synthetic_fitter_result, synthetic_report

HOSTILE = 'Tom & <script>alert(x)</script> "q" \\input{/etc/passwd} $x$ pct% #a_b ^~ {}[] \u00e9\u4e2d'


class TestTypeset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fit = synthetic_fitter_result()

    def make(self, template="free_fall", fit=None, title="Synthetic fixture report", text=None):
        fit = fit or self.fit
        rep = synthetic_report(fit, template)
        rep["title"] = title
        if text:
            rep["sections"][0]["text"][1] = text
        return rep, fit

    def test_html_escapes_user_text(self):
        rep, fit = self.make(title=HOSTILE, text=HOSTILE + " {{g}}")
        rep["sections"][0]["title"] = HOSTILE
        html = render_html(rep, fit)
        self.assertNotIn("<script", html)
        self.assertNotIn('"q"', html)
        self.assertIn("&lt;script&gt;alert(x)&lt;/script&gt;", html)
        self.assertIn("&quot;q&quot;", html)

    def test_hostile_unit_is_escaped_in_html_and_tex(self):
        fit = copy.deepcopy(self.fit)
        fit["gravity"]["unit"] = 'm<img src=x onerror=1>&"\\s'
        rep, fit = self.make(fit=fit)
        html, tex = render_html(rep, fit), render_tex(rep, fit)
        self.assertNotIn("<img src=x", html)
        self.assertEqual(html.count("<img "), 3)  # only the three generated chart images
        self.assertIn("\\textbackslash{}s", tex)

    def test_html_has_no_script_and_locks_down_csp(self):
        html = render_html(*self.make())
        self.assertNotRegex(html, r"(?i)<script|javascript:|\son\w+=")
        self.assertIn("default-src 'none'", html)
        self.assertEqual(len(re.findall(r'src="data:image/svg\+xml;base64,', html)), 3)

    def test_placeholders_render_exact_fitter_values_and_labels(self):
        rep, fit = self.make()
        html, tex = render_html(rep, fit), render_tex(rep, fit)
        g = format(fit["gravity"]["value"], ".6g")
        for doc in (html, tex):
            self.assertIn(g, doc)
            self.assertIn("(simulated)", doc)
            self.assertNotIn("{{", doc)
        self.assertIn("\u00b1", html)
        self.assertIn(r"$\pm$", tex)

    def test_measured_label_is_copied_not_assumed(self):
        fit = copy.deepcopy(self.fit)
        for k in ("gravity", "fit", "covariance", "model_selection"):
            fit[k]["source"]["label"] = "measured"
        rep, fit = self.make(fit=fit)
        for doc in (render_html(rep, fit), render_tex(rep, fit)):
            self.assertIn("(measured)", doc)
            self.assertNotIn("(simulated)", doc)
            self.assertIn("labels: measured", doc)

    def test_template_specific_content(self):
        docs = {}
        for tpl, info in TEMPLATE_TEXT.items():
            self.assertFalse(re.search(r"\d", info["model"] + "".join(info["assumptions"])), tpl)  # static text carries no numerals
            rep, fit = self.make(tpl)
            h, t = render_html(rep, fit), render_tex(rep, fit)
            docs[tpl] = h
            self.assertIn(f"<h2>{info['name']}</h2>", h)
            self.assertIn(info["model"].rstrip("."), t)
            for other, oi in TEMPLATE_TEXT.items():
                if other != tpl:
                    self.assertNotIn(oi["model"], h)
        self.assertEqual(len(set(docs.values())), 4)

    def test_untraceable_or_unknown_template_refused_and_writes_nothing(self):
        rep, fit = self.make()
        bad = copy.deepcopy(rep)
        bad["numbers"]["g"]["value"] += 1e-9
        unk = copy.deepcopy(rep)
        unk["template"] = "evil"
        for r in (bad, unk):
            for fn in (render_html, render_tex):
                with self.assertRaises(ReportError):
                    fn(r, fit)
        with tempfile.TemporaryDirectory() as d, self.assertRaises(ReportError):
            write_documents(bad, fit, Path(d) / "out")
        self.assertFalse((Path(d) / "out").exists())

    def test_unreferenced_number_in_text_still_refused(self):
        rep, fit = self.make(text="g is 9.81 here")
        with self.assertRaises(ReportError):
            render_html(rep, fit)

    def test_deterministic_bytes(self):
        rep, fit = self.make()
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            for x, y in zip(write_documents(rep, fit, a), write_documents(rep, fit, b)):
                self.assertEqual(x.read_bytes(), y.read_bytes())

    def test_tex_escape_covers_specials(self):
        s = tex_escape('\\{}$&#^_~%<>|"[]\x00\n\u00e9')
        self.assertNotRegex(s.replace(r"\\", ""), r"(?<!\\)[$&#%]")
        self.assertIn(r"\textbackslash{}", s)
        self.assertIn(r"\texttt{U+00E9}", s)
        self.assertNotIn("\x00", s)

    @unittest.skipUnless(shutil.which("pdflatex"), "pdflatex not installed")
    def test_hostile_tex_compiles_without_executing_injection(self):
        rep, fit = self.make(title=HOSTILE, text=HOSTILE + " {{g}}")
        rep["sections"][0]["title"] = HOSTILE
        with tempfile.TemporaryDirectory() as d:
            tex = write_documents(rep, fit, d)[1]
            r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-no-shell-escape", "--disable-installer",
                                tex.name], cwd=d, capture_output=True, text=True, timeout=120)
            self.assertEqual(r.returncode, 0, r.stdout[-1500:])
            self.assertTrue((Path(d) / "report.pdf").stat().st_size > 1000)


if __name__ == "__main__":
    unittest.main()
