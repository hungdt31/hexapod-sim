from ..config import RobotConfig
from .base import RobotState, SimBackend
from .kinematic import KinematicBackend
from .mujoco_backend import MujocoBackend, mujoco_available


def available_backends() -> list[str]:
    return ["kinematic"] + (["mujoco"] if mujoco_available() else [])


def make_backend(name: str, cfg: RobotConfig, pose=None) -> SimBackend:
    if name == "kinematic":
        return KinematicBackend(cfg, pose)
    if name == "mujoco":
        return MujocoBackend(cfg)
    raise ValueError(f"backend không hợp lệ: {name!r}")


__all__ = ["KinematicBackend", "MujocoBackend", "RobotState", "SimBackend", "available_backends",
           "make_backend", "mujoco_available"]
