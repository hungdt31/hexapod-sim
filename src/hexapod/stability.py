"""Ổn định tĩnh: đa giác chống đỡ và lề ổn định."""

from __future__ import annotations

import numpy as np


def convex_hull(points: np.ndarray) -> np.ndarray:
    """Bao lồi (monotone chain), ngược chiều kim đồng hồ, shape (k, 2)."""
    pts = sorted(map(tuple, np.asarray(points, dtype=float)[:, :2].tolist())) if len(points) else []
    if len(pts) < 3:
        return np.array(pts, dtype=float).reshape(-1, 2)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: list = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return np.array(lower[:-1] + upper[:-1], dtype=float)


def stability_margin(polygon: np.ndarray, com_xy: np.ndarray) -> float:
    """Khoảng cách có dấu từ hình chiếu CoM tới cạnh gần nhất; âm = nằm ngoài đa giác."""
    if len(polygon) < 3:
        return -0.05
    inside, best = True, np.inf
    for i in range(len(polygon)):
        a, b = polygon[i], polygon[(i + 1) % len(polygon)]
        e = b - a
        cr = e[0] * (com_xy[1] - a[1]) - e[1] * (com_xy[0] - a[0])
        if cr < 0:
            inside = False
        best = min(best, abs(cr) / float(np.hypot(*e)))
    return float(best if inside else -best)
