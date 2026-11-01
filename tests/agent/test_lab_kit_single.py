"""N33: a one-ball cradle is a pendulum, so the fitted exit speed must match sqrt(2 g L (1 - cos a))."""
import math

from tests.agent.test_lab_kit import _run


def test_one_ball_cradle_matches_energy():
    cr = _run(("cradle", {"count": 1}))["cradle-1"]
    assert math.isclose(cr["exit_speed"]["value"], cr["theory_impact_speed_m_s"]["value"], rel_tol=0.02)
