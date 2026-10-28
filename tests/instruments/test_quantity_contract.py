import math
import unittest

from contracts.fit.quantity import Quantity, validate_quantity


class QuantityContractTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "value": 9.81,
            "unit": "m/s^2",
            "uncertainty": 0.05,
            "error": -0.01,
            "source": {"label": "simulated", "evidence": "fixture seed 7"},
        }

    def test_round_trip_preserves_error_separately(self):
        quantity = Quantity(**self.payload)
        self.assertEqual(quantity.to_dict(), self.payload)
        self.assertNotEqual(quantity.uncertainty, abs(quantity.error))

    def test_rejects_bad_booleans_nonfinite_and_provenance(self):
        for field, value in (("value", True), ("value", 10 ** 1000),
                             ("uncertainty", math.nan), ("error", math.inf)):
            with self.subTest(field=field):
                bad = dict(self.payload, **{field: value})
                with self.assertRaises(ValueError):
                    validate_quantity(bad)
        for source in ({"label": "measured", "evidence": "x"},
                       {"label": "simulated", "evidence": ""},
                       {"label": "simulated", "evidence": "x", "extra": 1}):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    validate_quantity(dict(self.payload, source=source))

    def test_rejects_negative_uncertainty_and_missing_unit(self):
        for bad in (dict(self.payload, uncertainty=-1), dict(self.payload, unit=None)):
            with self.assertRaises(ValueError):
                validate_quantity(bad)

    def test_constructor_normalizes_and_freezes_source(self):
        source = {"label": "simulated", "evidence": "fixture"}
        quantity = Quantity(1, "s", 0, source)
        source["evidence"] = "mutated"
        self.assertEqual(quantity.source["evidence"], "fixture")
        with self.assertRaises(TypeError):
            quantity.source["evidence"] = "changed"


if __name__ == "__main__":
    unittest.main()
