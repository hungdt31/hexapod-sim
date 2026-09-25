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


def test_balance_feedback_leans_ik_frame_toward_level():
    cfg = RobotConfig.load()
    cfg.stability.kp_roll = 0.5
    cfg.stability.max_correction_deg = 90.0
    ctl = HexapodController(cfg)
    ik_roll, ik_pitch = ctl._ik_roll_pitch((np.radians(10), 0.0))
    # thân cảm nhận nghiêng dương hơn đã lệnh -> khung IK bù giảm để san bằng
    assert ik_roll < ctl.pose.roll
    assert ik_pitch == ctl.pose.pitch  # pitch cảm nhận == đã lệnh -> sai lệch = 0, không bù


def test_balance_feedback_disabled_ignores_sensed_rpy():
    cfg = RobotConfig.load()
    cfg.stability.enabled = False
    q_no_sense = HexapodController(cfg).step(0.01, sensed_rpy=None).q
    q_tilted = HexapodController(cfg).step(0.01, sensed_rpy=(np.radians(10), 0.0)).q
    np.testing.assert_array_equal(q_no_sense, q_tilted)


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
