"""Giao diện chung cho backend mô phỏng (kinematic hoặc vật lý)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np

from ..body import BodyPose
from ..geometry import matrix_to_rpy, quat_to_matrix


@dataclass
class RobotState:
    t: float
    q: np.ndarray                 # (6, 3) góc khớp thực
    body_pos: np.ndarray          # (3,) hệ W
    body_quat: np.ndarray         # (4,) w, x, y, z
    contacts: np.ndarray          # (6,) bool
    feet: np.ndarray = field(default_factory=lambda: np.zeros((6, 3)))   # (6, 3) đầu chân, hệ W
    com: np.ndarray = field(default_factory=lambda: np.zeros(3))         # (3,) trọng tâm, hệ W

    @property
    def rpy(self) -> tuple[float, float, float]:
        return matrix_to_rpy(quat_to_matrix(self.body_quat))


class SimBackend(ABC):
    name: str = "base"
    pose: BodyPose | None = None  # tư thế thân do controller lệnh; chỉ backend không-vật-lý cần dùng

    @abstractmethod
    def reset(self, q0: np.ndarray) -> RobotState: ...

    @abstractmethod
    def step(self, q_target: np.ndarray, dt: float, hint: object | None = None) -> RobotState:
        """Tiến một vòng điều khiển dt với góc khớp mục tiêu q_target (6, 3).

        `hint` là ControlOutput của controller; backend kinematic dùng nó để tích phân tư thế thân,
        backend vật lý bỏ qua."""

    def close(self) -> None:  # noqa: B027 - tùy chọn
        pass
