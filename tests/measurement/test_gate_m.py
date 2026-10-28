"""Synthetic evaluator regressions, NOT actual-media measurements or gate success."""
import math
from pathlib import Path
import unittest
from unittest.mock import patch

from test_free_fall import record
from test_uncertainty import assumptions
from Build.measurement.gate_m import (evaluate_record, summarize, evaluate_sources,
                                      scene_approval_ids)


class GateMTests(unittest.TestCase):
    def trial(self, g=9.81):
        return evaluate_record(record(g=g, origin=0), assumptions(),
                               metric_authorized=True, custody_verified=True)

    def test_empty_is_input_readiness_failure_not_measured_failure(self):
        out = summarize([])
        self.assertFalse(out['gate_passed'])
        self.assertEqual(out['status'], 'NOT_MET_INPUT_READINESS')
        self.assertEqual(out['required_trials'], 3)
        self.assertEqual(out['measured_count'], 0)
        self.assertIsNone(out['mean_g_m_s2'])
        self.assertIsNone(out['mean_relative_error'])
        self.assertIsNone(out['coverage'])

    def test_approval_string_never_grants_authorization(self):
        with patch('Build.measurement.gate_m.fit_free_fall',
                   side_effect=AssertionError('unauthorized fitting forbidden')):
            out = evaluate_record(record(), assumptions(), custody_verified=True)
        self.assertIn('metric_use_not_authorized_by_receipt', out['blockers'])
        self.assertIsNone(out['g_m_s2'])

    def test_custody_required_even_with_authorization(self):
        out = evaluate_record(record(), assumptions(), metric_authorized=True)
        self.assertIn('held_out_custody_unverified', out['blockers'])
        self.assertIsNone(out['g_m_s2'])

    def test_unknown_scale_clock_and_scene_scope_abstain(self):
        data = record()
        data['scale'] = data['timebase'] = None
        data['approval']['scope'] = 'scene_tracking'
        out = evaluate_record(data, assumptions(), metric_authorized=True,
                              custody_verified=True)
        for blocker in ('metric_use_not_approved', 'scale_unverified',
                        'capture_timebase_unverified'):
            self.assertIn(blocker, out['blockers'])
        self.assertIsNone(out['relative_error'])

    def test_fitter_and_standard_uncertainty_not_coverage(self):
        out = self.trial()
        self.assertAlmostEqual(out['g_m_s2'], 9.81)
        self.assertGreater(out['standard_uncertainty_m_s2'], 0)
        self.assertIsNone(out['uncertainty_covers_reference'])
        self.assertIn('coverage_not_established_by_standard_uncertainty', out['blockers'])
        self.assertFalse(summarize([out]*3)['gate_passed'])

    def test_unknown_uncertainty_does_not_invent_measurement(self):
        out = evaluate_record(record(), {}, metric_authorized=True, custody_verified=True)
        self.assertIn('unknown_detection_std_px', out['blockers'])
        self.assertIsNone(out['g_m_s2'])

    def test_malformed_and_nonpositive_motion_do_not_escape(self):
        data = record()
        data['frames'][0]['pts_s'] = math.nan
        out = evaluate_record(data, assumptions(), metric_authorized=True, custody_verified=True)
        self.assertIn('invalid_input', out['blockers'][0])
        self.assertIsNone(self.trial(-1)['g_m_s2'])

    def test_fixed_denominator_threshold_and_coverage_boundaries(self):
        # These summary inputs are synthetic outcome fixtures, not receipts.
        def outcome(error, coverage=True, group='a'):
            return dict(g_m_s2=9.81*(1+error), relative_error=error,
                        uncertainty_covers_reference=coverage, capture_group=group,
                        blockers=[])
        good = outcome(.05)
        second = outcome(.049, group='b')
        self.assertFalse(summarize([good, second])['gate_passed'])
        third = outcome(.2, group='c')
        self.assertTrue(summarize([good, second, third])['gate_passed'])
        self.assertFalse(summarize([outcome(math.nextafter(.05, 1)), second, third])['gate_passed'])
        self.assertFalse(summarize([outcome(.01, None), second, third])['gate_passed'])
        self.assertFalse(summarize([good, good, third])['gate_passed'])

    def test_cannot_select_best_three_or_count_unknown_independence(self):
        fixture = dict(g_m_s2=9.81, relative_error=0., uncertainty_covers_reference=True,
                       capture_group=None, blockers=[])
        self.assertFalse(summarize([fixture]*3)['gate_passed'])
        known = [dict(fixture, capture_group=str(i)) for i in range(4)]
        self.assertFalse(summarize(known)['gate_passed'])

    def test_actual_sources_are_not_synthetic_success(self):
        root = Path(__file__).resolve().parents[2]
        out = evaluate_sources(root)
        self.assertEqual(out['evidence_kind'], 'actual_source_readiness_evaluation')
        self.assertEqual(out['scene_tracking_approved_count'], 1)
        self.assertEqual(out['metric_approved_count'], 0)
        self.assertEqual(out['eligible_count'], 0)
        self.assertEqual(out['gate']['measured_count'], 0)
        self.assertFalse(out['gate']['gate_passed'])
        self.assertEqual(len(out['trials']), 8)
        self.assertTrue(out['sources_sha256'])
        for trial in out['trials']:
            self.assertIsNone(trial['g_m_s2'])
            self.assertIsNone(trial['relative_error'])
            self.assertIsNone(trial['uncertainty_covers_reference'])

    def test_approval_receipt_line_endings_not_permission_changes(self):
        root = Path(__file__).resolve().parents[2]
        text = (root/'evidence/owner/S02/APPROVAL.md').read_text(encoding='utf-8')
        self.assertIn('ST03', scene_approval_ids(text))
        self.assertEqual(scene_approval_ids(text), scene_approval_ids(text.replace('\n', '\r\n')))
        self.assertEqual(scene_approval_ids(text.replace('tracking', 'metric')), frozenset())


if __name__ == '__main__':
    unittest.main()
