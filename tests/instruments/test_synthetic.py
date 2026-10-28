import unittest

from Build.instruments.synthetic import (camera_observation, light_gate_observation,
                                         ruler_observation, stopwatch_observation)


class SyntheticInstrumentTests(unittest.TestCase):
    def test_stopwatch_seed_and_bias_are_replayable(self):
        kwargs = dict(seed=9, bias_s=0.2, noise_std_s=0.1, resolution_s=0.01,
                      uncertainty_s=0.05)
        first = stopwatch_observation(2.0, **kwargs)
        self.assertEqual(first, stopwatch_observation(2.0, **kwargs))
        unbiased = stopwatch_observation(2.0, **dict(kwargs, bias_s=0.0))
        self.assertGreater(first["value"], unbiased["value"])
        self.assertEqual(first["source"]["label"], "simulated")
        self.assertEqual(first["error"], first["value"] - 2.0)

    def test_camera_ruler_gate_quantize_boundaries_and_negative_rejection(self):
        camera = camera_observation(3, 1.25, -1.25, 2.26,
                                    time_resolution_s=0.1, pixel_resolution_px=1,
                                    time_uncertainty_s=0.05, pixel_uncertainty_px=0.5,
                                    time_bias_s=0, pixel_bias_px=0)
        self.assertEqual(camera["time"]["value"], 1.3)
        self.assertAlmostEqual(camera["time"]["error"], 0.05)
        self.assertEqual(camera["x"]["value"], -1.0)  # half-away from zero
        self.assertEqual(camera["y"]["value"], 2.0)
        self.assertAlmostEqual(ruler_observation(1.24, resolution_m=0.1,
                                                 uncertainty_m=0.01, bias_m=0)["value"], 1.2)
        self.assertAlmostEqual(light_gate_observation(0.26, resolution_s=0.1,
                                                     uncertainty_s=0.01, bias_s=0)["value"], 0.3)
        with self.assertRaises(ValueError):
            ruler_observation(-1, resolution_m=0.1, uncertainty_m=0.01, bias_m=0)

    def test_negative_bias_and_overflow_are_explicitly_rejected(self):
        for call in (
            lambda: stopwatch_observation(0.1, seed=1, bias_s=-1, noise_std_s=0,
                                          resolution_s=0.1, uncertainty_s=0),
            lambda: ruler_observation(0.1, resolution_m=0.1, uncertainty_m=0, bias_m=-1),
            lambda: light_gate_observation(0.1, resolution_s=0.1, uncertainty_s=0, bias_s=-1),
            lambda: camera_observation(0.1, 0, 0, 0, time_resolution_s=0.1,
                                       pixel_resolution_px=1, time_uncertainty_s=0,
                                       pixel_uncertainty_px=0, time_bias_s=-1, pixel_bias_px=0),
        ):
            with self.assertRaises(ValueError):
                call()
        with self.assertRaises(ValueError):
            ruler_observation(10 ** 1000, resolution_m=1, uncertainty_m=0, bias_m=0)
        with self.assertRaises(ValueError):
            light_gate_observation(1e308, resolution_s=1e-308, uncertainty_s=0, bias_s=0)

    def test_each_quantized_output_reports_total_observed_minus_true(self):
        ruler = ruler_observation(1.24, resolution_m=0.1, uncertainty_m=0, bias_m=0.02)
        gate = light_gate_observation(0.26, resolution_s=0.1, uncertainty_s=0, bias_s=0.02)
        self.assertAlmostEqual(ruler["error"], ruler["value"] - 1.24)
        self.assertAlmostEqual(gate["error"], gate["value"] - 0.26)

    def test_invalid_sensor_parameters_rejected(self):
        with self.assertRaises(ValueError):
            stopwatch_observation(1, seed=True, bias_s=0, noise_std_s=0,
                                  resolution_s=0.1, uncertainty_s=0)
        with self.assertRaises(ValueError):
            camera_observation(0, 1, 0, 0, time_resolution_s=0,
                               pixel_resolution_px=1, time_uncertainty_s=0,
                               pixel_uncertainty_px=0, time_bias_s=0, pixel_bias_px=0)


if __name__ == "__main__":
    unittest.main()
