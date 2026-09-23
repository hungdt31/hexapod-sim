from .base import Gait


class RippleGait(Gait):
    """2 chân swing cùng lúc, lệch pha; luôn ≥ 4 chân chạm đất."""

    name = "ripple"
    beta = 2 / 3
    period = 1.2
    offsets = (0.0, 2 / 3, 1 / 3, 5 / 6, 1 / 6, 0.5)
    min_stance = 4
