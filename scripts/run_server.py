"""Khởi động server mô phỏng + web UI.

    python scripts/run_server.py                 # backend kinematic
    python scripts/run_server.py --backend mujoco --log-dir runs
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import uvicorn  # noqa: E402

from hexapod.config import RobotConfig  # noqa: E402
from hexapod.server.app import create_app  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None, help="file YAML cấu hình robot")
    ap.add_argument("--backend", default="kinematic", choices=["kinematic", "mujoco"])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--log-dir", default=None, help="thư mục ghi log CSV, ví dụ runs")
    a = ap.parse_args()
    app = create_app(RobotConfig.load(a.config), a.backend, a.log_dir)
    print(f"Mở http://{a.host}:{a.port}  (dev UI: http://localhost:5173)")
    uvicorn.run(app, host=a.host, port=a.port, log_level="info")
