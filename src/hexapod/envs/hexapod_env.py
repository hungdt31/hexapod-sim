"""Gymnasium wrapper (FR-18): nền tảng cho huấn luyện RL.

Hành động = phần bù góc khớp (18,) cộng vào đầu ra của controller dáng đi (residual policy).
Quan sát = góc khớp, roll/pitch, vận tốc thân, contact. Phần thưởng = vận tốc tiến − phạt nghiêng/năng lượng.
"""

from __future__ import annotations

import numpy as np

try:
    import gymnasium as gym
    from gymnasium import spaces
except ImportError as e:  # pragma: no cover
    raise ImportError("Cần gymnasium: pip install -e '.[rl]'") from e

from ..config import RobotConfig
from ..sim import Simulation


class HexapodEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, backend: str = "mujoco", episode_seconds: float = 10.0,
                 target_vx: float = 0.05, residual_scale: float = 0.3) -> None:
        self.cfg = RobotConfig.load()
        self.backend = backend
        self.max_steps = int(episode_seconds / self.cfg.sim.control_dt)
        self.target_vx = target_vx
        self.scale = residual_scale
        self.action_space = spaces.Box(-1.0, 1.0, shape=(18,), dtype=np.float32)
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(18 + 2 + 3 + 6,), dtype=np.float32)
        self.sim: Simulation | None = None

    def _obs(self) -> np.ndarray:
        s = self.sim.state  # type: ignore[union-attr]
        roll, pitch, _ = s.rpy
        vel = (s.body_pos - self._prev) / self.cfg.sim.control_dt
        return np.concatenate([s.q.reshape(-1), [roll, pitch], vel, s.contacts.astype(float)]).astype(np.float32)

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        self.sim = Simulation(self.cfg, self.backend)
        self.sim.controller.set_command(self.target_vx, 0, 0)
        self._prev = self.sim.state.body_pos.copy()
        self.steps = 0
        return self._obs(), {}

    def step(self, action):
        sim = self.sim
        assert sim is not None
        dt = self.cfg.sim.control_dt
        out = sim.controller.step(dt)
        target = out.q + self.scale * np.asarray(action, dtype=float).reshape(6, 3)
        self._prev = sim.state.body_pos.copy()
        sim.state = sim.backend.step(target, dt, out)
        s = sim.state
        roll, pitch, _ = s.rpy
        vx = (s.body_pos[0] - self._prev[0]) / dt
        reward = vx - 0.5 * (roll**2 + pitch**2) - 0.001 * float(np.square(action).sum())
        self.steps += 1
        terminated = bool(s.body_pos[2] < 0.04 or abs(roll) > 0.8 or abs(pitch) > 0.8)
        truncated = self.steps >= self.max_steps
        return self._obs(), float(reward), terminated, truncated, {}
