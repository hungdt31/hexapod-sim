"""Vòng mô phỏng chạy nền (asyncio), phát trạng thái tới mọi client ở broadcast_hz."""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time

from fastapi import WebSocket

from .. import LEG_NAMES
from ..backends import available_backends
from ..config import RobotConfig
from ..gait import GAITS
from ..io import CsvLogger, Scenario, ScenarioRunner
from ..mjcf import FOOT_RADIUS
from ..sim import Simulation
from .schemas import CommandMsg, ConfigMsg, ControlMsg, ScenarioMsg

log = logging.getLogger("hexapod.server")


class SimRunner:
    def __init__(self, cfg: RobotConfig, backend: str = "kinematic", log_dir: str | None = None) -> None:
        self.cfg = cfg
        self.sim = Simulation(cfg, backend)
        self.running = True
        self.clients: set[WebSocket] = set()
        self.scenario: ScenarioRunner | None = None
        self.logger = CsvLogger(cfg, log_dir) if log_dir else None
        self._task: asyncio.Task | None = None
        self.sim.step()

    # --- vòng lặp -------------------------------------------------------------
    async def start(self) -> None:
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        if self.logger:
            self.logger.close()

    def _tick(self) -> None:
        dt = self.cfg.sim.control_dt
        if self.scenario and not self.scenario.apply(self.sim.controller, dt):
            self.scenario = None
        frame = self.sim.step(dt)
        if self.logger:
            self.logger.log(frame)

    async def _loop(self) -> None:
        dt = self.cfg.sim.control_dt
        every = max(1, round(1.0 / (self.cfg.sim.broadcast_hz * dt)))
        k, next_t = 0, time.perf_counter()
        while True:
            if self.running:
                self._tick()
            k += 1
            if k % every == 0:
                await self.broadcast()
            next_t += dt
            await asyncio.sleep(max(0.0, next_t - time.perf_counter()))
            if time.perf_counter() - next_t > 0.5:   # bị chậm quá nhiều -> bỏ qua, không đuổi theo
                next_t = time.perf_counter()

    # --- giao tiếp -------------------------------------------------------------
    def hello(self) -> dict:
        c = self.cfg
        return {
            "type": "hello",
            "robot": {
                "body_radius": c.body.radius,
                "lengths": list(c.leg.lengths),
                "mount_angles_deg": list(c.leg.mount_angles_deg),
                "stand_height": c.body.stand_height,
                "foot_radius": FOOT_RADIUS,
                "leg_names": list(LEG_NAMES),
            },
            "gaits": {n: {"beta": g.beta, "period": g.period} for n, g in GAITS.items()},
            "backends": available_backends(),
            "control_dt": c.sim.control_dt,
            "broadcast_hz": c.sim.broadcast_hz,
        }

    def snapshot(self) -> dict:
        f = self.sim.last or self.sim.step(1e-6)
        msg = f.to_message(self.sim.controller.gait_name, self.sim.backend_name, self.running)
        p = self.sim.controller.pose
        msg["body_pose"] = {"height": p.height, "roll": p.roll, "pitch": p.pitch}
        msg["scenario_active"] = self.scenario is not None
        return msg

    async def broadcast(self) -> None:
        if not self.clients:
            return
        text = json.dumps(self.snapshot())
        dead = []
        for ws in list(self.clients):
            try:
                await ws.send_text(text)
            except Exception:  # noqa: BLE001
                dead.append(ws)
        for ws in dead:
            self.clients.discard(ws)

    def handle(self, msg: CommandMsg | ControlMsg | ConfigMsg | ScenarioMsg) -> str | None:
        """Áp dụng message; trả chuỗi lỗi nếu có."""
        ctl = self.sim.controller
        if isinstance(msg, CommandMsg):
            self.scenario = None
            ctl.set_command(msg.vx, msg.vy, msg.wz)
        elif isinstance(msg, ControlMsg):
            if msg.action == "start":
                self.running = True
            elif msg.action == "pause":
                self.running = False
            elif msg.action == "step":
                self.running = False
                self._tick()
            elif msg.action == "reset":
                self.scenario = None
                self.sim.reset()
                self.sim.step()
        elif isinstance(msg, ConfigMsg):
            if msg.gait:
                ctl.set_gait(msg.gait)
            if msg.body_pose:
                roll, pitch = (msg.body_pose.rpy[0], msg.body_pose.rpy[1]) if msg.body_pose.rpy else (None, None)
                ctl.set_body_pose(msg.body_pose.height, roll, pitch)
            if msg.swing_height is not None:
                ctl.swing_height = msg.swing_height
            if msg.backend:
                if msg.backend not in available_backends():
                    return f"Backend {msg.backend} chưa được cài. Chạy: pip install -e '.[physics]'"
                self.sim.switch_backend(msg.backend)
                self.sim.step()
        elif isinstance(msg, ScenarioMsg):
            if msg.yaml is None:
                self.scenario = None
                ctl.set_command(0, 0, 0)
            else:
                sc = Scenario.from_text(msg.yaml)
                ctl.set_gait(sc.gait)
                self.scenario = ScenarioRunner(sc)
                self.running = True
        return None
