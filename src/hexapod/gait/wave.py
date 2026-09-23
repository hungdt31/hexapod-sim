from .base import Gait


class WaveGait(Gait):
    """Lần lượt từng chân; luôn ≥ 5 chân chạm đất, ổn định nhất, chậm nhất."""

    name = "wave"
    beta = 5 / 6
    period = 1.8
    offsets = (0.0, 1 / 6, 2 / 6, 3 / 6, 4 / 6, 5 / 6)
    min_stance = 5
