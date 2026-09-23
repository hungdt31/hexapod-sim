"""HexapodController: lệnh vận tốc + tư thế thân -> góc khớp mục tiêu cho 18 khớp."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .body import BodyPose
from .config import RobotConfig
from .gait import GaitScheduler, make_gait
from .geometry import mount_positions
from .kinematics import LegKinematics
from .trajectory import foot_target


@dataclass
class VelocityCommand:
    vx: float = 0.0
    vy: float = 0.0
    wz: float = 0.0


@dataclass
class ControlOutput:
    q: np.ndarray                 # (6, 3) góc khớp mục tiêu
    swing: np.ndarray             # (6,) bool
    progress: np.ndarray          # (6,) tiến độ pha 0..1
    feet_heading: np.ndarray      # (6, 3) đầu chân trong hệ heading
    ik_warn: np.ndarray           # (6,) bool: IK phải kẹp
    stride: float = 0.0
    command: VelocityCommand = field(default_factory=VelocityCommand)


class HexapodController:
    def __init__(self, cfg: RobotConfig | None = None) -> None:
        self.cfg = cfg or RobotConfig()
        c = self.cfg
        self.leg = LegKinematics(*c.leg.lengths, limits=c.leg.joint_limits_deg.as_radians())
        self.mount_angles = c.mount_angles
        self.mounts = mount_positions(c.body.radius, self.mount_angles)
        reach = c.body.radius + c.leg.lengths[0] + c.leg.home_reach
        self.home = np.stack(
            [reach * np.cos(self.mount_angles), reach * np.sin(self.mount_angles), np.zeros(6)], axis=1
        )
        self.scheduler = GaitScheduler(make_gait(c.gait.default))
        self.command = VelocityCommand()
        self.pose = BodyPose(height=c.body.stand_height)
        self.swing_height = c.gait.swing_height
        self.max_stride = c.gait.max_stride
        self.t = 0.0

    # --- lệnh -------------------------------------------------------------
    def set_command(self, vx: float, vy: float, wz: float) -> None:
        self.command = VelocityCommand(float(vx), float(vy), float(wz))

    def set_body_pose(self, height: float | None = None, roll: float | None = None,
                      pitch: float | None = None) -> None:
        if height is not None:
            self.pose.height = float(height)
        if roll is not None:
            self.pose.roll = float(roll)
        if pitch is not None:
            self.pose.pitch = float(pitch)

    def set_gait(self, name: str) -> None:
        self.scheduler.set_gait(make_gait(name))

    @property
    def gait_name(self) -> str:
        return self.scheduler.gait.name

    # --- tính toán ---------------------------------------------------------
    def standing_q(self) -> np.ndarray:
        return np.stack([self._solve(i, self.home[i])[0] for i in range(6)])

    def _solve(self, i: int, p_heading: np.ndarray) -> tuple[np.ndarray, bool]:
        p_body = self.pose.heading_to_body(p_heading)
        p_leg = BodyPose.body_to_leg(p_body, self.mounts[i], self.mount_angles[i])
        return self.leg.ik_clamped(p_leg)

    def step(self, dt: float) -> ControlOutput:
        self.t += dt
        self.scheduler.step(dt)
        sch, cmd = self.scheduler, self.command
        q = np.zeros((6, 3))
        swing = np.zeros(6, dtype=bool)
        prog = np.zeros(6)
        feet = np.zeros((6, 3))
        warn = np.zeros(6, dtype=bool)
        stride = 0.0
        for i in range(6):
            sw, s = sch.phase(i)
            p, st = foot_target(self.home[i], cmd.vx, cmd.vy, cmd.wz, sch.beta, sch.period,
                                sw, s, self.swing_height, self.max_stride)
            q[i], ok = self._solve(i, p)
            swing[i], prog[i], feet[i], warn[i] = sw, s, p, not ok
            stride = max(stride, st)
        return ControlOutput(q, swing, prog, feet, warn, stride, cmd)
