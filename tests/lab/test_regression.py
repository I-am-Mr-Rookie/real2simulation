import unittest
from Build.lab.regression import run_regression


class RegressionTests(unittest.TestCase):
    def test_actual_four_template_analytic_comparison(self):
        result = run_regression()
        self.assertTrue(result['passed'], result)
        self.assertEqual({case['template'] for case in result['cases']},
                         {'free_fall', 'projectile', 'ramp', 'pendulum'})
        self.assertTrue(all(case['samples'] > 100 and case['deterministic'] for case in result['cases']))
