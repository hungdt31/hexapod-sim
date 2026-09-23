"""Bộ sinh pha dáng đi. Thêm dáng đi mới = 1 class con khai báo beta, period, offsets."""

from __future__ import annotations

import math


class Gait:
    name: str = "base"
    beta: float = 0.5                      # hệ số duty: tỉ lệ thời gian chân chạm đất
    period: float = 1.0                    # chu kỳ bước (s)
    offsets: tuple[float, ...] = (0.0,) * 6
    min_stance: int = 3

    def leg_phase(self, leg: int, t: float) -> float:
        return (t / self.period + self.offsets[leg]) % 1.0

    def phase(self, leg: int, t: float) -> tuple[bool, float]:
        """(đang swing?, tiến độ 0..1 trong pha hiện tại)."""
        return split_phase(self.leg_phase(leg, t), self.beta)


def split_phase(ph: float, beta: float) -> tuple[bool, float]:
    sw = 1.0 - beta
    if ph < sw:
        return True, ph / sw
    return False, (ph - sw) / beta


def circ_delta(a: float, b: float) -> float:
    """Khoảng cách pha ngắn nhất từ a tới b trên vòng tròn [0, 1)."""
    return (b - a + 0.5) % 1.0 - 0.5


class GaitScheduler:
    """Giữ pha chủ và offset từng chân; nội suy mượt khi đổi dáng đi (FR-08)."""

    def __init__(self, gait: Gait, blend_cycles: float = 0.67) -> None:
        self.gait = gait
        self.master = 0.0
        self.offsets = list(gait.offsets)
        self.beta = gait.beta
        self.period = gait.period
        self.blend_cycles = blend_cycles

    def set_gait(self, gait: Gait) -> None:
        self.gait = gait

    def step(self, dt: float) -> None:
        g = self.gait
        a = min(1.0, dt * 2.0)
        self.period += (g.period - self.period) * a
        self.beta += (g.beta - self.beta) * a
        rate = min(1.0, dt / (self.period * self.blend_cycles))
        for i in range(6):
            self.offsets[i] = (self.offsets[i] + circ_delta(self.offsets[i], g.offsets[i]) * rate) % 1.0
        self.master = math.fmod(self.master + dt / self.period, 1.0)

    def phase(self, leg: int) -> tuple[bool, float]:
        return split_phase((self.master + self.offsets[leg]) % 1.0, self.beta)
