"""Cấu hình robot, đọc từ YAML và kiểm tra bằng Pydantic."""

from __future__ import annotations

import math
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "configs" / "robot_default.yaml"


class BodyCfg(BaseModel):
    radius: float = Field(0.10, gt=0)
    mass: float = Field(1.2, gt=0)
    stand_height: float = Field(0.10, gt=0)


class JointLimits(BaseModel):
    coxa: tuple[float, float] = (-45.0, 45.0)
    femur: tuple[float, float] = (-90.0, 90.0)
    tibia: tuple[float, float] = (-150.0, 0.0)

    def as_radians(self) -> tuple[tuple[float, float], ...]:
        return tuple((math.radians(lo), math.radians(hi)) for lo, hi in (self.coxa, self.femur, self.tibia))


class LegCfg(BaseModel):
    lengths: tuple[float, float, float] = (0.05, 0.08, 0.12)
    mass: float = Field(0.15, gt=0)
    home_reach: float = Field(0.10, gt=0)
    joint_limits_deg: JointLimits = JointLimits()
    mount_angles_deg: tuple[float, float, float, float, float, float] = (-30, -90, -150, 150, 90, 30)

    @field_validator("lengths")
    @classmethod
    def _positive(cls, v: tuple[float, float, float]) -> tuple[float, float, float]:
        if any(x <= 0 for x in v):
            raise ValueError("chiều dài khâu phải > 0")
        return v


class ActuatorCfg(BaseModel):
    kp: float = Field(20.0, gt=0)
    kd: float = Field(0.5, ge=0)
    torque_max: float = Field(1.5, gt=0)


class GaitCfg(BaseModel):
    default: str = "tripod"
    swing_height: float = Field(0.04, gt=0)
    max_stride: float = Field(0.08, gt=0)


class SimCfg(BaseModel):
    physics_dt: float = Field(0.001, gt=0)
    control_dt: float = Field(0.01, gt=0)
    broadcast_hz: float = Field(30.0, gt=0)
    seed: int = 42


class RobotConfig(BaseModel):
    body: BodyCfg = BodyCfg()
    leg: LegCfg = LegCfg()
    actuator: ActuatorCfg = ActuatorCfg()
    gait: GaitCfg = GaitCfg()
    sim: SimCfg = SimCfg()

    @classmethod
    def load(cls, path: str | Path | None = None) -> RobotConfig:
        p = Path(path) if path else DEFAULT_CONFIG
        if not p.exists():
            return cls()
        with p.open(encoding="utf-8") as f:
            return cls.model_validate(yaml.safe_load(f) or {})

    def dump_yaml(self) -> str:
        return yaml.safe_dump(self.model_dump(mode="json"), sort_keys=False, allow_unicode=True)

    @property
    def mount_angles(self) -> list[float]:
        return [math.radians(a) for a in self.leg.mount_angles_deg]
