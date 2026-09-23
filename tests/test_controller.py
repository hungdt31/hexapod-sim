import numpy as np

from hexapod.backends import KinematicBackend
from hexapod.config import RobotConfig
from hexapod.controller import HexapodController


def test_body_rotation_keeps_feet_fixed():
    cfg = RobotConfig.load()
    ctl = HexapodController(cfg)
    be = KinematicBackend(cfg, ctl.pose)
    be.reset(ctl.standing_q())
    before = be.feet_world()
    ctl.set_body_pose(roll=np.radians(10), pitch=np.radians(-8))
    be.q = ctl.standing_q()
    after = be.feet_world()
    assert np.abs(after - before).max() < 1e-6


def test_stride_is_clamped():
    ctl = HexapodController()
    ctl.set_command(1.0, 0, 0)
    out = ctl.step(0.01)
    assert out.stride <= ctl.max_stride + 1e-12


def test_stance_feet_fixed_in_world_when_walking():
    from hexapod.sim import Simulation
    sim = Simulation(backend="kinematic")
    sim.controller.set_command(0.05, 0, 0)
    prev = None
    worst = 0.0
    for _ in range(300):
        f = sim.step()
        feet, stance = f.state.feet, ~f.control.swing
        if prev is not None:
            both = stance & prev[1]
            if both.any():
                worst = max(worst, float(np.abs(feet[both, :2] - prev[0][both, :2]).max()))
        prev = (feet.copy(), stance.copy())
    assert worst < 1e-3
