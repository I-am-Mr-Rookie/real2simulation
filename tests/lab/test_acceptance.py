import unittest

from Build.lab.acceptance import THRESHOLD, case_matrix, run_acceptance


class AcceptanceTests(unittest.TestCase):
    def test_matrix_covers_four_templates_and_explicit_edges(self):
        cases = case_matrix()
        self.assertEqual({case['template'] for case in cases},
                         {'free_fall', 'projectile', 'ramp', 'pendulum'})
        names = {case['case'] for case in cases}
        self.assertTrue({'upward-launch', 'zero-horizontal', 'tiny-height',
                         'endpoint-preflight', 'two-period-horizon',
                         'zero-answer-equilibrium'} <= names)
        self.assertEqual(THRESHOLD, 0.005)

    def test_actual_acceptance_keeps_all_cases_and_replay_evidence(self):
        result = run_acceptance(write_evidence=False)
        self.assertEqual(result['case_counts']['authored'], len(case_matrix()))
        self.assertEqual(result['case_counts']['rejected'], 0, result)
        self.assertTrue(result['passed'], result)
        self.assertTrue(all(case['deterministic'] and case['replay']['seedBound']
                            for case in result['cases']))
        equilibrium = next(case for case in result['cases']
                            if case['case'] == 'zero-answer-equilibrium')
        self.assertEqual(equilibrium['scale_policy'], 'zero_answer_guard')
        self.assertEqual(equilibrium['relative_error'], 0.0)


if __name__ == '__main__':
    unittest.main()
