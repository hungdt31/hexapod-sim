"""Vẽ log CSV bằng Matplotlib (debug, không cần frontend)."""

from __future__ import annotations

import csv
from pathlib import Path


def plot_run(csv_path: str | Path, show: bool = True, save: str | Path | None = None) -> None:
    import matplotlib.pyplot as plt

    with Path(csv_path).open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    t = [float(r["t"]) for r in rows]
    fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=False)
    ax[0].plot([float(r["body_x"]) for r in rows], [float(r["body_y"]) for r in rows], color="k", lw=2)
    ax[0].set_title("Quỹ đạo thân (nhìn từ trên)")
    ax[0].set_aspect("equal")
    for leg, col in ((0, "k"), (1, "#1B8A73")):
        ax[1].plot(t, [float(r[f"q_{leg}_1"]) for r in rows], color=col, lw=2, label=f"femur chân {leg}")
    ax[1].set_ylabel("rad")
    ax[1].legend()
    ax[2].plot(t, [float(r["stability_margin"]) for r in rows], color="k", lw=2)
    ax[2].axhline(0.01, color="#FF6B6B", ls="--")
    ax[2].set_ylabel("lề ổn định (m)")
    ax[2].set_xlabel("t (s)")
    fig.tight_layout()
    if save:
        fig.savefig(save, dpi=120)
    if show:
        plt.show()
