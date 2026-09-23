import numpy as np
import pytest

from hexapod.backends import mujoco_available
from hexapod.config import RobotConfig
from hexapod.io import CsvLogger
from hexapod.sim import Simulation
from hexapod.stability import convex_hull, stability_margin


def test_kinematic_60s_logs_6000_rows(tmp_path):
    cfg = RobotConfig.load()
    sim = Simulation(cfg, "kinematic")
    sim.controller.set_command(0.05, 0, 0)
    with CsvLogger(cfg, tmp_path, "run") as lg:
        for _ in range(6000):
            lg.log(sim.step())
    assert lg.rows == 6000
    assert len(lg.path.read_text().splitlines()) == 6001
    assert sim.state.body_pos[0] == pytest.approx(3.0, abs=1e-6)


def test_deterministic():
    def run():
        s = Simulation(backend="kinematic")
        s.controller.set_command(0.04, 0.01, 0.2)
        for _ in range(500):
            f = s.step()
        return f.state.feet
    np.testing.assert_array_equal(run(), run())


def test_margin_square():
    poly = convex_hull(np.array([[1, 1], [-1, 1], [-1, -1], [1, -1], [0, 0]]))
    assert len(poly) == 4
    assert stability_margin(poly, np.array([0, 0])) == pytest.approx(1.0)
    assert stability_margin(poly, np.array([2, 0])) < 0


@pytest.mark.skipif(not mujoco_available(), reason="cần MuJoCo")
def test_mujoco_walks_without_falling():
    sim = Simulation(backend="mujoco")
    sim.controller.set_command(0.05, 0, 0)
    for _ in range(6000):
        f = sim.step()
        roll, pitch, _ = f.state.rpy
        assert abs(roll) < np.radians(15) and abs(pitch) < np.radians(15)
        assert f.state.body_pos[2] > 0.06
    assert f.state.body_pos[0] > 2.5
