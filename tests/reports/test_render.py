import copy
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from Build.reports import ReportError
from Build.reports.render import build_charts, build_tables, write_all
from tests.reports.fixture import synthetic_fitter_result, synthetic_report


class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fit = synthetic_fitter_result()

    def make(self, fit=None):
        fit = fit or self.fit
        return synthetic_report(fit), fit

    def test_summary_table_preserves_value_unit_uncertainty_label(self):
        rep, fit = self.make()
        rows = {r["id"]: r for r in build_tables(rep, fit)[0]["rows"]}
        g = rows["g"]
        self.assertEqual((g["value"], g["unit"], g["uncertainty"], g["label"]),
                         (fit["gravity"]["value"], "m/s^2", fit["gravity"]["uncertainty"], "simulated"))
        self.assertEqual((rows["n"]["value"], rows["n"]["unit"]), (8, "1"))
        self.assertNotIn("uncertainty", rows["rmse"])  # none claimed where the fitter gave none
        self.assertEqual(float(g["display"]), float(format(fit["gravity"]["value"], ".6g")))

    def test_residual_table_matches_fitter(self):
        rep, fit = self.make()
        t = build_tables(rep, fit)[1]
        self.assertEqual([r["residual"] for r in t["rows"]], fit["fit"]["residuals"])
        self.assertEqual([r["fitted"] for r in t["rows"]], fit["fit"]["fitted"])
        self.assertEqual({(r["unit"], r["label"]) for r in t["rows"]}, {("m", "simulated")})
        self.assertEqual(t["labels"], ["simulated"])

    def test_charts_wellformed_labelled_and_carry_exact_data(self):
        rep, fit = self.make()
        charts = build_charts(rep, fit)
        self.assertEqual(set(charts), {"gravity", "residuals", "model_selection"})
        for name, svg in charts.items():
            root = ET.fromstring(svg)
            self.assertIn("source: simulated", svg)
            self.assertIn(rep["fitter_digest"], svg)
        ns = {"s": "http://www.w3.org/2000/svg"}
        g = ET.fromstring(charts["gravity"])
        self.assertEqual(float(g.find(".//s:rect[@data-value]", ns).get("data-value")), fit["gravity"]["value"])
        self.assertEqual(float(g.find(".//s:line[@data-uncertainty]", ns).get("data-uncertainty")), fit["gravity"]["uncertainty"])
        self.assertIn("value [m/s^2]", charts["gravity"])
        res = ET.fromstring(charts["residuals"])
        self.assertEqual([float(r.get("data-value")) for r in res.findall(".//s:rect[@data-value]", ns)], fit["fit"]["residuals"])
        self.assertIn("value [m]", charts["residuals"])
        self.assertNotIn("data-uncertainty", charts["residuals"])  # none invented

    def test_output_is_deterministic_bytes(self):
        rep, fit = self.make()
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            pa, pb = write_all(rep, fit, a), write_all(rep, fit, b)
            self.assertEqual([p.name for p in pa], ["tables.json", "chart_gravity.svg", "chart_residuals.svg", "chart_model_selection.svg"])
            for x, y in zip(pa, pb):
                self.assertEqual(x.read_bytes(), y.read_bytes())

    def test_untraceable_report_is_refused_and_writes_nothing(self):
        rep, fit = self.make()
        rep["numbers"]["g"]["value"] += 1e-9
        for fn in (build_tables, build_charts):
            with self.assertRaises(ReportError):
                fn(rep, fit)
        with tempfile.TemporaryDirectory() as d, self.assertRaises(ReportError):
            write_all(rep, fit, Path(d) / "out")
        self.assertFalse((Path(d) / "out" / "tables.json").exists())

    def test_measured_label_is_copied_not_assumed(self):
        fit = copy.deepcopy(self.fit)
        for k in ("gravity", "fit", "covariance", "model_selection"):
            fit[k]["source"]["label"] = "measured"
        rep, fit = self.make(fit)
        self.assertEqual(build_tables(rep, fit)[0]["labels"], ["measured"])
        for svg in build_charts(rep, fit).values():
            self.assertIn("source: measured", svg)
            self.assertNotIn("simulated", svg)

    def test_hostile_unit_is_escaped(self):
        fit = copy.deepcopy(self.fit)
        fit["gravity"]["unit"] = 'm<&>"s'
        rep, fit = self.make(fit)
        svg = build_charts(rep, fit)["gravity"]
        ET.fromstring(svg)
        self.assertNotIn("<&>", svg)

    def test_unavailable_aic_is_skipped_not_drawn(self):
        fit = copy.deepcopy(self.fit)
        fit["model_selection"]["aic"][0] = None
        fit["model_selection"]["aic_status"][0] = "unavailable_nonfinite"
        rep, fit = self.make(fit)
        svg = build_charts(rep, fit)["model_selection"]
        self.assertEqual(svg.count("data-value="), 1)
        fit["model_selection"]["aic_status"] = ["unavailable_nonfinite"] * 2
        rep, fit = self.make(fit)
        self.assertNotIn("model_selection", build_charts(rep, fit))


if __name__ == "__main__":
    unittest.main()
