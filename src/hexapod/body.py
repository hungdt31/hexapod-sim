"""Tư thế thân: chuyển điểm đầu chân từ hệ heading (mặt đất, theo hướng yaw) sang hệ gốc chân."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .geometry import rot_x, rot_y, rot_z


@dataclass
class BodyPose:
    height: float = 0.10
    roll: float = 0.0
    pitch: float = 0.0
    offset_x: float = 0.0
    offset_y: float = 0.0

    def rotation(self) -> np.ndarray:
        return rot_y(self.pitch) @ rot_x(self.roll)

    def heading_to_body(self, p: np.ndarray) -> np.ndarray:
        """p (…,3) trong hệ heading -> hệ thân B."""
        t = np.array([self.offset_x, self.offset_y, self.height])
        return (np.asarray(p) - t) @ self.rotation()  # = Rᵀ (p - t)

    @staticmethod
    def body_to_leg(p_body: np.ndarray, mount: np.ndarray, mount_angle: float) -> np.ndarray:
        return rot_z(-mount_angle) @ (np.asarray(p_body) - mount)

    @staticmethod
    def leg_to_body(p_leg: np.ndarray, mount: np.ndarray, mount_angle: float) -> np.ndarray:
        return rot_z(mount_angle) @ np.asarray(p_leg) + mount
