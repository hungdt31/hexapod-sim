"""Backend động học thuần: khớp đạt ngay góc lệnh, thân di chuyển theo lệnh vận tốc."""

from __future__ import annotations

import math

import numpy as np

from ..body import BodyPose
from ..config import RobotConfig
from ..geometry import mount_positions, rot_z, rpy_matrix, rpy_to_quat
from ..kinematics import LegKinematics
from .base import RobotState, SimBackend


class KinematicBackend(SimBackend):
    name = "kinematic"

    def __init__(self, cfg: RobotConfig, pose: BodyPose | None = None) -> None:
        self.cfg = cfg
        self.pose = pose or BodyPose(height=cfg.body.stand_height)
        self.leg = LegKinematics(*cfg.leg.lengths, limits=cfg.leg.joint_limits_deg.as_radians())
        self.angles = cfg.mount_angles
        self.mounts = mount_positions(cfg.body.radius, self.angles)
        self.x = self.y = self.yaw = self.t = 0.0
        self.q = np.zeros((6, 3))

    def reset(self, q0: np.ndarray) -> RobotState:
        self.x = self.y = self.yaw = self.t = 0.0
        self.q = np.array(q0, dtype=float)
        return self._state()

    def step(self, q_target: np.ndarray, dt: float, hint: object | None = None) -> RobotState:
        cmd = getattr(hint, "command", None)
        if cmd is not None:
            c, s = math.cos(self.yaw), math.sin(self.yaw)
            self.x += (cmd.vx * c - cmd.vy * s) * dt
            self.y += (cmd.vx * s + cmd.vy * c) * dt
            self.yaw += cmd.wz * dt
        self.q = np.array(q_target, dtype=float)
        self.t += dt
        return self._state()

    def feet_world(self) -> np.ndarray:
        R = rpy_matrix(self.pose.roll, self.pose.pitch, self.yaw)
        p = self.body_position()
        out = np.zeros((6, 3))
        for i in range(6):
            fb = BodyPose.leg_to_body(self.leg.fk(self.q[i]), self.mounts[i], self.angles[i])
            out[i] = p + R @ fb
        return out

    def body_position(self) -> np.ndarray:
        off = rot_z(self.yaw) @ np.array([self.pose.offset_x, self.pose.offset_y, 0.0])
        return np.array([self.x, self.y, self.pose.height]) + off

    def _state(self) -> RobotState:
        feet = self.feet_world()
        pos = self.body_position()
        return RobotState(
            t=self.t,
            q=self.q.copy(),
            body_pos=pos,
            body_quat=rpy_to_quat(self.pose.roll, self.pose.pitch, self.yaw),
            contacts=feet[:, 2] < 2e-3,
            feet=feet,
            com=pos.copy(),
        )
