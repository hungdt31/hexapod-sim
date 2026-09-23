from .base import Gait, GaitScheduler, split_phase
from .ripple import RippleGait
from .tripod import TripodGait
from .wave import WaveGait

GAITS: dict[str, type[Gait]] = {g.name: g for g in (TripodGait, RippleGait, WaveGait)}


def make_gait(name: str) -> Gait:
    try:
        return GAITS[name]()
    except KeyError as e:
        raise ValueError(f"dáng đi không hợp lệ: {name!r}; chọn một trong {sorted(GAITS)}") from e


__all__ = ["GAITS", "Gait", "GaitScheduler", "RippleGait", "TripodGait", "WaveGait", "make_gait", "split_phase"]
