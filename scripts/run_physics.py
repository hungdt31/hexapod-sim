"""Chạy MuJoCo: có viewer (điều khiển bằng phím) hoặc headless theo kịch bản.

    python scripts/run_physics.py --viewer                  # mở cửa sổ MuJoCo, điều khiển bằng phím
    python scripts/run_physics.py configs/scenarios/walk_square.yaml   # headless, ghi log

Phím trong viewer: I/K tiến-lùi, J/L sang ngang, U/O xoay, 1/2/3 = tripod/ripple/wave, 0 = dừng.
(MuJoCo viewer đã dùng WASD cho camera nên phím điều khiển robot khác với web UI.)
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hexapod.config import RobotConfig  # noqa: E402
from hexapod.sim import Simulation  # noqa: E402


def viewer(cfg_path: str | None) -> None:
    import mujoco.viewer

    cfg = RobotConfig.load(cfg_path)
    sim = Simulation(cfg, "mujoco")
    ctl = sim.controller
    ctl.set_command(0.05, 0, 0)
    be = sim.backend
    step = {"I": (0.01, 0, 0), "K": (-0.01, 0, 0), "J": (0, 0.01, 0), "L": (0, -0.01, 0),
            "U": (0, 0, 0.1), "O": (0, 0, -0.1)}
    gaits = {"1": "tripod", "2": "ripple", "3": "wave"}

    def on_key(code: int) -> None:
        k = chr(code) if 32 <= code < 127 else ""
        c = ctl.command
        if k in step:
            d = step[k]
            ctl.set_command(max(-0.1, min(0.1, c.vx + d[0])), max(-0.08, min(0.08, c.vy + d[1])),
                            max(-0.8, min(0.8, c.wz + d[2])))
        elif k in gaits:
            ctl.set_gait(gaits[k])
        elif k == "0":
            ctl.set_command(0, 0, 0)
        c = ctl.command
        print(f"\rgait={ctl.gait_name:6s} vx={c.vx:+.2f} vy={c.vy:+.2f} wz={c.wz:+.2f}   ", end="", flush=True)

    dt = cfg.sim.control_dt
    with mujoco.viewer.launch_passive(be.model, be.data, key_callback=on_key) as v:  # type: ignore[attr-defined]
        while v.is_running():
            t0 = time.perf_counter()
            sim.step(dt)
            v.sync()
            time.sleep(max(0.0, dt - (time.perf_counter() - t0)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario", nargs="?", default=None)
    ap.add_argument("--config", default=None)
    ap.add_argument("--viewer", action="store_true")
    ap.add_argument("--export-mjcf", default=None, help="ghi file MJCF, ví dụ models/hexapod.xml")
    a = ap.parse_args()
    if a.export_mjcf:
        from hexapod.mjcf import build_mjcf
        Path(a.export_mjcf).parent.mkdir(parents=True, exist_ok=True)
        Path(a.export_mjcf).write_text(build_mjcf(RobotConfig.load(a.config)), encoding="utf-8")
        print("đã ghi", a.export_mjcf)
    elif a.viewer or not a.scenario:
        viewer(a.config)
    else:
        from run_kinematic import run
        run(a.scenario, "mujoco", a.config, plot=False)
