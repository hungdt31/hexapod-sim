"""Simulation: ghép controller + backend + tính ổn định thành một vòng điều khiển."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .backends import RobotState, SimBackend, make_backend
from .config import RobotConfig
from .controller import ControlOutput, HexapodController
from .stability import convex_hull, stability_margin


@dataclass
class Frame:
    state: RobotState
    control: ControlOutput
    support: np.ndarray
    margin: float

    def to_message(self, gait: str, backend: str, running: bool) -> dict:
        s, c = self.state, self.control
        roll, pitch, yaw = s.rpy
        return {
            "type": "state",
            "t": round(s.t, 4),
            "running": running,
            "gait": gait,
            "backend": backend,
            "body": {"pos": _r(s.body_pos), "rpy": [round(roll, 5), round(pitch, 5), round(yaw, 5)],
                     "quat": _r(s.body_quat)},
            "q": _r(s.q),
            "q_cmd": _r(c.q),
            "contacts": s.contacts.astype(bool).tolist(),
            "swing": c.swing.astype(bool).tolist(),
            "phase": _r(c.progress, 3),
            "feet": _r(s.feet),
            "com": _r(s.com),
            "support": _r(self.support),
            "stability_margin": round(self.margin, 5),
            "stride": round(c.stride, 4),
            "ik_warn": int(c.ik_warn.sum()),
            "command": {"vx": c.command.vx, "vy": c.command.vy, "wz": c.command.wz},
        }


def _r(a: np.ndarray, n: int = 5) -> list:
    return np.round(np.asarray(a, dtype=float), n).tolist()


class Simulation:
    def __init__(self, cfg: RobotConfig | None = None, backend: str = "kinematic") -> None:
        self.cfg = cfg or RobotConfig.load()
        self.controller = HexapodController(self.cfg)
        self.backend_name = backend
        self.backend: SimBackend = make_backend(backend, self.cfg, self.controller.pose)
        self.state = self.backend.reset(self.controller.standing_q())
        self.last: Frame | None = None

    def switch_backend(self, name: str) -> None:
        if name == self.backend_name:
            return
        self.backend.close()
        self.backend = make_backend(name, self.cfg, self.controller.pose)
        self.backend_name = name
        self.reset()

    def reset(self) -> None:
        gait = self.controller.gait_name
        pose = self.controller.pose
        cmd = self.controller.command
        self.controller = HexapodController(self.cfg)
        self.controller.set_gait(gait)
        self.controller.set_body_pose(pose.height, pose.roll, pose.pitch)
        self.controller.set_command(cmd.vx, cmd.vy, cmd.wz)
        if hasattr(self.backend, "pose"):
            self.backend.pose = self.controller.pose  # type: ignore[attr-defined]
        self.state = self.backend.reset(self.controller.standing_q())
        self.last = None

    def step(self, dt: float | None = None) -> Frame:
        dt = dt or self.cfg.sim.control_dt
        out = self.controller.step(dt)
        self.state = self.backend.step(out.q, dt, out)
        stance = self.state.feet[self.state.contacts]
        poly = convex_hull(stance) if len(stance) else np.zeros((0, 2))
        margin = stability_margin(poly, self.state.com[:2])
        self.last = Frame(self.state, out, poly, margin)
        return self.last
