"""Ma trận quay và phép biến đổi hệ tọa độ (Z hướng lên, X hướng về trước)."""

from __future__ import annotations

import numpy as np


def rot_x(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def rpy_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
    """R = Rz(yaw) · Ry(pitch) · Rx(roll)."""
    return rot_z(yaw) @ rot_y(pitch) @ rot_x(roll)


def quat_to_matrix(q: np.ndarray) -> np.ndarray:
    w, x, y, z = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def matrix_to_rpy(m: np.ndarray) -> tuple[float, float, float]:
    pitch = float(np.arcsin(np.clip(-m[2, 0], -1.0, 1.0)))
    roll = float(np.arctan2(m[2, 1], m[2, 2]))
    yaw = float(np.arctan2(m[1, 0], m[0, 0]))
    return roll, pitch, yaw


def rpy_to_quat(roll: float, pitch: float, yaw: float) -> np.ndarray:
    cr, sr = np.cos(roll / 2), np.sin(roll / 2)
    cp, sp = np.cos(pitch / 2), np.sin(pitch / 2)
    cy, sy = np.cos(yaw / 2), np.sin(yaw / 2)
    return np.array([
        cr * cp * cy + sr * sp * sy,
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
    ])


def mount_positions(radius: float, angles: list[float]) -> np.ndarray:
    """Vị trí khớp coxa của 6 chân trong hệ thân B, shape (6, 3)."""
    a = np.asarray(angles)
    return np.stack([radius * np.cos(a), radius * np.sin(a), np.zeros_like(a)], axis=1)
