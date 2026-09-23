from .base import Gait


class TripodGait(Gait):
    """3 chân nhấc cùng lúc: nhóm {RF, RR, LM} và {RM, LR, LF}."""

    name = "tripod"
    beta = 0.5
    period = 1.0
    offsets = (0.0, 0.5, 0.0, 0.5, 0.0, 0.5)
    min_stance = 3
