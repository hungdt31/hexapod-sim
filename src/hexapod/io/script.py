"""Kịch bản lệnh YAML (FR-11): chuỗi lệnh vận tốc, mỗi lệnh có thời lượng."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class ScriptCommand(BaseModel):
    vx: float = 0.0
    vy: float = 0.0
    wz: float = 0.0
    duration: float = Field(gt=0)
    gait: str | None = None


class Scenario(BaseModel):
    gait: str = "tripod"
    commands: list[ScriptCommand]

    @classmethod
    def load(cls, path: str | Path) -> Scenario:
        with Path(path).open(encoding="utf-8") as f:
            return cls.model_validate(yaml.safe_load(f))

    @classmethod
    def from_text(cls, text: str) -> Scenario:
        return cls.model_validate(yaml.safe_load(text))

    @property
    def duration(self) -> float:
        return sum(c.duration for c in self.commands)


class ScenarioRunner:
    def __init__(self, scenario: Scenario) -> None:
        self.scenario = scenario
        self.t = 0.0

    def command_at(self, t: float) -> ScriptCommand | None:
        acc = 0.0
        for c in self.scenario.commands:
            acc += c.duration
            if t < acc:
                return c
        return None

    def apply(self, controller, dt: float) -> bool:
        """Áp lệnh tại thời điểm hiện tại vào controller; trả False khi hết kịch bản."""
        c = self.command_at(self.t)
        self.t += dt
        if c is None:
            controller.set_command(0, 0, 0)
            return False
        if c.gait and c.gait != controller.gait_name:
            controller.set_gait(c.gait)
        controller.set_command(c.vx, c.vy, c.wz)
        return True
