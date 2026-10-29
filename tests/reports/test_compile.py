import tempfile
import unittest
import shutil
import subprocess
from pathlib import Path

from Build.reports.compile import compile_all, compile_pdf
from Build.reports.typeset import TEMPLATE_TEXT
from tests.reports.fixture import synthetic_fitter_result, synthetic_report

FIT = synthetic_fitter_result()
mk = lambda tpl: synthetic_report(FIT, tpl)


class TestCompile(unittest.TestCase):
    @unittest.skipUnless(shutil.which("pdflatex"), "pdflatex not installed")
    def test_all_four_templates_compile_to_pdf_with_fitter_numbers(self):
        with tempfile.TemporaryDirectory() as d:
            res = compile_all(mk, FIT, d)
            self.assertEqual(set(res), set(TEMPLATE_TEXT))
            g = format(FIT["gravity"]["value"], ".6g")
            for tpl, e in res.items():
                self.assertEqual(e["status"], "pdf", (tpl, e))
                pdf = Path(d) / tpl / e["pdf"]
                self.assertEqual(pdf.read_bytes()[:5], b"%PDF-")
                if shutil.which("pdftotext"):
                    txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
                    self.assertIn(g, txt)
                    self.assertIn(TEMPLATE_TEXT[tpl]["name"], txt)
                    self.assertIn("simulated", txt)
            self.assertEqual(len({e["pdf_sha256"] for e in res.values()}), 4)

    def test_missing_compiler_falls_back_to_html_and_removes_stale_pdf(self):
        with tempfile.TemporaryDirectory() as d:
            res = compile_all(mk, FIT, d, binary="no-such-pdflatex-binary")
            for tpl, e in res.items():
                self.assertEqual((e["status"], e["pdf"]), ("html-print-fallback", None))
                self.assertTrue((Path(d) / tpl / e["html"]).is_file())
                self.assertFalse((Path(d) / tpl / "report.pdf").exists())
            stale = Path(d) / "free_fall" / "report.pdf"
            stale.write_bytes(b"%PDF-stale" * 200)
            self.assertIsNone(compile_pdf(Path(d) / "free_fall" / "report.tex", binary="no-such-pdflatex-binary")["pdf"])
            self.assertFalse(stale.exists())

    @unittest.skipUnless(shutil.which("pdflatex"), "pdflatex not installed")
    def test_broken_tex_is_a_fallback_not_a_pdf(self):
        with tempfile.TemporaryDirectory() as d:
            tex = Path(d) / "report.tex"
            tex.write_text("\\documentclass{article}\\begin{document}\\undefinedcommand\\end{document}")
            (Path(d) / "report.html").write_text("<p>x</p>")
            e = compile_pdf(tex)
            self.assertEqual((e["status"], e["pdf"]), ("html-print-fallback", None))
            self.assertFalse((Path(d) / "report.pdf").exists())


if __name__ == "__main__":
    unittest.main()

