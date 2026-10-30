"""S17f: structural accessibility + print-fallback checks on every template's HTML (fixture-labelled; no fabricated PDF claims)."""
import re
import unittest
from html.parser import HTMLParser

from Build.reports import render_html
from Build.reports.diff import diff_report
from Build.reports.typeset import TEMPLATE_TEXT
from tests.reports.fixture import synthetic_fitter_result, synthetic_report
from tests.reports.templates import report as tpl_report, request as tpl_request

FIT = synthetic_fitter_result()


class Probe(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.headings, self.ids, self.th, self.imgs, self.regions = [], [], [], [], [], []

    def handle_starttag(self, tag, a):
        a = dict(a)
        self.tags.append(tag)
        if "id" in a:
            self.ids.append(a["id"])
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        if tag == "th":
            self.th.append(a.get("scope"))
        if tag == "img":
            self.imgs.append(a.get("alt", ""))
        if tag == "div" and a.get("role") == "region":
            self.regions.append(a)


class TestA11y(unittest.TestCase):
    def probe(self, tpl):
        p = Probe()
        doc = render_html(synthetic_report(FIT, tpl), FIT)
        p.feed(doc)
        return p, doc

    def test_every_template_semantics(self):
        for tpl in TEMPLATE_TEXT:
            p, doc = self.probe(tpl)
            with self.subTest(tpl):
                self.assertIn('<html lang="en">', doc)
                self.assertEqual(p.headings.count(1), 1)
                self.assertEqual(p.headings[0], 1)
                self.assertTrue(all(b - a <= 1 for a, b in zip(p.headings, p.headings[1:])), p.headings)
                self.assertEqual(p.tags.count("main"), 1)
                self.assertIn('href="#main"', doc)
                self.assertEqual(len(p.ids), len(set(p.ids)))
                self.assertEqual(p.tags.count("caption"), p.tags.count("table"))
                self.assertTrue(p.th and all(s in ("col", "row") for s in p.th))
                self.assertTrue(p.regions and all(r.get("tabindex") == "0" and r.get("aria-label") for r in p.regions))
                self.assertTrue(p.imgs and all(len(a) > 20 for a in p.imgs))
                self.assertIn("viewport", doc)

    def test_print_css_and_html_fallback_note(self):
        _, doc = self.probe("free_fall")
        self.assertIn("@media print", doc)
        self.assertIn("Save as PDF", doc)
        self.assertNotIn("<script", doc)

    def test_a11y_markup_adds_no_numbers_and_diff_still_clean(self):
        for tpl in TEMPLATE_TEXT:
            r = diff_report(tpl_report(tpl), tpl_request(tpl))
            self.assertEqual(r["mismatches"], [], tpl)


if __name__ == "__main__":
    unittest.main()
