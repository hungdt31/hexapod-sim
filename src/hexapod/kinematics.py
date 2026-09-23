"""Động học thuận/nghịch giải tích cho chân 3-DOF (coxa–femur–tibia).

Quy ước trong hệ gốc chân Lᵢ (X hướng ra ngoài, Z hướng lên):
- θ1 (coxa): quay quanh Z.
- θ2 (femur): dương = nâng đùi lên.
- θ3 (tibia): 0 = duỗi thẳng, âm = gập xuống.
Cấu hình IK: "gối hướng lên" (knee-up).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


class UnreachableError(ValueError):
    """Điểm đầu chân nằm ngoài vùng làm việc."""


@dataclass(frozen=True)
class LegKinematics:
    l1: float
    l2: float
    l3: float
    limits: tuple[tuple[float, float], ...] = (
        (-math.pi / 4, math.pi / 4),
        (-math.pi / 2, math.pi / 2),
        (-5 * math.pi / 6, 0.0),
    )

    def fk(self, q: np.ndarray) -> np.ndarray:
        """(3,) góc khớp -> (3,) vị trí đầu chân trong hệ Lᵢ."""
        t1, t2, t3 = float(q[0]), float(q[1]), float(q[2])
        r = self.l1 + self.l2 * math.cos(t2) + self.l3 * math.cos(t2 + t3)
        z = self.l2 * math.sin(t2) + self.l3 * math.sin(t2 + t3)
        return np.array([r * math.cos(t1), r * math.sin(t1), z])

    def knee(self, q: np.ndarray) -> np.ndarray:
        t1, t2 = float(q[0]), float(q[1])
        r = self.l1 + self.l2 * math.cos(t2)
        return np.array([r * math.cos(t1), r * math.sin(t1), self.l2 * math.sin(t2)])

    def ik(self, p: np.ndarray) -> np.ndarray:
        """(3,) vị trí -> (3,) góc khớp. Ném UnreachableError nếu ngoài tầm với hoặc vượt giới hạn."""
        q, ok = self.ik_clamped(p)
        if not ok:
            raise UnreachableError(f"điểm {np.round(p, 4).tolist()} ngoài vùng làm việc")
        return q

    def ik_clamped(self, p: np.ndarray) -> tuple[np.ndarray, bool]:
        """IK luôn trả nghiệm gần nhất; cờ thứ hai = False nếu phải kẹp tầm với/giới hạn khớp."""
        x, y, z = float(p[0]), float(p[1]), float(p[2])
        ok = True
        t1 = math.atan2(y, x)
        r = math.hypot(x, y) - self.l1
        d = math.hypot(r, z)
        d_min, d_max = abs(self.l2 - self.l3) + 1e-9, self.l2 + self.l3 - 1e-9
        if d > d_max or d < d_min:
            ok = False
            d = min(max(d, d_min), d_max)
        a1 = math.acos(_clip((self.l2**2 + d**2 - self.l3**2) / (2 * self.l2 * d)))
        a2 = math.acos(_clip((self.l2**2 + self.l3**2 - d**2) / (2 * self.l2 * self.l3)))
        q = np.array([t1, math.atan2(z, r) + a1, a2 - math.pi])
        if not self.within_limits(q):
            ok = False
            q = self.clamp(q)
        return q, ok

    def within_limits(self, q: np.ndarray, tol: float = 1e-9) -> bool:
        return all(lo - tol <= v <= hi + tol for v, (lo, hi) in zip(q, self.limits, strict=True))

    def clamp(self, q: np.ndarray) -> np.ndarray:
        return np.array([min(max(v, lo), hi) for v, (lo, hi) in zip(q, self.limits, strict=True)])


def _clip(v: float) -> float:
    return max(-1.0, min(1.0, v))
