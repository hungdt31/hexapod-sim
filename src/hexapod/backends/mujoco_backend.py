"""Backend vật lý MuJoCo: trọng lực, ma sát, va chạm, điều khiển vị trí khớp (PD)."""

from __future__ import annotations

import numpy as np

from ..config import RobotConfig
from ..mjcf import FOOT_RADIUS, build_mjcf
from .base import RobotState, SimBackend

try:
    import mujoco
except ImportError:  # pragma: no cover - phụ thuộc tùy chọn
    mujoco = None


def mujoco_available() -> bool:
    return mujoco is not None


class MujocoBackend(SimBackend):
    name = "mujoco"

    def __init__(self, cfg: RobotConfig) -> None:
        if mujoco is None:
            raise RuntimeError("Chưa cài MuJoCo. Chạy: pip install -e '.[physics]'")
        self.cfg = cfg
        self.xml = build_mjcf(cfg)
        self.model = mujoco.MjModel.from_xml_string(self.xml)
        self.data = mujoco.MjData(self.model)
        self.torso = self.model.body("torso").id
        self.floor = self.model.geom("floor").id
        self.foot_geoms = np.array([self.model.geom(f"foot_{i}").id for i in range(6)])
        self.joint_qadr = np.array([
            self.model.joint(f"j{i}_{j}").qposadr[0] for i in range(6) for j in ("coxa", "femur", "tibia")
        ])
        self.n_sub = max(1, round(cfg.sim.control_dt / self.model.opt.timestep))

    def reset(self, q0: np.ndarray) -> RobotState:
        mujoco.mj_resetData(self.model, self.data)
        self.data.qpos[2] = self.cfg.body.stand_height + FOOT_RADIUS + 0.002
        self.data.qpos[self.joint_qadr] = np.asarray(q0).reshape(-1)
        self.data.ctrl[:] = np.asarray(q0).reshape(-1)
        mujoco.mj_forward(self.model, self.data)
        for _ in range(300):  # để robot ổn định trên nền
            mujoco.mj_step(self.model, self.data)
        self.data.time = 0.0
        return self._state()

    def step(self, q_target: np.ndarray, dt: float, hint: object | None = None) -> RobotState:
        self.data.ctrl[:] = np.asarray(q_target).reshape(-1)
        n = max(1, round(dt / self.model.opt.timestep))
        for _ in range(n):
            mujoco.mj_step(self.model, self.data)
        return self._state()

    def _contacts(self) -> np.ndarray:
        c = np.zeros(6, dtype=bool)
        for k in range(self.data.ncon):
            con = self.data.contact[k]
            for g, other in ((con.geom1, con.geom2), (con.geom2, con.geom1)):
                if other == self.floor:
                    hit = np.nonzero(self.foot_geoms == g)[0]
                    if hit.size:
                        c[hit[0]] = True
        return c

    def _state(self) -> RobotState:
        d = self.data
        feet = d.geom_xpos[self.foot_geoms].copy()
        feet[:, 2] -= FOOT_RADIUS
        return RobotState(
            t=float(d.time),
            q=d.qpos[self.joint_qadr].reshape(6, 3).copy(),
            body_pos=d.qpos[0:3].copy(),
            body_quat=d.qpos[3:7].copy(),
            contacts=self._contacts(),
            feet=feet,
            com=d.subtree_com[self.torso].copy(),
        )
