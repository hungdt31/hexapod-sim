"""Ghi log trạng thái mỗi vòng điều khiển ra CSV (FR-17) + bản sao cấu hình (NFR-05)."""

from __future__ import annotations

import csv
import time
from pathlib import Path

from .. import LEG_NAMES
from ..config import RobotConfig


def _header() -> list[str]:
    cols = ["t", "body_x", "body_y", "body_z", "roll", "pitch", "yaw"]
    cols += [f"q_{i}_{j}" for i in range(6) for j in range(3)]
    cols += [f"q_cmd_{i}_{j}" for i in range(6) for j in range(3)]
    cols += [f"contact_{i}" for i in range(6)]
    cols += ["stability_margin"]
    return cols


class CsvLogger:
    def __init__(self, cfg: RobotConfig, root: str | Path = "runs", name: str | None = None) -> None:
        stamp = name or time.strftime("%Y%m%d-%H%M%S")
        self.dir = Path(root) / stamp
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / "config.yaml").write_text(cfg.dump_yaml(), encoding="utf-8")
        (self.dir / "legs.txt").write_text("\n".join(f"{i} {n}" for i, n in enumerate(LEG_NAMES)), encoding="utf-8")
        self.path = self.dir / "state.csv"
        self._f = self.path.open("w", newline="", encoding="utf-8")
        self._w = csv.writer(self._f)
        self._w.writerow(_header())
        self.rows = 0

    def log(self, frame) -> None:
        s, c = frame.state, frame.control
        roll, pitch, yaw = s.rpy
        row = [f"{s.t:.4f}", *(f"{v:.6f}" for v in s.body_pos), f"{roll:.6f}", f"{pitch:.6f}", f"{yaw:.6f}"]
        row += [f"{v:.6f}" for v in s.q.reshape(-1)]
        row += [f"{v:.6f}" for v in c.q.reshape(-1)]
        row += [str(int(b)) for b in s.contacts]
        row += [f"{frame.margin:.6f}"]
        self._w.writerow(row)
        self.rows += 1

    def close(self) -> None:
        self._f.close()

    def __enter__(self) -> CsvLogger:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
