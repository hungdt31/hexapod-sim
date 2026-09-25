"""Sinh mô hình MJCF (MuJoCo) từ RobotConfig."""

from __future__ import annotations

import math

from .config import RobotConfig

FOOT_RADIUS = 0.014
LINK_RADIUS = 0.011


def build_mjcf(cfg: RobotConfig) -> str:
    b, lg, act = cfg.body, cfg.leg, cfg.actuator
    l1, l2, l3 = lg.lengths
    lim = lg.joint_limits_deg
    m_link = lg.mass / 3.0
    legs, acts = [], []
    for i, a_deg in enumerate(lg.mount_angles_deg):
        a = math.radians(a_deg)
        x, y = b.radius * math.cos(a), b.radius * math.sin(a)
        legs.append(f"""
      <body name="coxa_{i}" pos="{x:.5f} {y:.5f} 0" euler="0 0 {a_deg}">
        <joint name="j{i}_coxa" axis="0 0 1" range="{lim.coxa[0]} {lim.coxa[1]}"/>
        <geom class="link" fromto="0 0 0 {l1} 0 0" mass="{m_link:.4f}"/>
        <body name="femur_{i}" pos="{l1} 0 0">
          <joint name="j{i}_femur" axis="0 -1 0" range="{lim.femur[0]} {lim.femur[1]}"/>
          <geom class="link" fromto="0 0 0 {l2} 0 0" mass="{m_link:.4f}"/>
          <body name="tibia_{i}" pos="{l2} 0 0">
            <joint name="j{i}_tibia" axis="0 -1 0" range="{lim.tibia[0]} {lim.tibia[1]}"/>
            <geom class="link" fromto="0 0 0 {l3} 0 0" mass="{m_link:.4f}"/>
            <geom name="foot_{i}" class="foot" pos="{l3} 0 0"/>
          </body>
        </body>
      </body>""")
        for j in ("coxa", "femur", "tibia"):
            lo, hi = getattr(lim, j)
            acts.append(
                f'    <position name="a{i}_{j}" joint="j{i}_{j}" kp="{act.kp}" '
                f'ctrlrange="{math.radians(lo):.5f} {math.radians(hi):.5f}" '
                f'forcerange="{-act.torque_max} {act.torque_max}"/>'
            )
    z0 = b.stand_height + FOOT_RADIUS + 0.005
    t = cfg.terrain
    hfield_asset = (
        f'<hfield name="terrain" nrow="{t.grid_n}" ncol="{t.grid_n}" size="10 10 {t.amplitude} 0.1"/>'
        if t.enabled else ""
    )
    floor_geom = (
        '<geom name="floor" type="hfield" hfield="terrain" material="grid" contype="0" conaffinity="1"/>'
        if t.enabled else
        '<geom name="floor" type="plane" size="20 20 0.1" material="grid" contype="0" conaffinity="1"/>'
    )
    return f"""<mujoco model="hexapod">
  <compiler angle="degree" autolimits="true"/>
  <option timestep="{cfg.sim.physics_dt}" integrator="implicitfast"/>
  <visual><headlight diffuse="0.7 0.7 0.7" ambient="0.35 0.35 0.35"/></visual>
  <asset>
    <texture name="grid" type="2d" builtin="checker" rgb1="1 0.97 0.9" rgb2="0.93 0.9 0.82" width="512" height="512"/>
    <material name="grid" texture="grid" texrepeat="40 40"/>
    <material name="body" rgba="1 1 1 1"/>
    <material name="leg" rgba="0.23 0.81 0.67 1"/>
    <material name="foot" rgba="1 0.82 0.25 1"/>
    {hfield_asset}
  </asset>
  <default>
    <joint damping="{act.kd}" armature="0.002"/>
    <geom contype="0" conaffinity="0"/>
    <default class="link"><geom type="capsule" size="{LINK_RADIUS}" material="leg"/></default>
    <default class="foot">
      <geom type="sphere" size="{FOOT_RADIUS}" material="foot" mass="0.005"
            contype="1" conaffinity="0" condim="3" friction="1.2 0.02 0.001"/>
    </default>
  </default>
  <worldbody>
    <light pos="0 0 3" dir="0 0 -1" diffuse="0.6 0.6 0.6"/>
    {floor_geom}
    <body name="torso" pos="0 0 {z0:.4f}">
      <freejoint name="root"/>
      <geom name="torso" type="cylinder" size="{b.radius * 1.1:.4f} 0.017" mass="{b.mass}" material="body"
            contype="1" conaffinity="0"/>
      <site name="imu" pos="0 0 0"/>{"".join(legs)}
    </body>
  </worldbody>
  <actuator>
{chr(10).join(acts)}
  </actuator>
</mujoco>
"""
