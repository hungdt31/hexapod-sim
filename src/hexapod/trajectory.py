"""Quỹ đạo đầu chân trong hệ heading (gốc = hình chiếu tâm thân, X theo hướng yaw)."""

from __future__ import annotations

import math

import numpy as np


def foot_velocity(home: np.ndarray, vx: float, vy: float, wz: float) -> np.ndarray:
    """v_foot = −(v + ω × p_home), chỉ thành phần XY."""
    return -np.array([vx - wz * home[1], vy + wz * home[0]])


def foot_target(
    home: np.ndarray,
    vx: float,
    vy: float,
    wz: float,
    beta: float,
    period: float,
    swing: bool,
    s: float,
    swing_height: float,
    max_stride: float,
) -> tuple[np.ndarray, float]:
    """Trả (điểm đầu chân (3,), độ dài bước thực tế)."""
    vf = foot_velocity(home, vx, vy, wz)
    stance_time = beta * period
    stride = float(np.hypot(*vf)) * stance_time
    if stride > max_stride:
        vf *= max_stride / stride
        stride = max_stride
    k = (0.5 - s) if swing else (s - 0.5)
    xy = home[:2] + vf * stance_time * k
    z = swing_height * math.sin(math.pi * s) if swing else 0.0
    return np.array([xy[0], xy[1], z]), stride
