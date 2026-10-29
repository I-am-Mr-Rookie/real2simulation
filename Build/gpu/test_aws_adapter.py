import unittest

import aws_adapter as m

ON = {m.ENV_FLAG: "1"}
OK = m.OWNER_GATES


def without(key, sub=None):
    g = {**OK, "budget": dict(OK["budget"])}
    (g["budget"] if sub else g).pop(sub or key)
    return g


class AwsAdapter(unittest.TestCase):
    def test_default_off_even_with_all_gates(self):
        r = m.activate(OK, env={})
        self.assertFalse(r["active"])
        self.assertEqual(len(r["reasons"]), 1)
        self.assertTrue(r["reasons"][0].startswith("disabled"))

    def test_flag_must_be_exactly_1(self):
        for v in ("true", "yes", "0", " 1"):
            self.assertFalse(m.activate(OK, env={m.ENV_FLAG: v})["active"], v)

    def test_all_gates_pass_plans_but_never_launches(self):
        r = m.activate(OK, env=ON)
        self.assertEqual(r["reasons"], [])
        self.assertTrue(r["active"])
        self.assertFalse(r["launched"])
        self.assertEqual(r["plan"]["market"], "spot")

    def test_on_demand_refused(self):
        r = m.activate({**OK, "market": "on-demand"}, env=ON)
        self.assertFalse(r["active"])
        self.assertTrue(any(x.startswith("market") for x in r["reasons"]))

    def test_each_missing_gate_refuses(self):
        cases = {"region": without("region"), "market": without("market"),
                 "quota": without("spot_quota_vcpu"), "budget": without("budget")}
        for sub in ("amount_usd", "services", "alerts"):
            cases[f"budget.{sub}"] = without("budget", sub)
        cases["empty"] = {}
        cases["none"] = None
        for name, g in cases.items():
            r = m.activate(g, env=ON)
            self.assertFalse(r["active"], name)
            self.assertIsNone(r["plan"], name)

    def test_bad_values_refuse(self):
        bad = [{"region": "us-east-1"}, {"spot_quota_vcpu": 0}, {"spot_quota_vcpu": 2},
               {"spot_quota_vcpu": True}, {"spot_quota_vcpu": "8"},
               {"budget": {**OK["budget"], "amount_usd": 51}},
               {"budget": {**OK["budget"], "amount_usd": 0}},
               {"budget": {**OK["budget"], "services": ["EC2 - Other"]}},
               {"budget": {**OK["budget"], "alerts": ["actual:100"]}}]
        for b in bad:
            self.assertFalse(m.activate({**OK, **b}, env=ON)["active"], b)

    def test_no_aws_sdk_imported(self):
        import sys
        from pathlib import Path
        self.assertNotIn("boto3", sys.modules)
        self.assertNotIn("boto3", Path(m.__file__).read_text(encoding="utf-8").split('"""', 2)[2])


if __name__ == "__main__":
    unittest.main()

