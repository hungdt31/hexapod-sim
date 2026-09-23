"""Message WebSocket giữa Web UI và server."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter


class CommandMsg(BaseModel):
    type: Literal["command"]
    vx: float = Field(0.0, ge=-0.2, le=0.2)
    vy: float = Field(0.0, ge=-0.2, le=0.2)
    wz: float = Field(0.0, ge=-2.0, le=2.0)


class ControlMsg(BaseModel):
    type: Literal["control"]
    action: Literal["start", "pause", "step", "reset"]


class BodyPoseMsg(BaseModel):
    rpy: tuple[float, float, float] | None = None   # rad; yaw bị bỏ qua
    height: float | None = Field(None, ge=0.05, le=0.16)


class ConfigMsg(BaseModel):
    type: Literal["config"]
    gait: Literal["tripod", "ripple", "wave"] | None = None
    backend: Literal["kinematic", "mujoco"] | None = None
    body_pose: BodyPoseMsg | None = None
    swing_height: float | None = Field(None, ge=0.005, le=0.08)


class ScenarioMsg(BaseModel):
    type: Literal["scenario"]
    yaml: str | None = None   # None = dừng kịch bản


ClientMsg = Annotated[CommandMsg | ControlMsg | ConfigMsg | ScenarioMsg, Field(discriminator="type")]
client_adapter: TypeAdapter[ClientMsg] = TypeAdapter(ClientMsg)
