import copy
import unittest

from Build.reports import ReportError, digest, number_entry, resolve, validate_report
from Build.reports.contract import TEMPLATES
from tests.reports.fixture import synthetic_fitter_result, synthetic_report


class ReportContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fit = synthetic_fitter_result()

    def report(self):
        return synthetic_report(copy.deepcopy(self.fit))

    def rejects(self, report, fit=None, text=None):
        with self.assertRaises(ReportError) as cm:
            validate_report(report, fit or self.fit)
        if text:
            self.assertIn(text, str(cm.exception))

    def test_traced_report_accepted_for_all_templates(self):
        for template in TEMPLATES:
            validate_report(synthetic_report(self.fit, template), self.fit)

    def test_numbers_copy_fitter_value_unit_label_exactly(self):
        g = self.report()["numbers"]["g"]
        self.assertEqual((g["value"], g["unit"], g["label"]), (self.fit["gravity"]["value"], "m/s^2", "simulated"))
        self.assertEqual(g["uncertainty"], self.fit["gravity"]["uncertainty"])
        self.assertEqual(resolve(self.fit, "fit.residuals[2]")[1:], ("m", "simulated"))
        self.assertEqual(resolve(self.fit, "fit.rss")[1], "m^2")

    def test_model_authored_value_rejected(self):
        for bad in (9.81, self.fit["gravity"]["value"] + 1e-12, True, float("nan"), "9.81"):
            r = self.report(); r["numbers"]["g"]["value"] = bad
            self.rejects(r)
        r = self.report(); r["numbers"]["n"]["value"] = float(r["numbers"]["n"]["value"])
        self.rejects(r, text="value_not_from_fitter")  # 8.0 != int 8 type: no silent coercion

    def test_model_authored_number_without_path_rejected(self):
        r = self.report(); r["numbers"]["extra"] = {"value": 9.81, "unit": "m/s^2", "label": "simulated"}
        self.rejects(r, text="bad_number_entry")
        r = self.report(); r["numbers"]["extra"] = {"path": "gravity.value", "value": 9.81, "unit": "m/s^2", "label": "simulated"}
        self.rejects(r, text="value_not_from_fitter")

    def test_numerals_in_prose_rejected(self):
        for text in ("Fitted g is 9.81 m/s^2.", "g is about nine point eight.", "Roughly ½ of runs.", "g is 9\u00b2",
                     "Value \u0669 here", "Trial one: {{g}}", "Value {{g}} ten"):
            r = self.report(); r["sections"][0]["text"] = [text]
            self.rejects(r, text="unreferenced_number")
        r = self.report(); r["title"] = "Run 3"
        self.rejects(r, text="title_contains_unreferenced_number")
        r = self.report(); r["sections"][0]["title"] = "Results 2"
        self.rejects(r)

    def test_placeholders_must_resolve(self):
        r = self.report(); r["sections"][0]["text"] = ["Value {{missing}}."]
        self.rejects(r, text="placeholder_without_number")
        r = self.report(); r["sections"][0]["text"] = ["Value {{g}} {{ unfinished"]
        self.rejects(r, text="malformed_placeholder")

    def test_label_unit_and_digest_cannot_be_changed(self):
        r = self.report(); r["numbers"]["g"]["label"] = "measured"
        self.rejects(r, text="unit_or_label_not_from_fitter")
        r = self.report(); r["numbers"]["g"]["unit"] = "m/s"
        self.rejects(r, text="unit_or_label_not_from_fitter")
        r = self.report(); r["numbers"]["g"]["uncertainty"] = 0.0
        self.rejects(r, text="uncertainty_not_from_fitter")
        other = copy.deepcopy(self.fit); other["gravity"]["value"] += 1.0
        self.rejects(self.report(), fit=other, text="fitter_digest_mismatch")
        r = self.report(); r["fitter_digest"] = digest(other)
        self.rejects(r, fit=other, text="value_not_from_fitter")

    def test_label_never_upgraded_by_fitter_relabel(self):
        # Even if a fitter result claimed "measured", the report must carry that label, not infer it.
        fit = copy.deepcopy(self.fit); fit["gravity"]["source"]["label"] = "measured"
        rep = synthetic_report(fit)
        self.assertEqual(rep["numbers"]["g"]["label"], "measured")
        fit["gravity"]["source"]["label"] = "invented"
        with self.assertRaises(ReportError):
            number_entry(fit, "gravity.value")

    def test_structure_is_closed(self):
        r = self.report(); r["summary"] = "g = 9.81"
        self.rejects(r, text="report_fields_must_be_exactly")
        r = self.report(); r["sections"][0]["g"] = 9.81
        self.rejects(r, text="fields_must_be_exactly")
        r = self.report(); r["numbers"]["g"]["extra"] = 1
        self.rejects(r, text="bad_number_entry")
        r = self.report(); r["template"] = "madeup"
        self.rejects(r, text="unknown_template")
        r = self.report(); r["numbers"]["g1"] = r["numbers"]["g"]
        self.rejects(r, text="bad_number_id")
        r = self.report(); r["schema"] = "other"
        self.rejects(r, text="unsupported_schema")

    def test_only_reportable_fitter_paths_and_ok_results(self):
        for path in ("status", "fit.coefficients", "fit.coefficients[0]", "fit.residuals", "fit.residuals[99]",
                     "gravity", "gravity.source", "covariance.valid", "model_selection.aic[x]", "../gravity.value"):
            with self.assertRaises(ReportError, msg=path):
                resolve(self.fit, path)
        with self.assertRaises(ReportError):
            resolve({"status": "error", "error": {"code": "x"}}, "gravity.value")
        err = {"status": "ok"}
        with self.assertRaises(ReportError):
            resolve(err, "gravity.value")

    def test_nonfinite_fitter_value_rejected(self):
        fit = copy.deepcopy(self.fit); fit["gravity"]["value"] = float("inf")
        with self.assertRaises(ReportError):
            resolve(fit, "gravity.value")


if __name__ == "__main__":
    unittest.main()
