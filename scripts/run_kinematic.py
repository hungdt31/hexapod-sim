"""Chạy kịch bản bằng backend kinematic (headless), ghi log CSV, tùy chọn vẽ đồ thị.

    python scripts/run_kinematic.py configs/scenarios/walk_square.yaml --plot
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hexapod.config import RobotConfig  # noqa: E402
from hexapod.io import CsvLogger, Scenario, ScenarioRunner  # noqa: E402
from hexapod.sim import Simulation  # noqa: E402


def run(scenario_path: str, backend: str, cfg_path: str | None, plot: bool) -> Path:
    cfg = RobotConfig.load(cfg_path)
    sc = Scenario.load(scenario_path)
    sim = Simulation(cfg, backend)
    sim.controller.set_gait(sc.gait)
    runner = ScenarioRunner(sc)
    dt = cfg.sim.control_dt
    t0 = time.perf_counter()
    min_margin = 1.0
    with CsvLogger(cfg) as logger:
        while runner.apply(sim.controller, dt):
            f = sim.step(dt)
            logger.log(f)
            min_margin = min(min_margin, f.margin)
        wall = time.perf_counter() - t0
        s = sim.state
        speed = sc.duration / wall
        print(f"[{backend}] xong {sc.duration:.1f} s mô phỏng trong {wall:.2f} s ({speed:.0f}× thời gian thực)")
        print(f"  vị trí cuối: x={s.body_pos[0]:.3f} y={s.body_pos[1]:.3f} z={s.body_pos[2]:.3f} m, "
              f"yaw={s.rpy[2]:.2f} rad; lề ổn định nhỏ nhất {min_margin:.3f} m")
        print(f"  log: {logger.path} ({logger.rows} dòng)")
        path = logger.path
    if plot:
        from hexapod.viz.plots import plot_run
        plot_run(path)
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario", nargs="?", default="configs/scenarios/walk_square.yaml")
    ap.add_argument("--config", default=None)
    ap.add_argument("--plot", action="store_true")
    a = ap.parse_args()
    run(a.scenario, "kinematic", a.config, a.plot)
